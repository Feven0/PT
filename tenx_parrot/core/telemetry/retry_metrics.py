"""Retry metrics."""
from typing import Dict, Any, Optional
from contextlib import contextmanager
from time import perf_counter

from .metrics import MetricsManager
from ..types import MetricType

class RetryMetrics:
    """Helper class for standardized retry metric collection."""

    def __init__(self, metrics: MetricsManager, retry_name: str):
        """Initialize retry metrics.
        
        Args:
            metrics: Metrics manager instance
            retry_name: Name of the retry manager for metric prefixing
        """
        self.metrics = metrics
        self.retry_name = retry_name
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        """Register default retry metrics."""
        # Attempt Metrics
        self.metrics.register_metric(
            name=f"{self.retry_name}_attempts_total",
            type=MetricType.COUNTER,
            description=f"Total number of retry attempts by {self.retry_name}",
            labels={"operation": "", "attempt": ""},
            component="retry"
        )

        # Success/Failure Metrics
        self.metrics.register_metric(
            name=f"{self.retry_name}_operations_total",
            type=MetricType.COUNTER,
            description=f"Total number of operations handled by {self.retry_name}",
            labels={"operation": "", "status": ""},
            component="retry"
        )

        # Backoff Metrics
        self.metrics.register_metric(
            name=f"{self.retry_name}_backoff_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Backoff duration in seconds for {self.retry_name}",
            labels={"operation": "", "attempt": ""},
            component="retry"
        )

        # Duration Metrics
        self.metrics.register_metric(
            name=f"{self.retry_name}_operation_duration_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Duration of operations in {self.retry_name}",
            labels={"operation": "", "attempt": ""},
            component="retry"
        )

        # Error Metrics
        self.metrics.register_metric(
            name=f"{self.retry_name}_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of errors in {self.retry_name}",
            labels={"error_type": "", "operation": "", "attempt": ""},
            component="retry"
        )

    def record_attempt(self, operation: str, attempt: int) -> None:
        """Record retry attempt.
        
        Args:
            operation: Name of the operation
            attempt: Attempt number
        """
        self.metrics.record(
            name=f"{self.retry_name}_attempts_total",
            value=1.0,
            labels={"operation": operation, "attempt": str(attempt)}
        )

    def record_operation(self, operation: str, status: str = "success") -> None:
        """Record operation outcome.
        
        Args:
            operation: Name of the operation
            status: Operation status (success/failure)
        """
        self.metrics.record(
            name=f"{self.retry_name}_operations_total",
            value=1.0,
            labels={"operation": operation, "status": status}
        )

    def record_backoff(self, operation: str, attempt: int, duration: float) -> None:
        """Record backoff duration.
        
        Args:
            operation: Name of the operation
            attempt: Attempt number
            duration: Backoff duration in seconds
        """
        self.metrics.record(
            name=f"{self.retry_name}_backoff_seconds",
            value=duration,
            labels={"operation": operation, "attempt": str(attempt)}
        )

    def record_operation_duration(self, operation: str, attempt: int, duration: float) -> None:
        """Record operation duration.
        
        Args:
            operation: Name of the operation
            attempt: Attempt number
            duration: Operation duration in seconds
        """
        self.metrics.record(
            name=f"{self.retry_name}_operation_duration_seconds",
            value=duration,
            labels={"operation": operation, "attempt": str(attempt)}
        )

    def record_error(self, error_type: str, operation: str, attempt: int) -> None:
        """Record retry error.
        
        Args:
            error_type: Type of error
            operation: Operation where error occurred
            attempt: Attempt number
        """
        self.metrics.record(
            name=f"{self.retry_name}_errors_total",
            value=1.0,
            labels={
                "error_type": error_type,
                "operation": operation,
                "attempt": str(attempt)
            }
        )

    @contextmanager
    def operation_duration(self, operation: str, attempt: int):
        """Context manager to measure operation duration.
        
        Args:
            operation: Name of the operation
            attempt: Attempt number
        """
        start_time = perf_counter()
        try:
            yield
        except Exception as e:
            self.record_error(type(e).__name__, operation, attempt)
            raise
        finally:
            duration = perf_counter() - start_time
            self.record_operation_duration(operation, attempt, duration)

    @contextmanager
    def retry_operation(self, operation: str):
        """Context manager to track full retry operation.
        
        Args:
            operation: Name of the operation
        """
        attempt = 0
        start_time = perf_counter()
        status = "success"
        
        try:
            while True:
                attempt += 1
                self.record_attempt(operation, attempt)
                
                try:
                    with self.operation_duration(operation, attempt):
                        yield attempt
                    break  # Success - exit retry loop
                except Exception as e:
                    if attempt >= self.max_attempts:  # Assuming max_attempts is configured
                        status = "failure"
                        raise
                    self.record_error(type(e).__name__, operation, attempt)
                    backoff_time = self._calculate_backoff(attempt)  # Assuming backoff calculation
                    self.record_backoff(operation, attempt, backoff_time)
                    # Sleep for backoff_time here
        finally:
            self.record_operation(operation, status) 