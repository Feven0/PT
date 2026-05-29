"""Health check models."""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import Field

from core.types.model import CoreBaseModel
from core.types.components import HealthStatus


class StorageHealth(CoreBaseModel):
    """Storage health model."""
    status: HealthStatus
    latency_ms: float
    error_rate: float
    last_error: Optional[str] = None
    last_check: datetime
    details: Dict = Field(default_factory=dict)


class ServiceHealth(CoreBaseModel):
    """Service health model."""
    status: HealthStatus
    uptime: float
    memory_usage: float
    cpu_usage: float
    error_count: int
    last_error: Optional[str] = None
    last_check: datetime
    details: Dict = Field(default_factory=dict)


class CacheHealth(CoreBaseModel):
    """Cache health model."""
    status: HealthStatus
    hit_rate: float
    miss_rate: float
    memory_usage: float
    eviction_count: int
    last_check: datetime
    details: Dict = Field(default_factory=dict)


class QueueHealth(CoreBaseModel):
    """Queue health model."""
    status: HealthStatus
    queue_size: int
    processing_rate: float
    error_rate: float
    worker_count: int
    last_check: datetime
    details: Dict = Field(default_factory=dict)


class SystemHealth(CoreBaseModel):
    """System health model."""
    status: HealthStatus
    strapi: Optional[StorageHealth] = None
    weaviate: Optional[StorageHealth] = None
    cache: Optional[CacheHealth] = None
    queue: Optional[QueueHealth] = None
    services: Dict[str, ServiceHealth] = Field(default_factory=dict)
    last_check: datetime
    details: Dict = Field(default_factory=dict)

    def get_overall_status(self) -> HealthStatus:
        """Calculate overall system health status."""
        statuses = [
            self.strapi.status if self.strapi else HealthStatus.UNKNOWN,
            self.weaviate.status if self.weaviate else HealthStatus.UNKNOWN,
            self.cache.status if self.cache else HealthStatus.UNKNOWN,
            self.queue.status if self.queue else HealthStatus.UNKNOWN,
            *[s.status for s in self.services.values()]
        ]
        
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN 