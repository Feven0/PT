"""Error handling middleware."""
from typing import Dict, Any, Callable, Awaitable
from datetime import datetime, timezone
import traceback
import json

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.errors.exceptions import (
    BackendError,
    ServiceError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    StateError,
    WebSocketError,
    SessionError,
    DatabaseError,
    ExternalServiceError,
    RateLimitError,
    ConfigurationError
)
from core.logging import BackendLogger
from core.metrics import MetricsManager

logger = BackendLogger(__name__).get_logger()

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling."""

    def __init__(
        self,
        app: Any,
        metrics: Optional[MetricsManager] = None
    ):
        """Initialize middleware.
        
        Args:
            app: FastAPI application
            metrics: Optional metrics manager
        """
        super().__init__(app)
        self.metrics = metrics
        
        # Register error metrics if metrics manager available
        if self.metrics:
            self.metrics.register_counter(
                "error_total",
                "Total number of errors",
                ["error_type", "error_code", "http_status"]
            )

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and handle errors.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in chain
            
        Returns:
            Response with error details if error occurred
        """
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            return await self._handle_error(e, request)

    async def _handle_error(
        self,
        error: Exception,
        request: Request
    ) -> Response:
        """Handle different types of errors.
        
        Args:
            error: Exception that occurred
            request: FastAPI request
            
        Returns:
            JSON response with error details
        """
        # Get error details
        error_details = self._get_error_details(error)
        
        # Log error
        self._log_error(error, error_details, request)
        
        # Track error metrics
        self._track_error_metrics(error_details)
        
        # Return error response
        return JSONResponse(
            status_code=error_details["http_status"],
            content=error_details
        )

    def _get_error_details(self, error: Exception) -> Dict[str, Any]:
        """Get standardized error details.
        
        Args:
            error: Exception to process
            
        Returns:
            Standardized error details
        """
        if isinstance(error, BackendError):
            # Use built-in error details
            details = error.to_dict()
            details["http_status"] = error.http_status
            return details
            
        # Handle unknown errors
        return {
            "code": "internal_error",
            "message": str(error),
            "details": {
                "error_type": error.__class__.__name__,
                "traceback": traceback.format_exc()
            },
            "http_status": 500,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _log_error(
        self,
        error: Exception,
        error_details: Dict[str, Any],
        request: Request
    ) -> None:
        """Log error with context.
        
        Args:
            error: Original exception
            error_details: Processed error details
            request: FastAPI request
        """
        # Get request context
        context = {
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "error_code": error_details["code"],
            "http_status": error_details["http_status"]
        }
        
        # Add headers (excluding sensitive data)
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = "[REDACTED]"
        context["headers"] = headers
        
        # Log with appropriate level
        if error_details["http_status"] >= 500:
            logger.error(
                error_details["message"],
                exc_info=error,
                extra={"context": context}
            )
        else:
            logger.warning(
                error_details["message"],
                extra={"context": context}
            )

    def _track_error_metrics(self, error_details: Dict[str, Any]) -> None:
        """Track error metrics if metrics manager available.
        
        Args:
            error_details: Processed error details
        """
        if not self.metrics:
            return
            
        self.metrics.increment_counter(
            "error_total",
            labels={
                "error_type": error_details.get("details", {}).get("error_type", "unknown"),
                "error_code": error_details["code"],
                "http_status": str(error_details["http_status"])
            }
        ) 