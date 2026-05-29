"""Repository metrics."""
from typing import Dict, Any, Optional, Set
from contextlib import contextmanager
from time import perf_counter
from datetime import datetime

from .metrics import MetricsManager
from ..types import MetricType

class RepositoryMetrics:
    """Helper class for standardized repository metric collection."""

    def __init__(self, metrics: MetricsManager, repository_name: str):
        """Initialize repository metrics.
        
        Args:
            metrics: Metrics manager instance
            repository_name: Name of the repository for metric prefixing
        """
        self.metrics = metrics
        self.repository_name = repository_name
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        """Register default repository metrics."""
        # Performance Metrics
        self.metrics.register_metric(
            name=f"{self.repository_name}_operation_duration_seconds",
            type=MetricType.HISTOGRAM,
            description=f"Duration of {self.repository_name} operations in seconds",
            labels={"operation": "", "status": ""},
            component=self.repository_name
        )

        self.metrics.register_metric(
            name=f"{self.repository_name}_query_count_total",
            type=MetricType.COUNTER,
            description=f"Total number of {self.repository_name} queries",
            labels={"query_type": "", "status": ""},
            component=self.repository_name
        )

        # Cache Metrics
        self.metrics.register_metric(
            name=f"{self.repository_name}_cache_hits_total",
            type=MetricType.COUNTER,
            description=f"Total number of {self.repository_name} cache hits",
            labels={"operation": ""},
            component=self.repository_name
        )

        self.metrics.register_metric(
            name=f"{self.repository_name}_cache_misses_total",
            type=MetricType.COUNTER,
            description=f"Total number of {self.repository_name} cache misses",
            labels={"operation": ""},
            component=self.repository_name
        )

        # Connection Metrics
        self.metrics.register_metric(
            name=f"{self.repository_name}_connections_active",
            type=MetricType.GAUGE,
            description=f"Number of active {self.repository_name} connections",
            component=self.repository_name
        )

        # Row Metrics
        self.metrics.register_metric(
            name=f"{self.repository_name}_rows_affected",
            type=MetricType.HISTOGRAM,
            description=f"Number of rows affected by {self.repository_name} operations",
            labels={"operation": ""},
            component=self.repository_name
        )

    def record_operation_duration(self, operation: str, duration: float, status: str = "success") -> None:
        """Record duration of an operation.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            status: Operation status (success/error)
        """
        self.metrics.record(
            name=f"{self.repository_name}_operation_duration_seconds",
            value=duration,
            labels={"operation": operation, "status": status}
        )

    def increment_query_count(self, query_type: str, status: str = "success") -> None:
        """Increment query counter.
        
        Args:
            query_type: Type of query (select/insert/update/delete)
            status: Query status (success/error)
        """
        self.metrics.record(
            name=f"{self.repository_name}_query_count_total",
            value=1.0,
            labels={"query_type": query_type, "status": status}
        )

    def record_cache_hit(self, operation: str) -> None:
        """Record cache hit.
        
        Args:
            operation: Name of the operation
        """
        self.metrics.record(
            name=f"{self.repository_name}_cache_hits_total",
            value=1.0,
            labels={"operation": operation}
        )

    def record_cache_miss(self, operation: str) -> None:
        """Record cache miss.
        
        Args:
            operation: Name of the operation
        """
        self.metrics.record(
            name=f"{self.repository_name}_cache_misses_total",
            value=1.0,
            labels={"operation": operation}
        )

    def set_active_connections(self, count: int) -> None:
        """Set number of active connections.
        
        Args:
            count: Number of active connections
        """
        self.metrics.record(
            name=f"{self.repository_name}_connections_active",
            value=float(count)
        )

    def record_rows_affected(self, operation: str, count: int) -> None:
        """Record number of rows affected by an operation.
        
        Args:
            operation: Name of the operation
            count: Number of rows affected
        """
        self.metrics.record(
            name=f"{self.repository_name}_rows_affected",
            value=float(count),
            labels={"operation": operation}
        )

    @contextmanager
    def operation_duration(self, operation: str, query_type: str = None):
        """Context manager to measure operation duration.
        
        Args:
            operation: Name of the operation
            query_type: Optional query type for query counting
        """
        start_time = perf_counter()
        status = "success"
        try:
            yield
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = perf_counter() - start_time
            self.record_operation_duration(operation, duration, status)
            if query_type:
                self.increment_query_count(query_type, status) 