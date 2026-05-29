"""Admin dashboard service."""
from typing import List, Dict, Optional, Set, Any
from datetime import datetime, timedelta
from uuid import UUID

from core.base.service import BaseService
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager
from core.telemetry.decorators import track_component_operation
from domain.models.admin import AdminOverview, InterviewMetrics, UserMetrics, SystemMetrics
from repositories.admin import AdminRepository
from core.types.components import HealthStatus, HealthStatusInfo
from core.types.metrics import MetricType



class AdminService(BaseService):
    """Service for admin operations."""

    REQUIRED_CONFIG = {
        "max_recent_activities": int,
        "max_alerts": int,
        "batch_size": int,
        "cache_ttl": int,
        "max_concurrent": int        
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        admin_repository: AdminRepository,
        metrics: MetricsManager,
        alert_manager: AlertManager,        
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize admin service.
        
        Args:
            name: Service name
            admin_repository: Repository for admin operations (required)
            metrics: Metrics collector (required)
            alert_manager: Alert manager (required)
            config: Application configuration (required)
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(
            name=name, 
            config=config, 
            metrics=metrics, 
            logger=logger or BackendLogger("admin_service"),
            dependencies=dependencies or set(),
            REQUIRED_CONFIG=self.REQUIRED_CONFIG
        )
    
        # Initialize required dependencies
        self.admin_repository = admin_repository
        self.alert_manager = alert_manager
        
        
        # Initialize admin settings from validated config with defaults
        self._max_recent_activities = self._config.get("max_recent_activities", 100)
        self._max_alerts = self._config.get("max_alerts", 50)       
        self._batch_size = self._config.get("batch_size", 100)
        self._cache_ttl = self._config.get("cache_ttl", 3600)
        self._max_concurrent = self._config.get("max_concurrent", 10)
        
        # Initialize health status
        self._health_status = HealthStatusInfo(
            status=HealthStatus.STARTING,
            details={
                "status": "initializing",
                "component": self.name,
                "config": {
                    "max_recent_activities": self._max_recent_activities,
                    "max_alerts": self._max_alerts,
                    "batch_size": self._batch_size,
                    "cache_ttl": self._cache_ttl,
                    "max_concurrent": self._max_concurrent
                }
            }
        )
        
        if self.metrics:
            self._register_metrics()

    def _register_metrics(self) -> None:
        """Register admin service metrics."""
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        self.metrics.register_metric(
            f"{self.name}_active_sessions",
            MetricType.GAUGE,
            f"Number of active chat sessions in {self.name}"
        )
        
        self.metrics.register_metric(
            f"{self.name}_session_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of chat sessions in {self.name}"
        )
        
        
        

    @track_component_operation("get_dashboard_overview")
    async def get_dashboard_overview(self) -> AdminOverview:
        """Get complete admin dashboard overview."""
        try:
            overview = await self.admin_repository.get_admin_overview()
            return overview
        except Exception as e:
            await self.alert_manager.send_alert(
                "admin_dashboard_failed",
                f"Failed to get admin dashboard: {str(e)}"
            )
            raise

    @track_component_operation("get_interview_metrics")
    async def get_interview_metrics(self) -> InterviewMetrics:
        """Get interview-related metrics."""
        try:
            metrics = await self.admin_repository.get_interview_metrics()
            return metrics
        except Exception as e:
            await self.alert_manager.send_alert(
                "interview_metrics_failed",
                f"Failed to get interview metrics: {str(e)}"
            )
            raise

    @track_component_operation("get_user_metrics")
    async def get_user_metrics(self) -> UserMetrics:
        """Get user-related metrics."""
        try:
            metrics = await self.admin_repository.get_user_metrics()
            return metrics
        except Exception as e:
            await self.alert_manager.send_alert(
                "user_metrics_failed",
                f"Failed to get user metrics: {str(e)}"
            )
            raise

    @track_component_operation("get_system_metrics")
    async def get_system_metrics(self) -> SystemMetrics:
        """Get system performance metrics."""
        try:
            metrics = await self.admin_repository.get_system_metrics()
            return metrics
        except Exception as e:
            await self.alert_manager.send_alert(
                "system_metrics_failed",
                f"Failed to get system metrics: {str(e)}"
            )
            raise

    @track_component_operation("get_recent_activities")
    async def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """Get recent system activities."""
        try:
            activities = await self.admin_repository.get_recent_activities(limit)
            return activities
        except Exception as e:
            await self.alert_manager.send_alert(
                "activities_lookup_failed",
                f"Failed to get recent activities: {str(e)}"
            )
            raise

    @track_component_operation("get_system_alerts")
    async def get_system_alerts(self) -> List[Dict]:
        """Get system alerts."""
        try:
            alerts = await self.admin_repository.get_system_alerts()
            return alerts
        except Exception as e:
            await self.alert_manager.send_alert(
                "alerts_lookup_failed",
                f"Failed to get system alerts: {str(e)}"
            )
            raise 