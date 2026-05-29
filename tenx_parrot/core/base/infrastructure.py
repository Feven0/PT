"""Base infrastructure client implementation."""
from typing import Optional, Any, Dict, Set, Generic, TypeVar, List
from datetime import datetime, timezone

from core.base.component import BaseComponent
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker
from core.resilience.rate_limiter import RateLimiter
from core.alert.manager import AlertManager
from core.types.protocols import InfrastructureProviderProtocol
from core.types.components import HealthStatus, HealthStatusInfo

T = TypeVar("T")

class BaseInfrastructureClient(BaseComponent, InfrastructureProviderProtocol):
    """Base class for all infrastructure clients."""
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        retry: Optional[RetryManager] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        rate_limiter: Optional[RateLimiter] = None,
        alert_manager: Optional[AlertManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize base infrastructure client.
        
        Args:
            name: Client name
            config: Application configuration
            metrics: Optional metrics manager
            retry: Optional retry manager
            circuit_breaker: Optional circuit breaker
            rate_limiter: Optional rate limiter
            alert_manager: Optional alert manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies or set()
        )
        self.retry = retry
        self.circuit_breaker = circuit_breaker
        self.rate_limiter = rate_limiter
        self.alert_manager = alert_manager
        self._health_status = HealthStatusInfo(
            status=HealthStatus.UNKNOWN,
            details={}
        )
        self.last_health_check = datetime.now(timezone.utc)

        if self.logger:
            self.logger.debug(
                f"{name} infrastructure_created",
                context="infrastructure",
                dependencies=list(self.dependencies)
            )        
        
    async def _execute_with_resilience(
        self,
        operation: str,
        func: callable,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """Execute operation with resilience patterns.
        
        Args:
            operation: Operation name for metrics/logging
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Operation result
            
        Raises:
            Exception: If operation fails
        """
        # Apply rate limiting if configured
        if self.rate_limiter:
            await self.rate_limiter.acquire()
            
        try:
            # Apply circuit breaker if configured
            if self.circuit_breaker:
                await self.circuit_breaker.before_call()
                
            # Apply retry if configured
            if self.retry:
                result = await self.retry.execute(
                    func,
                    *args,
                    **kwargs
                )
            else:
                result = await func(*args, **kwargs)
                
            # Record success metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "success"}
                )
                
            return result
            
        except Exception as e:
            # Record failure metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": operation}
                )
                
            # Update circuit breaker
            if self.circuit_breaker:
                await self.circuit_breaker.on_error(e)
                
            # Send alert if configured
            if self.alert_manager:
                await self.alert_manager.send_alert(
                    f"{self.name}_{operation}_failed",
                    str(e),
                    severity="error",
                    context={
                        "client": self.name,
                        "operation": operation,
                        "error": str(e)
                    }
                )
                
            raise
            
        finally:
            # Release rate limiter
            if self.rate_limiter:
                self.rate_limiter.release()
                
    async def check_health(self) -> HealthStatusInfo:
        """Check infrastructure client health.
        
        Returns:
            Current health status information
        """
        try:
            await self.validate_connection()
            self._health_status.update(
                status=HealthStatus.HEALTHY,
                details=self._get_health_details()
            )
        except Exception as e:
            self._health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    **self._get_health_details(),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            
        self.last_health_check = datetime.now(timezone.utc)
        return self._health_status
        
    def _get_health_details(self) -> Dict[str, Any]:
        """Get health check details.
        
        Returns:
            Health check details
        """
        return {
            "client": self.name,
            "state": self.state.value,
            "retry_enabled": bool(self.retry),
            "circuit_breaker_enabled": bool(self.circuit_breaker),
            "rate_limiter_enabled": bool(self.rate_limiter)
        }
        
    async def validate_connection(self) -> None:
        """Validate infrastructure client connection.
        
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement validate_connection") 