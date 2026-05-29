"""Base component implementation."""
from typing import Dict, Any, Optional, Set, TYPE_CHECKING, TypeVar, Generic, Union
import asyncio
from datetime import datetime, timezone
from time import perf_counter

from core.logging import BackendLogger
    
if TYPE_CHECKING:
    from core.telemetry.metrics import MetricsManager

from core.types.components import (
    HealthStatus,
    ComponentState,
    HealthStatusInfo,
    ComponentStateInfo
)
from core.config import AppConfig
from core.types.metrics import MetricType

from .lifecycle import LifecycleAware

class BaseComponent(LifecycleAware):
    """Base component implementation."""
    
    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        logger: Optional['BackendLogger'] = None,
        metrics: Optional['MetricsManager'] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize base component.
        
        Args:
            name: Component name
            config: Component configuration or AppConfig
            logger: Logger instance
            metrics: Metrics manager instance
            dependencies: Set of dependencies
        """
        super().__init__()
        
        self.name = name
        if isinstance(config, AppConfig):
            self._config = AppConfig.get_by_component_name(config, name)
        else:
            self._config = config
            
        self._logger = logger or BackendLogger(name).get_logger()
        self._metrics = metrics
        self._dependencies = dependencies or set()
        self._initialization_lock = asyncio.Lock()
        
        # Update initial health status with component details
        self.update_health_details({
                "component": name,
                "state": self.state,
                "initialized": False,
                "dependencies": list(self._dependencies)
        })
        
        # Register standard component metrics if metrics manager is available
        if self._metrics:
            self._register_standard_metrics()

        if self.logger:
            self.logger.debug(
                f"{name} component created",
                context="component",
                dependencies=list(self._dependencies)
            )
            
    def _register_standard_metrics(self) -> None:
        """Register standard component metrics."""
        # State Metrics
        self._metrics.register_metric(
            name=f"{self.name}_state",
            type=MetricType.GAUGE,
            description=f"Current state of {self.name}",
            labels={"state": ""},
            component=self.name
        )
        
        # Operation Metrics
        self._metrics.register_metric(
            name=f"{self.name}_operations_total",
            type=MetricType.COUNTER,
            description=f"Total operations in {self.name}",
            labels={"operation": "", "status": ""},
            component=self.name
        )
        
        self._metrics.register_metric(
            name=f"{self.name}_operation_duration_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Operation duration in {self.name}",
            labels={"operation": "", "status": ""},
            component=self.name
        )
        
        # Error Metrics
        self._metrics.register_metric(
            name=f"{self.name}_errors_total",
            type=MetricType.COUNTER,
            description=f"Total errors in {self.name}",
            labels={"error_type": "", "operation": ""},
            component=self.name
        )
        
    def record_operation(self, operation: str, duration: float, status: str = "success") -> None:
        """Record component operation metrics.
        
        Args:
            operation: Operation name
            duration: Operation duration in seconds
            status: Operation status (success/error)
        """
        if not self._metrics:
            return
            
        self._metrics.record(
            name=f"{self.name}_operations_total",
            value=1,
            labels={"operation": operation, "status": status}
        )
        
        self._metrics.record(
            name=f"{self.name}_operation_duration_seconds",
            value=duration,
            labels={"operation": operation, "status": status}
        )
        
    def record_error(self, error_type: str, operation: str) -> None:
        """Record component error metrics.
        
        Args:
            error_type: Type of error
            operation: Operation where error occurred
        """
        if not self._metrics:
            return
            
        self._metrics.record(
            name=f"{self.name}_errors_total",
            value=1,
            labels={"error_type": error_type, "operation": operation}
        )
        
    def update_state_metric(self, state: ComponentState) -> None:
        """Update component state metric.
        
        Args:
            state: New component state
        """
        if not self._metrics:
            return
            
        self._metrics.record(
            name=f"{self.name}_state",
            value=1,
            labels={"state": state.value}
        )
        # Reset other states to 0
        for other_state in ComponentState:
            if other_state != state:
                self._metrics.record(
                    name=f"{self.name}_state",
                    value=0,
                    labels={"state": other_state.value}
                )
        
    @property
    def logger(self) -> 'BackendLogger':
        """Get logger instance."""
        return self._logger
        
    
    @property
    def config(self) -> Union[Dict[str, Any], 'AppConfig']:
        """Get component configuration."""
        return self._config
    
    @property
    def metrics(self) -> Optional['MetricsManager']:
        """Get metrics manager instance."""
        return self._metrics
    
    @config.setter
    def config(self, value: Union[Dict[str, Any], 'AppConfig']) -> None:
        """Set component configuration."""
        self._config = value

    @metrics.setter
    def metrics(self, value: Optional['MetricsManager']) -> None:
        """Set metrics manager instance."""
        self._metrics = value

    @logger.setter
    def logger(self, value: Optional['BackendLogger']) -> None:
        """Set logger instance."""
        self._logger = value

        
    @property
    def dependencies(self) -> Set[str]:
        """Get component dependencies."""
        return self._dependencies.copy()
    
        
    def add_dependency(self, component_name: str) -> None:
        """Add dependency.
        
        Args:
            component_name: Name of component to depend on
        """
        self._dependencies.add(component_name)
        self._health_status.update(
            details={
                **self._health_status.details,
                "dependencies": list(self._dependencies)
            }
        )
        
    def remove_dependency(self, component_name: str) -> None:
        """Remove dependency.
        
        Args:
            component_name: Name of component to remove dependency on
        """
        self._dependencies.discard(component_name)
        self._health_status.update(
            details={
                **self._health_status.details,
                "dependencies": list(self._dependencies)
            }
        )
        
    async def initialize(self) -> None:
        """Initialize component."""
        async with self._initialization_lock:
            if self._is_initialized:
                return
                
            try:
                self.state = ComponentState.INITIALIZING
                self.update_state_metric(self.state)
                start_time = perf_counter()
                
                # Initialize implementation
                if hasattr(self, '_initialize_impl'):
                    await self._initialize_impl()
                if hasattr(self, '_do_initialize'):
                    await self._do_initialize()
                if hasattr(self, '_initialize'):
                    await self._initialize()
                
                self._is_initialized = True
                self.state = ComponentState.INITIALIZED
                self.update_state_metric(self.state)
                
                duration = perf_counter() - start_time
                self.record_operation("initialize", duration, "success")
                
                if self.logger:
                    self.logger.info(
                        "component_initialized",
                        component=self.name
                    )
                
            except Exception as e:
                self.state = ComponentState.FAILED
                self.update_state_metric(self.state)
                self.record_error(type(e).__name__, "initialize")
                
                if self.logger:
                    self.logger.error(
                        "component_initialization_failed",
                        error=str(e),
                        component=self.name
                    )
                raise
                
    async def start(self) -> None:
        """Start component."""
        if not self._is_initialized:
            await self.initialize()
            
        try:
            start_time = perf_counter()
            
            # Update state to starting
            self.state = ComponentState.STARTING
            self.update_state_metric(self.state)
            
            # Start implementation
            if hasattr(self, '_start_impl'):
                await self._start_impl()
            if hasattr(self, '_do_start'):
                await self._do_start()
            if hasattr(self, '_start'):
                await self._start()
            
            self.state = ComponentState.RUNNING
            self.update_state_metric(self.state)
            
            duration = perf_counter() - start_time
            self.record_operation("start", duration, "success")
            
            if self.logger:
                self.logger.info(
                    "component_started",
                    component=self.name
                )
            
        except Exception as e:
            self.state = ComponentState.FAILED
            self.update_state_metric(self.state)
            self.record_error(type(e).__name__, "start")
            
            if self.logger:
                self.logger.error(
                    "component_start_failed",
                    error=str(e),
                    component=self.name
                )
            raise
            
    async def stop(self) -> None:
        """Stop component."""
        try:
            start_time = perf_counter()
            
            # Update state to stopping
            self.state = ComponentState.STOPPING
            self.update_state_metric(self.state)
            
            # Stop implementation
            if hasattr(self, '_stop_impl'):
                await self._stop_impl()
            if hasattr(self, '_do_stop'):
                await self._do_stop()
            if hasattr(self, '_stop'):
                await self._stop()
            
            self.state = ComponentState.STOPPED
            self.update_state_metric(self.state)
            
            duration = perf_counter() - start_time
            self.record_operation("stop", duration, "success")
            
            if self.logger:
                self.logger.info(
                    "component_stopped",
                    component=self.name
                )
            
        except Exception as e:
            self.state = ComponentState.FAILED
            self.update_state_metric(self.state)
            self.record_error(type(e).__name__, "stop")
            
            if self.logger:
                self.logger.error(
                    "component_stop_failed",
                    error=str(e),
                    component=self.name
                )
            raise
            
    async def check_health(self) -> HealthStatusInfo:
        """Check component health."""
        try:
            start_time = perf_counter()
            
            # Check implementation health
            if hasattr(self, '_check_health_impl'):
                await self._check_health_impl()
            if hasattr(self, '_do_check_health'):
                await self._do_check_health()
            if hasattr(self, '_check_health'):
                await self._check_health()

            # Update health status
            self._health_status.update(
                status=HealthStatus.HEALTHY,
                details={
                    "component": self.name,
                    "state": str(self.state),
                    "initialized": self._is_initialized,
                    "dependencies": list(self._dependencies),
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            )
            
            duration = perf_counter() - start_time
            self.record_operation("health_check", duration, "success")
            
            return self._health_status
            
        except Exception as e:
            self.record_error(type(e).__name__, "health_check")
            
            if self.logger:
                self.logger.error(
                    "component_health_check_failed",
                    error=str(e),
                    component=self.name
                )
            
            self._health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    "component": self.name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            )
            return self._health_status
            
    async def _initialize_impl(self) -> None:
        """Initialize implementation."""
        pass
        
    async def _start_impl(self) -> None:
        """Start implementation."""
        pass
        
    async def _stop_impl(self) -> None:
        """Stop implementation."""
        pass
        
    async def _check_health_impl(self) -> None:
        """Check implementation health."""
        pass
        
    async def cleanup(self) -> None:
        """Clean up component resources.
        
        This method ensures proper cleanup of resources by:
        1. Stopping the component if running
        2. Cleaning up any resources
        3. Resetting component state
        """
        try:
            # Stop if not already stopped
            if self.state not in [ComponentState.STOPPED, ComponentState.FAILED]:
                await self.stop()
            
            # Cleanup implementation
            await self._cleanup_impl()
            
            # Reset state
            self._is_initialized = False
            self.state = ComponentState.STOPPED
            self.update_state_metric(self.state)
            
            if self.logger:
                self.logger.info(
                    "component_cleaned_up",
                    component=self.name
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(
                    "component_cleanup_failed",
                    error=str(e),
                    component=self.name
                )
            raise

    async def _cleanup_impl(self) -> None:
        """Implementation specific cleanup.
        
        This method should be overridden by subclasses to provide
        component-specific cleanup logic.
        """
        pass 

    def update_health_details(self, details: Dict[str, Any]) -> None:
        """Update component health details.
        
        Args:
            details: Dictionary of health details to update
        """
        if not hasattr(self, '_health_status'):
            self._health_status = HealthStatusInfo(
                status=HealthStatus.UNKNOWN,
                details={},
                state_info=self._state_info
            )
        
        current_details = self._health_status.details.copy()
        current_details.update(details)
        self._health_status.update(details=current_details) 