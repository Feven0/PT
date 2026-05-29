"""Metric type definitions."""
from typing import (
    Dict, Any, Optional, 
    Set, Protocol, 
    runtime_checkable, 
    Union,
)
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field

from core.types.model import CoreBaseModel
from .components import ComponentState, HealthStatus

MetricValue = Union[int, float]
MetricLabels = Dict[str, str]
MetricTags = Dict[str, str]


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"        # Monotonically increasing counter
    GAUGE = "gauge"           # Value that can go up and down
    HISTOGRAM = "histogram"    # Distribution of values
    SUMMARY = "summary"       # Distribution with quantiles


class Metric(CoreBaseModel):
    """Metric definition."""
    name: str = Field(description="Metric name")
    mtype: MetricType = Field(description="Metric type")
    description: str = Field(description="Metric description")
    default_value: Optional[MetricValue] = Field(default=None, description="Default metric value")
    labels: MetricLabels = Field(default_factory=dict, description="Metric labels")
    timestamp: datetime = Field(default_factory=datetime.now, description="Metric timestamp")
    component: Optional[str] = Field(default=None, description="Component name")
    unit: Optional[str] = Field(default=None, description="Metric unit")


@runtime_checkable
class MetricsProtocol(Protocol):
    """Protocol for metrics management."""
    
    def register_metric(
        self,
        name: str,
        mtype: MetricType,
        description: str,
        default_value: Optional[MetricValue] = None,
        labels: Optional[MetricLabels] = None,
        component: Optional[str] = None,
        unit: Optional[str] = None,
        **kwargs
    ) -> None:
        """Register a new metric with type and metadata."""
        ...
    
    def record(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric value."""
        ...
    
    def get_metric(self, name: str) -> Optional[Any]:
        """Get metric by name."""
        ...
    
    def get_component_metrics(self, component: str) -> Set[str]:
        """Get all metric names for a component."""
        ...
    
    def with_labels(self, labels: Dict[str, str]) -> 'MetricsProtocol':
        """Create a new metrics instance with default labels."""
        ...
    
    async def export(self) -> Dict[str, Any]:
        """Export all metrics data."""
        ... 