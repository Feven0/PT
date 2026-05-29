"""Error handling utilities."""
from typing import Dict, Any, Optional, Type, TYPE_CHECKING, Union
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import functools
import asyncio
from datetime import datetime

from core.alert.manager import AlertManager
from core.config import AppConfig
from core.logging import BackendLogger
from .exceptions import ServiceError, ValidationError, NotFoundError

if TYPE_CHECKING:
    from core.telemetry.metrics import MetricsManager
    MetricsManagerType = MetricsManager
else:
    MetricsManagerType = 'MetricsManager'



def setup_error_handlers(
    app: Any,
    alert_manager: AlertManager,
    metrics: MetricsManagerType
) -> None:
    """Set up FastAPI error handlers.
    
    Args:
        app: FastAPI application
        alert_manager: Alert manager
        metrics: Metrics collector
    """
    @app.exception_handler(ServiceError)
    async def service_error_handler(
        request: Request,
        error: ServiceError
    ) -> JSONResponse:
        """Handle service errors."""
        # Track error metrics
        metrics.counter(
            "service_errors_total",
            labels={
                "code": error.code,
                "status": error.status_code
            }
        )
        
        # Create alert for 5xx errors
        if error.status_code >= 500:
            await alert_manager.create_alert(
                "error",
                f"Service error: {error.message}",
                context={
                    "error": error.to_dict(),
                    "request": {
                        "method": request.method,
                        "url": str(request.url),
                        "headers": dict(request.headers)
                    }
                }
            )
            
        return JSONResponse(
            status_code=error.status_code,
            content=error.to_dict()
        )
        
    @app.exception_handler(HTTPException)
    async def http_error_handler(
        request: Request,
        error: HTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        service_error = ServiceError(
            message=str(error.detail),
            code="HTTP_ERROR",
            status_code=error.status_code
        )
        return await service_error_handler(request, service_error)
        
    @app.exception_handler(Exception)
    async def generic_error_handler(
        request: Request,
        error: Exception
    ) -> JSONResponse:
        """Handle unexpected errors."""
        service_error = ServiceError(
            message="An unexpected error occurred",
            code="INTERNAL_ERROR",
            status_code=500,
            details={"error": str(error)}
        )
        return await service_error_handler(request, service_error)


def handle_errors(
    error_type: Type[ServiceError],
    message: Optional[str] = None
):
    """Decorator for error handling.
    
    Args:
        error_type: Type of error to handle
        message: Optional error message
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise error_type(
                    message=message or str(e),
                    details={"original_error": str(e)}
                )
        return wrapper
    return decorator 


class ErrorHandler:
    """Error handler for FastAPI applications."""
    
    def __init__(
        self,
        config: Any,
        metrics: Optional[MetricsManagerType] = None,
        alert_manager: Optional[AlertManager] = None,
        logger: Optional[BackendLogger] = None
    ):
        """Initialize error handler.
        
        Args:
            config: Error handler configuration
            logger: Logger instance
            metrics: Optional metrics collector
        """
        # Ensure config is deserialized
        if isinstance(config, dict):            
            config = AppConfig(**config)
            
        self.config = config
        self.logger = logger
        self.metrics = metrics
        self.alert_manager = alert_manager

        if not logger:
            logger = BackendLogger(__name__)
            
        logger.name = "error_handler"
        logger.level = "ERROR"
        logger.use_colors = True
        self.logger = logger.get_logger()
        
    async def handle_application_error(
        self,
        request: Request,
        error: ServiceError
    ) -> JSONResponse:
        """Handle application errors."""
        # Log error
        self.logger.error(
            "Application error",
            error_code=error.code,
            error_message=str(error),
            request_path=str(request.url.path),
            request_method=request.method
        )
        
        # Track metrics
        self.metrics.counter(
            "application_errors_total",
            labels={
                "code": error.code,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=error.status_code,
            content=error.to_dict()
        )
        
    async def handle_validation_error(
        self,
        request: Request,
        error: ValidationError
    ) -> JSONResponse:
        """Handle validation errors."""
        service_error = ValidationError(
            message=str(error),
            details={"errors": error.errors()}
        )
        return await self.handle_application_error(request, service_error)
        
    async def handle_app_validation_error(
        self,
        request: Request,
        error: ValidationError
    ) -> JSONResponse:
        """Handle application validation errors."""
        return await self.handle_application_error(request, error)
        
    async def handle_not_found_error(
        self,
        request: Request,
        error: NotFoundError
    ) -> JSONResponse:
        """Handle not found errors."""
        return await self.handle_application_error(request, error)
        
    async def handle_authentication_error(
        self,
        request: Request,
        error: ServiceError
    ) -> JSONResponse:
        """Handle authentication errors."""
        service_error = ServiceError(
            message=str(error),
            code="AUTHENTICATION_ERROR",
            status_code=401
        )
        return await self.handle_application_error(request, service_error)
        
    async def handle_authorization_error(
        self,
        request: Request,
        error: ServiceError
    ) -> JSONResponse:
        """Handle authorization errors."""
        service_error = ServiceError(
            message=str(error),
            code="AUTHORIZATION_ERROR",
            status_code=403
        )
        return await self.handle_application_error(request, service_error)
        
    async def handle_service_error(
        self,
        request: Request,
        error: ServiceError
    ) -> JSONResponse:
        """Handle service errors."""
        return await self.handle_application_error(request, error)
        
    async def handle_internal_error(
        self,
        request: Request,
        error: Exception
    ) -> JSONResponse:
        """Handle internal errors."""
        service_error = ServiceError(
            message="An unexpected error occurred",
            code="INTERNAL_ERROR",
            status_code=500,
            details={"error": str(error)}
        )
        return await self.handle_application_error(request, service_error) 