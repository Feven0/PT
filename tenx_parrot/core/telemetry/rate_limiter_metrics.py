"""Rate limiter metrics."""
from typing import Dict, Any, Optional
from contextlib import contextmanager
from time import perf_counter

from .metrics import MetricsManager
from ..types import MetricType

class RateLimiterMetrics:
    """Helper class for standardized rate limiter metric collection."""

    def __init__(self, metrics: MetricsManager, limiter_name: str):
        """Initialize rate limiter metrics.
        
        Args:
            metrics: Metrics manager instance
            limiter_name: Name of the rate limiter for metric prefixing
        """
        self.metrics = metrics
        self.limiter_name = limiter_name
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        """Register default rate limiter metrics."""
        # Request Metrics
        self.metrics.register_metric(
            name=f"{self.limiter_name}_requests_total",
            type=MetricType.COUNTER,
            description=f"Total number of requests processed by {self.limiter_name}",
            labels={"operation": "", "status": ""},
            component="rate_limiter"
        )

        # Throttling Metrics
        self.metrics.register_metric(
            name=f"{self.limiter_name}_throttled_total",
            type=MetricType.COUNTER,
            description=f"Total number of throttled requests by {self.limiter_name}",
            labels={"operation": "", "reason": ""},
            component="rate_limiter"
        )

        # Token Bucket Metrics
        self.metrics.register_metric(
            name=f"{self.limiter_name}_tokens_remaining",
            type=MetricType.GAUGE,
            description=f"Number of tokens remaining in {self.limiter_name}",
            labels={"bucket": ""},
            component="rate_limiter"
        )

        self.metrics.register_metric(
            name=f"{self.limiter_name}_token_refill_rate",
            type=MetricType.GAUGE,
            description=f"Token refill rate for {self.limiter_name}",
            labels={"bucket": ""},
            component="rate_limiter"
        )

        # Window Metrics
        self.metrics.register_metric(
            name=f"{self.limiter_name}_window_requests",
            type=MetricType.GAUGE,
            description=f"Number of requests in current window for {self.limiter_name}",
            labels={"window": ""},
            component="rate_limiter"
        )

        # Latency Metrics
        self.metrics.register_metric(
            name=f"{self.limiter_name}_check_duration_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Duration of rate limit checks in {self.limiter_name}",
            labels={"operation": ""},
            component="rate_limiter"
        )

        # Error Metrics
        self.metrics.register_metric(
            name=f"{self.limiter_name}_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of rate limiter errors in {self.limiter_name}",
            labels={"error_type": "", "operation": ""},
            component="rate_limiter"
        )

    def record_request(self, operation: str, status: str = "allowed") -> None:
        """Record rate limit request.
        
        Args:
            operation: Name of the operation
            status: Request status (allowed/denied)
        """
        self.metrics.record(
            name=f"{self.limiter_name}_requests_total",
            value=1.0,
            labels={"operation": operation, "status": status}
        )

    def record_throttle(self, operation: str, reason: str) -> None:
        """Record throttled request.
        
        Args:
            operation: Name of the operation
            reason: Reason for throttling
        """
        self.metrics.record(
            name=f"{self.limiter_name}_throttled_total",
            value=1.0,
            labels={"operation": operation, "reason": reason}
        )

    def set_tokens_remaining(self, bucket: str, tokens: int) -> None:
        """Set number of tokens remaining.
        
        Args:
            bucket: Name of the token bucket
            tokens: Number of tokens remaining
        """
        self.metrics.record(
            name=f"{self.limiter_name}_tokens_remaining",
            value=float(tokens),
            labels={"bucket": bucket}
        )

    def set_token_refill_rate(self, bucket: str, rate: float) -> None:
        """Set token refill rate.
        
        Args:
            bucket: Name of the token bucket
            rate: Tokens per second refill rate
        """
        self.metrics.record(
            name=f"{self.limiter_name}_token_refill_rate",
            value=rate,
            labels={"bucket": bucket}
        )

    def set_window_requests(self, window: str, count: int) -> None:
        """Set number of requests in current window.
        
        Args:
            window: Window identifier
            count: Number of requests
        """
        self.metrics.record(
            name=f"{self.limiter_name}_window_requests",
            value=float(count),
            labels={"window": window}
        )

    def record_check_duration(self, operation: str, duration: float) -> None:
        """Record duration of rate limit check.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
        """
        self.metrics.record(
            name=f"{self.limiter_name}_check_duration_seconds",
            value=duration,
            labels={"operation": operation}
        )

    def record_error(self, error_type: str, operation: str) -> None:
        """Record rate limiter error.
        
        Args:
            error_type: Type of error
            operation: Operation where error occurred
        """
        self.metrics.record(
            name=f"{self.limiter_name}_errors_total",
            value=1.0,
            labels={"error_type": error_type, "operation": operation}
        )

    @contextmanager
    def check_duration(self, operation: str):
        """Context manager to measure rate limit check duration.
        
        Args:
            operation: Name of the operation
        """
        start_time = perf_counter()
        try:
            yield
        except Exception as e:
            self.record_error(type(e).__name__, operation)
            raise
        finally:
            duration = perf_counter() - start_time
            self.record_check_duration(operation, duration) 