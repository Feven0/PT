# Core Base Classes

## Overview

The core base classes provide foundational functionality for the application. They implement common patterns and interfaces that ensure consistency and maintainability across the codebase.

## Base Classes

### BaseManager

The `BaseManager` class provides lifecycle management for application components:

```python
class BaseManager(LifecycleAware):
    def __init__(self, name: str, config: AppConfig):
        self.name = name
        self.config = config
        self.logger = BackendLogger(name)
        self.metrics = MetricsCollector(name)
        
    async def initialize(self) -> None:
        """Initialize the manager."""
        await self._do_initialize()
        
    async def start(self) -> None:
        """Start the manager."""
        await self._do_start()
        
    async def stop(self) -> None:
        """Stop the manager."""
        await self._do_stop()
```

### UnifiedMiddleware

The `UnifiedMiddleware` class provides centralized request processing:

```python
class UnifiedMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = BackendLogger("middleware")
        self.metrics = MetricsCollector("middleware")
        
    async def __call__(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request through middleware stack."""
        try:
            # Create request context
            request.state.context = await self._create_context(request)
            
            # Validate request
            await self._validate_request(request)
            
            # Check rate limits
            await self._check_rate_limits(request)
            
            # Authenticate request
            await self._authenticate_request(request)
            
            # Process request
            response = await call_next(request)
            
            # Process response
            return await self._process_response(response)
            
        except Exception as e:
            return await self._handle_error(e)
            
        finally:
            await self._cleanup_resources(request)
```

### RequestContext

The `RequestContext` class manages request-specific data:

```python
class RequestContext:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.start_time = time.time()
        self.metadata = {}
        self.resources = []
        
    def add_metadata(self, key: str, value: Any) -> None:
        """Add request metadata."""
        self.metadata[key] = value
        
    def track_resource(self, resource: Any) -> None:
        """Track resource for cleanup."""
        self.resources.append(resource)
        
    async def cleanup(self) -> None:
        """Clean up tracked resources."""
        for resource in self.resources:
            await resource.close()
```

### ErrorHandler

The `ErrorHandler` class provides standardized error handling:

```python
class ErrorHandler:
    def __init__(self):
        self.logger = BackendLogger("errors")
        self.metrics = MetricsCollector("errors")
        
    async def handle_error(self, error: Exception) -> Response:
        """Handle error and return appropriate response."""
        error_type = type(error).__name__
        error_code = getattr(error, "code", "INTERNAL_ERROR")
        status_code = getattr(error, "status_code", 500)
        
        # Log error
        self.logger.error(
            "request_error",
            error_type=error_type,
            error_code=error_code,
            error_message=str(error)
        )
        
        # Update metrics
        self.metrics.counter(
            "errors_total",
            labels={"type": error_type}
        )
        
        # Return error response
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": str(error)
                }
            }
        )
```

### MetricsCollector

The `MetricsCollector` class manages application metrics:

```python
class MetricsCollector:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.metrics = {}
        
    def counter(self, name: str, labels: Dict[str, str] = None) -> None:
        """Increment counter metric."""
        metric_name = f"{self.namespace}_{name}"
        if metric_name not in self.metrics:
            self.metrics[metric_name] = 0
        self.metrics[metric_name] += 1
        
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set gauge metric value."""
        metric_name = f"{self.namespace}_{name}"
        self.metrics[metric_name] = value
        
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Record histogram metric value."""
        metric_name = f"{self.namespace}_{name}"
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)
```

## Usage Examples

### Component Lifecycle

```python
class CacheManager(BaseManager):
    async def _do_initialize(self) -> None:
        """Initialize Redis connection."""
        self.redis = await create_redis_pool(self.config.redis_url)
        
    async def _do_start(self) -> None:
        """Start monitoring task."""
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        
    async def _do_stop(self) -> None:
        """Stop monitoring and close connection."""
        self.monitor_task.cancel()
        self.redis.close()
        await self.redis.wait_closed()
```

### Request Processing

```python
@app.middleware("http")
async def process_request(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Process request through middleware stack."""
    middleware = UnifiedMiddleware(app)
    return await middleware(request, call_next)
```

### Error Handling

```python
@app.exception_handler(Exception)
async def global_error_handler(request: Request, error: Exception) -> Response:
    """Handle all unhandled exceptions."""
    handler = ErrorHandler()
    return await handler.handle_error(error)
```

### Metrics Collection

```python
@app.middleware("http")
async def track_metrics(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Track request metrics."""
    metrics = MetricsCollector("http")
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    metrics.histogram(
        "request_duration_seconds",
        duration,
        labels={"path": request.url.path}
    )
    
    return response
```