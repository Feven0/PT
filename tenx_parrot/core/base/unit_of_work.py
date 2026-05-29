"""Unit of Work pattern implementation for transaction management."""
from typing import Dict, Any, Optional, AsyncContextManager, Set, List, Type, TypeVar, Generic
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import asyncio

from core.base.lifecycle import LifecycleAware
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager


class TransactionError(Exception):
    """Base class for transaction-related errors."""
    pass


class TransactionState:
    """Transaction state enumeration."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    ERROR = "error"


class UnitOfWork(LifecycleAware):
    """Unit of Work implementation for managing transactions."""
    
    def __init__(
        self,
        config: AppConfig,
        metrics: MetricsManager,
        alert_manager: AlertManager
    ):
        """Initialize Unit of Work.
        
        Args:
            config: Application configuration
            metrics: Metrics collector
            alert_manager: Alert manager instance
        """
        super().__init__(name="unit_of_work")
        self.config = config
        self.metrics = metrics
        self.alert_manager = alert_manager
        
        # Transaction state
        self._state = TransactionState.INACTIVE
        self._start_time: Optional[datetime] = None
        self._error: Optional[Exception] = None
        
        # Initialize metrics
        self.metrics.update({
            "transactions_total": 0,
            "transactions_active": 0,
            "transactions_committed": 0,
            "transactions_rolled_back": 0,
            "transactions_error": 0
        })
        
    @property
    def state(self) -> str:
        """Get current transaction state."""
        return self._state
        
    @property
    def error(self) -> Optional[Exception]:
        """Get current transaction error if any."""
        return self._error
        
    @property
    def duration(self) -> Optional[float]:
        """Get transaction duration in seconds if active."""
        if self._start_time and self._state == TransactionState.ACTIVE:
            return (datetime.now(timezone.utc) - self._start_time).total_seconds()
        return None
        
    async def _initialize_impl(self) -> None:
        """Initialize Unit of Work."""
        self._state = TransactionState.INACTIVE
        self._start_time = None
        self._error = None
        
    async def _start_impl(self) -> None:
        """Start Unit of Work."""
        pass
        
    async def _stop_impl(self) -> None:
        """Stop Unit of Work."""
        # Rollback any active transaction
        if self._state == TransactionState.ACTIVE:
            await self.rollback()
            
    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager["UnitOfWork"]:
        """Start new transaction context.
        
        Returns:
            Transaction context manager
            
        Raises:
            TransactionError: If transaction is already active
        """
        if self._state == TransactionState.ACTIVE:
            raise TransactionError("Transaction already active")
            
        try:
            # Start transaction
            await self.begin()
            yield self
            
            # Commit if no errors
            await self.commit()
            
        except Exception as e:
            # Rollback on error
            self._error = e
            await self.rollback()
            raise
            
    async def begin(self) -> None:
        """Begin new transaction.
        
        Raises:
            TransactionError: If transaction is already active
        """
        if self._state == TransactionState.ACTIVE:
            raise TransactionError("Transaction already active")
            
        self._state = TransactionState.ACTIVE
        self._start_time = datetime.now(timezone.utc)
        self._error = None
        
        self.metrics.increment("transactions_total")
        self.metrics.increment("transactions_active")
        
    async def commit(self) -> None:
        """Commit current transaction.
        
        Raises:
            TransactionError: If no active transaction
        """
        if self._state != TransactionState.ACTIVE:
            raise TransactionError("No active transaction")
            
        try:
            # Commit changes
            self._state = TransactionState.COMMITTED
            self.metrics.increment("transactions_committed")
            self.metrics.decrement("transactions_active")
            
            # Record metrics
            if self.duration:
                self.metrics.observe("transaction_duration", self.duration)
                
        except Exception as e:
            self._error = e
            self._state = TransactionState.ERROR
            self.metrics.increment("transactions_error")
            raise TransactionError(f"Commit failed: {str(e)}")
            
    async def rollback(self) -> None:
        """Rollback current transaction.
        
        Raises:
            TransactionError: If no active transaction
        """
        if self._state != TransactionState.ACTIVE:
            raise TransactionError("No active transaction")
            
        try:
            # Rollback changes
            self._state = TransactionState.ROLLED_BACK
            self.metrics.increment("transactions_rolled_back")
            self.metrics.decrement("transactions_active")
            
            # Record metrics
            if self.duration:
                self.metrics.observe("transaction_duration", self.duration)
                
            # Alert on rollback
            if self._error:
                await self.alert_manager.send_alert(
                    "transaction_rollback",
                    f"Transaction rolled back due to error: {str(self._error)}"
                )
                
        except Exception as e:
            self._error = e
            self._state = TransactionState.ERROR
            self.metrics.increment("transactions_error")
            raise TransactionError(f"Rollback failed: {str(e)}")
            
    def __repr__(self) -> str:
        """Get string representation."""
        return (
            f"UnitOfWork(state={self._state}, "
            f"duration={self.duration}, "
            f"error={self._error})"
        )

    def elapsed_time(self) -> float:
        """Get elapsed time since unit of work started.
        
        Returns:
            Elapsed time in seconds
        """
        if not self._start_time:
            return 0.0
        return (datetime.now(timezone.utc) - self._start_time).total_seconds()

    async def __aenter__(self) -> "UnitOfWork":
        """Enter context manager.
        
        Returns:
            Unit of work instance
        """
        self._start_time = datetime.now(timezone.utc)
        await self.start()
        return self 