"""Base middleware component."""
from typing import Optional, Dict, Any, List, Set, Union
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import uuid
from starlette.responses import JSONResponse

from core.base.component import BaseComponent
from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.types.metrics import MetricType

class MiddlewareComponent(BaseComponent):
    """Base class for middleware components."""
    
    def __init__(
        self,
        app: ASGIApp,
        name: str,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        **kwargs
    ):
        super().__init__(name=name, 
                         config=kwargs.get('config', None),
                         metrics=metrics, 
                         logger=logger, 
                         dependencies=kwargs.get('dependencies', None)
                         )
        self.app = app
        self._active_requests: Set[str] = set()  # Track active request IDs as strings only
        self._shutdown_event = asyncio.Event()
        self._cleanup_timeout = 10.0  # 10 seconds timeout
        
        # Register metrics
        if self.metrics:
            self._register_request_metrics()

    def _register_request_metrics(self) -> None:
        """Register standard request metrics and middleware-specific metrics."""
        if not self.metrics:
            return
        
        # Active requests
        self.metrics.register_metric(
            name=f"{self.name}_active_requests",
            type=MetricType.GAUGE,
            description=f"Number of active requests in {self.name}",
            component=self.name,
            labels={"method": "", "path": ""}  # Standard label order
        )
        
        # Total requests
        self.metrics.register_metric(
            name=f"{self.name}_requests_total",
            type=MetricType.COUNTER,
            description=f"Total number of requests handled by {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "status": ""}  # Standard label order
        )
        
        # Request duration
        self.metrics.register_metric(
            name=f"{self.name}_request_duration_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Duration of requests handled by {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "status": ""}  # Standard label order
        )
        
        # Errors
        self.metrics.register_metric(
            name=f"{self.name}_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of errors in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "error_type": ""}  # Standard label order
        )

        # Register middleware-specific metrics
        self._register_request_metrics_impl()

    def _register_request_metrics_impl(self) -> None:
        """Register middleware-specific metrics. Override in subclasses."""
        pass

    def _track_request(self, request_id: Union[str, int, uuid.UUID], scope: Scope) -> None:
        """Track an active request.
        
        Args:
            request_id: Request identifier (will be converted to string)
            scope: Request scope for labels
        """
        # Always convert request_id to string
        str_request_id = str(request_id)
        self._active_requests.add(str_request_id)
        
        # Get standard labels
        method = scope.get("method", "unknown")
        path = scope.get("path", "unknown")
        
        if self.metrics:
            self.metrics.record(
                f"{self.name}_active_requests",
                len(self._active_requests),
                labels={
                    "method": method,
                    "path": path
                }
            )
    
    def _untrack_request(self, request_id: Union[str, int, uuid.UUID], scope: Scope) -> None:
        """Stop tracking a request.
        
        Args:
            request_id: Request identifier (will be converted to string)
            scope: Request scope for labels
        """
        # Always convert request_id to string
        str_request_id = str(request_id)
        self._active_requests.discard(str_request_id)
        
        # Get standard labels
        method = scope.get("method", "unknown")
        path = scope.get("path", "unknown")
        
        if self.metrics:
            self.metrics.record(
                f"{self.name}_active_requests",
                len(self._active_requests),
                labels={
                    "method": method,
                    "path": path
                }
            )
    
    async def cleanup(self) -> None:
        """Cleanup middleware resources."""
        self._shutdown_event.set()
        if self._active_requests:
            try:
                # Wait for active requests with timeout
                await asyncio.wait_for(
                    self._wait_for_requests(),
                    timeout=self._cleanup_timeout
                )
            except asyncio.TimeoutError:
                self._logger.warning(
                    f"{self.name}_cleanup_timeout",
                    active_requests=len(self._active_requests)
                )
                
    async def _wait_for_requests(self) -> None:
        """Wait for active requests to complete."""
        while self._active_requests:
            await asyncio.sleep(0.1)
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        # Ensure request_id is a string
        request_id = str(scope.get("request_id", uuid.uuid4()))
        scope["request_id"] = request_id
        
        # Get standard labels
        method = scope.get("method", "unknown")
        path = scope.get("path", "unknown")
        
        self._track_request(request_id, scope)
        
        try:
            if self._shutdown_event.is_set():
                # Return 503 Service Unavailable during shutdown
                response = JSONResponse(
                    status_code=503,
                    content={"detail": "Service is shutting down"}
                )
                await response(scope, receive, send)
                return
                
            # Process request
            start_time = self.metrics.time() if self.metrics else None
            
            try:
                await self._process_request(scope, receive, send)
                
                if start_time and self.metrics:
                    duration = self.metrics.time() - start_time
                    self.metrics.record(
                        f"{self.name}_request_duration_seconds",
                        duration,
                        labels={
                            "method": method,
                            "path": path,
                            "status": "success"
                        }
                    )
                    self.metrics.record(
                        f"{self.name}_requests_total",
                        1,
                        labels={
                            "method": method,
                            "path": path,
                            "status": "success"
                        }
                    )
                    
            except Exception as e:
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
                    self.metrics.record(
                        f"{self.name}_request_duration_seconds",
                        self.metrics.time() - start_time if start_time else 0,
                        labels={
                            "method": method,
                            "path": path,
                            "status": "error"
                        }
                    )
                    self.metrics.record(
                        f"{self.name}_requests_total",
                        1,
                        labels={
                            "method": method,
                            "path": path,
                            "status": "error"
                        }
                    )
                self._logger.error(f"Error in middleware {self.name}: {e}")
                raise
                
        finally:
            self._untrack_request(request_id, scope)
    
    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request. Override this method in subclasses."""
        await self.app(scope, receive, send)
    
    async def _initialize_impl(self) -> None:
        """Initialize middleware."""
        self._logger.info(f"Initializing middleware {self.name}")
    
    async def _start_impl(self) -> None:
        """Start middleware."""
        self._logger.info(f"Starting middleware {self.name}")
    
    async def _stop_impl(self) -> None:
        """Stop middleware."""
        self._logger.info(f"Stopping middleware {self.name}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get middleware configuration."""
        return self.metadata
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update middleware configuration."""
        self._metadata.update(config)
    
    @property
    def middleware_order(self) -> int:
        """Get middleware order. Lower numbers run first."""
        return self.metadata.get("order", 100) 