"""Overall observer repository implementation."""
from typing import Optional, Dict, Any, List, Set
from datetime import datetime
import asyncio
import time

from core.types.base import ComponentNames as CN
from core.base import BaseRepository
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager
from core.cache.manager import CacheManager
from core.resilience.rate_limiter import RateLimiter
from core.resilience.retry import RetryWithBackoff
from core.types.metrics import MetricType
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.strapi.schemas import IPersonaSessionOverallObserver, IPersonaSessionOverallObserverSchema


class OverallObserverError(Exception):
    """Base overall observer error."""
    pass


class ConfigError(OverallObserverError):
    """Configuration error."""
    pass


class OverallObserverRepository(BaseRepository[IPersonaSessionOverallObserver]):
    """Overall observer repository implementation."""

    REQUIRED_CONFIG = {
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        cache: Optional[CacheManager] = None,        
        strapi_client: Optional[StrapiClient] = None,
        alert_manager: Optional[AlertManager] = None,
        dependencies: Optional[Set[str]] = None,
    ):
        """Initialize overall observer repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Optional metrics manager
            cache: Optional cache manager
            dependencies: Optional set of dependencies
            strapi_client: Optional Strapi client instance
            alert_manager: Optional alert manager instance
        """
        # Initialize base repository
        required_deps = {CN.metrics_manager, 
                         CN.cache_manager, 
                         CN.strapi_client, 
                         CN.alert_manager}
        if dependencies:
            required_deps.update(dependencies)
            
        self.strapi_client = strapi_client
        self.cache = cache
        self.alert_manager = alert_manager

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
        
        # Initialize observer repository settings from validated config
        self._cache_ttl = self._repository_config.get('cache_ttl', 3600)
        self._batch_size = self._repository_config.get('batch_size', 100)
        self._max_retries = self._repository_config.get('max_retries', 3)
        
        # Initialize resilience components
        if metrics:
            self._register_metrics()
            
        
        # Get Strapi service for overall observers
        self._observer_service = (StrapiServiceFactory(strapi_client, metrics)
                                .session_overall_observer_service)
        
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
            labels={"operation": "", "status": ""}
        )
        
        # Query Metrics
        self.metrics.register_metric(
            f"{self.name}_query_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of queries in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Observer Metrics
        self.metrics.register_metric(
            f"{self.name}_active_observers",
            MetricType.GAUGE,
            f"Number of active overall observers in {self.name}",
            labels={"user_id": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_total_observers",
            MetricType.COUNTER,
            f"Total number of overall observers in {self.name}"
        )
        
        self.metrics.register_metric(
            f"{self.name}_observer_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of overall observers in {self.name}",
            labels={"type": "", "status": ""}
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
        
        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )

    async def create_observer(
        self,
        user_id: str,
        job_id: str,
        attributes: Dict[str, Any]
    ) -> IPersonaSessionOverallObserver:
        """Create a new overall observer.
        
        Args:
            user_id: User ID
            job_id: Job ID
            attributes: Observer attributes
            
        Returns:
            Created observer
            
        Raises:
            OverallObserverError: If creation fails
        """
        try:
            # Create observer using Strapi service
            observer = IPersonaSessionOverallObserver(
                id="",  # Will be set by Strapi
                attributes=attributes,
                tinder_user_profile_id=user_id,
                tinder_job_profile_id=job_id
            )
            
            result = await self._observer_service.create(observer)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_total_observers",
                    1
                )
                self.metrics.record(
                    f"{self.name}_active_observers",
                    1,
                    labels={"user_id": user_id}
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
            raise OverallObserverError(f"Failed to create overall observer: {str(e)}")

    async def get_observer(self, observer_id: str) -> Optional[IPersonaSessionOverallObserver]:
        """Get an overall observer.
        
        Args:
            observer_id: Observer ID
            
        Returns:
            Observer if found, None otherwise
            
        Raises:
            OverallObserverError: If retrieval fails
        """
        try:
            # Try cache first
            cache_key = f"overall_observer:{observer_id}"
            if observer_data := await self.cache.get(cache_key):
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_cache_hits_total",
                        1,
                        labels={"operation": "get"}
                    )
                return IPersonaSessionOverallObserver(**observer_data)
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_cache_misses_total",
                    1,
                    labels={"operation": "get"}
                )
            
            # Get from Strapi
            observer = await self._observer_service.get(observer_id)
            
            if observer:
                # Cache result
                await self.cache.set(cache_key, observer.dict(), ttl=self._cache_ttl)
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_operations_total",
                        1,
                        labels={"operation": "get", "status": "success"}
                    )
                    
            return observer
            
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
            raise OverallObserverError(f"Failed to get overall observer: {str(e)}")

    async def list_observers(
        self,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[IPersonaSessionOverallObserver]:
        """List overall observers.
        
        Args:
            user_id: Optional user ID filter
            job_id: Optional job ID filter
            limit: Optional result limit
            offset: Optional result offset
            
        Returns:
            List of observers
            
        Raises:
            OverallObserverError: If listing fails
        """
        try:
            # Build filters
            filters = {}
            if user_id:
                filters["tinder_user_profile_id"] = user_id
            if job_id:
                filters["tinder_job_profile_id"] = job_id
                
            # Get from Strapi
            observers = await self._observer_service.list(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "list", "status": "success"}
                )
                
            return observers
            
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
            raise OverallObserverError(f"Failed to list overall observers: {str(e)}")

    async def update_observer(
        self,
        observer_id: str,
        updates: Dict[str, Any]
    ) -> Optional[IPersonaSessionOverallObserver]:
        """Update an overall observer.
        
        Args:
            observer_id: Observer ID
            updates: Fields to update
            
        Returns:
            Updated observer if found
            
        Raises:
            OverallObserverError: If update fails
        """
        try:
            # Get current observer
            observer = await self.get_observer(observer_id)
            if not observer:
                return None
                
            # Apply updates
            for key, value in updates.items():
                setattr(observer, key, value)
                
            # Update in Strapi
            updated = await self._observer_service.update(observer_id, observer)
            
            if updated:
                # Invalidate cache
                cache_key = f"overall_observer:{observer_id}"
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
            raise OverallObserverError(f"Failed to update overall observer: {str(e)}")

    async def delete_observer(self, observer_id: str) -> bool:
        """Delete an overall observer.
        
        Args:
            observer_id: Observer ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            OverallObserverError: If deletion fails
        """
        try:
            # Delete from Strapi
            result = await self._observer_service.delete(observer_id)
            
            if result:
                # Invalidate cache
                cache_key = f"overall_observer:{observer_id}"
                await self.cache.delete(cache_key)
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_operations_total",
                        1,
                        labels={"operation": "delete", "status": "success"}
                    )
                    
            return result
            
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
            raise OverallObserverError(f"Failed to delete overall observer: {str(e)}") 