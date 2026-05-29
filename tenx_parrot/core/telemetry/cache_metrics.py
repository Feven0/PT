"""Cache metrics."""
from typing import Dict, Any, Optional, Set
from contextlib import contextmanager
from time import perf_counter
from datetime import datetime

from .metrics import MetricsManager
from ..types import MetricType

class CacheMetrics:
    """Helper class for standardized cache metric collection."""

    def __init__(self, metrics: MetricsManager, cache_name: str):
        """Initialize cache metrics.
        
        Args:
            metrics: Metrics manager instance
            cache_name: Name of the cache for metric prefixing
        """
        self.metrics = metrics
        self.cache_name = cache_name
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        """Register default cache metrics."""
        # Hit/Miss Metrics
        self.metrics.register_metric(
            name=f"{self.cache_name}_hits_total",
            type=MetricType.COUNTER,
            description=f"Total number of cache hits for {self.cache_name}",
            labels={"operation": ""},
            component="cache"
        )

        self.metrics.register_metric(
            name=f"{self.cache_name}_misses_total",
            type=MetricType.COUNTER,
            description=f"Total number of cache misses for {self.cache_name}",
            labels={"operation": ""},
            component="cache"
        )

        # Memory Metrics
        self.metrics.register_metric(
            name=f"{self.cache_name}_memory_bytes",
            type=MetricType.GAUGE,
            description=f"Memory usage in bytes for {self.cache_name}",
            component="cache"
        )

        self.metrics.register_metric(
            name=f"{self.cache_name}_items_total",
            type=MetricType.GAUGE,
            description=f"Total number of items in {self.cache_name}",
            component="cache"
        )

        # Operation Metrics
        self.metrics.register_metric(
            name=f"{self.cache_name}_operation_duration_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Duration of {self.cache_name} operations in seconds",
            labels={"operation": "", "status": ""},
            component="cache"
        )

        # Eviction Metrics
        self.metrics.register_metric(
            name=f"{self.cache_name}_evictions_total",
            type=MetricType.COUNTER,
            description=f"Total number of cache evictions for {self.cache_name}",
            labels={"reason": ""},
            component="cache"
        )

        # Error Metrics
        self.metrics.register_metric(
            name=f"{self.cache_name}_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of cache errors for {self.cache_name}",
            labels={"error_type": "", "operation": ""},
            component="cache"
        )

    def record_hit(self, operation: str) -> None:
        """Record cache hit.
        
        Args:
            operation: Name of the operation
        """
        self.metrics.record(
            name=f"{self.cache_name}_hits_total",
            value=1.0,
            labels={"operation": operation}
        )

    def record_miss(self, operation: str) -> None:
        """Record cache miss.
        
        Args:
            operation: Name of the operation
        """
        self.metrics.record(
            name=f"{self.cache_name}_misses_total",
            value=1.0,
            labels={"operation": operation}
        )

    def set_memory_usage(self, bytes_used: int) -> None:
        """Set memory usage.
        
        Args:
            bytes_used: Memory usage in bytes
        """
        self.metrics.record(
            name=f"{self.cache_name}_memory_bytes",
            value=float(bytes_used)
        )

    def set_item_count(self, count: int) -> None:
        """Set number of items in cache.
        
        Args:
            count: Number of items
        """
        self.metrics.record(
            name=f"{self.cache_name}_items_total",
            value=float(count)
        )

    def record_operation_duration(self, operation: str, duration: float, status: str = "success") -> None:
        """Record duration of an operation.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            status: Operation status (success/error)
        """
        self.metrics.record(
            name=f"{self.cache_name}_operation_duration_seconds",
            value=duration,
            labels={"operation": operation, "status": status}
        )

    def record_eviction(self, reason: str) -> None:
        """Record cache eviction.
        
        Args:
            reason: Reason for eviction (e.g., "memory_limit", "ttl_expired")
        """
        self.metrics.record(
            name=f"{self.cache_name}_evictions_total",
            value=1.0,
            labels={"reason": reason}
        )

    def record_error(self, error_type: str, operation: str) -> None:
        """Record cache error.
        
        Args:
            error_type: Type of error
            operation: Operation where error occurred
        """
        self.metrics.record(
            name=f"{self.cache_name}_errors_total",
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

    @contextmanager
    def track_get_operation(self, operation: str):
        """Context manager to track get operation with hit/miss tracking.
        
        Args:
            operation: Name of the operation
        """
        with self.operation_duration(operation):
            result = yield
            if result is None:
                self.record_miss(operation)
            else:
                self.record_hit(operation) 