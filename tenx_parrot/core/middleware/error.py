"""Error handling middleware."""
import traceback
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR
)

from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.types.metrics import MetricType

from .base import MiddlewareComponent

class ErrorResponse(JSONResponse):
    """Standardized error response."""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        code: str,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        content = {
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers
        )


class ErrorHandlingMiddleware(MiddlewareComponent):
    """Middleware for centralized error handling."""
    
    def __init__(
        self,
        app: ASGIApp,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        include_traceback: bool = False,
        **kwargs
    ):
        super().__init__(
            app=app,
            name="error_middleware",
            metrics=metrics,
            logger=logger,
            order=-1,  # Run first to catch all errors
            **kwargs
        )
        self.include_traceback = include_traceback
        
        # Error handlers by exception type
        self._handlers = {
            ValueError: self._handle_validation_error,
            KeyError: self._handle_key_error,
            PermissionError: self._handle_permission_error,
            NotImplementedError: self._handle_not_implemented_error,
            TimeoutError: self._handle_timeout_error
        }
    
    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request with error handling."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        try:
            await self.app(scope, receive, send)
            
        except Exception as e:
            # Get context from previous middleware
            context = scope.get("state", {}).get("context", {})
            request_id = context.get("request_id", "unknown")
            
            # Handle error
            error_response = await self._handle_error(e, request_id)
            
            # Update metrics
            self._update_error_metrics(e, error_response.status_code)
            
            # Send error response
            await error_response(scope, receive, send)
    
    async def _handle_error(self, error: Exception, request_id: str) -> ErrorResponse:
        """Handle error and create appropriate response."""
        # Get error handler
        handler = self._handlers.get(type(error), self._handle_unknown_error)
        
        try:
            # Handle error
            response = await handler(error)
            
            # Log error
            self._log_error(error, response.status_code, request_id)
            
            return response
            
        except Exception as e:
            # Fallback to unknown error handler
            self._logger.error(f"Error in error handler: {e}")
            return await self._handle_unknown_error(error)
    
    def _log_error(self, error: Exception, status_code: int, request_id: str) -> None:
        """Log error with context."""
        error_type = type(error).__name__
        error_msg = str(error)
        
        extra = {
            "error_type": error_type,
            "status_code": status_code,
            "request_id": request_id
        }
        
        if self.include_traceback:
            extra["traceback"] = traceback.format_exc()
        
        self._logger.error(
            f"Request error: {error_msg}",
            extra=extra
        )
    
    def _update_error_metrics(self, error: Exception, status_code: int) -> None:
        """Update error metrics."""
        error_type = type(error).__name__
        self.metrics.record(
            f"{self.name}_errors_total",
            1,
            labels={
                "error_type": error_type,
                "status_code": str(status_code)
            }
        )
    
    async def _handle_validation_error(self, error: ValueError) -> ErrorResponse:
        """Handle validation error."""
        return ErrorResponse(
            status_code=HTTP_400_BAD_REQUEST,
            message=str(error),
            code="VALIDATION_ERROR"
        )
    
    async def _handle_key_error(self, error: KeyError) -> ErrorResponse:
        """Handle key error."""
        return ErrorResponse(
            status_code=HTTP_400_BAD_REQUEST,
            message=f"Missing required field: {str(error)}",
            code="MISSING_FIELD"
        )
    
    async def _handle_permission_error(self, error: PermissionError) -> ErrorResponse:
        """Handle permission error."""
        return ErrorResponse(
            status_code=HTTP_403_FORBIDDEN,
            message=str(error),
            code="PERMISSION_DENIED"
        )
    
    async def _handle_not_implemented_error(self, error: NotImplementedError) -> ErrorResponse:
        """Handle not implemented error."""
        return ErrorResponse(
            status_code=HTTP_501_NOT_IMPLEMENTED,
            message=str(error),
            code="NOT_IMPLEMENTED"
        )
    
    async def _handle_timeout_error(self, error: TimeoutError) -> ErrorResponse:
        """Handle timeout error."""
        return ErrorResponse(
            status_code=HTTP_408_REQUEST_TIMEOUT,
            message="Request timed out",
            code="TIMEOUT"
        )
    
    async def _handle_unknown_error(self, error: Exception) -> ErrorResponse:
        """Handle unknown error."""
        return ErrorResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            code="INTERNAL_ERROR",
            details={"error": str(error)} if self.include_traceback else None
        )
    
    def add_error_handler(self, error_type: type, handler: callable) -> None:
        """Add custom error handler."""
        self._handlers[error_type] = handler
    
    def remove_error_handler(self, error_type: type) -> None:
        """Remove error handler."""
        self._handlers.pop(error_type, None)
    
    def get_error_handlers(self) -> Dict[type, callable]:
        """Get all error handlers."""
        return self._handlers.copy()
    
    def update_include_traceback(self, include: bool) -> None:
        """Update traceback inclusion setting."""
        self.include_traceback = include 
    
    def _register_metrics(self) -> None:
        """Register middleware metrics."""
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "endpoint": ""}
        ) 