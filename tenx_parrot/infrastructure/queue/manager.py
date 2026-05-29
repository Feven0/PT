"""Queue manager implementation."""
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime, timezone

from core.base.manager import BaseManager
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation
from core.cache.manager import CacheManager
from core.cache.exceptions import QueueOperationError

class QueueError(Exception):
    """Base queue error."""
    pass

class ConfigError(QueueError):
    """Configuration error."""
    pass

class QueueManager(BaseManager):
    """Queue manager for handling message queuing operations."""
    
    REQUIRED_CONFIG = {
        "queues": dict,
        "dlq_suffix": str,
        "max_retries": int,
        "default_timeout": int,
        "batch_size": int,
        "retry_delay": int,
        "dlq_enabled": bool,
        "dlq_max_size": int
    }
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        cache_manager: CacheManager,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None
    ):
        """Initialize queue manager.
        
        Args:
            name: Manager name
            config: Application configuration
            cache_manager: Cache manager instance
            metrics: Optional metrics manager
            logger: Optional logger instance
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger
        )
        
        # Get validated config
        self.queue_config = self._get_manager_config()
        self.cache_manager = cache_manager
        
        # Register metrics
        if self.metrics:
            self._register_metrics()
            
        # Update health status with config details
        self.health.details.update({
            "config": {
                "dlq_suffix": self.queue_config['dlq_suffix'],
                "max_retries": self.queue_config['max_retries'],
                "default_timeout": self.queue_config['default_timeout'],
                "batch_size": self.queue_config['batch_size'],
                "retry_delay": self.queue_config['retry_delay'],
                "queues": list(self.queue_config['queues'].keys())
            }
        })
        
    def _get_manager_config(self) -> Dict[str, Any]:
        """Get and validate manager configuration.
        
        Returns:
            Dict containing validated configuration with defaults
            
        Raises:
            ConfigError: If configuration is invalid
        """
        try:
            # Extract config with defaults
            config = {
                'queues': self._config.get('queues', {}),
                'dlq_suffix': self._config.get('dlq_suffix', '_dlq'),
                'max_retries': self._config.get('max_retries', 3),
                'default_timeout': self._config.get('default_timeout', 30),
                'batch_size': self._config.get('batch_size', 10),
                'retry_delay': self._config.get('retry_delay', 5),
                'dlq_enabled': self._config.get('dlq_enabled', True),
                'dlq_max_size': self._config.get('dlq_max_size', 1000)
            }
            
            # Validate fields and types
            for field, field_type in self.REQUIRED_CONFIG.items():
                value = config.get(field)
                if not isinstance(value, field_type):
                    if self.logger:
                        self.logger.warning(
                            f"Invalid type for {field}, attempting conversion",
                            field=field,
                            expected=field_type.__name__,
                            actual=type(value).__name__
                        )
                    try:
                        config[field] = field_type(value)
                    except (ValueError, TypeError):
                        raise ConfigError(f"Invalid type for {field}")
            
            # Validate specific constraints
            if not config['queues']:
                raise ConfigError("At least one queue must be configured")
            if config['max_retries'] < 0:
                raise ConfigError("Max retries must be non-negative")
            if config['default_timeout'] < 1:
                raise ConfigError("Default timeout must be greater than 0")
            if config['batch_size'] < 1:
                raise ConfigError("Batch size must be greater than 0")
            if config['retry_delay'] < 0:
                raise ConfigError("Retry delay must be non-negative")
                
            return config
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    "Failed to validate queue config",
                    error=str(e)
                )
            # Return safe defaults
            return {
                'queues': {},
                'dlq_suffix': '_dlq',
                'max_retries': 3,
                'default_timeout': 30,
                'batch_size': 10,
                'retry_delay': 5,
                'dlq_enabled': True,
                'dlq_max_size': 1000
            }
    
    def _register_metrics(self) -> None:
        """Register queue metrics."""
        # Operation metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "queue": "", "status": ""}
        )
        
        # Message metrics
        self.metrics.register_metric(
            f"{self.name}_messages_total",
            MetricType.COUNTER,
            f"Total number of messages in {self.name}",
            labels={"queue": "", "type": ""}
        )
        
        # Queue size metrics
        self.metrics.register_metric(
            f"{self.name}_queue_size",
            MetricType.GAUGE,
            f"Current size of queues in {self.name}",
            labels={"queue": "", "type": ""}
        )
        
        # Processing metrics
        self.metrics.register_metric(
            f"{self.name}_processing_duration_seconds",
            MetricType.HISTOGRAM,
            f"Time taken to process messages in {self.name}",
            labels={"queue": ""}
        )
        
        # Error metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"queue": "", "type": ""}
        )
        
        # DLQ metrics
        self.metrics.register_metric(
            f"{self.name}_dlq_messages",
            MetricType.GAUGE,
            f"Number of messages in DLQ in {self.name}",
            labels={"queue": ""}
        )
    
    @track_component_operation
    def _get_queue_name(self, queue: str) -> str:
        """Get full queue name.
        
        Args:
            queue: Queue type
            
        Returns:
            Full queue name
            
        Raises:
            ValueError: If queue not found
        """
        queue_name = self.queue_config.queues.get(queue)
        if not queue_name:
            if self.metrics:
                self.metrics.increment_counter(
                    f"{self.name}_errors_total",
                    labels={"queue": queue, "type": "invalid_queue"}
                )
            raise ValueError(f"Queue not found: {queue}")
            
        return queue_name
        
    def _get_dlq_name(self, queue: str) -> str:
        """Get dead letter queue name.
        
        Args:
            queue: Queue type
            
        Returns:
            DLQ name
        """
        return f"{self._get_queue_name(queue)}{self.queue_config.dlq_suffix}"
        
    async def push(
        self,
        queue: str,
        message: Any,
        delay: Optional[int] = None
    ) -> None:
        """Push message to queue.
        
        Args:
            queue: Queue type
            message: Message to push
            delay: Optional delay in seconds
            
        Raises:
            QueueError: If operation fails
        """
        try:
            queue_name = self._get_queue_name(queue)
            await self.cache_manager.queue_push(queue_name, message, delay)
            
        except Exception as e:
            self.logger.error(
                "queue_push_failed",
                error=str(e),
                queue=queue
            )
            raise QueueError(f"Failed to push to queue: {str(e)}")
            
    async def pop(
        self,
        queue: str,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Pop message from queue.
        
        Args:
            queue: Queue type
            timeout: Optional timeout in seconds
            
        Returns:
            Message if available, None if queue empty
            
        Raises:
            QueueError: If operation fails
        """
        try:
            queue_name = self._get_queue_name(queue)
            return await self.cache_manager.queue_pop(queue_name, timeout)
            
        except Exception as e:
            self.logger.error(
                "queue_pop_failed",
                error=str(e),
                queue=queue
            )
            raise QueueError(f"Failed to pop from queue: {str(e)}")
            
    async def move_to_dlq(
        self,
        queue: str,
        message: Dict[str, Any],
        error: str
    ) -> None:
        """Move message to dead letter queue.
        
        Args:
            queue: Queue type
            message: Failed message
            error: Error message
            
        Raises:
            QueueError: If operation fails
        """
        try:
            if not self.queue_config.dlq_enabled:
                return
                
            dlq_name = self._get_dlq_name(queue)
            
            # Add error info to message
            message["_dlq"] = {
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "original_queue": self._get_queue_name(queue)
            }
            
            await self.cache_manager.queue_push(dlq_name, message)
            
            # Check DLQ size and trim if needed
            length = await self.cache_manager.queue_length(dlq_name)
            if length > self.queue_config.dlq_max_size:
                # Remove oldest messages
                to_remove = length - self.queue_config.dlq_max_size
                for _ in range(to_remove):
                    await self.cache_manager.queue_pop(dlq_name)
                    
        except Exception as e:
            self.logger.error(
                "move_to_dlq_failed",
                error=str(e),
                queue=queue
            )
            raise QueueError(f"Failed to move message to DLQ: {str(e)}")
            
    async def process_queue(
        self,
        queue: str,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
        batch_size: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> None:
        """Process messages from queue.
        
        Args:
            queue: Queue type
            handler: Async function to handle messages
            batch_size: Optional batch size (defaults to config batch_size)
            timeout: Optional timeout in seconds
            
        Raises:
            QueueError: If operation fails
        """
        try:
            queue_name = self._get_queue_name(queue)
            size = batch_size or self.queue_config.batch_size
            
            while True:
                processed = 0
                for _ in range(size):
                    message = await self.cache_manager.queue_pop(queue_name, timeout)
                    if not message:
                        break
                        
                    try:
                        await handler(message)
                        processed += 1
                        
                    except Exception as e:
                        self.logger.error(
                            "message_processing_failed",
                            error=str(e),
                            queue=queue,
                            message=message
                        )
                        await self.move_to_dlq(queue, message, str(e))
                        
                if processed == 0:
                    break
                    
        except Exception as e:
            self.logger.error(
                "queue_processing_failed",
                error=str(e),
                queue=queue
            )
            raise QueueError(f"Failed to process queue: {str(e)}")
            
    async def retry_dlq(
        self,
        queue: str,
        max_retries: Optional[int] = None
    ) -> int:
        """Retry messages from dead letter queue.
        
        Args:
            queue: Queue type
            max_retries: Optional maximum number of messages to retry
            
        Returns:
            Number of messages retried
            
        Raises:
            QueueError: If operation fails
        """
        try:
            if not self.queue_config.dlq_enabled:
                return 0
                
            dlq_name = self._get_dlq_name(queue)
            queue_name = self._get_queue_name(queue)
            retried = 0
            
            while True:
                if max_retries and retried >= max_retries:
                    break
                    
                message = await self.cache_manager.queue_pop(dlq_name)
                if not message:
                    break
                    
                # Remove DLQ metadata and push back to main queue
                if "_dlq" in message:
                    del message["_dlq"]
                    
                await self.cache_manager.queue_push(queue_name, message)
                retried += 1
                
            return retried
            
        except Exception as e:
            self.logger.error(
                "retry_dlq_failed",
                error=str(e),
                queue=queue
            )
            raise QueueError(f"Failed to retry DLQ messages: {str(e)}")
            
    async def get_queue_info(self, queue: str) -> Dict[str, int]:
        """Get queue information.
        
        Args:
            queue: Queue type
            
        Returns:
            Dictionary with queue lengths
            
        Raises:
            QueueError: If operation fails
        """
        try:
            queue_name = self._get_queue_name(queue)
            main_length = await self.cache_manager.queue_length(queue_name)
            
            result = {
                "main": main_length,
                "dlq": 0
            }
            
            if self.queue_config.dlq_enabled:
                dlq_name = self._get_dlq_name(queue)
                result["dlq"] = await self.cache_manager.queue_length(dlq_name)
                
            return result
            
        except Exception as e:
            self.logger.error(
                "get_queue_info_failed",
                error=str(e),
                queue=queue
            )
            raise QueueError(f"Failed to get queue info: {str(e)}")
            
    async def clear_queue(
        self,
        queue: str,
        include_dlq: bool = True
    ) -> None:
        """Clear queue.
        
        Args:
            queue: Queue type
            include_dlq: Whether to also clear DLQ
            
        Raises:
            QueueError: If operation fails
        """
        try:
            queue_name = self._get_queue_name(queue)
            await self.cache_manager.queue_clear(queue_name)
            
            if include_dlq and self.queue_config.dlq_enabled:
                dlq_name = self._get_dlq_name(queue)
                await self.cache_manager.queue_clear(dlq_name)
                
        except Exception as e:
            self.logger.error(
                "clear_queue_failed",
                error=str(e),
                queue=queue
            )
            raise QueueError(f"Failed to clear queue: {str(e)}")
            
    async def check_status(self) -> None:
        """Check queue status.
        
        Raises:
            QueueError: If status check fails
        """
        try:
            # Check if cache manager is healthy
            if not self.cache_manager.is_healthy():
                raise QueueError("Cache manager is not healthy")
            
        except Exception as e:
            raise QueueError(f"Queue status check failed: {str(e)}") 