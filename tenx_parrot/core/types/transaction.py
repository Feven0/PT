"""Transaction type definitions."""
from typing import Protocol, TypeVar, Generic, Any, Dict, Optional
from enum import Enum

from .protocols import ComponentProtocol

class TransactionState(str, Enum):
    """Transaction state enumeration."""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"

class TransactionIsolationLevel(str, Enum):
    """Transaction isolation level enumeration."""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"

class TransactionContext:
    """Transaction context."""
    state: TransactionState
    isolation_level: TransactionIsolationLevel
    metadata: Dict[str, Any]

class TransactionProtocol(ComponentProtocol):
    """Transaction protocol."""
    
    async def begin(self) -> None:
        """Begin transaction."""
        pass
        
    async def commit(self) -> None:
        """Commit transaction."""
        pass
        
    async def rollback(self) -> None:
        """Rollback transaction."""
        pass
        
    async def get_state(self) -> TransactionState:
        """Get transaction state."""
        pass 