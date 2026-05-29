"""Circuit breaker implementation."""
from typing import Dict, Any, Optional, Callable, TypeVar, Generic, Awaitable, Set, Type, Union
from datetime import datetime, timezone
import asyncio
import pickle
from enum import Enum
import functools

from core.base.manager import BaseManager
from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.config import AppConfig, CircuitBreakerConfig
from core.types import ComponentState
from core.errors.exceptions import ServiceUnavailableError
from core.types.metrics import MetricType
from core.types.resilience import CircuitState

T = TypeVar('T')
R = TypeVar('R')

class CircuitBreakerError(Exception):
    """Circuit breaker error."""
    pass

def timeout(seconds: float) -> Callable:
    """Timeout decorator.
    
    Args:
        seconds: Timeout in seconds
        
    Returns:
        Timeout decorator
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                raise ServiceUnavailableError(
                    f"Operation timed out after {seconds} seconds",
                    service=func.__name__,
                    retry_after=int(seconds)
                )
                
        return wrapper
    return decorator

def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    reset_timeout: float = 60.0,
    half_open_timeout: float = 30.0
) -> Callable:
    """Circuit breaker decorator.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        reset_timeout: Time in seconds before resetting to half-open
        half_open_timeout: Time in seconds in half-open before closing
        
    Returns:
        Circuit breaker decorator
    """
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(
            name=name,
            operation=func,
            failure_threshold=failure_threshold,
            reset_timeout=reset_timeout,
            half_open_timeout=half_open_timeout
        )
        
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker.execute(*args, **kwargs)
            
        return wrapper
    return decorator


class CircuitBreaker(Generic[T, R]):
    """Circuit breaker implementation."""
    
    def __init__(
        self,
        name: str,
        operation: Callable[[T], Awaitable[R]],
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_timeout: float = 30.0
    ):
        """Initialize circuit breaker.
        
        Args:
            name: Circuit breaker name
            operation: Protected operation
            failure_threshold: Number of failures before opening
            reset_timeout: Time in seconds before resetting to half-open
            half_open_timeout: Time in seconds in half-open before closing
        """
        self.name = name
        self.operation = operation
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        
    def _should_allow_execution(self) -> bool:
        """Check if execution should be allowed."""
        now = datetime.now(timezone.utc)
        
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            # Check if enough time has passed to try half-open
            if self.last_failure_time and (now - self.last_failure_time).total_seconds() >= self.reset_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            # Only allow one request at a time in half-open
            if self.last_success_time and (now - self.last_success_time).total_seconds() >= self.half_open_timeout:
                self.state = CircuitState.CLOSED
                return True
            return False
            
        return True
        
    async def execute(self, arg: T) -> R:
        """Execute protected operation.
        
        Args:
            arg: Operation argument
            
        Returns:
            Operation result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if not self._should_allow_execution():
            raise CircuitBreakerError(f"Circuit {self.name} is {self.state}")
            
        self.total_calls += 1
        
        try:
            result = await self.operation(arg)
            self.successful_calls += 1
            self.last_success_time = datetime.now(timezone.utc)
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
                
            return result
            
        except Exception as e:
            self.failed_calls += 1
            self.failures += 1
            self.last_failure_time = datetime.now(timezone.utc)
            
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                
            raise


