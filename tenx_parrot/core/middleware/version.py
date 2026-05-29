"""API version negotiation middleware."""
from typing import Dict, Optional, Any
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse

from .base import MiddlewareComponent
from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.types.metrics import MetricType

class VersionNegotiationMiddleware(MiddlewareComponent):
    """API version negotiation middleware."""
    
    def __init__(
        self,
        app: ASGIApp,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        default_version: str = "1.0",
        supported_versions: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        super().__init__(
            app=app,
            name="version_middleware",
            metrics=metrics,
            logger=logger,
            **kwargs
        )
        self._default_version = default_version
        self._supported_versions = supported_versions or {"1.0": "/v1"}

    def _register_request_metrics_impl(self) -> None:
        """Register version negotiation specific metrics."""
        if not self.metrics:
            return
            
        # Version requests
        self.metrics.register_metric(
            name=f"{self.name}_requests_by_version",
            type=MetricType.COUNTER,
            description=f"Number of requests by API version in {self.name}",
            component=self.name,
            labels={"version": "", "path": "", "method": ""}
        )
        
        # Version negotiation failures
        self.metrics.register_metric(
            name=f"{self.name}_negotiation_failures_total",
            type=MetricType.COUNTER,
            description=f"Number of version negotiation failures in {self.name}",
            component=self.name,
            labels={"requested_version": "", "path": "", "method": ""}
        )
        
        # Default version fallbacks
        self.metrics.register_metric(
            name=f"{self.name}_default_fallbacks_total",
            type=MetricType.COUNTER,
            description=f"Number of fallbacks to default version in {self.name}",
            component=self.name,
            labels={"path": "", "method": ""}
        )
    
    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process request with version negotiation."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        try:
            # Get requested version
            headers = dict(scope.get("headers", []))
            version = headers.get(b"accept-version", self._default_version.encode()).decode()
            
            # Record default version fallback if needed
            if version == self._default_version and self.metrics:
                self.metrics.record(
                    f"{self.name}_default_fallbacks_total",
                    1,
                    labels={
                        "path": scope.get("path", ""),
                        "method": scope.get("method", "")
                    }
                )
            
            # Validate version
            if version not in self._supported_versions:
                # Record negotiation failure
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_negotiation_failures_total",
                        1,
                        labels={
                            "requested_version": version,
                            "path": scope.get("path", ""),
                            "method": scope.get("method", "")
                        }
                    )
                
                response = JSONResponse(
                    status_code=400,
                    content={
                        "error": "Unsupported API version",
                        "version": version,
                        "supported_versions": list(self._supported_versions.keys())
                    }
                )
                await response(scope, receive, send)
                return
                
            # Set version in scope state
            if "state" not in scope:
                scope["state"] = {}
            scope["state"]["version"] = version
            scope["state"]["version_path"] = self._supported_versions[version]
            
            # Record version request
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_by_version",
                    1,
                    labels={
                        "version": version,
                        "path": scope.get("path", ""),
                        "method": scope.get("method", "")
                    }
                )
                
            # Process request
            await self.app(scope, receive, send)
            
        except Exception as e:
            self._logger.error(f"Version negotiation failed: {str(e)}")
            raise 