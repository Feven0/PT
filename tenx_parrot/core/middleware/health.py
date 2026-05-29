"""Health check middleware component."""
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_503_SERVICE_UNAVAILABLE
)

from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.types.components import HealthStatus, HealthStatusInfo
from core.types.metrics import MetricType

from .base import MiddlewareComponent



class HealthCheckMiddleware(MiddlewareComponent):
    """Health check middleware."""
    
    def __init__(
        self,
        app: Optional[ASGIApp] = None,
        path: str = "/health",
        interval: int = 60,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        required_components: Optional[List[str]] = None,
        **kwargs
    ):
        """Initialize health check middleware.
        
        Args:
            app: ASGI application
            path: Health check endpoint path
            interval: Health check interval in seconds
            metrics: Metrics manager instance
            logger: Logger instance
            required_components: List of required component names
            **kwargs: Additional keyword arguments
        """
        super().__init__(
            app=app,
            name="health_middleware",
            metrics=metrics,
            logger=logger,
            order=10,  # Run after core middleware
            **kwargs
        )
        self.path = path
        self.interval = interval
        self.required_components = required_components or []
        self._last_check = None
        self._initialization_time = datetime.now(timezone.utc)
        self._health_status = HealthStatusInfo(
            status=HealthStatus.UNKNOWN,
            details={
                "status": "initializing",
                "uptime": 0,
                "last_check": None
            }
        )
    @property
    def _last_status(self) -> HealthStatusInfo:
        """Get last health status."""
        return self._health_status

    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        path = scope.get("path", "")
        if path != self.path:
            await self.app(scope, receive, send)
            return
            
        # Check if we need to refresh status
        if self._should_check_health():
            await self._check_health()
        
        # Create response
        response = JSONResponse(
            content=self._health_status.to_dict(),
            status_code=HTTP_200_OK if self._health_status.status == "healthy" else HTTP_503_SERVICE_UNAVAILABLE
        )
        
        await response(scope, receive, send)
    
    def _should_check_health(self) -> bool:
        """Check if we should refresh health status."""
        if not self._last_check:
            return True
            
        elapsed = datetime.now(timezone.utc) - self._last_check
        return elapsed.total_seconds() >= self.interval
    
    async def _check_health(self) -> None:
        """Check health of all components."""
        start_time = time.time()
        
        try:
            # Get container from context
            from core.di import get_current_container
            container = get_current_container()
            if not container:
                raise RuntimeError("No container found in context")
            
            # Check required components
            component_status = {}
            is_healthy = True
            
            for component_name in self.required_components:
                try:
                    component = container.get_component(component_name)
                    if not component:
                        component_status[component_name] = {
                            "status": "unknown",
                            "error": "Component not found"
                        }
                        is_healthy = False
                        continue
                    
                    # Check component state
                    state = container.get_component_state(component_name)
                    if not state or state == "failed":
                        component_status[component_name] = {
                            "status": "unhealthy",
                            "state": state,
                            "error": "Component in failed state"
                        }
                        is_healthy = False
                        continue
                    
                    # Check component health if it has a health check method
                    if hasattr(component, "check_health"):
                        health = await component.check_health()
                        component_status[component_name] = health
                        if health.get("status") != "healthy":
                            is_healthy = False
                    else:
                        component_status[component_name] = {
                            "status": "healthy",
                            "state": state
                        }
                    
                except Exception as e:
                    component_status[component_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    is_healthy = False
            
            # Create health status
            self._health_status = HealthStatusInfo(
                status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                details={
                    "components": component_status,
                    "uptime": self._get_uptime()
                }
            )
            
            # Update metrics
            self.metrics.record(
                f"{self.name}_check_status",
                1 if is_healthy else 0
            )
            
        except Exception as e:
            self._health_status = HealthStatusInfo(
                status=HealthStatus.UNHEALTHY,
                details={"error": str(e)}
            )
            self.metrics.record(
                f"{self.name}_check_status",
                0
            )
            
        finally:
            # Update check time and duration metric
            self._last_check = datetime.now(timezone.utc)
            duration = time.time() - start_time
            self.metrics.record(
                f"{self.name}_check_duration_seconds",
                duration
            )
    
    def _get_uptime(self) -> str:
        """Get application uptime."""
        if not self._initialization_time:
            return "unknown"
            
        uptime = datetime.now(timezone.utc) - self._initialization_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    async def _initialize_impl(self) -> None:
        """Initialize middleware."""
        await super()._initialize_impl()
        await self._check_health()
    
    def update_interval(self, interval: int) -> None:
        """Update health check interval."""
        self.interval = interval
    
    def update_required_components(self, components: List[str]) -> None:
        """Update required components list."""
        self.required_components = components
    
    def get_last_status(self) -> Optional[HealthStatusInfo]:
        """Get last health check status."""
        return self._health_status 
    
    def _register_metrics(self) -> None:
        """Register middleware metrics."""
        self.metrics.register_metric(
            f"{self.name}_health_status",
            MetricType.GAUGE,
            f"Current health status in {self.name}",
            labels={"component": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_check_duration_seconds",
            MetricType.HISTOGRAM,
            f"Health check duration in seconds in {self.name}",
            labels={"component": ""},
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
        ) 