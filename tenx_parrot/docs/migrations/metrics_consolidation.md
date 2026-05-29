# Metrics System Consolidation

This document describes the changes made to consolidate the metrics system implementations and provides guidance for migration.

## Overview

We've consolidated multiple metrics implementations into a single enhanced `MetricsManager` class in `core/telemetry/metrics.py`. This change:
- Removes redundant implementations
- Adds new features for component-level metrics
- Improves type safety and error handling
- Maintains backward compatibility

## Breaking Changes

None! We've maintained backward compatibility through:
1. The `MetricsCollector = MetricsManager` alias
2. Preserving all existing method signatures
3. Keeping the same configuration interface

## New Features

The enhanced `MetricsManager` adds several new features:

1. Component-level metric registration:
```python
metrics_manager.register_metrics(
    component_name="my_component",
    metrics=[{
        "name": "operation_count",
        "type": "counter",
        "description": "Number of operations",
        "labels": {"status": "success"}
    }]
)
```

2. Better metadata tracking:
```python
# Get metadata for a metric
metric = metrics_manager.get_metric("my_metric")
print(f"Type: {metric.type}, Labels: {metric.labels}")

# Get all metrics for a component
component_metrics = metrics_manager.get_component_metrics("my_component")
```

3. Type-safe metric operations:
```python
# Increment counter with validation
metrics_manager.increment_counter("request_count", 1, labels={"status": "success"})

# Observe histogram with validation
metrics_manager.observe_histogram("response_time", 0.5, labels={"endpoint": "/api"})
```

4. Initialization tracking:
```python
# Check if metrics are initialized
if metrics_manager.is_initialized:
    print(f"Initialized at: {metrics_manager.initialization_time}")
```

## Migration Guide

### For Existing Code

No changes required! The alias ensures all existing code continues to work.

### For New Code

1. Use the new component-level registration:
```python
@component(
    name="my_service",
    metrics=[
        {
            "name": "requests_total",
            "type": "counter",
            "description": "Total requests handled"
        }
    ]
)
class MyService:
    def __init__(self, metrics: MetricsManager):
        self._metrics = metrics
```

2. Take advantage of type-safe operations:
```python
# Instead of direct counter/gauge calls
self._metrics.increment_counter("requests_total", labels={"status": "success"})

# Instead of raw histogram observations
self._metrics.observe_histogram("response_time", duration, labels={"endpoint": path})
```

3. Use component association for better organization:
```python
self._metrics.register_metric(
    name="cache_hits",
    type="counter",
    description="Cache hit count",
    component=self.__class__.__name__
)
```

## Best Practices

1. Always use component-level registration for better organization
2. Leverage type-safe operations to catch errors early
3. Use labels consistently within components
4. Document metrics in component docstrings
5. Use meaningful metric names and descriptions

## Technical Details

The enhanced `MetricsManager` provides:

1. Thread-safe metric operations
2. Prometheus integration
3. Component-level metric tracking
4. Metadata storage
5. Type validation
6. Label validation
7. Error handling with detailed messages

## Questions and Support

If you encounter any issues or have questions about the migration, please:
1. Check the metrics documentation in `docs/components/telemetry.md`
2. Review the example code in `examples/metrics/`
3. Open an issue with the tag `metrics-migration` 