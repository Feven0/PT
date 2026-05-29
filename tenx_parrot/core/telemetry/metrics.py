"""Metrics management."""
from typing import (
    Dict, Any, Optional, 
    Set, TypeVar, Union, List
)
from datetime import datetime, timezone
import asyncio
import logging
from dataclasses import dataclass, field
from contextlib import contextmanager

from prometheus_client import (
    Counter, 
    Gauge, 
    Histogram, 
    CollectorRegistry
)

from core.types.components import (
    HealthStatus,
    HealthStatusInfo,
    ComponentState
)
from core.types.metrics import (
    MetricType, 
    MetricsProtocol,
    MetricValue,
    MetricLabels,
    MetricTags,
    Metric
)
from core.config import MetricsConfig

from core.base.lifecycle import LifecycleAware
from core.errors.exceptions import ServiceError


logger = logging.getLogger(__name__)

# Type variables for better type hints
T = TypeVar('T', bound='MetricsManager')


class MetricsManager(LifecycleAware):
    """Metrics manager implementation."""
    
    def __init__(
        self,
        name: str,
        config: Optional[Union[MetricsConfig, Dict[str, Any]]] = None,
        registry: Optional[CollectorRegistry] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Initialize metrics manager.
        
        Args:
            name: Metrics manager name
            config: Optional metrics configuration
            registry: Optional Prometheus registry
            dependencies: Optional dependencies
        """
        super().__init__()
        
        self.name = name
        # Convert dict config to MetricsConfig if needed
        if isinstance(config, dict):
            self.config = MetricsConfig(**config)
        else:
            self.config = config or MetricsConfig()
            
        self._dependencies = dependencies or set()
        self._registry = registry or CollectorRegistry()
        self._metrics: Dict[str, Any] = {}
        self._components: Dict[str, Set[str]] = {}
        self._initialization_lock = asyncio.Lock()
        self._collection_lock = asyncio.Lock()
        self._default_labels: Dict[str, str] = {}
        self._state = ComponentState.CREATED
        self._is_initialized = False
        
        # Add health status initialization
        self._health_status = HealthStatusInfo(
            status=HealthStatus.UNKNOWN,
            details={
                "status": "initializing",
                "component": name,
                "initialized": False,
                "state": self._state.value,
                "dependencies": list(self._dependencies),
                "config": {
                    "enabled": self.config.enabled,
                    "namespace": self.config.namespace,
                    "subsystem": self.config.subsystem
                }
            }
        )

    def register_metric(
        self,
        name: str,
        mtype: Union[MetricType, str]=MetricType.COUNTER,
        description: str="",
        default_value: Optional[MetricValue] = None,
        labels: Optional[MetricLabels] = None,
        component: Optional[str] = None,
        unit: Optional[str] = None,
        **kwargs
    ) -> None:
        """Register new metric."""

        if name in self._metrics:
            return
        
        if isinstance(mtype, str):
            mtype = MetricType(mtype)

        # if not mtype and kwargs.get('type'):
        #     mtype = kwargs.get('type')

        metric = Metric(
            name=name,
            mtype=mtype,
            description=description,
            default_value=default_value,
            labels=labels or {},
            component=component,
            unit=unit
        )

        if mtype == MetricType.HISTOGRAM:
            self._metrics[name] = Histogram(
                name,
                description,
                labelnames=list(metric.labels.keys()),
                registry=self._registry,
                buckets=self.config.buckets  # Use configured buckets
            )
        elif mtype == MetricType.COUNTER:
            self._metrics[name] = Counter(
                name,
                description,
                labelnames=list(metric.labels.keys()),
                registry=self._registry
            )
        elif mtype == MetricType.GAUGE:
            self._metrics[name] = Gauge(
                name,
                description,
                labelnames=list(metric.labels.keys()),
                registry=self._registry
            )
        else:            
            raise ValueError(f"Invalid metric type: {mtype}")

        if component:
            if component not in self._components:
                self._components[component] = set()
            self._components[component].add(name)

    @contextmanager
    def timer(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        """Context manager for timing operations.
        
        Args:
            name: Name of the operation to time
            labels: Optional labels to attach to the metric
            
        Example:
            with metrics.timer("operation_name", {"label": "value"}):
                # Do something to measure
                pass
        """
        start_time = self.time()
        try:
            yield
        finally:
            duration = self.time() - start_time
            # Record duration in histogram
            self.record(
                f"{name}_duration_seconds",
                duration,
                labels=labels
            )

    def time(self) -> float:
        """Get current time."""
        return datetime.now(timezone.utc).timestamp()

    def record(
        self,
        name: str,
        value: MetricValue,
        labels: Optional[MetricLabels] = None
    ) -> None:
        """Record metric value."""
        if name not in self._metrics:
            logger.warning(f"Metric not registered: {name}")
            return

        metric = self._metrics[name]
        try:
            # Merge default labels with provided labels
            merged_labels = {**self._default_labels, **(labels or {})}
            
            if isinstance(metric, Counter):
                if merged_labels:
                    metric.labels(**merged_labels).inc(value)
                else:
                    metric.inc(value)
            elif isinstance(metric, Gauge):
                if merged_labels:
                    metric.labels(**merged_labels).set(value)
                else:
                    metric.set(value)
            elif isinstance(metric, Histogram):
                if merged_labels:
                    metric.labels(**merged_labels).observe(value)
                else:
                    metric.observe(value)
        except Exception as e:
            logger.error(f"Failed to record metric {name}: {str(e)}")
            self.record(
                f"{self.name}_errors_total",
                1,
                {"error_type": type(e).__name__}
            )

    def get_metric(self, name: str) -> Optional[Any]:
        """Get metric by name."""
        return self._metrics.get(name)

    def get_component_metrics(self, component: str) -> Set[str]:
        """Get metrics for component."""
        return self._components.get(component, set())

    def with_labels(self, labels: Dict[str, str]) -> T:
        """Create a new metrics instance with default labels."""
        new_manager = MetricsManager(
            name=self.name,
            config=self.config,
            registry=self._registry,
        )
        new_manager._metrics = self._metrics
        new_manager._components = self._components
        new_manager._default_labels = {**self._default_labels, **labels}
        return new_manager

    async def export(self) -> Dict[str, Any]:
        """Export all metrics data."""
        try:
            async with self._collection_lock:
                result: Dict[str, Any] = {}
                for name, metric in self._metrics.items():
                    if isinstance(metric, (Counter, Gauge)):
                        result[name] = metric._value.get()
                    elif isinstance(metric, Histogram):
                        result[name] = {
                            'sum': metric._sum.get(),
                            'count': metric._count.get(),
                            'buckets': metric._buckets
                        }
                return result
        except Exception as e:
            logger.error(f"Failed to export metrics: {str(e)}")
            raise ServiceError(
                message=f"Metrics export failed: {str(e)}",
                code="METRICS_EXPORT_ERROR"
            )

      
    @property
    def dependencies(self) -> Set[str]:
        """Get component dependencies."""
        return self._dependencies.copy()

    def add_dependency(self, component_name: str) -> None:
        """Add dependency.
        
        Args:
            component_name: Name of component to depend on
        """
        self._dependencies.add(component_name)
        
    def remove_dependency(self, component_name: str) -> None:
        """Remove dependency.
        
        Args:
            component_name: Name of component to remove dependency on
        """
        self._dependencies.discard(component_name)

    def _register_request_metrics(self) -> None:
        """Register standard metrics."""
 
        self.register_metric(
            name=f"{self.name}_errors_total",
            mtype=MetricType.COUNTER,
            description=f"Total number of errors in {self.name}",
            labels={"error_type": "", "status_code": ""}
        )
        

    async def initialize(self) -> None:
        """Initialize component."""
        async with self._initialization_lock:
            if self._is_initialized:
                return
                
            try:
                self.state = ComponentState.INITIALIZING


                # Initialize implementation
                await self._initialize_impl()
                
                self._is_initialized = True
                self.state = ComponentState.INITIALIZED
                logger.info(f"{self.name} component initialized")
                
            except Exception as e:
                self.state = ComponentState.FAILED
                logger.error(f"{self.name} component initialization failed: {str(e)}")
                raise

    async def start(self) -> None:
        """Start component."""
        if not self._is_initialized:
            await self.initialize()
            
        try:
            self.state = ComponentState.STARTING
            # Start implementation
            await self._start_impl()
            
            self.state = ComponentState.RUNNING
            logger.info(f"{self.name} component started")
            
        except Exception as e:
            self.state = ComponentState.FAILED
            logger.error(f"{self.name} component start failed: {str(e)}")
            raise
            
    async def stop(self) -> None:
        """Stop component."""
        try:
            # Stop implementation
            self.state = ComponentState.STOPPING
            await self._stop_impl()
            
            self.state = ComponentState.STOPPED
            logger.info(f"{self.name} component stopped")
            
        except Exception as e:
            self.state = ComponentState.FAILED
            logger.error(f"{self.name} component stop failed: {str(e)}")
            raise

    @property
    def health_status(self) -> HealthStatusInfo:
        """Get component health status."""
        return self._health_status

    async def check_health(self) -> HealthStatusInfo:
        """Check component health."""
        try:
            # Check implementation health
            await self._check_health_impl()
            
            # Update health status
            self._health_status.update(
                status=HealthStatus.HEALTHY,
                details={
                    "component": self.name,
                    "state": self._state.value,
                    "is_initialized": self._is_initialized,
                    "dependencies": list(self._dependencies),
                    "metrics_count": len(self._metrics),
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            )
            
            return self._health_status
            
        except Exception as e:
            logger.error(f"{self.name} component health check failed: {str(e)}")
            self._health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    "component": self.name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            )
            return self._health_status

    async def _initialize_impl(self) -> None:
        """Initialize implementation."""
        pass
        
    async def _start_impl(self) -> None:
        """Start implementation."""
        pass
        
    async def _stop_impl(self) -> None:
        """Stop implementation."""
        pass
        
    async def _check_health_impl(self) -> None:
        """Check implementation health."""
        # Verify registry is available
        if not self._registry:
            raise RuntimeError("Metrics registry is not available")
            
        # Verify we can create a metric
        test_metric_name = "_health_check_test"
        if test_metric_name not in self._metrics:
            self.register_metric(
                name=test_metric_name,
                mtype=MetricType.COUNTER,
                description="Health check test metric"
            ) 