"""Protocol definitions for core types."""
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic, Any, Dict, Optional

from core.types.components import HealthStatusInfo

# Type variables for generic protocols
ConfigT = TypeVar('ConfigT')
MessageT = TypeVar('MessageT')
EntityT = TypeVar('EntityT')

class ComponentProtocol(Protocol):
    """Base protocol for all components."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component."""
        pass
        
    @abstractmethod
    async def start(self) -> None:
        """Start the component."""
        pass
        
    @abstractmethod
    async def stop(self) -> None:
        """Stop the component."""
        pass
        
    @abstractmethod
    async def check_health(self) -> HealthStatusInfo:
        """Check component health."""
        pass

class ServiceProtocol(ComponentProtocol, Protocol):
    """Base protocol for all services."""
    pass

class RepositoryProtocol(ComponentProtocol, Protocol):
    """Base protocol for all repositories."""
    pass

class InfrastructureProviderProtocol(ComponentProtocol, Protocol):
    """Base protocol for all infrastructure providers."""
    pass

class LoggerProtocol(Protocol):
    """Protocol for logging interface."""
    
    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        pass
        
    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        pass
        
    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        pass
        
    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        pass 