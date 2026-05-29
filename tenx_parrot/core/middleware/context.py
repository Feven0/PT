"""Context middleware implementation."""
from typing import Optional, Dict, Any
from starlette.types import ASGIApp, Receive, Scope, Send
import contextvars
import asyncio
import uuid
from datetime import datetime, timezone

from .base import MiddlewareComponent
from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.types.context import RequestContext
from core.types.metrics import MetricType

# Context variables
request_id_var = contextvars.ContextVar('request_id', default=None)
request_start_var = contextvars.ContextVar('request_start', default=None)
request_context_var = contextvars.ContextVar('request_context', default=None)

class ContextMiddleware(MiddlewareComponent):
    """Middleware for managing request context."""
    
    def __init__(
        self,
        app: ASGIApp,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        **kwargs
    ):
        super().__init__(
            app=app,
            name="context_middleware",
            metrics=metrics,
            logger=logger,
            **kwargs
        )
        self._context_timeouts: Dict[str, float] = {}
    
    def _register_request_metrics_impl(self) -> None:
        """Register context specific metrics."""
        if not self.metrics:
            return
            
        # Context timeouts
        self.metrics.register_metric(
            name=f"{self.name}_context_timeouts_total",
            type=MetricType.COUNTER,
            description=f"Total number of context timeouts in {self.name}",
            component=self.name,
            labels={"method": "", "path": ""}
        )
        
        # Active contexts
        self.metrics.register_metric(
            name=f"{self.name}_active_contexts",
            type=MetricType.GAUGE,
            description=f"Number of active request contexts in {self.name}",
            component=self.name,
            labels={"method": "", "path": ""}
        )
        
        # Context creation errors
        self.metrics.register_metric(
            name=f"{self.name}_context_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of context creation errors in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "error_type": ""}
        )
    
    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process request with context."""
        # Generate new request ID if not provided
        request_id = scope.get("request_id", str(uuid.uuid4()))
        scope["request_id"] = request_id
        method = scope.get("method", "")
        path = scope.get("path", "")
            
        try:
            # Set context variables
            request_start = datetime.now(timezone.utc)
            request_start_var.set(request_start)
            request_id_var.set(request_id)
            
            # Create request context
            context = RequestContext(
                request_id=request_id,
                start_time=request_start,
                path=path,
                method=method,
                client=scope.get("client", None),
                headers=dict(scope.get("headers", {}))
            )
            request_context_var.set(context)
            self._context_timeouts[request_id] = request_start.timestamp() + 30  # 30 second timeout
            
            # Record active context
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_active_contexts",
                    len(self._context_timeouts),
                    labels={
                        "method": method,
                        "path": path
                    }
                )
            
            await self.app(scope, receive, send)
            
        except Exception as e:
            # Record context error
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_context_errors_total",
                    1,
                    labels={
                        "method": method,
                        "path": path,
                        "error_type": type(e).__name__
                    }
                )
            raise
            
        finally:
            # Cleanup context
            request_id_var.set(None)
            request_start_var.set(None)
            request_context_var.set(None)
            self._context_timeouts.pop(request_id, None)
            
            # Update active contexts metric
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_active_contexts",
                    len(self._context_timeouts),
                    labels={
                        "method": method,
                        "path": path
                    }
                )
    
    async def cleanup(self) -> None:
        """Cleanup middleware resources."""
        await super().cleanup()
        
        # Clear any remaining contexts
        request_id_var.set(None)
        request_start_var.set(None)
        request_context_var.set(None)
        self._context_timeouts.clear()
        
    async def _cleanup_expired_contexts(self) -> None:
        """Cleanup expired request contexts."""
        current_time = datetime.now(timezone.utc).timestamp()
        expired = [
            (req_id, scope) for req_id, timeout in self._context_timeouts.items()
            if current_time > timeout
        ]
        for req_id, scope in expired:
            self._context_timeouts.pop(req_id, None)
            if req_id in self._active_requests:
                self._untrack_request(req_id, scope)
                self._logger.warning(
                    "request_context_expired",
                    request_id=req_id
                )
                
                # Record timeout metric
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_context_timeouts_total",
                        1,
                        labels={
                            "method": scope.get("method", ""),
                            "path": scope.get("path", "")
                        }
                    ) 