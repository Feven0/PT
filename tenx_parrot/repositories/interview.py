"""Interview repository implementation."""
from typing import Dict, Any, Optional, Set, Union, List
import time
from datetime import datetime

from core.types.base import ComponentNames as CN
from core.base import BaseRepository
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.cache.manager import CacheManager
from core.alert.manager import AlertManager
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.strapi.schemas import (
    IPersonaSession,
    IPersonaTrainee,
    IPersonaProfileInformation,
    IPersonaSessionObserver,
    IPersonaSessionOverallObserver
)
from infrastructure.weaviate.client import WeaviateInfrastructureClient
from infrastructure.weaviate.dynamic import WeaviateDynamicService
from infrastructure.weaviate.schemas import get_schema
from core.types.components import HealthStatus


class InterviewError(Exception):
    """Base interview error."""
    pass


class ConfigError(InterviewError):
    """Configuration error."""
    pass


class InterviewRepository(BaseRepository[IPersonaSession]):
    """Interview repository implementation."""

    REQUIRED_CONFIG = {
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int,
        'max_interviews': int
    }

    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional['MetricsManager'] = None,
        cache: Optional[CacheManager] = None,
        strapi_client: Optional[StrapiClient] = None,
        weaviate_client: Optional[WeaviateInfrastructureClient] = None,
        alert_manager: Optional[AlertManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Initialize interview repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Optional metrics manager
            cache: Optional cache manager
            strapi_client: Optional Strapi client instance
            weaviate_client: Optional Weaviate client instance
            alert_manager: Optional alert manager instance
            dependencies: Optional set of dependency names
        """
        # Initialize with required dependencies
        required_deps = {CN.metrics_manager, 
                         CN.cache_manager, 
                         CN.strapi_client,
                         CN.weaviate_client,
                         CN.alert_manager}
        if dependencies:
            required_deps.update(dependencies)
                    
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            cache=cache,
            logger=logger,
            dependencies=dependencies,
            required_config=self.REQUIRED_CONFIG
        )        

        self.strapi_client = strapi_client
        self.weaviate_client = weaviate_client
        self.cache = cache
        self.alert_manager = alert_manager
        
        # Initialize services
        self.weaviate_service = WeaviateDynamicService(
            client=weaviate_client,
            schema=get_schema("Interview"),
            logger=self.logger
        )
        
        # Initialize Strapi services
        strapi_factory = StrapiServiceFactory(strapi_client, metrics)
        self._session_service = strapi_factory.session_service
        self._trainee_service = strapi_factory.trainee_service
        self._profile_service = strapi_factory.profile_information_service
        
        # Get validated repository config
        self._repository_config = self._config
        
        # Initialize interview repository settings from validated config
        self._cache_ttl = self._repository_config.get('cache_ttl', 3600)
        self._batch_size = self._repository_config.get('batch_size', 100)
        self._max_retries = self._repository_config.get('max_retries', 3)
        self._max_interviews = self._repository_config.get('max_interviews', 1000)
        
        # Initialize resilience components
        if metrics:
            self._register_metrics()
            
        # Update health status with config details
        self.update_health_details({
            "config": {
                "cache_ttl": self._cache_ttl,
                "batch_size": self._batch_size,
                "max_retries": self._max_retries,
                "max_interviews": self._max_interviews,
            }
        })

    async def initialize(self) -> None:
        """Initialize repository."""
        await self.weaviate_service.initialize()

    def _register_metrics(self) -> None:
        """Register repository metrics."""
        # Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Interview Metrics
        self.metrics.register_metric(
            f"{self.name}_active_interviews",
            MetricType.GAUGE,
            f"Current number of active interviews in {self.name}",
            labels={"type": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_interview_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of interviews in {self.name}",
            labels={"interview_id": "", "status": ""}
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
        
        # Performance Metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )

    @track_component_operation("create_interview")
    async def create_interview(
        self,
        trainee_id: str,
        profile_id: str,
        attributes: Dict[str, Any]
    ) -> IPersonaSession:
        """Create a new interview session.
        
        Args:
            trainee_id: ID of the trainee
            profile_id: ID of the profile
            attributes: Additional attributes for the interview
            
        Returns:
            IPersonaSession: Created interview session
            
        Raises:
            InterviewError: If creation fails
        """
        try:
            # Verify trainee exists
            trainee = await self._trainee_service.get(trainee_id)
            if not trainee:
                raise InterviewError(f"Trainee {trainee_id} not found")
                
            # Verify profile exists
            profile = await self._profile_service.get(profile_id)
            if not profile:
                raise InterviewError(f"Profile {profile_id} not found")
                
            # Create session in Strapi
            session = IPersonaSession(
                id="",  # Will be set by Strapi
                attributes=attributes,
                trainee_id=trainee_id,
                profile_id=profile_id
            )
            
            result = await self._session_service.create(session)
            
            # Create in Weaviate
            weaviate_data = {
                "id": result.id,
                "trainee_id": trainee_id,
                "profile_id": profile_id,
                "attributes": attributes,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            await self.weaviate_service.create(weaviate_data)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_interviews",
                    1,
                    labels={"type": "session", "status": "active"}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create"}
                )
            raise InterviewError(f"Failed to create interview: {str(e)}")

    @track_component_operation("get_interview")
    async def get_interview(self, interview_id: str) -> Optional[IPersonaSession]:
        """Get an interview session.
        
        Args:
            interview_id: ID of the interview to retrieve
            
        Returns:
            IPersonaSession: Retrieved interview session or None if not found
            
        Raises:
            InterviewError: If retrieval fails
        """
        try:
            # Try cache first
            cache_key = f"interview:{interview_id}"
            if interview_data := await self.cache.get(cache_key):
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_cache_hits_total",
                        1,
                        labels={"operation": "get"}
                    )
                return IPersonaSession(**interview_data)
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_cache_misses_total",
                    1,
                    labels={"operation": "get"}
                )
            
            # Get from Strapi
            interview = await self._session_service.get(interview_id)
            
            if not interview:
                return None
                
            # Cache for future use
            await self.cache.set(
                cache_key,
                interview.to_dict(),
                ttl=self._cache_ttl
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get", "status": "success"}
                )
                
            return interview
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "get"}
                )
            raise InterviewError(f"Failed to get interview: {str(e)}")

    @track_component_operation("list_interviews")
    async def list_interviews(
        self,
        trainee_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[IPersonaSession]:
        """List interview sessions."""
        try:
            # Build filters
            filters = {}
            if trainee_id:
                filters["trainee_id"] = trainee_id
            if profile_id:
                filters["profile_id"] = profile_id
                
            # Get from Weaviate for better search capabilities
            weaviate_results = await self.weaviate_service.search(
                query="",
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Get full data from Strapi
            interviews = []
            for result in weaviate_results:
                interview = await self._session_service.get(result["id"])
                if interview:
                    interview.attributes.update(result.get("attributes", {}))
                    interviews.append(interview)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "list", "status": "success"}
                )
                
            return interviews
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "list", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "list"}
                )
            raise InterviewError(f"Failed to list interviews: {str(e)}")

    @track_component_operation("update_interview")
    async def update_interview(
        self,
        interview_id: str,
        updates: Dict[str, Any]
    ) -> Optional[IPersonaSession]:
        """Update an interview session.
        
        Args:
            interview_id: Interview ID
            updates: Fields to update
            
        Returns:
            Updated interview session if found
            
        Raises:
            InterviewError: If update fails
        """
        try:
            # Get current interview
            interview = await self.get_interview(interview_id)
            if not interview:
                return None
                
            # Apply updates
            for key, value in updates.items():
                setattr(interview, key, value)
                
            # Update in Strapi
            updated = await self._session_service.update(interview_id, interview)
            
            if updated:
                # Update in Weaviate
                weaviate_data = {
                    "attributes": updates,
                    "updated_at": datetime.now().isoformat()
                }
                await self.weaviate_service.update(interview_id, weaviate_data)
                
                # Invalidate cache
                cache_key = f"interview:{interview_id}"
                await self.cache.delete(cache_key)
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_operations_total",
                        1,
                        labels={"operation": "update", "status": "success"}
                    )
                    
            return updated
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "update", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "update"}
                )
            raise InterviewError(f"Failed to update interview: {str(e)}")

    @track_component_operation("delete_interview")
    async def delete_interview(self, interview_id: str) -> bool:
        """Delete an interview session.
        
        Args:
            interview_id: Interview ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            InterviewError: If deletion fails
        """
        try:
            # Delete from both storages
            strapi_success = await self._session_service.delete(interview_id)
            weaviate_success = await self.weaviate_service.delete(interview_id)
            
            if strapi_success and weaviate_success:
                # Invalidate cache
                cache_key = f"interview:{interview_id}"
                await self.cache.delete(cache_key)
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_operations_total",
                        1,
                        labels={"operation": "delete", "status": "success"}
                    )
                    self.metrics.record(
                        f"{self.name}_active_interviews",
                        -1,
                        labels={"type": "session", "status": "active"}
                    )
                    
            return strapi_success and weaviate_success
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "delete", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "delete"}
                )
            raise InterviewError(f"Failed to delete interview: {str(e)}")

    async def search_interviews(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[IPersonaSession]:
        """Search interview sessions."""
        try:
            # Search in Weaviate
            results = await self.weaviate_service.search(
                query=query,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Get full data from Strapi
            interviews = []
            for result in results:
                interview = await self._session_service.get(result["id"])
                if interview:
                    interview.attributes.update(result.get("attributes", {}))
                    interviews.append(interview)
                    
            return interviews
            
        except Exception as e:
            self.logger.error(f"Failed to search interviews: {str(e)}")
            return []

    async def cleanup(self) -> None:
        """Cleanup repository resources."""
        await super().cleanup()
        # Clear any cached data
        if self.cache:
            try:
                # Clear all interview-related cache entries
                await self.cache.clear()
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"Failed to cleanup interview cache: {str(e)}",
                        context="interview_repository",
                        error=str(e)
                    )

    async def check_health(self) -> Dict[str, Any]:
        """Check repository health.
        
        Returns:
            Health check results
        """
        health_status = await super().check_health()
        results = health_status.details

        # Check Weaviate connection
        try:
            weaviate_health = await self.weaviate_client.get_health()
            results.update({'weaviate_status': HealthStatus.HEALTHY})
        except Exception as e:
            results.update({'weaviate_status': HealthStatus.UNHEALTHY})

        return results
