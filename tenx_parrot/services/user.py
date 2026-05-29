"""User service implementation."""
from typing import Dict, Any, Optional, Set
import time

from core.base.service import BaseService
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert import AlertManager
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation
from repositories.user import UserRepository

class UserService(BaseService):
    """User service implementation."""

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        alert_manager: Optional[AlertManager] = None,
        user_repository: Optional[UserRepository] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize user service.
        
        Args:
            name: Service name
            config: Application configuration
            metrics: Optional metrics manager
            alert_manager: Optional alert manager
            user_repository: User repository instance
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
        
        self.alert_manager = alert_manager
        self.user_repository = user_repository

        # Initialize user service settings from config
        self._session_timeout = self._config.get("session_timeout", 3600)  # 1 hour default
        self._max_sessions = self._config.get("max_sessions", 1000)
        self._max_retries = self._config.get("max_retries", 3)
        
        # Update health status with user service specific details
        self._health_status.details.update({
            "session_timeout": self._session_timeout,
            "max_sessions": self._max_sessions,
            "max_retries": self._max_retries
        })

        # Register metrics if available
        if self.metrics:
            self._register_metrics()

    def _register_metrics(self) -> None:
        """Register service metrics."""
        # Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # User Metrics
        self.metrics.register_metric(
            f"{self.name}_active_users",
            MetricType.GAUGE,
            f"Current number of active users in {self.name}",
            labels={"type": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_user_sessions",
            MetricType.GAUGE,
            f"Current number of user sessions in {self.name}",
            labels={"user_id": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_user_operations_total",
            MetricType.COUNTER,
            f"Total number of user operations in {self.name}",
            labels={"operation": "", "status": "", "user_id": ""}
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

    @track_component_operation("initialize")
    async def _do_initialize(self) -> None:
        """Initialize user service."""
        try:
            # Initialize user repository
            if self.user_repository:
                await self.user_repository.initialize()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "initialize"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "error"}
                )
            raise

    @track_component_operation("start")
    async def _do_start(self) -> None:
        """Start user service."""
        try:
            # Start user repository
            if self.user_repository:
                await self.user_repository.start()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "start"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "error"}
                )
            raise

    @track_component_operation("stop")
    async def _do_stop(self) -> None:
        """Stop user service."""
        try:
            # Stop user repository
            if self.user_repository:
                await self.user_repository.stop()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_users",
                    0,
                    labels={"type": "total", "status": "active"}
                )
                self.metrics.record(
                    f"{self.name}_user_sessions",
                    0,
                    labels={"user_id": "total", "status": "active"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "stop"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "error"}
                )
            raise 