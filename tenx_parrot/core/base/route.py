"""Base route implementation."""
from typing import Dict, List, Optional, Set, Union, Any, Type, TypeVar, Generic, Callable
from datetime import datetime, timezone
from uuid import UUID
import inspect
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer

from core.errors.exceptions import ServiceError, AuthorizationError, ValidationError
from core.telemetry.metrics import MetricsCollector
from core.logging import BackendLogger
from core.security.auth import AuthManager
from core.types.user import User

T = TypeVar('T')


class BaseRoute(Generic[T]):
    """Base route class."""
    
    def __init__(
        self,
        name: str,
        prefix: str,
        tags: List[str],
        auth_manager: AuthManager,
        metrics: Optional[MetricsCollector] = None,
        logger: Optional[BackendLogger] = None
    ):
        """Initialize route.
        
        Args:
            name: Route name
            prefix: URL prefix
            tags: OpenAPI tags
            auth_manager: Auth manager
            metrics: Optional metrics collector
            logger: Optional logger
        """
        self.name = name
        self.prefix = prefix
        self.tags = tags
        self._auth_manager = auth_manager
        self._metrics = metrics
        self._logger = logger
        
        # Create router
        self.router = APIRouter(
            prefix=prefix,
            tags=tags
        )
        
        # Create OAuth2 scheme
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        
    async def get_current_user(
        self,
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))
    ) -> User:
        """Get current user from token.
        
        Args:
            token: Access token
            
        Returns:
            Current user
            
        Raises:
            HTTPException: If token is invalid or user is not found
        """
        try:
            return await self._auth_manager.get_current_user(token)
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
            
    def record_metrics(
        self,
        operation: str,
        start_time: datetime,
        status_code: int,
        error: Optional[Exception] = None
    ) -> None:
        """Record operation metrics.
        
        Args:
            operation: Operation name
            start_time: Start time
            status_code: Response status code
            error: Optional error
        """
        if not self._metrics:
            return
            
        # Record duration
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        self._metrics.record_value(
            "route_operation_duration",
            duration,
            tags={
                "route": self.name,
                "operation": operation,
                "status": status_code
            }
        )
        
        # Record error if any
        if error:
            self._metrics.increment_counter(
                "route_operation_error",
                tags={
                    "route": self.name,
                    "operation": operation,
                    "error": type(error).__name__
                }
            )
            
    def log_operation(
        self,
        operation: str,
        start_time: datetime,
        status_code: int,
        error: Optional[Exception] = None,
        **kwargs: Any
    ) -> None:
        """Log operation details.
        
        Args:
            operation: Operation name
            start_time: Start time
            status_code: Response status code
            error: Optional error
            kwargs: Additional log data
        """
        if not self._logger:
            return
            
        # Calculate duration
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Prepare log data
        log_data = {
            "route": self.name,
            "operation": operation,
            "duration": duration,
            "status_code": status_code,
            **kwargs
        }
        
        if error:
            # Log error
            self._logger.error(
                f"Route operation {operation} failed: {str(error)}",
                extra=log_data,
                exc_info=True
            )
        else:
            # Log success
            self._logger.info(
                f"Route operation {operation} completed",
                extra=log_data
            )
            
    def handle_error(self, error: Exception) -> HTTPException:
        """Handle operation error.
        
        Args:
            error: Operation error
            
        Returns:
            HTTP exception
        """
        if isinstance(error, ValidationError):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )
        elif isinstance(error, AuthorizationError):
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
                headers={"WWW-Authenticate": "Bearer"}
            )
        elif isinstance(error, ServiceError):
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(error)
            )
        else:
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            ) 