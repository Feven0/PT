"""Recovery type definitions."""
from typing import Any, Dict, Optional, Protocol, runtime_checkable, TypeVar, List, Union, Generic
from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import Field
from pydantic import ConfigDict

from core.types.model import CoreBaseModel
from .base import ComponentT


class RecoveryState(str, Enum):
    """Recovery states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecoveryStrategy(str, Enum):
    """Recovery strategies."""
    RETRY = "retry"
    ROLLBACK = "rollback"
    COMPENSATE = "compensate"
    SKIP = "skip"


class RecoveryPoint(CoreBaseModel):
    """Recovery point."""
    point_id: UUID = Field(description="Unique point identifier")
    component: str = Field(description="Component name")
    state: Dict[str, Any] = Field(description="Component state")
    timestamp: datetime = Field(description="Recovery point timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class RecoveryContext(CoreBaseModel):
    """Recovery context."""
    recovery_id: UUID = Field(description="Unique recovery identifier")
    state: RecoveryState = Field(description="Recovery state")
    strategy: RecoveryStrategy = Field(description="Recovery strategy")
    component: str = Field(description="Component name")
    error: Optional[Exception] = Field(default=None, description="Error that triggered recovery")
    recovery_points: List[RecoveryPoint] = Field(description="List of recovery points")
    start_time: datetime = Field(description="Recovery start time")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow arbitrary types like Exception
        from_attributes=True,  # Inherit from CoreBaseModel
        extra='allow'  # Allow extra fields
    )


T = TypeVar('T')


@runtime_checkable
class RecoveryProtocol(Protocol, Generic[T]):
    """Recovery protocol."""
    
    name: str
    state: str
    dependencies: List[str]
    
    async def create_recovery_point(
        self,
        component: str,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> RecoveryPoint:
        """Create a recovery point."""
        ...
    
    async def start_recovery(
        self,
        component: str,
        error: Exception,
        strategy: RecoveryStrategy,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RecoveryContext:
        """Start recovery process."""
        ...
    
    async def execute_recovery(
        self,
        recovery_id: UUID
    ) -> bool:
        """Execute recovery process."""
        ...
    
    async def cancel_recovery(
        self,
        recovery_id: UUID
    ) -> bool:
        """Cancel recovery process."""
        ...
    
    async def get_recovery_status(
        self,
        recovery_id: UUID
    ) -> Optional[RecoveryContext]:
        """Get recovery status."""
        ...
    
    async def list_recovery_points(
        self,
        component: Optional[str] = None
    ) -> List[RecoveryPoint]:
        """List recovery points."""
        ...
    
    async def list_active_recoveries(
        self,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[RecoveryContext]:
        """List active recovery processes."""
        ...
    
    async def cleanup_recovery_points(
        self,
        older_than: Optional[datetime] = None
    ) -> int:
        """Clean up old recovery points."""
        ...
    
    async def validate_recovery_state(
        self,
        recovery_id: UUID
    ) -> bool:
        """Validate recovery state."""
        ...
    
    async def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        ... 