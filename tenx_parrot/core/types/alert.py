"""Alert type definitions."""
from __future__ import annotations
from typing import Any, Dict, Optional, Protocol, runtime_checkable, List
from enum import Enum
from pydantic import Field

from core.types.model import CoreBaseModel
from core.types.base import InfrastructureProviderProtocol

class AlertLevel(str, Enum):
    """Alert severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
class AlertPriority(str, Enum):
    """Alert priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertMessage(CoreBaseModel):
    """Alert message structure."""
    subject: str = Field(description="Alert subject")
    message: str = Field(description="Alert message content")
    priority: AlertPriority = Field(description="Alert priority level")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    recipients: Optional[List[str]] = Field(default=None, description="List of recipients")
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of attachments")
    thread_id: Optional[str] = Field(default=None, description="Message thread ID")
    notification_settings: Optional[Dict[str, Any]] = Field(default=None, description="Notification settings")


class AlertProviderProtocol(Protocol):
    """Protocol for alert providers."""
    
    async def send(
        self,
        message: AlertMessage,
        template_name: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> bool:
        """Send alert message."""
        ...
    
    async def send_batch(
        self,
        messages: List[AlertMessage],
        template_name: Optional[str] = None
    ) -> Dict[str, bool]:
        """Send multiple alert messages."""
        ...
    
    def get_templates(self) -> Dict[str, Dict[str, str]]:
        """Get available alert templates."""
        ...
    
    def format_message(
        self,
        template_name: str,
        **kwargs: Any
    ) -> AlertMessage:
        """Format alert message using template."""
        ...
    
    async def create_thread(
        self,
        subject: str,
        participants: List[str]
    ) -> str:
        """Create a new message thread."""
        ...
    
    async def update_thread(
        self,
        thread_id: str,
        message: AlertMessage
    ) -> bool:
        """Update an existing message thread."""
        ...
    
    async def close_thread(
        self,
        thread_id: str,
        resolution: Optional[str] = None
    ) -> bool:
        """Close a message thread."""
        ... 