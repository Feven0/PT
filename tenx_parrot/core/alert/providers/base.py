"""Base alert provider implementation."""
from typing import Dict, Any, Optional, List, Protocol, runtime_checkable
from datetime import datetime, timezone

from core.base.component import BaseComponent
from core.types.alert import AlertMessage, AlertProviderProtocol
from core.types.components import HealthStatus, HealthStatusInfo
from core.types.metrics import MetricType


class BaseAlertProvider(BaseComponent, AlertProviderProtocol):
    """Base alert provider implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """Initialize base alert provider.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        super().__init__(name=name, config=config, **kwargs)
        self._templates: Dict[str, Dict[str, str]] = {}
        
    async def send(
        self,
        message: AlertMessage,
        template_name: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> bool:
        """Send alert message.
        
        Args:
            message: Alert message to send
            template_name: Optional template name
            thread_id: Optional thread ID
            
        Returns:
            True if message was sent successfully
            
        Raises:
            NotImplementedError: Must be implemented by provider
        """
        raise NotImplementedError()
        
    async def send_batch(
        self,
        messages: List[AlertMessage],
        template_name: Optional[str] = None
    ) -> Dict[str, bool]:
        """Send multiple alert messages.
        
        Args:
            messages: List of messages to send
            template_name: Optional template name
            
        Returns:
            Dict mapping message IDs to success status
        """
        results = {}
        for message in messages:
            try:
                success = await self.send(message, template_name)
                results[message.id] = success
            except Exception as e:
                self.logger.error(
                    "batch_send_failed",
                    error=str(e),
                    message_id=message.id
                )
                results[message.id] = False
        return results
        
    def get_templates(self) -> Dict[str, Dict[str, str]]:
        """Get available alert templates.
        
        Returns:
            Dict mapping template names to template definitions
        """
        return self._templates
        
    def format_message(
        self,
        template_name: str,
        **kwargs: Any
    ) -> AlertMessage:
        """Format alert message using template.
        
        Args:
            template_name: Template name
            **kwargs: Template variables
            
        Returns:
            Formatted alert message
            
        Raises:
            KeyError: If template not found
        """
        if template_name not in self._templates:
            raise KeyError(f"Template {template_name} not found")
            
        template = self._templates[template_name]
        try:
            subject = template["subject"].format(**kwargs)
            message = template["message"].format(**kwargs)
            
            return AlertMessage(
                subject=subject,
                message=message,
                priority=template.get("priority", "low"),
                metadata=kwargs
            )
        except KeyError as e:
            raise KeyError(f"Missing template variable: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to format template: {str(e)}")
            
    async def create_thread(
        self,
        subject: str,
        participants: List[str]
    ) -> str:
        """Create a new message thread.
        
        Args:
            subject: Thread subject
            participants: Thread participants
            
        Returns:
            Thread ID
            
        Raises:
            NotImplementedError: Must be implemented by provider
        """
        raise NotImplementedError()
        
    async def update_thread(
        self,
        thread_id: str,
        message: AlertMessage
    ) -> bool:
        """Update an existing message thread.
        
        Args:
            thread_id: Thread ID
            message: New message
            
        Returns:
            True if thread was updated successfully
            
        Raises:
            NotImplementedError: Must be implemented by provider
        """
        raise NotImplementedError()
        
    async def close_thread(
        self,
        thread_id: str,
        resolution: Optional[str] = None
    ) -> bool:
        """Close a message thread.
        
        Args:
            thread_id: Thread ID
            resolution: Optional resolution message
            
        Returns:
            True if thread was closed successfully
            
        Raises:
            NotImplementedError: Must be implemented by provider
        """
        raise NotImplementedError()
        
    def register_template(
        self,
        name: str,
        subject: str,
        message: str,
        priority: str = "low"
    ) -> None:
        """Register alert template.
        
        Args:
            name: Template name
            subject: Subject template
            message: Message template
            priority: Message priority
        """
        self._templates[name] = {
            "subject": subject,
            "message": message,
            "priority": priority
        }
        
    async def check_health(self) -> bool:
        """Check provider health.
        
        Returns:
            True if provider is healthy
        """
        try:
            # Try to send test message
            test_message = AlertMessage(
                subject="Health Check",
                message="Testing provider health",
                priority="low"
            )
            return await self.send(test_message)
        except Exception as e:
            self.logger.error(
                "health_check_failed",
                error=str(e),
                provider=self.name
            )
            return False 