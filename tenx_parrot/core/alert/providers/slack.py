"""Slack alert provider implementation."""
import aiohttp
from typing import Dict, Any, Optional, List

from core.types.alert import AlertMessage
from .base import BaseAlertProvider


class SlackAlertProvider(BaseAlertProvider):
    """Slack alert provider implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """Initialize Slack alert provider.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        super().__init__(name=name, config=config, **kwargs)
        
        # Slack settings
        self._webhook_url = self._config["webhook_url"]
        self._default_channel = self._config.get("default_channel", "#alerts")
        self._username = self._config.get("username", "Alert Bot")
        self._icon_emoji = self._config.get("icon_emoji", ":warning:")
        
        # Register default templates
        self.register_template(
            "default",
            subject="{subject}",
            message="{message}",
            priority="low"
        )
        
        self.register_template(
            "alert",
            subject="*[ALERT]* {subject}",
            message="""
            *Alert:* {subject}
            
            {message}
            
            *Priority:* {priority}
            *Time:* {timestamp}
            """,
            priority="high"
        )
        
    def _format_slack_message(
        self,
        message: AlertMessage,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format message for Slack API.
        
        Args:
            message: Alert message
            thread_ts: Optional thread timestamp
            
        Returns:
            Formatted Slack message
        """
        # Set color based on priority
        color_map = {
            "critical": "#FF0000",  # Red
            "high": "#FFA500",      # Orange
            "medium": "#FFFF00",    # Yellow
            "low": "#00FF00"        # Green
        }
        color = color_map.get(message.priority, "#808080")  # Gray default
        
        # Build attachment
        attachment = {
            "color": color,
            "title": message.subject,
            "text": message.message,
            "fields": []
        }
        
        # Add metadata fields
        if message.metadata:
            for key, value in message.metadata.items():
                attachment["fields"].append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
                
        slack_message = {
            "channel": message.recipients[0] if message.recipients else self._default_channel,
            "username": self._username,
            "icon_emoji": self._icon_emoji,
            "attachments": [attachment]
        }
        
        if thread_ts:
            slack_message["thread_ts"] = thread_ts
            
        return slack_message
        
    async def send(
        self,
        message: AlertMessage,
        template_name: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> bool:
        """Send Slack alert.
        
        Args:
            message: Alert message
            template_name: Optional template name
            thread_id: Optional thread ID
            
        Returns:
            True if message was sent successfully
        """
        try:
            # Format message
            slack_message = self._format_slack_message(message, thread_id)
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._webhook_url,
                    json=slack_message
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Slack API error: {error_text}")
                        
            return True
            
        except Exception as e:
            self.logger.error(
                "slack_send_failed",
                error=str(e),
                channel=slack_message.get("channel")
            )
            return False
            
    async def create_thread(
        self,
        subject: str,
        participants: List[str]
    ) -> str:
        """Create Slack thread.
        
        Args:
            subject: Thread subject
            participants: Thread participants (channels)
            
        Returns:
            Thread timestamp
        """
        # Create initial message
        message = AlertMessage(
            subject=subject,
            message="Thread created",
            priority="low",
            recipients=participants
        )
        
        # Send message and get thread timestamp
        try:
            slack_message = self._format_slack_message(message)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._webhook_url,
                    json=slack_message
                ) as response:
                    if response.status != 200:
                        raise ValueError(f"Slack API error: {await response.text()}")
                    data = await response.json()
                    return data["ts"]
                    
        except Exception as e:
            self.logger.error(
                "slack_thread_create_failed",
                error=str(e)
            )
            raise
            
    async def update_thread(
        self,
        thread_id: str,
        message: AlertMessage
    ) -> bool:
        """Update Slack thread.
        
        Args:
            thread_id: Thread timestamp
            message: New message
            
        Returns:
            True if thread was updated successfully
        """
        return await self.send(message, thread_id=thread_id)
        
    async def close_thread(
        self,
        thread_id: str,
        resolution: Optional[str] = None
    ) -> bool:
        """Close Slack thread.
        
        Args:
            thread_id: Thread timestamp
            resolution: Optional resolution message
            
        Returns:
            True if thread was closed successfully
        """
        message = AlertMessage(
            subject="Thread Closed",
            message=resolution or "Thread closed",
            priority="low"
        )
        return await self.send(message, thread_id=thread_id) 