"""Logging type definitions."""
from typing import Any, Optional, Protocol, runtime_checkable, ContextManager


@runtime_checkable
class LoggerProtocol(Protocol):
    """Protocol for logging."""
    
    @property
    def level(self) -> str:
        """Get current log level."""
        ...
    
    def set_level(self, level: str) -> None:
        """Set log level."""
        ...
    
    def with_context(self, **kwargs: Any) -> ContextManager['LoggerProtocol']:
        """Create logger with additional context."""
        ...
    
    def info(self, event: str, **kwargs: Any) -> None:
        """Log info level event with structured data."""
        ...
    
    def error(self, event: str, error: Optional[Exception] = None, **kwargs: Any) -> None:
        """Log error level event with structured data and optional exception."""
        ...
    
    def warning(self, event: str, **kwargs: Any) -> None:
        """Log warning level event with structured data."""
        ...
    
    def debug(self, event: str, **kwargs: Any) -> None:
        """Log debug level event with structured data."""
        ...
    
    def critical(self, event: str, error: Optional[Exception] = None, **kwargs: Any) -> None:
        """Log critical level event with structured data and optional exception."""
        ... 