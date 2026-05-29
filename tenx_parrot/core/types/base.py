"""Base type definitions."""
from __future__ import annotations
from typing import (
    Any, Dict, Optional, Protocol, Set, TypeVar, 
    runtime_checkable, List, Generic, Union, Type
)
from datetime import datetime
from enum import Enum

from core.types.components import (
    HealthStatus,
    HealthStatusInfo,
    ComponentState,
    ComponentNames
)

# Generic type variables
T = TypeVar("T")
ID = TypeVar("ID", str, int, bytes)
ConfigT = TypeVar("ConfigT")
MessageT = TypeVar("MessageT")
EntityT = TypeVar("EntityT")
ComponentT = TypeVar("ComponentT")


@runtime_checkable
class ComponentProtocol(Protocol):
    """Base component protocol."""
    
    name: str
    state: ComponentState
    dependencies: Set[str]
    
    async def initialize(self) -> None:
        """Initialize component."""
        ...
        
    async def start(self) -> None:
        """Start component."""
        ...
        
    async def stop(self) -> None:
        """Stop component."""
        ...
        
    async def check_health(self) -> HealthStatusInfo:
        """Check component health."""
        ...
    
    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to the component."""
        ...
    
    def remove_dependency(self, dependency: str) -> None:
        """Remove a dependency from the component."""
        ...
    
    def has_dependency(self, dependency: str) -> bool:
        """Check if component has a dependency."""
        ...
    
    async def wait_for_dependencies(self, timeout: Optional[float] = None) -> bool:
        """Wait for all dependencies to be ready."""
        ...


@runtime_checkable
class InfrastructureProviderProtocol(Protocol, Generic[T]):
    """Base infrastructure provider protocol."""
    
    name: str
    state: ComponentState
    dependencies: Set[str]
    health_status: HealthStatusInfo
    last_health_check: datetime
    
    async def initialize(self) -> None:
        """Initialize component."""
        ...
        
    async def start(self) -> None:
        """Start component."""
        ...
        
    async def stop(self) -> None:
        """Stop component."""
        ...
        
    async def check_health(self) -> HealthStatusInfo:
        """Check component health."""
        ...
        
    async def validate_connection(self) -> None:
        """Validate provider connection."""
        ...
    
    async def connect(self) -> None:
        """Establish connection to the provider."""
        ...
    
    async def disconnect(self) -> None:
        """Close connection to the provider."""
        ...
    
    async def reconnect(self) -> None:
        """Re-establish connection to the provider."""
        ...
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get provider connection information."""
        ...
    
    async def get_provider_stats(self) -> Dict[str, Any]:
        """Get provider statistics."""
        ...
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate provider configuration."""
        ...


@runtime_checkable
class ServiceProtocol(ComponentProtocol, Protocol[T]):
    """Base service protocol."""
    
    async def process(self, data: T) -> Any:
        """Process service request."""
        ...
    
    async def validate(self, data: T) -> bool:
        """Validate service input."""
        ...
    
    async def handle_error(self, error: Exception, data: T) -> None:
        """Handle service error."""
        ...
    
    async def pre_process(self, data: T) -> T:
        """Pre-process service input."""
        ...
    
    async def post_process(self, result: Any, data: T) -> Any:
        """Post-process service output."""
        ...
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        ...
    
    async def validate_service_state(self) -> bool:
        """Validate service state."""
        ...


@runtime_checkable
class RepositoryProtocol(ComponentProtocol, Protocol[EntityT]):
    """Base repository protocol."""
    
    async def create(self, data: EntityT) -> EntityT:
        """Create new entity."""
        ...
    
    async def read(self, id: Union[str, int]) -> Optional[EntityT]:
        """Read entity by ID."""
        ...
    
    async def update(self, id: Union[str, int], data: EntityT) -> EntityT:
        """Update existing entity."""
        ...
    
    async def delete(self, id: Union[str, int]) -> bool:
        """Delete entity by ID."""
        ...
    
    async def list(
        self,
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, str]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> List[EntityT]:
        """List entities with filtering, sorting and pagination."""
        ...
    
    async def count(
        self,
        filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count entities matching filter."""
        ...
    
    async def exists(self, id: Union[str, int]) -> bool:
        """Check if entity exists."""
        ...
    
    async def create_many(self, items: List[EntityT]) -> List[EntityT]:
        """Create multiple entities."""
        ...
    
    async def update_many(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any]
    ) -> int:
        """Update multiple entities."""
        ...
    
    async def delete_many(
        self,
        filter: Dict[str, Any]
    ) -> int:
        """Delete multiple entities."""
        ...
    
    async def validate_schema(self) -> bool:
        """Validate repository schema."""
        ...
    
    async def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        ... 