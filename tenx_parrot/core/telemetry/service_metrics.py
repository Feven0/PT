"""Service metrics."""
from typing import Dict, Any, Optional, Set, TypeVar, Generic, TYPE_CHECKING
from contextlib import contextmanager
from time import perf_counter
from datetime import datetime


from core.types.metrics import MetricType
from core.types.components import ComponentState

if TYPE_CHECKING:
    from core.telemetry.metrics import MetricsManager

class ServiceMetrics:
    """Helper class for standardized service metric collection."""

    def __init__(self, metrics: 'MetricsManager', service_name: str):
        """Initialize service metrics.
        
        Args:
            metrics: Metrics manager instance
            service_name: Name of the service for metric prefixing
        """
        self.metrics = metrics
        self.service_name = service_name
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        """Register default service metrics."""
        # Performance Metrics
        self.metrics.register_metric(
            name=f"{self.service_name}_operation_duration_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Duration of {self.service_name} operations in seconds",
            labels={"operation": "", "status": ""},
            component=self.service_name
        )
        
        self.metrics.register_metric(
            name=f"{self.service_name}_requests_total",
            type=MetricType.COUNTER,
            description=f"Total number of {self.service_name} requests",
            labels={"operation": "", "status": ""},
            component=self.service_name
        )

        # State Metrics
        self.metrics.register_metric(
            name=f"{self.service_name}_state",
            type=MetricType.GAUGE,
            description=f"Current state of {self.service_name}",
            labels={"state": ""},
            component=self.service_name
        )

        # Error Metrics
        self.metrics.register_metric(
            name=f"{self.service_name}_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of {self.service_name} errors",
            labels={"error_type": "", "operation": ""},
            component=self.service_name
        )

    def record_operation_duration(self, operation: str, duration: float, status: str = "success") -> None:
        """Record duration of an operation.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            status: Operation status (success/error)
        """
        self.metrics.record(
            name=f"{self.service_name}_operation_duration_seconds",
            value=duration,
            labels={"operation": operation, "status": status}
        )

    def increment_request_count(self, operation: str, status: str = "success") -> None:
        """Increment request counter.
        
        Args:
            operation: Name of the operation
            status: Request status (success/error)
        """
        self.metrics.record(
            name=f"{self.service_name}_requests_total",
            value=1.0,
            labels={"operation": operation, "status": status}
        )

    def set_service_state(self, state: ComponentState) -> None:
        """Set service state.
        
        Args:
            state: Current service state
        """
        self.metrics.record(
            name=f"{self.service_name}_state",
            value=1.0,
            labels={"state": state.value}
        )
        # Reset other states to 0
        for other_state in ComponentState:
            if other_state != state:
                self.metrics.record(
                    name=f"{self.service_name}_state",
                    value=0.0,
                    labels={"state": other_state.value}
                )

    def record_error(self, error_type: str, operation: str) -> None:
        """Record service error.
        
        Args:
            error_type: Type of error
            operation: Operation where error occurred
        """
        self.metrics.record(
            name=f"{self.service_name}_errors_total",
            value=1.0,
            labels={"error_type": error_type, "operation": operation}
        )

    @contextmanager
    def operation_duration(self, operation: str):
        """Context manager to measure operation duration.
        
        Args:
            operation: Name of the operation
        """
        start_time = perf_counter()
        status = "success"
        try:
            yield
        except Exception as e:
            status = "error"
            self.record_error(type(e).__name__, operation)
            raise
        finally:
            duration = perf_counter() - start_time
            self.record_operation_duration(operation, duration, status)
            self.increment_request_count(operation, status) 