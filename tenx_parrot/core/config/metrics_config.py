"""Metrics configuration."""
from typing import Optional, Tuple
from pydantic import Field, ConfigDict

from ..types.model import CoreBaseModel

# Metrics configuration
class MetricsConfig(CoreBaseModel):
    """Metrics configuration."""
    enabled: bool = Field(default=True, description="Enable metrics collection")
    namespace: str = Field(default="app", description="Metrics namespace")
    subsystem: str = Field(default="core", description="Metrics subsystem")
    buckets: Tuple[float, ...] = Field(
        default=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 25.0, 50.0, 75.0, 100.0),
        description="Histogram buckets"
    )
