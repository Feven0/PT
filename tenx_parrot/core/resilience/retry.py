"""Retry pattern implementation."""
from typing import Optional, Any, Set, Dict, Callable, TypeVar, Type, Union, List, TYPE_CHECKING
from datetime import datetime, timezone
import asyncio
import random
import time
from contextlib import asynccontextmanager
from functools import wraps

from core.base.component import BaseComponent
from core.base.manager import BaseManager
from core.types.components import HealthStatus, HealthStatusInfo, ComponentState
from core.config import AppConfig, RetryConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.types.metrics import MetricsProtocol, MetricType
from core.types.protocols import LoggerProtocol

if TYPE_CHECKING:
    from core.alerts.manager import AlertManager

T = TypeVar('T')

class RetryWithBackoff(BaseComponent):
    """Retry with exponential backoff implementation."""
    
    def __init__(
        self,
        name: str,
        config: Optional[RetryConfig] = None,
        max_attempts: Optional[int] = None,
        base_delay: Optional[float] = None,
        max_delay: Optional[float] = None,
        exponential_base: float = 2.0,
        jitter: bool = True,
        logger: Optional[BackendLogger] = None,
        metrics: Optional[MetricsManager] = None,
        alert_manager: Optional[Any] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize retry handler.
        
        Args:
            name: Handler name
            config: Optional retry configuration
            max_attempts: Maximum number of attempts (overrides config)
            base_delay: Base delay between attempts in seconds (overrides config)
            max_delay: Maximum delay between attempts in seconds (overrides config)
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            logger: Optional logger instance
            metrics: Optional metrics manager
            alert_manager: Optional alert manager
            dependencies: Optional set of dependencies
        """
        super().__init__(
            name=name,
            config=config or RetryConfig(),
            logger=logger,
            metrics=metrics,
            dependencies=dependencies
        )
        
        # Use explicit params if provided, otherwise use config
        self.retry_config = config or RetryConfig()
        self.max_attempts = max_attempts or self.retry_config.max_retries
        self.base_delay = base_delay or self.retry_config.initial_delay
        self.max_delay = max_delay or self.retry_config.max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.alert_manager = alert_manager
        
        # Tracking state
        self._attempt_counts: Dict[str, int] = {}
        self._last_attempts: Dict[str, datetime] = {}
        self._operation_durations: Dict[str, List[float]] = {}
        
        # Register metrics if available
        if self.metrics:
            self._register_metrics()
            
    def _register_metrics(self) -> None:
        """Register retry metrics."""
        if not self.metrics:
            return
            
        # register policies metrics
        self.metrics.register_metric(
            name=f"{self.name}_policies_total",
            type=MetricType.GAUGE,
            description=f"Total number of retry policies in {self.name}",
            component=self.name
        )
        # Attempt Metrics
        self.metrics.register_metric(
            name=f"{self.name}_attempts_total",
            type=MetricType.COUNTER,
            description=f"Total number of retry attempts in {self.name}",
            component=self.name
        )
        
        # Success/Failure Metrics
        self.metrics.register_metric(
            name=f"{self.name}_operations_total",
            type=MetricType.COUNTER,
            description=f"Total number of operations in {self.name}",
            component=self.name
        )
        
        # Backoff Metrics
        self.metrics.register_metric(
            name=f"{self.name}_backoff_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Backoff duration in seconds for {self.name}",
            component=self.name
        )
        
        # Duration Metrics
        self.metrics.register_metric(
            name=f"{self.name}_operation_duration_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Duration of operations in {self.name}",
            component=self.name
        )
        
        # Error Metrics
        self.metrics.register_metric(
            name=f"{self.name}_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of errors in {self.name}",
            component=self.name
        )
        
    async def check_health(self) -> HealthStatusInfo:
        """Check retry handler health.
        
        Returns:
            Health status information
        """
        try:
            # Get retry statistics
            total_retries = sum(self._attempt_counts.values())
            active_retries = len(self._attempt_counts)
            recent_retries = sum(
                1 for ts in self._last_attempts.values()
                if (datetime.now(timezone.utc) - ts).total_seconds() < 300  # Last 5 minutes
            )
            
            # Calculate average operation duration
            avg_duration = 0.0
            if self._operation_durations:
                total_duration = sum(sum(durations) for durations in self._operation_durations.values())
                total_ops = sum(len(durations) for durations in self._operation_durations.values())
                if total_ops > 0:
                    avg_duration = total_duration / total_ops
            
            # Determine health status
            if self.state != ComponentState.RUNNING:
                status = HealthStatus.UNHEALTHY
            elif total_retries == 0:
                status = HealthStatus.HEALTHY
            elif recent_retries > 10:  # More than 10 retries in last 5 minutes
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
                
            # Update health status
            self._health_status.update(
                status=status,
                details={
                    "total_retries": total_retries,
                    "active_retries": active_retries,
                    "recent_retries": recent_retries,
                    "avg_operation_duration": avg_duration,
                    "max_retries": self.max_attempts,
                    "initial_delay": self.base_delay,
                    "max_delay": self.max_delay,
                    "exponential_base": self.exponential_base,
                    "jitter_enabled": self.jitter,
                    "config": self.retry_config.model_dump()
                }
            )
            
            return self._health_status
            
        except Exception as e:
            self._health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return self._health_status
            
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt.
        
        Args:
            attempt: Current attempt number
            
        Returns:
            Delay in seconds
        """
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            delay *= (0.5 + random.random())
            
        return delay
        
    @asynccontextmanager
    async def retry_context(self, operation: str):
        """Retry context manager.
        
        Args:
            operation: Operation name for metrics
        """
        attempt = 0
        start_time = time.time()
        
        while True:
            attempt += 1
            operation_start = time.time()
            
            try:
                if self.metrics:
                    self.metrics.record(
                        name=f"{self.name}_attempts_total",
                        value=1.0,
                        labels={"operation": operation, "attempt": str(attempt)}
                    )
                    
                yield attempt
                
                # Record operation duration
                duration = time.time() - operation_start
                if operation not in self._operation_durations:
                    self._operation_durations[operation] = []
                self._operation_durations[operation].append(duration)
                
                # Success - record metrics and exit
                if self.metrics:
                    self.metrics.record(
                        name=f"{self.name}_operation_duration_seconds",
                        value=duration,
                        labels={"operation": operation, "attempt": str(attempt)}
                    )
                    self.metrics.record(
                        name=f"{self.name}_operations_total",
                        value=1.0,
                        labels={"operation": operation, "status": "success"}
                    )
                break
                
            except Exception as e:
                # Check if exception type is monitored
                if self.retry_config.monitored_exceptions and not isinstance(e, tuple(self.retry_config.monitored_exceptions)):
                    raise
                    
                # Record error metrics
                if self.metrics:
                    duration = time.time() - operation_start
                    self.metrics.record(
                        name=f"{self.name}_operation_duration_seconds",
                        value=duration,
                        labels={"operation": operation, "attempt": str(attempt)}
                    )
                    self.metrics.record(
                        name=f"{self.name}_errors_total",
                        value=1.0,
                        labels={
                            "error_type": type(e).__name__,
                            "operation": operation,
                            "attempt": str(attempt)
                        }
                    )
                    
                # Check if we should retry
                if attempt >= self.max_attempts:
                    if self.metrics:
                        self.metrics.record(
                            name=f"{self.name}_operations_total",
                            value=1.0,
                            labels={"operation": operation, "status": "failure"}
                        )
                        
                    # Send alert on final failure
                    if self.alert_manager:
                        await self.alert_manager.send_alert(
                            f"{self.name}_{operation}_failed",
                            str(e),
                            severity="error",
                            context={
                                "operation": operation,
                                "attempts": attempt,
                                "error": str(e)
                            }
                        )
                    raise
                    
                # Calculate and wait for delay
                delay = self._calculate_delay(attempt)
                if self.metrics:
                    self.metrics.record(
                        name=f"{self.name}_backoff_seconds",
                        value=delay,
                        labels={"operation": operation, "attempt": str(attempt)}
                    )
                    
                await asyncio.sleep(delay)
        
    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """Execute function with retry.
        
        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retry attempts fail
        """
        operation_id = f"{func.__name__}_{id(func)}"
        self._attempt_counts[operation_id] = 0
        self._last_attempts[operation_id] = datetime.now(timezone.utc)
        
        async with self.retry_context(func.__name__) as attempt:
            self._attempt_counts[operation_id] = attempt
            result = await func(*args, **kwargs)
            
            # Clear tracking on success
            del self._attempt_counts[operation_id]
            del self._last_attempts[operation_id]
            
            return result

class RetryManager(BaseManager[RetryWithBackoff]):
    """Retry manager implementation."""
    
    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional['MetricsManager'] = None,
        alert_manager: Optional['AlertManager'] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Initialize retry manager.
        
        Args:
            name: Retry manager name
            config: Retry configuration or AppConfig
            metrics: Optional metrics manager
            dependencies: Optional dependencies
        """
        super().__init__(name=name, 
                         config=config, 
                         metrics=metrics, 
                         dependencies=dependencies)
        
        # Initialize retry settings from config
        self._max_retries = self._config.get("max_retries", 3)
        self._initial_delay = self._config.get("initial_delay", 1.0)
        self._max_delay = self._config.get("max_delay", 60.0)
        self._exponential_base = self._config.get("exponential_base", 2.0)
        self._jitter = self._config.get("jitter", True)
        
        # Update health status with retry specific details
        self._health_status.details.update({
            "max_retries": self._max_retries,
            "initial_delay": self._initial_delay,
            "max_delay": self._max_delay,
            "exponential_base": self._exponential_base,
            "jitter": self._jitter
        })
        
        self.alert_manager = alert_manager
        self._retries: Dict[str, RetryWithBackoff] = {}
        
    async def _initialize_impl(self) -> None:
        """Initialize retry policies from config."""
        # Create default retry policy
        default_config = RetryConfig(
            max_retries=self._max_retries,
            initial_delay=self._initial_delay,
            max_delay=self._max_delay,
            exponential_base=self._exponential_base,
            jitter=self._jitter
        )
        
        default_retry = RetryWithBackoff(
            name="default",
            config=default_config,
            metrics=self.metrics,
            logger=self.logger,
            alert_manager=self.alert_manager
        )
        await self.register_managed_component(default_retry)
        self._retries["default"] = default_retry
        
        # Create custom retry policies from config
        if 'policies' in self._config:
            policies = self._config.policies
        else:
            policies = {}
            
        for name, policy_config in policies.items():
            config = RetryConfig(**policy_config)
            retry = RetryWithBackoff(
                name=name,
                config=config,
                metrics=self.metrics,
                logger=self.logger,
                alert_manager=self.alert_manager
            )
            await self.register_managed_component(retry)
            self._retries[name] = retry
            
        if self.metrics:
            self.metrics.record(
                name=f"{self.name}_policies_total",
                value=float(len(self._retries)),
                labels={}
            )
            
    def get_retry(self, name: str = "default") -> RetryWithBackoff:
        """Get retry policy by name.
        
        Args:
            name: Name of retry policy
            
        Returns:
            RetryWithBackoff instance
        """
        if name not in self._retries:
            self.logger.warning(f"Retry policy {name} not found, using default")
            return self._retries["default"]
        return self._retries[name]
        
    async def with_retry(
        self,
        name: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """Execute function with retry policy.
        
        Args:
            name: Name of retry policy
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Function result
        """
        retry = self.get_retry(name)
        return await retry.execute(func, *args, **kwargs)
        
    def retry(
        self,
        name: str = "default"
    ) -> Callable:
        """Decorator for retrying operations.
        
        Args:
            name: Name of retry policy
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                return await self.with_retry(name, func, *args, **kwargs)
            return wrapper
        return decorator

def retry(
    attempts: int = 3,
    delay: float = 1.0,
    max_delay: Optional[float] = None,
    exponential: bool = True,
    jitter: bool = True,
    alert_manager: Optional[Any] = None
) -> Callable:
    """Retry decorator.
    
    Args:
        attempts: Maximum number of attempts
        delay: Base delay between attempts in seconds
        max_delay: Maximum delay between attempts in seconds
        exponential: Whether to use exponential backoff
        jitter: Whether to add random jitter to delays
        alert_manager: Optional alert manager for notifications
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        retry_handler = RetryWithBackoff(
            name=f"retry_{func.__name__}",
            max_attempts=attempts,
            base_delay=delay,
            max_delay=max_delay,
            exponential_base=2.0 if exponential else 1.0,
            jitter=jitter,
            alert_manager=alert_manager
        )
        
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await retry_handler.execute(func, *args, **kwargs)
            
        return wrapper
    return decorator 