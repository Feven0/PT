"""WebSocket metrics."""
from typing import Dict, Any, Optional, Set
from contextlib import contextmanager
from time import perf_counter
from datetime import datetime

from .metrics import MetricsManager
from ..types import MetricType

class WebSocketMetrics:
    """Helper class for standardized WebSocket metric collection."""

    def __init__(self, metrics: MetricsManager, endpoint: str):
        """Initialize WebSocket metrics.
        
        Args:
            metrics: Metrics manager instance
            endpoint: WebSocket endpoint name for metric prefixing
        """
        self.metrics = metrics
        self.endpoint = endpoint
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        """Register default WebSocket metrics."""
        # Connection Metrics
        self.metrics.register_metric(
            name=f"websocket_{self.endpoint}_connections_active",
            type=MetricType.GAUGE,
            description=f"Number of active WebSocket connections for {self.endpoint}",
            component="websocket"
        )

        # Message Metrics
        self.metrics.register_metric(
            name=f"websocket_{self.endpoint}_messages_total",
            type=MetricType.COUNTER,
            description=f"Total number of WebSocket messages for {self.endpoint}",
            labels={"message_type": "", "direction": ""},
            component="websocket"
        )

        # Error Metrics
        self.metrics.register_metric(
            name=f"websocket_{self.endpoint}_errors_total",
            type=MetricType.COUNTER,
            description=f"Total number of WebSocket errors for {self.endpoint}",
            labels={"error_type": ""},
            component="websocket"
        )

        # Latency Metrics
        self.metrics.register_metric(
            name=f"websocket_{self.endpoint}_message_latency_seconds",
            type=MetricType.HISTOGRAM,
            description=f"WebSocket message processing latency for {self.endpoint}",
            labels={"message_type": ""},
            component="websocket"
        )

        # Message Size Metrics
        self.metrics.register_metric(
            name=f"websocket_{self.endpoint}_message_size_bytes",
            type=MetricType.HISTOGRAM,
            description=f"WebSocket message size in bytes for {self.endpoint}",
            labels={"message_type": "", "direction": ""},
            component="websocket"
        )

    def set_active_connections(self, count: int) -> None:
        """Set number of active connections.
        
        Args:
            count: Number of active connections
        """
        self.metrics.record(
            name=f"websocket_{self.endpoint}_connections_active",
            value=float(count)
        )

    def increment_message_count(self, message_type: str, direction: str) -> None:
        """Increment message counter.
        
        Args:
            message_type: Type of message
            direction: Message direction (sent/received)
        """
        self.metrics.record(
            name=f"websocket_{self.endpoint}_messages_total",
            value=1.0,
            labels={"message_type": message_type, "direction": direction}
        )

    def record_error(self, error_type: str) -> None:
        """Record WebSocket error.
        
        Args:
            error_type: Type of error
        """
        self.metrics.record(
            name=f"websocket_{self.endpoint}_errors_total",
            value=1.0,
            labels={"error_type": error_type}
        )

    def record_message_latency(self, message_type: str, latency: float) -> None:
        """Record message processing latency.
        
        Args:
            message_type: Type of message
            latency: Processing latency in seconds
        """
        self.metrics.record(
            name=f"websocket_{self.endpoint}_message_latency_seconds",
            value=latency,
            labels={"message_type": message_type}
        )

    def record_message_size(self, message_type: str, direction: str, size: int) -> None:
        """Record message size.
        
        Args:
            message_type: Type of message
            direction: Message direction (sent/received)
            size: Message size in bytes
        """
        self.metrics.record(
            name=f"websocket_{self.endpoint}_message_size_bytes",
            value=float(size),
            labels={"message_type": message_type, "direction": direction}
        )

    @contextmanager
    def message_processing(self, message_type: str):
        """Context manager to measure message processing.
        
        Args:
            message_type: Type of message being processed
        """
        start_time = perf_counter()
        try:
            yield
        except Exception as e:
            self.record_error(type(e).__name__)
            raise
        finally:
            latency = perf_counter() - start_time
            self.record_message_latency(message_type, latency) 