"""Middleware type definitions."""
from typing import Any, Dict, Optional, Protocol, runtime_checkable, TypeVar, Callable, Awaitable, Union, List, Generic
from datetime import datetime
from uuid import UUID
from pydantic import Field

from core.types.model import CoreBaseModel
from .base import ComponentT


class RequestContext(CoreBaseModel):
    """Request context."""
    request_id: UUID = Field(description="Unique request identifier")
    method: str = Field(description="HTTP method")
    path: str = Field(description="Request path")
    headers: Dict[str, str] = Field(description="Request headers")
    query_params: Dict[str, str] = Field(description="Query parameters")
    body: Optional[Any] = Field(default=None, description="Request body")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    start_time: datetime = Field(default_factory=datetime.now, description="Request start time")


class ResponseContext(CoreBaseModel):
    """Response context."""
    status_code: int = Field(description="HTTP status code")
    headers: Dict[str, str] = Field(description="Response headers")
    body: Any = Field(description="Response body")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


Request = TypeVar('Request')
Response = TypeVar('Response')
Handler = Callable[[Request], Awaitable[Response]]
NextMiddleware = Callable[[Request], Awaitable[Response]]


@runtime_checkable
class MiddlewareProtocol(Protocol, Generic[Request, Response]):
    """Middleware protocol."""
    
    name: str
    state: str
    dependencies: List[str]
    
    async def process_request(
        self,
        request: Request,
        context: RequestContext,
        next_middleware: NextMiddleware
    ) -> Response:
        """Process request through middleware chain."""
        ...
    
    async def process_response(
        self,
        response: Response,
        context: ResponseContext
    ) -> Response:
        """Process response through middleware chain."""
        ...
    
    async def handle_error(
        self,
        error: Exception,
        request: Request,
        context: RequestContext
    ) -> Response:
        """Handle error in middleware chain."""
        ...
    
    def add_handler(
        self,
        path: str,
        method: str,
        handler: Handler
    ) -> None:
        """Add request handler."""
        ...
    
    def remove_handler(
        self,
        path: str,
        method: str
    ) -> None:
        """Remove request handler."""
        ...
    
    async def get_middleware_stats(self) -> Dict[str, Any]:
        """Get middleware statistics."""
        ...
    
    async def validate_middleware_chain(self) -> bool:
        """Validate middleware chain."""
        ... 