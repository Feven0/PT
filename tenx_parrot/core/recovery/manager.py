"""Recovery management."""
from typing import Dict, Any, Optional, Set, TYPE_CHECKING, TypeVar, Generic, Union, List
from enum import Enum
import asyncio
from datetime import datetime, timedelta, timezone


if TYPE_CHECKING:
    from core.telemetry.metrics import MetricsManager
    from core.logging import BackendLogger

from core.base.manager import BaseManager
from core.config import AppConfig, RecoveryConfig
from core.logging import BackendLogger
from core.types.recovery import RecoveryStrategy



class RecoveryManager(BaseManager):
    """Manager for system recovery operations."""
    
    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional['MetricsManager'] = None,
        logger: Optional['BackendLogger'] = None,
        dependencies: Optional[Dict[str, Any]] = None
    ):
        """Initialize cache manager.
        
        Args:
            name: Manager name
            config: Application configuration
            metrics: Optional metrics manager
            logger: Optional logger instance
        """

        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
            
        
 
        self._is_initialized = False
        self.recovery_history: List[Dict[str, Any]] = []
        self.recovery_attempts: Dict[str, int] = {}
        self.last_recovery: Dict[str, datetime] = {}
        
        # Get thresholds from config, ensuring all values are positive
        self.recovery_thresholds = {
            k: max(1, v) for k, v in self._config.get('thresholds',{
            "service": 3,
            "connection": 5, 
            "storage": 3
        }).items()
        }
               
        # Add strategy-specific tracking
        self.strategy_history: Dict[RecoveryStrategy, List[Dict[str, Any]]] = {
            strategy: [] for strategy in RecoveryStrategy
        }
               
    @property
    def config(self) -> RecoveryConfig:
        """Get recovery configuration."""
        return RecoveryConfig(**self._config)
    
    @property
    def cleanup_interval(self) -> int:
        """Get cleanup interval with safety bounds."""
        return max(60, self.config.cleanup_interval)
        
    @property
    def attempt_expiry(self) -> int:
        """Get attempt expiry with safety bounds."""
        return max(300, self.config.attempt_expiry)
        
    @property
    def cooldown_period(self) -> int:
        """Get cooldown period with safety bounds."""
        return max(60, self.config.cooldown_period)
        
    @property
    def default_threshold(self) -> int:
        """Get default threshold with safety bounds."""
        return max(1, self.config.default_threshold)
        
    async def _do_initialize(self) -> None:
        """Initialize recovery manager."""
        if not self.config.enabled:
            self.logger.warning("Recovery manager disabled by configuration")
            return
            
        # Initialize recovery tracking
        self.recovery_attempts.clear()
        self.last_recovery.clear()
        
    async def _do_start(self) -> None:
        """Start recovery manager."""
        if not self.config.enabled:
            return
            
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def _do_stop(self) -> None:
        """Stop recovery manager."""
        # Cancel cleanup task
        if hasattr(self, 'cleanup_task'):
            self.cleanup_task.cancel()
            
    async def attempt_recovery(
        self,
        component: str,
        recovery_strategy: Optional[RecoveryStrategy] = None,
        error: Optional[Exception] = None
    ) -> bool:
        """Attempt to recover a failed component with a specific strategy."""
        if not self.config.enabled:
            return False
            
        # Check recovery threshold
        attempts = self.recovery_attempts.get(component, 0)
        threshold = self.recovery_thresholds.get(
            component.split(':')[0],
            self.default_threshold
        )
        
        if attempts >= threshold:
            self.logger.warning(
                "recovery_threshold_exceeded",
                context="recovery",
                component=component,
                attempts=attempts,
                threshold=threshold
            )
            return False
            
        # Check cooldown period
        last_attempt = self.last_recovery.get(component)
        cooldown = timedelta(seconds=self.cooldown_period)
        if last_attempt and (datetime.now(timezone.utc) - last_attempt) < cooldown:
            self.logger.warning(
                "recovery_cooldown",
                context="recovery",
                component=component,
                last_attempt=last_attempt
            )
            return False
            
        # Attempt recovery
        try:
            attempt_time = datetime.now(timezone.utc)
            success = False
            
            # TODO: Implement actual recovery logic using recovery_strategy
            # Set success based on actual recovery outcome
            
            # Record attempt with strategy and outcome
            attempt_record = {
                "component": component,
                "strategy": recovery_strategy,
                "timestamp": attempt_time,
                "success": success,
                "error": str(error) if error else None
            }
            
            self.recovery_history.append(attempt_record)
            if recovery_strategy:
                self.strategy_history[recovery_strategy].append(attempt_record)

            self.recovery_attempts[component] = attempts + 1
            self.last_recovery[component] = attempt_time

            self.logger.info(
                "recovery_attempted",
                context="recovery",
                component=component,
                attempt=attempts + 1
            )
            
            # Update metrics
            self.metrics["recovery_attempts"] = self.metrics.get("recovery_attempts", 0) + 1
            return success
            
        except Exception as e:
            self.logger.error(
                "recovery_failed",
                context="recovery",
                component=component,
                error=str(e)
            )
            return False
            
    def get_recovery_history(
        self,
        component: Optional[str] = None,
        recovery_strategy: Optional[RecoveryStrategy] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get filtered recovery history."""
        end = end_time or datetime.now(timezone.utc)
        start = start_time or end - timedelta(days=self.config.max_history_days)
        
        return [
            entry for entry in self.recovery_history
            if (component is None or entry['component'] == component)
            and (recovery_strategy is None or entry['strategy'] == recovery_strategy)
            and (start <= entry['timestamp'] <= end)
            and (not success_only or entry['success'])
        ]

    async def reset_recovery(self, component: str) -> None:
        """Reset recovery attempts for component."""
        self.recovery_attempts.pop(component, None)
        self.last_recovery.pop(component, None)
        self.recovery_history = [
            entry for entry in self.recovery_history
            if entry['component'] != component
        ]
        
        self.logger.info(
            "recovery_reset",
            context="recovery",
            component=component
        )
        
    async def _cleanup_loop(self) -> None:
        """Clean up old recovery attempts."""
        while True:
            try:
                now = datetime.now(timezone.utc)
                expiry = timedelta(seconds=self.attempt_expiry)
                # Remove attempts older than expiry time
                for component in list(self.last_recovery.keys()):
                    if (now - self.last_recovery[component]) > expiry:
                        await self.reset_recovery(component)
                        
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    "recovery_cleanup_failed",
                    context="recovery",
                    error=str(e)
                )
                await asyncio.sleep(60) 