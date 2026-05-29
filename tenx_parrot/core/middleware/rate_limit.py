"""Rate limiting middleware."""
from typing import Optional, TYPE_CHECKING
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse
import asyncio
import time
from datetime import datetime, timezone

from core.errors.exceptions import ServiceError
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.types.metrics import MetricType

from .base import MiddlewareComponent

if TYPE_CHECKING:
    from core.cache.manager import CacheManager


class RateLimitMiddleware(MiddlewareComponent):
    """Request rate limiting middleware."""
    
    def __init__(
        self,
        app: ASGIApp,
        rate: int = 100,
        period: int = 60,
        cache: Optional['CacheManager'] = None,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        **kwargs
    ):
        super().__init__(
            app=app,
            name="rate_limit_middleware",
            metrics=metrics,
            logger=logger,
            order=3,  # Run after context and request processing
            **kwargs
        )
        self._rate = rate
        self._period = period
        self._cache = cache
        
    def _register_request_metrics_impl(self) -> None:
        """Register rate limit specific metrics."""
        if not self.metrics:
            return
            
        # Rate limit exceeded events
        self.metrics.register_metric(
            name=f"{self.name}_exceeded_total",
            type=MetricType.COUNTER,
            description=f"Number of rate limit exceeded events in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "client_id": ""}
        )
        
        # Remaining rate limit
        self.metrics.register_metric(
            name=f"{self.name}_remaining",
            type=MetricType.GAUGE,
            description=f"Remaining rate limit for client in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "client_id": ""}
        )
        
        # Rate limit requests
        self.metrics.register_metric(
            name=f"{self.name}_requests_total",
            type=MetricType.COUNTER,
            description=f"Total number of rate limited requests in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "client_id": "", "status": ""}
        )

    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process request with rate limiting."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        # Get client identifier
        client = scope.get("client", None)
        client_id = client[0] if client else "unknown"
        method = scope.get("method", "")
        path = scope.get("path", "")
        
        try:
            # Check rate limit
            key = f"rate_limit:{client_id}"
            count = await self._cache.increment(key) if self._cache else 1
            
            # Set expiry on first request
            if count == 1 and self._cache:
                await self._cache.expire(key, self._period)
                
            # Check if limit exceeded
            if count > self._rate:
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_exceeded_total",
                        1,
                        labels={
                            "method": method,
                            "path": path,
                            "client_id": client_id
                        }
                    )
                    
                self._logger.warning(
                    "rate_limit_exceeded",
                    client_id=client_id,
                    method=method,
                    path=path,
                    rate=self._rate,
                    period=self._period
                )
                
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "details": {
                            "retry_after": self._period,
                            "limit": self._rate,
                            "period": self._period
                        }
                    }
                )
                await response(scope, receive, send)
                return
                
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "method": method,
                        "path": path,
                        "client_id": client_id,
                        "status": "allowed"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_remaining",
                    self._rate - count,
                    labels={
                        "method": method,
                        "path": path,
                        "client_id": client_id
                    }
                )
                
            # Process request
            await self.app(scope, receive, send)
            
        except Exception as e:
            self._logger.error(
                "rate_limit_error",
                client_id=client_id,
                method=method,
                path=path,
                error=str(e)
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={
                        "method": method,
                        "path": path,
                        "error_type": type(e).__name__
                    }
                )
            raise
            
    async def cleanup(self) -> None:
        """Cleanup middleware resources."""
        await super().cleanup()
        if self._cache:
            # Clear rate limit keys
            pattern = "rate_limit:*"
            try:
                keys = await self._cache.keys(pattern)
                if keys:
                    await self._cache.delete_many(keys)
            except Exception as e:
                self._logger.error(f"Failed to cleanup rate limit keys: {str(e)}")
                
    def update_limits(self, rate: int, period: int) -> None:
        """Update rate limiting parameters.
        
        Args:
            rate: New rate limit
            period: New time period in seconds
        """
        self._rate = rate
        self._period = period 