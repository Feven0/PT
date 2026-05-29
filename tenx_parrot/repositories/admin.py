"""Admin repository implementation."""
from typing import Optional, List, Dict, Any, Set, Union
from datetime import datetime, timedelta
from uuid import UUID

from core.types.base import ComponentNames as CN
from core.base import BaseRepository
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.cache.manager import CacheManager
from core.alert.manager import AlertManager
from core.base.unit_of_work import UnitOfWork
from core.base.registry import LifecycleRegistry
from core.types.metrics import MetricType
from domain.models.admin import (
    AdminOverview, 
    InterviewMetrics, 
    UserMetrics, 
    SystemMetrics
)
from core.config import AppConfig
from core.resilience.rate_limiter import RateLimiter
from core.resilience.retry import RetryWithBackoff
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.strapi.schemas import (
    IPersonaSession,
    IPersonaTrainee,
    IPersonaProfileInformation,
    IPersonaSessionOverallObserver
)

logger = BackendLogger(__name__)

class AdminError(Exception):
    """Base admin error."""
    pass


class ConfigError(AdminError):
    """Configuration error."""
    pass


class AdminRepository(BaseRepository[AdminOverview]):
    """Admin repository implementation."""

    REQUIRED_CONFIG = {
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        strapi_client: Optional[StrapiClient] = None,
        metrics: Optional[MetricsManager] = None,
        cache: Optional[CacheManager] = None,                        
        alert_manager: Optional[AlertManager] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Initialize admin repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Metrics manager
            cache: Cache manager instance
            strapi_client: Strapi client instance
            alert_manager: Alert manager instance
            dependencies: Optional set of dependencies
        """
        # Initialize base repository
        required_deps = {CN.metrics_manager, 
                         CN.cache_manager, 
                         CN.strapi_client, 
                         CN.alert_manager}
        if dependencies:
            required_deps.update(dependencies)
        

        super().__init__(
            name=name, 
            config=config, 
            metrics=metrics, 
            cache=cache, 
            dependencies=required_deps,
            required_config=self.REQUIRED_CONFIG
        )
        
        # Get validated repository config
        self._repository_config = self._config
        
        # Initialize admin repository settings from validated config
        self._cache_ttl = self._repository_config.get('cache_ttl', 3600)
        self._batch_size = self._repository_config.get('batch_size', 100)
        self._max_retries = self._repository_config.get('max_retries', 3)
        
        self.strapi_client = strapi_client
        self.cache = cache
        self.alert_manager = alert_manager
                
        # Initialize resilience components
        if metrics:
            self._register_metrics()
            

        
        # Get Strapi services
        strapi_factory = StrapiServiceFactory(strapi_client, metrics)
        self._session_service = strapi_factory.session_service
        self._trainee_service = strapi_factory.trainee_service
        self._profile_service = strapi_factory.profile_information_service
        self._observer_service = strapi_factory.session_overall_observer_service
        
        # Update health status with config details
        self.update_health_details({
            "config": {
                "cache_ttl": self._cache_ttl,
                "batch_size": self._batch_size,
                "max_retries": self._max_retries
            }
        })


    def _register_metrics(self) -> None:
        """Register repository metrics."""
        # Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"method": "", "path": "", "operation": "", "status": ""}
        )
        
        # Query Metrics
        self.metrics.register_metric(
            f"{self.name}_query_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of queries in {self.name}",
            labels={"method": "", "path": "", "operation": "", "status": ""}
        )

        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"method": "", "path": "", "error_type": ""}
        )

        # Health Metrics
        self.metrics.register_metric(
            f"{self.name}_health_check_status",
            MetricType.GAUGE,
            f"Current health check status in {self.name}",
            labels={"method": "", "path": "", "status": ""}
        )

        # Performance Metrics
        self.metrics.register_metric(
            f"{self.name}_performance_metrics",
            MetricType.GAUGE,
            f"Performance metrics in {self.name}",
            labels={"method": "", "path": "", "metric_type": ""}
        )

        # Cache Metrics
        self.metrics.register_metric(
            f"{self.name}_cache_hits_total",
            MetricType.COUNTER,
            f"Total number of cache hits in {self.name}",
            labels={"operation": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_cache_misses_total",
            MetricType.COUNTER,
            f"Total number of cache misses in {self.name}",
            labels={"operation": ""}
        )

        # Admin-specific Metrics
        self.metrics.register_metric(
            f"{self.name}_active_users",
            MetricType.GAUGE,
            f"Number of active users in {self.name}",
            labels={"method": "", "path": ""}
        )

        self.metrics.register_metric(
            f"{self.name}_system_alerts",
            MetricType.GAUGE,
            f"Number of active system alerts in {self.name}",
            labels={"method": "", "path": "", "alert_type": ""}
        )

    async def get_interview_metrics(self) -> InterviewMetrics:
        """Get interview-related metrics."""
        try:
            # Try cache first
            cache_key = "interview_metrics"
            if metrics_data := await self.cache.get(cache_key):
                return InterviewMetrics(**metrics_data)

            # Get active sessions count
            active_sessions = await self._session_service.count(
                filters={"status": "active"}
            )
            
            # Get completed sessions count
            completed_sessions = await self._session_service.count(
                filters={"status": "completed"}
            )
            
            # Get total sessions
            total_sessions = await self._session_service.count()
            
            # Calculate metrics
            metrics = InterviewMetrics(
                total_interviews=total_sessions,
                completed_interviews=completed_sessions,
                active_interviews=active_sessions,
                average_duration_minutes=await self._calculate_average_duration(),
                completion_rate=completed_sessions / total_sessions if total_sessions > 0 else 0.0
            )

            # Cache results
            await self.cache.set(cache_key, metrics.dict(), ttl=300)
            return metrics

        except Exception as e:
            await self.alert_manager.send_alert(
                "interview_metrics_failed",
                f"Failed to get interview metrics: {str(e)}"
            )
            raise

    async def get_user_metrics(self) -> UserMetrics:
        """Get user-related metrics."""
        try:
            # Try cache first
            cache_key = "user_metrics"
            if metrics_data := await self.cache.get(cache_key):
                return UserMetrics(**metrics_data)

            # Get total trainees
            total_trainees = await self._trainee_service.count()
            
            # Get active trainees (those with active sessions)
            active_trainees = await self._trainee_service.count(
                filters={"sessions": {"status": "active"}}
            )
            
            # Get new trainees in last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            new_trainees = await self._trainee_service.count(
                filters={"created_at_gte": thirty_days_ago.isoformat()}
            )

            metrics = UserMetrics(
                total_users=total_trainees,
                active_users=active_trainees,
                new_users_last_30_days=new_trainees
            )

            # Cache results
            await self.cache.set(cache_key, metrics.dict(), ttl=300)
            return metrics

        except Exception as e:
            await self.alert_manager.send_alert(
                "user_metrics_failed",
                f"Failed to get user metrics: {str(e)}"
            )
            raise

    async def get_system_metrics(self) -> SystemMetrics:
        """Get system performance metrics."""
        try:
            current_metrics = self.metrics.get_current_metrics()
            return SystemMetrics(
                average_response_time_ms=current_metrics.get("avg_response_time_ms", 0.0),
                error_rate=current_metrics.get("error_rate", 0.0),
                system_uptime_hours=current_metrics.get("uptime_hours", 0.0)
            )
        except Exception as e:
            await self.alert_manager.send_alert(
                "system_metrics_failed",
                f"Failed to get system metrics: {str(e)}"
            )
            raise

    async def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """Get recent system activities."""
        try:
            # Try cache first
            cache_key = f"recent_activities:{limit}"
            if activities := await self.cache.get(cache_key):
                return activities

            # Get recent sessions
            recent_sessions = await self._session_service.list(
                sort=["-created_at"],
                limit=limit
            )
            
            # Get recent observations
            recent_observations = await self._observer_service.list(
                sort=["-created_at"],
                limit=limit
            )
            
            # Combine and sort activities
            activities = []
            
            for session in recent_sessions:
                activities.append({
                    "type": "session",
                    "id": session.id,
                    "trainee_id": session.trainee_id,
                    "timestamp": session.created_at,
                    "details": session.attributes
                })
                
            for observation in recent_observations:
                activities.append({
                    "type": "observation",
                    "id": observation.id,
                    "trainee_id": observation.trainee_id,
                    "timestamp": observation.created_at,
                    "details": observation.attributes
                })
            
            # Sort by timestamp and limit
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            activities = activities[:limit]

            # Cache results
            await self.cache.set(cache_key, activities, ttl=60)
            return activities

        except Exception as e:
            await self.alert_manager.send_alert(
                "activities_lookup_failed",
                f"Failed to get recent activities: {str(e)}"
            )
            raise

    async def get_system_alerts(self) -> List[Dict]:
        """Get current system alerts."""
        try:
            return await self.alert_manager.get_active_alerts()
        except Exception as e:
            self.logger.error(
                "alerts_lookup_failed",
                error=str(e)
            )
            return []

    async def get_admin_overview(self) -> AdminOverview:
        """Get complete admin dashboard overview."""
        try:
            # Try cache first
            cache_key = "admin_overview"
            if overview_data := await self.cache.get(cache_key):
                return AdminOverview(**overview_data)

            # Gather all metrics
            interview_metrics = await self.get_interview_metrics()
            user_metrics = await self.get_user_metrics()
            system_metrics = await self.get_system_metrics()
            recent_activities = await self.get_recent_activities()
            alerts = await self.get_system_alerts()

            overview = AdminOverview(
                interview_metrics=interview_metrics,
                user_metrics=user_metrics,
                system_metrics=system_metrics,
                recent_activities=recent_activities,
                alerts=alerts
            )

            # Cache results
            await self.cache.set(cache_key, overview.dict(), ttl=60)
            return overview

        except Exception as e:
            await self.alert_manager.send_alert(
                "admin_overview_failed",
                f"Failed to get admin overview: {str(e)}"
            )
            raise

    async def _calculate_average_duration(self) -> float:
        """Calculate average session duration in minutes."""
        try:
            completed_sessions = await self._session_service.list(
                filters={"status": "completed"},
                limit=self._batch_size
            )
            
            if not completed_sessions:
                return 0.0
                
            total_duration = sum(
                (session.end_time - session.start_time).total_seconds() / 60
                for session in completed_sessions
                if session.end_time and session.start_time
            )
            
            return total_duration / len(completed_sessions)
            
        except Exception as e:
            self.logger.error(
                "duration_calculation_failed",
                error=str(e)
            )
            return 0.0 