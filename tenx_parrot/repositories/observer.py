"""Observer repository implementation."""
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
from infrastructure.strapi.schemas import IPersonaSessionObserver, IPersonaSessionObserverSchema


class ObserverError(Exception):
    """Base observer error."""
    pass


class ConfigError(ObserverError):
    """Configuration error."""
    pass


class ObserverNotFoundError(ObserverError):
    """Error raised when observer is not found."""
    pass


class ObserverCreationError(ObserverError):
    """Error raised when observer creation fails."""
    pass


class ObserverUpdateError(ObserverError):
    """Error raised when observer update fails."""
    pass


class ObserverDeletionError(ObserverError):
    """Error raised when observer deletion fails."""
    pass


class ObserverRepository(BaseRepository[IPersonaSessionObserver]):
    """Observer repository implementation."""

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
        dependencies: Optional[Set[str]] = None,
        strapi_client: Optional[StrapiClient] = None,
        alert_manager: Optional[AlertManager] = None
    ):
        """Initialize observer repository.
        
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
            
        
        # Get Strapi service for observers
        self._observer_service = (StrapiServiceFactory(strapi_client, metrics)
                                .session_observer_service)
        
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
            f"Number of active observers in {self.name}",
            labels={"session_id": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_total_observers",
            MetricType.COUNTER,
            f"Total number of observers in {self.name}"
        )
        
        self.metrics.register_metric(
            f"{self.name}_observer_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of observers in {self.name}",
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
        session_id: str,
        attributes: Dict[str, Any]
    ) -> IPersonaSessionObserver:
        """Create a new observer.
        
        Args:
            session_id: Session ID (string)
            attributes: Observer attributes
            
        Returns:
            Created observer
            
        Raises:
            ObserverCreationError: If creation fails
        """
        try:
            # Create observer using Strapi service
            observer = IPersonaSessionObserver(
                id="",  # Will be set by Strapi
                attributes=attributes,
                i_persona_session_id=session_id
            )
            
            result = await self._observer_service.create(observer)
            
            if not result:
                raise ObserverCreationError(f"Failed to create observer for session {session_id}")
            
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
                    labels={"session_id": session_id}
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
            raise ObserverCreationError(f"Failed to create observer: {str(e)}") from e

    async def get_observer(self, observer_id: str) -> Optional[IPersonaSessionObserver]:
        """Get an observer.
        
        Args:
            observer_id: Observer ID (string)
            
        Returns:
            Observer if found, None otherwise
            
        Raises:
            ObserverNotFoundError: If observer is not found
            ObserverError: If retrieval fails
        """
        try:
            # Try cache first
            cache_key = f"observer:{observer_id}"
            if observer_data := await self.cache.get(cache_key):
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_cache_hits_total",
                        1,
                        labels={"operation": "get"}
                    )
                return IPersonaSessionObserver(**observer_data)
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_cache_misses_total",
                    1,
                    labels={"operation": "get"}
                )
            
            # Get from Strapi
            observer = await self._observer_service.get(observer_id)
            
            if not observer:
                raise ObserverNotFoundError(f"Observer with ID {observer_id} not found")
            
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
            
        except ObserverNotFoundError:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get", "status": "not_found"}
                )
            raise
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
            raise ObserverError(f"Failed to get observer: {str(e)}") from e

    async def list_observers(
        self,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[IPersonaSessionObserver]:
        """List observers.
        
        Args:
            session_id: Optional session ID filter (string)
            limit: Optional result limit
            offset: Optional result offset
            
        Returns:
            List of observers
            
        Raises:
            ObserverError: If listing fails
        """
        try:
            # Build filters
            filters = {}
            if session_id:
                filters["i_persona_session_id"] = session_id
                
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
            raise ObserverError(f"Failed to list observers: {str(e)}") from e

    async def update_observer(
        self,
        observer_id: str,
        updates: Dict[str, Any]
    ) -> Optional[IPersonaSessionObserver]:
        """Update an observer.
        
        Args:
            observer_id: Observer ID (string)
            updates: Fields to update
            
        Returns:
            Updated observer if found
            
        Raises:
            ObserverNotFoundError: If observer is not found
            ObserverUpdateError: If update fails
        """
        try:
            # Get current observer
            observer = await self.get_observer(observer_id)
            if not observer:
                raise ObserverNotFoundError(f"Observer with ID {observer_id} not found")
                
            # Apply updates
            for key, value in updates.items():
                setattr(observer, key, value)
                
            # Update in Strapi
            updated = await self._observer_service.update(observer_id, observer)
            
            if not updated:
                raise ObserverUpdateError(f"Failed to update observer with ID {observer_id}")
            
            if updated:
                # Invalidate cache
                cache_key = f"observer:{observer_id}"
                await self.cache.delete(cache_key)
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_operations_total",
                        1,
                        labels={"operation": "update", "status": "success"}
                    )
                    
            return updated
            
        except ObserverNotFoundError:
            raise
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
            raise ObserverUpdateError(f"Failed to update observer: {str(e)}") from e

    async def delete_observer(self, observer_id: str) -> bool:
        """Delete an observer.
        
        Args:
            observer_id: Observer ID (string)
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ObserverNotFoundError: If observer is not found
            ObserverDeletionError: If deletion fails
        """
        try:
            # Check if observer exists
            observer = await self.get_observer(observer_id)
            if not observer:
                raise ObserverNotFoundError(f"Observer with ID {observer_id} not found")
            
            # Delete from Strapi
            result = await self._observer_service.delete(observer_id)
            
            if not result:
                raise ObserverDeletionError(f"Failed to delete observer with ID {observer_id}")
            
            # Invalidate cache
            cache_key = f"observer:{observer_id}"
            await self.cache.delete(cache_key)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "delete", "status": "success"}
                )
                
            return True
            
        except ObserverNotFoundError:
            raise
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
            raise ObserverDeletionError(f"Failed to delete observer: {str(e)}") from e 