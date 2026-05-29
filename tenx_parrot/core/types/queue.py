"""Queue types and protocols."""
from typing import Dict, Any, Optional, Protocol, runtime_checkable

@runtime_checkable
class QueueProviderProtocol(Protocol):
    """Protocol for queue providers."""
    
    async def queue_push(
        self, 
        queue: str, 
        message: Any, 
        delay: Optional[int] = None
    ) -> None:
        """Push message to queue.
        
        Args:
            queue: Queue name
            message: Message to push
            delay: Optional delay in seconds
            
        Raises:
            QueueOperationError: If operation fails
        """
        ...
        
    async def queue_pop(
        self, 
        queue: str, 
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Pop message from queue.
        
        Args:
            queue: Queue name
            timeout: Optional timeout in seconds
            
        Returns:
            Message if available, None if queue empty
            
        Raises:
            QueueOperationError: If operation fails
        """
        ...
        
    async def queue_length(self, queue: str) -> int:
        """Get queue length.
        
        Args:
            queue: Queue name
            
        Returns:
            Number of messages in queue
            
        Raises:
            QueueOperationError: If operation fails
        """
        ...
        
    async def queue_clear(self, queue: str) -> None:
        """Clear queue.
        
        Args:
            queue: Queue name
            
        Raises:
            QueueOperationError: If operation fails
        """
        ... 