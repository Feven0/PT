# Middleware and Container Architecture

## Overview

The application uses a robust middleware architecture and dependency injection container to manage components, handle requests, and ensure proper lifecycle management. This document explains the key concepts and components.

## Middleware Stack

### 1. Error Handling Middleware
**Purpose**: Provides centralized error handling for the entire application.
**Advantages**:
- Consistent error responses across all endpoints
- Automatic error logging and metrics
- Customizable error handlers for different types of errors
- Debug mode support with optional stack traces

Example error response:
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field": "email",
            "reason": "Invalid email format"
        },
        "timestamp": "2024-01-20T12:34:56Z"
    }
}
```

### 2. Context Middleware
**Purpose**: Manages request context and tracking information.
**Advantages**:
- Unique request ID for each request
- Correlation ID tracking across services
- Request timing and duration tracking
- Request metadata storage

Example context data:
```python
{
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "correlation_id": "abc-123-def-456",
    "start_time": "2024-01-20T12:34:56Z",
    "user_id": "user_123"
}
```

### 3. Request Processing Middleware
**Purpose**: Handles request lifecycle and concurrency.
**Advantages**:
- Request timeout management
- Concurrent request limiting
- Request queue management
- Request metrics collection

Configuration example:
```python
{
    "max_concurrent_requests": 100,
    "request_timeout": 30,  # seconds
    "queue_size": 50
}
```

### 4. Unified Middleware
**Purpose**: Combines common HTTP processing features.
**Advantages**:
- Security headers management
- Response compression
- Response caching
- Cross-cutting concerns handling

### 5. Health Check Middleware
**Purpose**: Monitors application and component health.
**Advantages**:
- Real-time health status
- Component-level health checks
- Uptime tracking
- Health metrics collection

Example health check response:
```json
{
    "status": "healthy",
    "details": {
        "components": {
            "database": {
                "status": "healthy",
                "latency": "20ms"
            },
            "cache": {
                "status": "healthy",
                "used_memory": "128MB"
            }
        },
        "uptime": "5d 12h 34m 56s"
    }
}
```

## Container Structure

The application uses a dependency injection container to manage components and their lifecycles.

### Component Registry
Components are registered with the container and given unique names:
```python
@component(name="database")
class DatabaseComponent:
    async def initialize(self):
        # Setup database connection
        pass
```

### Lifecycle Management
Components go through the following lifecycle stages:
1. **Registration**: Component is registered with the container
2. **Initialization**: `initialize()` method called during startup
3. **Start**: `start()` method called after initialization
4. **Running**: Component is active and processing requests
5. **Stop**: `stop()` method called during shutdown
6. **Cleanup**: Resources are released

### Dependency Resolution
The container automatically resolves and injects dependencies:
```python
@component(name="user_service")
class UserService:
    def __init__(self, database: DatabaseComponent):
        self.database = database
```

### Component States
Components can be in the following states:
- **Uninitialized**: Not yet initialized
- **Initializing**: During initialization
- **Running**: Active and healthy
- **Failed**: Initialization or runtime failure
- **Stopping**: During shutdown
- **Stopped**: Shutdown complete

## Best Practices

1. **Component Registration**:
   - Give components meaningful, unique names
   - Document component dependencies
   - Include health check methods

2. **Error Handling**:
   - Use appropriate error types
   - Include relevant error details
   - Log errors with context

3. **Health Checks**:
   - Implement health checks for critical components
   - Include performance metrics
   - Set appropriate check intervals

4. **Middleware Order**:
   - Error handling first
   - Context/tracking next
   - Business logic middleware last

5. **Configuration**:
   - Use environment variables for settings
   - Include reasonable defaults
   - Document all configuration options

## Example Usage

### Creating a New Component
```python
from core.di import component

@component(
    name="email_service",
    dependencies=["database", "cache"],
    metrics=[
        {
            "name": "emails_sent_total",
            "type": "counter",
            "description": "Total emails sent"
        }
    ]
)
class EmailService:
    def __init__(self, database, cache):
        self.database = database
        self.cache = cache
    
    async def initialize(self):
        # Setup email client
        pass
    
    async def check_health(self):
        return {
            "status": "healthy",
            "queue_size": 0
        }
```

### Using Components in Routes
```python
from fastapi import Depends
from core.di import inject

@router.post("/send-email")
async def send_email(
    data: EmailData,
    email_service: EmailService = Depends(inject("email_service"))
):
    await email_service.send(data)
    return {"status": "sent"}
```

## Troubleshooting

Common issues and solutions:

1. **Component Initialization Failures**:
   - Check component dependencies
   - Verify configuration values
   - Check component logs

2. **Health Check Failures**:
   - Check component status
   - Verify resource availability
   - Check connection settings

3. **Performance Issues**:
   - Monitor concurrent requests
   - Check component metrics
   - Review resource usage 