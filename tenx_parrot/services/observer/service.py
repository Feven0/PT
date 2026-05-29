# Create backend/services/observer/service.py
"""Observer management service."""
from typing import Dict, Any, Optional, List, Set, Union
from datetime import datetime, timezone
from uuid import UUID

from core.base.service import BaseService
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.config.base import AppConfig
from core.types.metrics import MetricType
from core.errors.exceptions import ServiceError
from repositories.observer import ObserverRepository
from repositories.overall_observer import OverallObserverRepository

logger = BackendLogger(__name__).get_logger()

class ObserverError(ServiceError):
    """Observer service error."""
    pass

class ObserverService(BaseService):
    """Observer management service."""
    
    REQUIRED_CONFIG = {
        "cache_ttl": int,
        "batch_size": int,
        "max_retries": int
    }
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        observer_repository: ObserverRepository,
        overall_observer_repository: OverallObserverRepository,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize service.
        
        Args:
            name: Service name
            config: Application configuration
            observer_repository: Observer repository
            overall_observer_repository: Overall observer repository
            metrics: Optional metrics manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        self.observer_repository = observer_repository
        self.overall_observer_repository = overall_observer_repository
        
        # Register metrics if available
        if self.metrics:
            self._register_metrics()
    
    def _register_metrics(self) -> None:
        """Register observer metrics."""
        # Operation metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Observer metrics
        self.metrics.register_metric(
            f"{self.name}_active_observers",
            MetricType.GAUGE,
            f"Number of active observers in {self.name}"
        )
        
        self.metrics.register_metric(
            f"{self.name}_observations_total",
            MetricType.COUNTER,
            f"Total number of observations in {self.name}",
            labels={"type": "", "session_id": ""}
        )
        
        # Error metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )
    
    async def create_observer(
        self,
        session_id: str,
        observer_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an observer for a session.
        
        Args:
            session_id: Session ID
            observer_config: Observer configuration
            
        Returns:
            Created observer
        """
        try:
            observer = await self.observer_repository.create_observer(
                session_id=session_id,
                observer_data=observer_config
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create_observer", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_observers",
                    1
                )
            
            return observer
            
        except Exception as e:
            self.logger.error(f"Failed to create observer: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create_observer", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create_observer"}
                )
            raise ObserverError(f"Failed to create observer: {str(e)}")
    
    async def get_observer(
        self,
        observer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get observer by ID.
        
        Args:
            observer_id: Observer ID
            
        Returns:
            Observer if found, None otherwise
        """
        try:
            observer = await self.observer_repository.get_observer(observer_id)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_observer", "status": "success"}
                )
            
            return observer
            
        except Exception as e:
            self.logger.error(f"Failed to get observer: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_observer", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "get_observer"}
                )
            raise ObserverError(f"Failed to get observer: {str(e)}")
    
    async def list_observers(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List observers for a session.
        
        Args:
            session_id: Session ID
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of observers
        """
        try:
            observers = await self.observer_repository.list_observers(
                session_id=session_id,
                limit=limit,
                offset=offset
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "list_observers", "status": "success"}
                )
            
            return observers
            
        except Exception as e:
            self.logger.error(f"Failed to list observers: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "list_observers", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "list_observers"}
                )
            raise ObserverError(f"Failed to list observers: {str(e)}")
    
    async def update_observer(
        self,
        observer_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update observer.
        
        Args:
            observer_id: Observer ID
            updates: Updates to apply
            
        Returns:
            Updated observer
        """
        try:
            observer = await self.observer_repository.update_observer(
                observer_id=observer_id,
                updates=updates
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "update_observer", "status": "success"}
                )
            
            return observer
            
        except Exception as e:
            self.logger.error(f"Failed to update observer: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "update_observer", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "update_observer"}
                )
            raise ObserverError(f"Failed to update observer: {str(e)}")
    
    async def delete_observer(
        self,
        observer_id: str
    ) -> bool:
        """Delete observer.
        
        Args:
            observer_id: Observer ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.observer_repository.delete_observer(observer_id)
            
            # Record metrics
            if self.metrics and result:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "delete_observer", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_observers",
                    -1
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete observer: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "delete_observer", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "delete_observer"}
                )
            raise ObserverError(f"Failed to delete observer: {str(e)}")
    
    async def store_observation(
        self,
        session_id: str,
        observer_id: str,
        observation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store an observation.
        
        Args:
            session_id: Session ID
            observer_id: Observer ID
            observation: Observation data
            
        Returns:
            Stored observation
        """
        try:
            result = await self.observer_repository.store_observation(
                session_id=session_id,
                observer_id=observer_id,
                observation=observation
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "store_observation", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_observations_total",
                    1,
                    labels={
                        "type": observation.get("type", "unknown"),
                        "session_id": session_id
                    }
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to store observation: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "store_observation", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "store_observation"}
                )
            raise ObserverError(f"Failed to store observation: {str(e)}")
    
    async def get_observations(
        self,
        session_id: str,
        observer_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get observations for a session.
        
        Args:
            session_id: Session ID
            observer_id: Optional observer ID to filter by
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of observations
        """
        try:
            observations = await self.observer_repository.get_observations(
                session_id=session_id,
                observer_id=observer_id,
                limit=limit,
                offset=offset
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_observations", "status": "success"}
                )
            
            return observations
            
        except Exception as e:
            self.logger.error(f"Failed to get observations: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_observations", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "get_observations"}
                )
            raise ObserverError(f"Failed to get observations: {str(e)}")
    
    async def create_overall_observer(
        self,
        session_id: str,
        observer_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an overall observer for a session.
        
        Args:
            session_id: Session ID
            observer_config: Observer configuration
            
        Returns:
            Created overall observer
        """
        try:
            observer = await self.overall_observer_repository.create_observer(
                session_id=session_id,
                observer_data=observer_config
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create_overall_observer", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_observers",
                    1
                )
            
            return observer
            
        except Exception as e:
            self.logger.error(f"Failed to create overall observer: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create_overall_observer", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create_overall_observer"}
                )
            raise ObserverError(f"Failed to create overall observer: {str(e)}")
    
    async def get_overall_observer(
        self,
        observer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get overall observer by ID.
        
        Args:
            observer_id: Observer ID
            
        Returns:
            Overall observer if found, None otherwise
        """
        try:
            observer = await self.overall_observer_repository.get_observer(observer_id)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_overall_observer", "status": "success"}
                )
            
            return observer
            
        except Exception as e:
            self.logger.error(f"Failed to get overall observer: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_overall_observer", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "get_overall_observer"}
                )
            raise ObserverError(f"Failed to get overall observer: {str(e)}")
    
    async def notify_observers(
        self,
        session_id: str,
        event: Dict[str, Any]
    ) -> None:
        """Notify all observers for a session.
        
        Args:
            session_id: Session ID
            event: Event data to send to observers
        """
        try:
            # Get all observers for the session
            observers = await self.list_observers(session_id)
            
            # Notify each observer
            for observer in observers:
                await self.observer_repository.notify_observer(
                    observer_id=observer["id"],
                    event=event
                )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "notify_observers", "status": "success"}
                )
            
        except Exception as e:
            self.logger.error(f"Failed to notify observers: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "notify_observers", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "notify_observers"}
                )
            raise ObserverError(f"Failed to notify observers: {str(e)}")