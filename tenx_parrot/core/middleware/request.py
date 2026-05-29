"""Request processing middleware component."""
import time
from typing import Optional, Dict, Any, Set, Union
from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import asyncio
import uuid
from datetime import datetime, timezone

from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.types.metrics import MetricType

from .base import MiddlewareComponent


class RequestProcessingMiddleware(MiddlewareComponent):
    """Middleware for request processing and monitoring."""
    
    def __init__(
        self,
        app: ASGIApp,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        max_concurrent_requests: int = 100,
        request_timeout: float = 30.0,
        **kwargs
    ):
        super().__init__(
            app=app,
            name="request_processing_middleware",
            metrics=metrics,
            logger=logger,
            order=1,  # Run after context middleware
            **kwargs
        )
        self.max_concurrent_requests = max_concurrent_requests
        self.request_timeout = request_timeout
        self._active_requests: Set[str] = set()  # Track active request IDs
        self._request_start_times: Dict[str, datetime] = {}
        self._request_queue: Dict[str, float] = {}
    
    def _register_request_metrics_impl(self) -> None:
        """Register request processing specific metrics."""
        if not self.metrics:
            return
            
        # Queue size
        self.metrics.register_metric(
            name=f"{self.name}_queue_size",
            type=MetricType.GAUGE,
            description=f"Current size of request processing queue in {self.name}",
            component=self.name,
            labels={"method": "", "path": ""}
        )
        
        # Queue timeouts
        self.metrics.register_metric(
            name=f"{self.name}_queue_timeouts_total",
            type=MetricType.COUNTER,
            description=f"Total number of request queue timeouts in {self.name}",
            component=self.name,
            labels={"method": "", "path": ""}
        )
        
        # Request processing time
        self.metrics.register_metric(
            name=f"{self.name}_processing_time_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Time spent processing requests in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "status": ""}
        )
        
        # Concurrent requests
        self.metrics.register_metric(
            name=f"{self.name}_concurrent_requests",
            type=MetricType.GAUGE,
            description=f"Number of concurrent requests being processed in {self.name}",
            component=self.name,
            labels={"method": "", "path": ""}
        )
    
    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request with monitoring."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        # Get context from previous middleware
        context = scope.get("state", {}).get("context", {})
        request_id = context.get("request_id", "unknown")
        method = scope.get("method", "")
        path = scope.get("path", "")
        
        # Track request timing
        start_time = datetime.now(timezone.utc)
        self._request_start_times[request_id] = start_time
        
        # Check concurrent requests limit
        if len(self._active_requests) >= self.max_concurrent_requests:
            self._logger.warning(
                "Max concurrent requests reached",
                extra={"request_id": request_id}
            )
            # Add to queue
            self._request_queue[request_id] = time.time()
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_queue_size",
                    len(self._request_queue),
                    labels={"method": method, "path": path}
                )
            
            # Wait for queue space
            while len(self._active_requests) >= self.max_concurrent_requests:
                await self._check_timeouts()
                await self._cleanup_queue()
                await asyncio.sleep(0.1)  # Use asyncio.sleep instead of time.sleep
            
            # Remove from queue
            self._request_queue.pop(request_id, None)
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_queue_size",
                    len(self._request_queue),
                    labels={"method": method, "path": path}
                )
        
        # Process request
        try:
            self._active_requests.add(request_id)
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_concurrent_requests",
                    len(self._active_requests),
                    labels={"method": method, "path": path}
                )
            
            # Add processing metadata
            scope["state"]["processing"] = {
                "start_time": time.time(),
                "timeout": self.request_timeout
            }
            
            # Process request with timeout
            try:
                await asyncio.wait_for(
                    self.app(scope, receive, send),
                    timeout=self.request_timeout
                )
                
                # Record successful processing
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_processing_time_seconds",
                        time.time() - scope["state"]["processing"]["start_time"],
                        labels={"method": method, "path": path, "status": "success"}
                    )
                    
            except asyncio.TimeoutError:
                self._logger.warning(
                    "request_timeout",
                    request_id=request_id,
                    timeout=self.request_timeout
                )
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_processing_time_seconds",
                        self.request_timeout,
                        labels={"method": method, "path": path, "status": "timeout"}
                    )
                raise
                
        finally:
            # Cleanup request timing
            self._request_start_times.pop(request_id, None)
            self._active_requests.remove(request_id)
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_concurrent_requests",
                    len(self._active_requests),
                    labels={"method": method, "path": path}
                )
    
    async def _check_timeouts(self) -> None:
        """Check for request timeouts."""
        current_time = time.time()
        timed_out = []
        
        for request_id, start_time in self._request_queue.items():
            if current_time - start_time > self.request_timeout:
                timed_out.append(request_id)
                self._logger.warning(
                    "Request timed out in queue",
                    extra={"request_id": request_id}
                )
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_queue_timeouts_total",
                        1,
                        labels={
                            "method": "unknown",  # We don't have scope here
                            "path": "unknown"
                        }
                    )
        
        for request_id in timed_out:
            self._request_queue.pop(request_id, None)
        
        if self.metrics:
            self.metrics.record(
                f"{self.name}_queue_size",
                len(self._request_queue),
                labels={
                    "method": "unknown",
                    "path": "unknown"
                }
            )
    
    async def _cleanup_queue(self) -> None:
        """Clean up request queue."""
        # Remove completed requests from queue
        completed = []
        for request_id in self._request_queue:
            if len(self._active_requests) < self.max_concurrent_requests:
                completed.append(request_id)
            else:
                break
        
        for request_id in completed:
            self._request_queue.pop(request_id, None)
        
        if self.metrics and completed:
            self.metrics.record(
                f"{self.name}_queue_size",
                len(self._request_queue),
                labels={
                    "method": "unknown",
                    "path": "unknown"
                }
            )
    
    async def _initialize_impl(self) -> None:
        """Initialize middleware."""
        await super()._initialize_impl()
        self._active_requests = set()
        self._request_start_times.clear()
        self._request_queue.clear()
        if self.metrics:
            self.metrics.record(
                f"{self.name}_concurrent_requests",
                0,
                labels={"method": "unknown", "path": "unknown"}
            )
            self.metrics.record(
                f"{self.name}_queue_size",
                0,
                labels={"method": "unknown", "path": "unknown"}
            )
    
    async def _stop_impl(self) -> None:
        """Stop middleware."""
        await super()._stop_impl()
        self._active_requests = set()
        self._request_start_times.clear()
        self._request_queue.clear()
        if self.metrics:
            self.metrics.record(
                f"{self.name}_concurrent_requests",
                0,
                labels={"method": "unknown", "path": "unknown"}
            )
            self.metrics.record(
                f"{self.name}_queue_size",
                0,
                labels={"method": "unknown", "path": "unknown"}
            )
    
    def get_active_requests_count(self) -> int:
        """Get number of active requests."""
        return len(self._active_requests)
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self._request_queue)
    
    def update_limits(self, max_concurrent_requests: int, request_timeout: float) -> None:
        """Update request processing limits."""
        self.max_concurrent_requests = max_concurrent_requests
        self.request_timeout = request_timeout
    
    async def cleanup(self) -> None:
        """Cleanup middleware resources."""
        await super().cleanup()
        self._active_requests = set()
        self._request_start_times.clear()
        self._request_queue.clear()
        if self.metrics:
            self.metrics.record(
                f"{self.name}_concurrent_requests",
                0,
                labels={"method": "unknown", "path": "unknown"}
            )
            self.metrics.record(
                f"{self.name}_queue_size",
                0,
                labels={"method": "unknown", "path": "unknown"}
            )

    async def _cleanup_expired_requests(self) -> None:
        """Cleanup expired requests."""
        current_time = time.time()
        expired = []
        for request_id, start_time in self._request_start_times.items():
            if (current_time - start_time.timestamp()) > self.request_timeout:
                expired.append(request_id)
                self._logger.warning(
                    "request_expired",
                    request_id=request_id
                )
        
        for request_id in expired:
            self._request_start_times.pop(request_id, None)
            if request_id in self._active_requests:
                self._active_requests.remove(request_id)
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_concurrent_requests",
                        len(self._active_requests),
                        labels={"method": "unknown", "path": "unknown"}
                    )