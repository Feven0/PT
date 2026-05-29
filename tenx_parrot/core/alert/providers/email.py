"""Email alert provider implementation."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List

from core.types.alert import AlertMessage
from .base import BaseAlertProvider


class EmailAlertProvider(BaseAlertProvider):
    """Email alert provider implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """Initialize email alert provider.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        super().__init__(name=name, config=config, **kwargs)
        
        # SMTP settings
        self._host = self._config.get("host", "localhost")
        self._port = self._config.get("port", 587)
        self._username = self._config.get("username")
        self._password = self._config.get("password")
        self._use_tls = self._config.get("use_tls", True)
        self._from_address = self._config.get("from_address")
        self._default_recipients = self._config.get("default_recipients", [])
        
        # Register default templates
        self.register_template(
            "default",
            subject="{subject}",
            message="{message}",
            priority="low"
        )
        
        self.register_template(
            "alert",
            subject="[ALERT] {subject}",
            message="""
            Alert: {subject}
            
            {message}
            
            Priority: {priority}
            Time: {timestamp}
            """,
            priority="high"
        )
        
    async def send(
        self,
        message: AlertMessage,
        template_name: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> bool:
        """Send email alert.
        
        Args:
            message: Alert message
            template_name: Optional template name
            thread_id: Optional thread ID
            
        Returns:
            True if email was sent successfully
        """
        try:
            # Get recipients
            recipients = message.recipients or self._default_recipients
            if not recipients:
                self.logger.warning("No recipients specified")
                return False
                
            # Create message
            email = MIMEMultipart()
            email["From"] = self._from_address
            email["To"] = ", ".join(recipients)
            email["Subject"] = message.subject
            
            # Add thread ID if provided
            if thread_id:
                email["References"] = thread_id
                email["In-Reply-To"] = thread_id
                
            # Add message body
            email.attach(MIMEText(message.message, "plain"))
            
            # Connect to SMTP server
            with smtplib.SMTP(self._host, self._port) as server:
                if self._use_tls:
                    server.starttls()
                    
                if self._username and self._password:
                    server.login(self._username, self._password)
                    
                # Send email
                server.send_message(email)
                
            return True
            
        except Exception as e:
            self.logger.error(
                "email_send_failed",
                error=str(e),
                recipients=recipients
            )
            return False
            
    async def create_thread(
        self,
        subject: str,
        participants: List[str]
    ) -> str:
        """Create email thread.
        
        Args:
            subject: Thread subject
            participants: Thread participants
            
        Returns:
            Thread ID (Message-ID)
        """
        # Create unique Message-ID
        import uuid
        message_id = f"<{uuid.uuid4()}@{self._host}>"
        
        # Create initial message
        message = AlertMessage(
            subject=subject,
            message="Thread created",
            priority="low",
            recipients=participants
        )
        
        # Send message with Message-ID
        await self.send(message, thread_id=message_id)
        return message_id
        
    async def update_thread(
        self,
        thread_id: str,
        message: AlertMessage
    ) -> bool:
        """Update email thread.
        
        Args:
            thread_id: Thread ID (Message-ID)
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
        """Close email thread.
        
        Args:
            thread_id: Thread ID (Message-ID)
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