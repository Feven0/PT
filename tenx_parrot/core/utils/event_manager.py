"""Event management for tool system."""
from typing import Dict, List, Any, Callable, Awaitable, Optional
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass, field
from core.base.manager import BaseManager

logger = logging.getLogger(__name__)

EventHandler = Callable[[str, Dict[str, Any]], Awaitable[None]]

@dataclass
class EventSubscription:
    """Subscription to tool events."""
    handler: EventHandler
    event_types: List[str]
    created_at: datetime = field(default_factory=datetime.now)

class EventManager(BaseManager):
    """Manages tool events and handlers."""
    
    def __init__(self):
        """Initialize event manager."""
        super().__init__()
        self.subscribers: Dict[str, EventSubscription] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize the event manager."""
        self.processing_task = asyncio.create_task(self._process_events())
        self.initialized = True
        logger.info("Event manager initialized")
        
    async def cleanup(self) -> None:
        """Clean up event manager."""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        self.subscribers.clear()
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        self.initialized = False
        logger.info("Event manager cleaned up")
        
    def subscribe(
        self,
        handler: EventHandler,
        event_types: Optional[List[str]] = None,
        subscriber_id: Optional[str] = None
    ) -> str:
        """Subscribe to tool events."""
        if subscriber_id is None:
            subscriber_id = f"sub_{len(self.subscribers)}"
            
        self.subscribers[subscriber_id] = EventSubscription(
            handler=handler,
            event_types=event_types or ["*"]
        )
        
        logger.info(
            f"Added subscriber {subscriber_id} for events: {event_types}"
        )
        return subscriber_id
        
    def unsubscribe(self, subscriber_id: str) -> None:
        """Unsubscribe from tool events."""
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
            logger.info(f"Removed subscriber {subscriber_id}")
            
    async def emit(
        self,
        event_type: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit a tool event."""
        await self.event_queue.put({
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        })
        
    async def _process_events(self) -> None:
        """Process events from queue."""
        while True:
            try:
                event = await self.event_queue.get()
                event_type = event["type"]
                
                for sub_id, subscription in self.subscribers.items():
                    if (
                        "*" in subscription.event_types
                        or event_type in subscription.event_types
                    ):
                        try:
                            await subscription.handler(
                                event_type,
                                event["data"]
                            )
                        except Exception as e:
                            logger.error(
                                f"Error in event handler {sub_id}: {e}"
                            )
                            
                self.event_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                
    def list_subscribers(self) -> Dict[str, List[str]]:
        """List all subscribers and their event types."""
        return {
            sub_id: sub.event_types
            for sub_id, sub in self.subscribers.items()
        } 