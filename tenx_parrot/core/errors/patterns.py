"""Error handling patterns."""
from typing import Any, Callable, Dict, Optional, Type, TypeVar
from functools import wraps

from .handlers import ServiceError
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker
from core.logging import BackendLogger

T = TypeVar('T')

class ResilientOperation:
    """Resilient operation pattern."""
    
    def __init__(
        self,
        name: str,
        retry_manager: RetryManager,
        circuit_breaker: CircuitBreaker,
        logger: Optional[BackendLogger] = None,
        error_type: Type[ServiceError] = ServiceError,
        retry_policy: str = "default"
    ):
        """Initialize resilient operation.
        
        Args:
            name: Operation name
            retry_manager: Retry manager
            circuit_breaker: Circuit breaker
            logger: Optional logger
            error_type: Error type to raise
            retry_policy: Retry policy name
        """
        self.name = name
        self._retry_manager = retry_manager
        self._circuit_breaker = circuit_breaker
        self._logger = logger or BackendLogger(name=f"resilient.{name}")
        self._error_type = error_type
        self._retry_policy = retry_policy
        
    async def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute operation with resilience patterns.
        
        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            ServiceError: If operation fails
        """
        try:
            # Check circuit breaker
            if not self._circuit_breaker.allow_request(self.name):
                raise self._error_type(
                    message=f"Circuit breaker open for {self.name}",
                    code="CIRCUIT_BREAKER_OPEN",
                    status_code=503,
                    details={"operation": self.name}
                )
            
            # Execute with retry
            result = await self._retry_manager.with_retry(
                self._retry_policy,
                func,
                *args,
                **kwargs
            )
            
            # Record success
            self._circuit_breaker.record_success(self.name)
            return result
            
        except Exception as e:
            # Record failure
            self._circuit_breaker.record_failure(self.name)
            
            # Transform error
            if isinstance(e, ServiceError):
                raise
                
            self._logger.error(f"Operation {self.name} failed: {e}")
            raise self._error_type(
                message=str(e),
                code="OPERATION_FAILED",
                status_code=500,
                details={
                    "operation": self.name,
                    "original_error": str(e)
                }
            )
    
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Use as decorator."""
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.execute(func, *args, **kwargs)
        return wrapper


def resilient(
    name: str,
    retry_policy: str = "default",
    error_type: Type[ServiceError] = ServiceError
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for resilient operations.
    
    Args:
        name: Operation name
        retry_policy: Retry policy name
        error_type: Error type to raise
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Get components from container
            container = getattr(self, "container", None)
            if not container:
                raise ValueError("Component must have container attribute")
                
            operation = ResilientOperation(
                name=name,
                retry_manager=container.retry_manager(),
                circuit_breaker=container.circuit_breaker(),
                logger=container.logger(),
                error_type=error_type,
                retry_policy=retry_policy
            )
            return await operation.execute(func, self, *args, **kwargs)
        return wrapper
    return decorator 