class CircuitBreakerManager(BaseManager[CircuitBreaker[Any, Any]]):
    """Circuit breaker manager implementation."""
    
    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional['MetricsManager'] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Initialize circuit breaker manager.
        
        Args:
            name: Circuit breaker manager name
            config: Circuit breaker configuration or AppConfig
            metrics: Optional metrics manager
            dependencies: Optional dependencies
        """
        # Initialize with required dependencies
        required_deps = {"metrics", "state_store", "alert_manager"}
        if dependencies:
            required_deps.update(dependencies)
                    
        super().__init__(name=name, 
                         config=config, 
                         metrics=metrics, 
                         dependencies=dependencies)
        
        # Initialize circuit breaker settings from config
        self._failure_threshold = self._config.get("failure_threshold", 5)
        self._reset_timeout = self._config.get("timeout", 30.0)
        self._half_open_timeout = self._config.get("half_open_timeout", 15.0)
        self._success_threshold = self._config.get("success_threshold", 3)
        
        # Update health status with circuit breaker specific details
        self._health_status.details.update({
            "failure_threshold": self._failure_threshold,
            "timeout": self._reset_timeout,
            "half_open_timeout": self._half_open_timeout,
            "success_threshold": self._success_threshold
        })
        
        self._breakers: Dict[str, CircuitBreaker[Any, Any]] = {}
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_interval = 10  # seconds
        
    async def _initialize_impl(self) -> None:
        """Initialize circuit breaker manager."""
        await super()._initialize_impl()
        
        self._breakers.clear()
        
        # Register metrics
        if self.metrics:
            self.metrics.register_metric(
                name=f"{self.name}_state",
                type=MetricType.GAUGE,
                description=f"Current state of {self.name} circuit breaker",
                component=self.name
            )
            self.metrics.register_metric(
                name=f"{self.name}_failures_total",
                type=MetricType.COUNTER,
                description=f"Total number of failures in {self.name}",
                component=self.name
            )
            self.metrics.register_metric(
                name=f"{self.name}_successes_total",
                type=MetricType.COUNTER,
                description=f"Total number of successes in {self.name}",
                component=self.name
            )
            self.metrics.register_metric(
                name=f"{self.name}_state_changes_total",
                type=MetricType.COUNTER,
                description=f"Total number of state changes in {self.name}",
                component=self.name
            )
            
        # Initialize state store integration
        if "state_store" in self.dependencies:
            try:
                stored_breakers = await self._state_store.get_circuit_breakers()
                for name, breaker_data in stored_breakers.items():
                    # Deserialize operation
                    operation = pickle.loads(breaker_data["operation"])
                    await self.create_breaker(
                        name=name,
                        operation=operation,
                        failure_threshold=breaker_data.get("failure_threshold", 5),
                        reset_timeout=breaker_data.get("reset_timeout", 60.0),
                        half_open_timeout=breaker_data.get("half_open_timeout", 30.0)
                    )
            except Exception as e:
                self.logger.error(
                    "state_store_load_failed",
                    error=str(e),
                    manager=self.name
                )
                
    async def _save_state(self, name: str, breaker: CircuitBreaker[Any, Any]) -> None:
        """Save breaker state to store."""
        if "state_store" not in self.dependencies:
            return
            
        try:
            # Serialize operation
            operation_bytes = pickle.dumps(breaker.operation)
            await self._state_store.save_circuit_breaker(
                name,
                {
                    "operation": operation_bytes,
                    "failure_threshold": breaker.failure_threshold,
                    "reset_timeout": breaker.reset_timeout,
                    "half_open_timeout": breaker.half_open_timeout,
                    "state": breaker.state,
                    "failures": breaker.failures,
                    "last_failure_time": breaker.last_failure_time,
                    "last_success_time": breaker.last_success_time,
                    "total_calls": breaker.total_calls,
                    "successful_calls": breaker.successful_calls,
                    "failed_calls": breaker.failed_calls
                }
            )
        except Exception as e:
            self.logger.error(
                "state_store_save_failed",
                error=str(e),
                breaker=name
            )
            
    async def _notify_state_change(
        self,
        breaker: CircuitBreaker[Any, Any],
        old_state: CircuitState,
        new_state: CircuitState
    ) -> None:
        """Notify state change."""
        if "alert_manager" not in self.dependencies:
            return
            
        try:
            severity = "warning" if new_state == CircuitState.OPEN else "info"
            message = (
                f"Circuit breaker {breaker.name} changed state from "
                f"{old_state} to {new_state}"
            )
            
            if new_state == CircuitState.OPEN:
                message += (
                    f" after {breaker.failures} failures. "
                    f"Success rate: {breaker.successful_calls/breaker.total_calls:.2%}"
                )
            elif new_state == CircuitState.CLOSED:
                message += " after successful recovery"
                
            await self._alert_manager.send_alert(
                title=f"Circuit Breaker State Change",
                message=message,
                severity=severity,
                tags={
                    "breaker": breaker.name,
                    "from_state": old_state,
                    "to_state": new_state,
                    "failures": breaker.failures,
                    "total_calls": breaker.total_calls,
                    "success_rate": (
                        breaker.successful_calls / breaker.total_calls
                        if breaker.total_calls > 0 else 0
                    )
                }
            )
        except Exception as e:
            self.logger.error(
                "alert_manager_notify_failed",
                error=str(e),
                breaker=breaker.name
            )
            
    async def create_breaker(
        self,
        name: str,
        operation: Callable[[T], Awaitable[R]],
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_timeout: float = 30.0
    ) -> CircuitBreaker[T, R]:
        """Create circuit breaker.
        
        Args:
            name: Circuit breaker name
            operation: Protected operation
            failure_threshold: Number of failures before opening
            reset_timeout: Time in seconds before resetting to half-open
            half_open_timeout: Time in seconds in half-open before closing
            
        Returns:
            Circuit breaker instance
        """
        breaker = CircuitBreaker(
            name=name,
            operation=operation,
            failure_threshold=failure_threshold,
            reset_timeout=reset_timeout,
            half_open_timeout=half_open_timeout
        )
        
        self._breakers[name] = breaker
        await self._save_state(name, breaker)
        
        if self.metrics:
            self.metrics.record(
                name=f"{self.name}_breakers_total",
                value=float(len(self._breakers)),
                labels={"state": breaker.state}
            )
            
        return breaker
        
    async def get_breaker(self, name: str) -> Optional[CircuitBreaker[Any, Any]]:
        """Get circuit breaker.
        
        Args:
            name: Circuit breaker name
            
        Returns:
            Circuit breaker if found
        """
        return self._breakers.get(name)
        
    async def delete_breaker(self, name: str) -> None:
        """Delete circuit breaker.
        
        Args:
            name: Circuit breaker name
        """
        breaker = self._breakers.pop(name, None)
        if breaker:
            if "state_store" in self.dependencies:
                try:
                    await self._state_store.delete_circuit_breaker(name)
                except Exception as e:
                    self.logger.error(
                        "state_store_delete_failed",
                        error=str(e),
                        breaker=name
                    )
                    
            if self.metrics:
                self.metrics.record(
                    name=f"{self.name}_breakers_total",
                    value=float(len(self._breakers)),
                    labels={"state": breaker.state}
                )
                
    async def _monitor_breakers(self) -> None:
        """Monitor circuit breakers."""
        while True:
            try:
                for name, breaker in self._breakers.items():
                    old_state = breaker.state
                    
                    # Check if breaker should transition states
                    if breaker._should_allow_execution():
                        if breaker.state != old_state:
                            await self._notify_state_change(
                                breaker,
                                old_state,
                                breaker.state
                            )
                            
                            if self.metrics:
                                self.metrics.record(
                                    name=f"{self.name}_state_changes_total",
                                    value=1.0,
                                    labels={
                                        "breaker": name,
                                        "from_state": old_state,
                                        "to_state": breaker.state
                                    }
                                )
                                
                    # Update metrics
                    if self.metrics:
                        self.metrics.record(
                            name=f"{self.name}_breakers_total",
                            value=float(len(self._breakers)),
                            labels={"state": breaker.state}
                        )
                        self.metrics.record(
                            name=f"{self.name}_failures_total",
                            value=float(breaker.failures),
                            labels={"breaker": name}
                        )
                        
                    # Save state
                    await self._save_state(name, breaker)
                    
                await asyncio.sleep(self._monitor_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    "breaker_monitor_failed",
                    error=str(e),
                    manager=self.name
                )
                await asyncio.sleep(60)  # Retry after 1 minute 