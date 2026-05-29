"""Repository transaction management."""
from typing import Optional, Union, List, Dict, Set, Any, AsyncContextManager
from contextlib import asynccontextmanager
from enum import Enum
from asyncio import Lock

from core.base.component import Component
from core.telemetry.metrics import MetricsCollector
from core.logging import BackendLogger
from core.base.component import BaseComponent
from core.config import AppConfig

class TransactionState(Enum):
    """Transaction state."""
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


class RepositoryTransaction:
    """Repository transaction context."""
    
    def __init__(self, id: str):
        """Initialize transaction.
        
        Args:
            id: Transaction ID
        """
        self.id = id
        self.state = TransactionState.ACTIVE
        self.operations: List[Dict[str, Any]] = []
        
    def add_operation(
        self,
        repository: str,
        operation: str,
        args: tuple,
        kwargs: dict
    ) -> None:
        """Add operation to transaction.
        
        Args:
            repository: Repository name
            operation: Operation name
            args: Operation arguments
            kwargs: Operation keyword arguments
        """
        self.operations.append({
            "repository": repository,
            "operation": operation,
            "args": args,
            "kwargs": kwargs
        })
        
    def commit(self) -> None:
        """Mark transaction as committed."""
        self.state = TransactionState.COMMITTED
        
    def rollback(self) -> None:
        """Mark transaction as rolled back."""
        self.state = TransactionState.ROLLED_BACK


class RepositoryTransactionManager(BaseComponent):
    """Manager for coordinating repository transactions."""
    
    def __init__(
        self,
        name: str,
        config: Optional[Union[AppConfig, Any, Dict[str, Any]]] = None,
        metrics: Optional[MetricsCollector] = None,
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
        super().__init__(name,
                         config=config,
                         metrics=metrics,
                         logger=logger or BackendLogger(name),
                         dependencies=dependencies or set())
        
        self._config = config
        self._active_transactions: Dict[str, RepositoryTransaction] = {}
        self._lock = Lock()
        
        # Register metrics
        if metrics:
            metrics.gauge(
                "active_transactions",
                0,
                labels={"name": name}
            )
            metrics.counter(
                "transaction_starts_total",
                labels={"name": name}
            )
            metrics.counter(
                "transaction_commits_total",
                labels={"name": name}
            )
            metrics.counter(
                "transaction_rollbacks_total",
                labels={"name": name}
            )
            metrics.counter(
                "transaction_operations_total",
                labels={"name": name}
            )
            
    @asynccontextmanager
    async def transaction(self, id: str) -> AsyncContextManager[RepositoryTransaction]:
        """Start new transaction.
        
        Args:
            id: Transaction ID
            
        Yields:
            Transaction context
        """
        try:
            # Start transaction
            async with self._lock:
                if id in self._active_transactions:
                    raise ValueError(f"Transaction {id} already exists")
                    
                transaction = RepositoryTransaction(id)
                self._active_transactions[id] = transaction
                
                if self._metrics:
                    self._metrics.gauge(
                        "active_transactions",
                        len(self._active_transactions),
                        labels={"name": self.name}
                    )
                    self._metrics.counter(
                        "transaction_starts_total",
                        labels={"name": self.name}
                    )
                    
            try:
                yield transaction
                
                # Commit transaction
                transaction.commit()
                if self._metrics:
                    self._metrics.counter(
                        "transaction_commits_total",
                        labels={"name": self.name}
                    )
                    self._metrics.counter(
                        "transaction_operations_total",
                        value=len(transaction.operations),
                        labels={"name": self.name}
                    )
                    
            except:
                # Rollback transaction
                transaction.rollback()
                if self._metrics:
                    self._metrics.counter(
                        "transaction_rollbacks_total",
                        labels={"name": self.name}
                    )
                raise
                
        finally:
            # End transaction
            async with self._lock:
                self._active_transactions.pop(id, None)
                if self._metrics:
                    self._metrics.gauge(
                        "active_transactions",
                        len(self._active_transactions),
                        labels={"name": self.name}
                    )
                    
    def get_transaction(self, id: str) -> Optional[RepositoryTransaction]:
        """Get active transaction.
        
        Args:
            id: Transaction ID
            
        Returns:
            Transaction if found and active
        """
        transaction = self._active_transactions.get(id)
        if transaction and transaction.state == TransactionState.ACTIVE:
            return transaction
        return None 