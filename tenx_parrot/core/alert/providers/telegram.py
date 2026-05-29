"""Telegram alert provider implementation."""
import aiohttp
from typing import Dict, Any, Optional, List

from core.types.alert import AlertMessage
from .base import BaseAlertProvider


class TelegramAlertProvider(BaseAlertProvider):
    """Telegram alert provider implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """Initialize Telegram alert provider.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        super().__init__(name=name, config=config, **kwargs)
        
        # Telegram settings
        self._bot_token = self._config["bot_token"]
        self._api_base = f"https://api.telegram.org/bot{self._bot_token}"
        self._default_chat_id = self._config.get("default_chat_id")
        self._parse_mode = self._config.get("parse_mode", "HTML")
        
        # Register default templates
        self.register_template(
            "default",
            subject="{subject}",
            message="{message}",
            priority="low"
        )
        
        self.register_template(
            "alert",
            subject="<b>[ALERT]</b> {subject}",
            message="""
            <b>Alert:</b> {subject}
            
            {message}
            
            <b>Priority:</b> {priority}
            <b>Time:</b> {timestamp}
            """,
            priority="high"
        )
        
    def _format_telegram_message(
        self,
        message: AlertMessage,
        reply_to: Optional[int] = None
    ) -> Dict[str, Any]:
        """Format message for Telegram API.
        
        Args:
            message: Alert message
            reply_to: Optional message ID to reply to
            
        Returns:
            Formatted Telegram message
        """
        # Format text with HTML
        text = f"<b>{message.subject}</b>\n\n{message.message}"
        
        # Add metadata if present
        if message.metadata:
            text += "\n\n<b>Additional Info:</b>"
            for key, value in message.metadata.items():
                text += f"\n• <b>{key}:</b> {value}"
                
        # Build message payload
        payload = {
            "chat_id": message.recipients[0] if message.recipients else self._default_chat_id,
            "text": text,
            "parse_mode": self._parse_mode,
            "disable_web_page_preview": True
        }
        
        if reply_to:
            payload["reply_to_message_id"] = reply_to
            
        return payload
        
    async def send(
        self,
        message: AlertMessage,
        template_name: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> bool:
        """Send Telegram alert.
        
        Args:
            message: Alert message
            template_name: Optional template name
            thread_id: Optional thread ID (message ID to reply to)
            
        Returns:
            True if message was sent successfully
        """
        try:
            # Format message
            payload = self._format_telegram_message(
                message,
                reply_to=int(thread_id) if thread_id else None
            )
            
            # Send to Telegram
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._api_base}/sendMessage",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Telegram API error: {error_text}")
                        
            return True
            
        except Exception as e:
            self.logger.error(
                "telegram_send_failed",
                error=str(e),
                chat_id=payload.get("chat_id")
            )
            return False
            
    async def create_thread(
        self,
        subject: str,
        participants: List[str]
    ) -> str:
        """Create Telegram thread (message group).
        
        Args:
            subject: Thread subject
            participants: Thread participants (chat IDs)
            
        Returns:
            Message ID as thread ID
        """
        # Create initial message
        message = AlertMessage(
            subject=subject,
            message="Thread created",
            priority="low",
            recipients=participants
        )
        
        # Send message and get message ID
        try:
            payload = self._format_telegram_message(message)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._api_base}/sendMessage",
                    json=payload
                ) as response:
                    if response.status != 200:
                        raise ValueError(f"Telegram API error: {await response.text()}")
                    data = await response.json()
                    return str(data["result"]["message_id"])
                    
        except Exception as e:
            self.logger.error(
                "telegram_thread_create_failed",
                error=str(e)
            )
            raise
            
    async def update_thread(
        self,
        thread_id: str,
        message: AlertMessage
    ) -> bool:
        """Update Telegram thread.
        
        Args:
            thread_id: Message ID to reply to
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
        """Close Telegram thread.
        
        Args:
            thread_id: Message ID to reply to
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