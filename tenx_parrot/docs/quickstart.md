# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv or conda (recommended)
- Git

## Setup Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/tenx-ipersona.git
   cd tenx-ipersona
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run Development Server**
   ```bash
   uvicorn tenx_ipersona.backend.app:app --reload
   ```

## First Steps

### 1. Explore the API
- Open http://localhost:8000/docs in your browser
- Review available endpoints
- Try out sample requests

### 2. Check Health Status
- Visit http://localhost:8000/health
- Review component health
- Check metrics

### 3. Run Tests
```bash
pytest
```

## Development Workflow

### 1. Creating a New Component

1. Create component file:
   ```python
   # tenx_ipersona/backend/services/my_service.py
   from core.di import component
   
   @component(
       name="my_service",
       dependencies=["database"]  # List required dependencies
   )
   class MyService:
       def __init__(self, database):
           self.database = database
           
       async def initialize(self):
           # Setup code
           pass
           
       async def check_health(self):
           return {
               "status": "healthy",
               "details": {"initialized": True}
           }
   ```

2. Register in container:
   ```python
   # tenx_ipersona/backend/core/di/container.py
   from services.my_service import MyService
   
   class Container:
       my_service = providers.Component(MyService)
   ```

### 2. Creating an API Endpoint

1. Create route file:
   ```python
   # tenx_ipersona/backend/api/v1/my_endpoint.py
   from fastapi import APIRouter, Depends
   from core.di import inject
   
   router = APIRouter()
   
   @router.get("/my-endpoint")
   async def get_data(
       service = Depends(inject("my_service"))
   ):
       return await service.get_data()
   ```

2. Include router:
   ```python
   # tenx_ipersona/backend/api/v1/__init__.py
   from .my_endpoint import router as my_router
   
   router.include_router(my_router, prefix="/my-endpoint")
   ```

### 3. Adding Middleware

1. Create middleware:
   ```python
   # tenx_ipersona/backend/core/middleware/my_middleware.py
   from core.middleware import MiddlewareComponent
   
   class MyMiddleware(MiddlewareComponent):
       async def process_request(self, request):
           # Handle request
           pass
   ```

2. Add to application:
   ```python
   # tenx_ipersona/backend/app.py
   from core.middleware import MyMiddleware
   
   app.add_middleware(MyMiddleware)
   ```

## Common Tasks

### Database Operations

```python
@component(name="user_repository")
class UserRepository:
    def __init__(self, database):
        self.db = database
        
    async def get_user(self, user_id: str):
        return await self.db.fetch_one(
            "SELECT * FROM users WHERE id = :id",
            {"id": user_id}
        )
```

### Authentication

```python
@component(name="auth_service")
class AuthService:
    async def authenticate(self, token: str):
        # Validate token
        user = await self.validate_token(token)
        return user
```

### Error Handling

```python
from core.errors import ServiceError

class UserNotFoundError(ServiceError):
    def __init__(self, user_id: str):
        super().__init__(
            message=f"User {user_id} not found",
            code="USER_NOT_FOUND",
            status_code=404
        )
```

## Debugging

### 1. Enable Debug Logging
```python
# .env
LOG_LEVEL=debug
```

### 2. Check Component Health
```bash
curl http://localhost:8000/health
```

### 3. View Metrics
```bash
curl http://localhost:8000/metrics
```

## Best Practices

1. **Component Design**
   - Single responsibility
   - Clear dependencies
   - Health checks
   - Proper cleanup

2. **Error Handling**
   - Use custom exceptions
   - Include context
   - Proper logging

3. **Testing**
   - Unit tests for components
   - Integration tests for APIs
   - Mock dependencies

4. **Documentation**
   - Document component purpose
   - List dependencies
   - Include examples

## Troubleshooting

### Common Issues

1. **Component Not Found**
   - Check registration in container
   - Verify dependency injection
   - Check import paths

2. **Health Check Failures**
   - Check component logs
   - Verify dependencies
   - Check configuration

3. **Performance Issues**
   - Enable debug logging
   - Check metrics
   - Monitor resource usage

## Next Steps

1. Review [Architecture Overview](architecture/overview.md)
2. Explore [Component System](architecture/components.md)
3. Study [Middleware Stack](architecture/middleware_and_container.md)
4. Check [API Documentation](api/README.md) 