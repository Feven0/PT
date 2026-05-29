"""Metric collection decorators."""
import functools
from time import perf_counter
from typing import Any, Callable, Optional, TypeVar, cast

from .service_metrics import ServiceMetrics
from .repository_metrics import RepositoryMetrics
from .websocket_metrics import WebSocketMetrics
from core.base.component import BaseComponent

F = TypeVar('F', bound=Callable[..., Any])

def track_service_operation(operation: str) -> Callable[[F], F]:
    """Decorator to track service operation metrics.
    
    Args:
        operation: Name of the operation to track
        
    Example:
        @track_service_operation("process_request")
        async def process_request(self, request):
            # Method implementation
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            if not hasattr(self, '_metrics') or not isinstance(self._metrics, ServiceMetrics):
                return await func(self, *args, **kwargs)
                
            metrics: ServiceMetrics = self._metrics
            start_time = perf_counter()
            status = "success"
            
            try:
                result = await func(self, *args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                metrics.record_error(type(e).__name__, operation)
                raise
            finally:
                duration = perf_counter() - start_time
                metrics.record_operation_duration(operation, duration, status)
                metrics.increment_request_count(operation, status)
                
        return cast(F, wrapper)
    return decorator

def track_repository_operation(operation: str, query_type: Optional[str] = None) -> Callable[[F], F]:
    """Decorator to track repository operation metrics.
    
    Args:
        operation: Name of the operation to track
        query_type: Optional query type for query counting
        
    Example:
        @track_repository_operation("get_user", query_type="select")
        async def get_user(self, user_id: str):
            # Method implementation
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            if not hasattr(self, '_metrics') or not isinstance(self._metrics, RepositoryMetrics):
                return await func(self, *args, **kwargs)
                
            metrics: RepositoryMetrics = self._metrics
            start_time = perf_counter()
            status = "success"
            
            try:
                result = await func(self, *args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = perf_counter() - start_time
                metrics.record_operation_duration(operation, duration, status)
                if query_type:
                    metrics.increment_query_count(query_type, status)
                
        return cast(F, wrapper)
    return decorator

def track_websocket_message(message_type: str) -> Callable[[F], F]:
    """Decorator to track WebSocket message processing metrics.
    
    Args:
        message_type: Type of message being processed
        
    Example:
        @track_websocket_message("chat_message")
        async def handle_chat_message(self, message):
            # Method implementation
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            if not hasattr(self, '_metrics') or not isinstance(self._metrics, WebSocketMetrics):
                return await func(self, *args, **kwargs)
                
            metrics: WebSocketMetrics = self._metrics
            start_time = perf_counter()
            
            try:
                result = await func(self, *args, **kwargs)
                return result
            except Exception as e:
                metrics.record_error(type(e).__name__)
                raise
            finally:
                latency = perf_counter() - start_time
                metrics.record_message_latency(message_type, latency)
                
        return cast(F, wrapper)
    return decorator 

def track_component_operation(operation: str) -> Callable[[F], F]:
    """Decorator to track component operation metrics.
    
    Args:
        operation: Name of the operation to track
        
    Example:
        @track_component_operation("process_data")
        async def process_data(self, data):
            # Method implementation
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            if not isinstance(self, BaseComponent):
                return await func(self, *args, **kwargs)
                
            start_time = perf_counter()
            status = "success"
            
            try:
                result = await func(self, *args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                self.record_error(type(e).__name__, operation)
                raise
            finally:
                duration = perf_counter() - start_time
                self.record_operation(operation, duration, status)
                
        return cast(F, wrapper)
    return decorator 