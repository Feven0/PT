"""Distributed tracing middleware."""
from typing import Optional, Dict, Any
from fastapi import Request, Response
from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Receive, Scope, Send
from core.logging import logger, BackendLogger
from core.telemetry.metrics import MetricsManager
from core.config import AppConfig
from core.types.metrics import MetricType
import uuid
from datetime import datetime, timezone

from .base import MiddlewareComponent


class TracingMiddleware(MiddlewareComponent):
    """OpenTelemetry distributed tracing middleware."""
    
    def __init__(
        self,
        app: ASGIApp,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        **kwargs
    ):
        super().__init__(
            app=app,
            name="tracing_middleware",
            metrics=metrics,
            logger=logger,
            **kwargs
        )
    
    def _register_request_metrics_impl(self) -> None:
        """Register tracing specific metrics."""
        if not self.metrics:
            return
            
        # Traced requests
        self.metrics.register_metric(
            name=f"{self.name}_traced_requests_total",
            type=MetricType.COUNTER,
            description=f"Total number of traced requests in {self.name}",
            component=self.name,
            labels={"path": "", "method": "", "status_code": ""}
        )
        
        # Trace spans
        self.metrics.register_metric(
            name=f"{self.name}_spans_total",
            type=MetricType.COUNTER,
            description=f"Total number of trace spans created in {self.name}",
            component=self.name,
            labels={"path": "", "method": "", "span_type": ""}
        )
        
        # Trace errors
        self.metrics.register_metric(
            name=f"{self.name}_trace_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of tracing errors in {self.name}",
            component=self.name,
            labels={"path": "", "method": "", "error_type": ""}
        )
    
    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process request with distributed tracing."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        # Get or generate trace ID
        trace_id = scope.get("headers", {}).get("x-trace-id", str(uuid.uuid4()))
        scope["trace_id"] = trace_id
        
        try:
            # Process request
            await self.app(scope, receive, send)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_traced_requests_total",
                    1,
                    labels={
                        "method": scope.get("method", ""),
                        "path": scope.get("path", ""),
                        "status_code": scope.get("status_code", 200)
                    }
                )
                
        except Exception as e:
            # Record error metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={
                        "method": scope.get("method", ""),
                        "path": scope.get("path", ""),
                        "error": type(e).__name__
                    }
                )
            raise 