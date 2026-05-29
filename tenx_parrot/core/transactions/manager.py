"""Transaction management implementation."""
from typing import Optional, Union, Dict, Set, Any, AsyncContextManager
from asyncio import Lock
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import uuid

from core.base.manager import BaseManager
from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.config import AppConfig

class TransactionState:
    """Transaction state enumeration."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    ERROR = "error"

class TransactionError(Exception):
    """Base class for transaction-related errors."""
    pass

class Transaction:
    """Transaction context."""
    
    def __init__(self, id: str):
        self.id = id
        self.state = TransactionState.INACTIVE
        self.start_time = datetime.now(timezone.utc)
        self.end_time: Optional[datetime] = None
        self.error: Optional[Exception] = None

class TransactionManager(BaseManager[Transaction]):
    """Manager for coordinating transactions."""
    
    def __init__(
        self,
        name: str,
        config: Optional[Union[AppConfig, Any, Dict[str, Any]]] = None,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize transaction manager.
        
        Args:
            name: Manager name
            config: Manager configuration
            metrics: Optional metrics collector
            logger: Optional logger
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        
        self._active_transactions: Dict[str, Transaction] = {}
        self._lock = Lock()
        
    async def _initialize_impl(self) -> None:
        """Initialize transaction manager."""
        self._active_transactions.clear()
        
        # Register metrics
        if self.metrics:
            self.metrics.gauge(
                "active_transactions",
                0,
                labels={"name": self.name}
            )
            self.metrics.counter(
                "transaction_starts_total",
                labels={"name": self.name}
            )
            self.metrics.counter(
                "transaction_commits_total",
                labels={"name": self.name}
            )
            self.metrics.counter(
                "transaction_rollbacks_total",
                labels={"name": self.name}
            )
            
    async def _start_impl(self) -> None:
        """Start transaction manager."""
        pass
        
    async def _stop_impl(self) -> None:
        """Stop transaction manager."""
        # Rollback any active transactions
        async with self._lock:
            for tx_id in list(self._active_transactions.keys()):
                await self.rollback(tx_id)
                
    async def _check_health_impl(self) -> None:
        """Check transaction manager health."""
        self._health_status.details.update({
            "active_transactions": len(self._active_transactions),
            "transaction_states": {
                tx_id: tx.state
                for tx_id, tx in self._active_transactions.items()
            }
        })
        
    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager[Transaction]:
        """Start new transaction context.
        
        Returns:
            Transaction context manager
            
        Raises:
            TransactionError: If transaction creation fails
        """
        tx_id = str(uuid.uuid4())
        try:
            tx = await self.begin(tx_id)
            yield tx
            await self.commit(tx_id)
        except Exception as e:
            await self.rollback(tx_id)
            raise TransactionError(f"Transaction failed: {str(e)}")
            
    async def begin(self, tx_id: str) -> Transaction:
        """Begin new transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction instance
            
        Raises:
            TransactionError: If transaction already exists
        """
        async with self._lock:
            if tx_id in self._active_transactions:
                raise TransactionError(f"Transaction {tx_id} already exists")
                
            tx = Transaction(tx_id)
            tx.state = TransactionState.ACTIVE
            self._active_transactions[tx_id] = tx
            
            if self.metrics:
                self.metrics.increment(
                    "transaction_starts_total",
                    labels={"name": self.name}
                )
                self.metrics.gauge(
                    "active_transactions",
                    len(self._active_transactions),
                    labels={"name": self.name}
                )
                
            await self.add_to_resource_pool("transactions", tx)
            return tx
            
    async def commit(self, tx_id: str) -> None:
        """Commit transaction.
        
        Args:
            tx_id: Transaction ID
            
        Raises:
            TransactionError: If transaction not found or invalid state
        """
        async with self._lock:
            tx = self._active_transactions.get(tx_id)
            if not tx:
                raise TransactionError(f"Transaction {tx_id} not found")
                
            if tx.state != TransactionState.ACTIVE:
                raise TransactionError(
                    f"Transaction {tx_id} in invalid state: {tx.state}"
                )
                
            tx.state = TransactionState.COMMITTED
            tx.end_time = datetime.now(timezone.utc)
            
            if self.metrics:
                self.metrics.increment(
                    "transaction_commits_total",
                    labels={"name": self.name}
                )
                
            await self.remove_from_resource_pool("transactions", tx)
            del self._active_transactions[tx_id]
            
    async def rollback(self, tx_id: str) -> None:
        """Rollback transaction.
        
        Args:
            tx_id: Transaction ID
            
        Raises:
            TransactionError: If transaction not found
        """
        async with self._lock:
            tx = self._active_transactions.get(tx_id)
            if not tx:
                raise TransactionError(f"Transaction {tx_id} not found")
                
            tx.state = TransactionState.ROLLED_BACK
            tx.end_time = datetime.now(timezone.utc)
            
            if self.metrics:
                self.metrics.increment(
                    "transaction_rollbacks_total",
                    labels={"name": self.name}
                )
                
            await self.remove_from_resource_pool("transactions", tx)
            del self._active_transactions[tx_id]
            
    async def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """Get transaction by ID.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction if found
        """
        return self._active_transactions.get(tx_id)
        
    async def get_active_transactions(self) -> Dict[str, Transaction]:
        """Get all active transactions.
        
        Returns:
            Dictionary of transaction ID to transaction
        """
        return self._active_transactions.copy() 