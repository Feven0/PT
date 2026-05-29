"""Email service for sending notifications."""
from typing import Dict, Any, List, Optional
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from core.base.service import BaseService
from core.config import AppConfig
from core.types.components import HealthStatus


class EmailService(BaseService):
    """Service for sending email notifications."""
    
    def __init__(self, config: AppConfig):
        """Initialize email service.
        
        Args:
            config: Application configuration
        """
        super().__init__(name="email", config=config)
        self.smtp_client: Optional[aiosmtplib.SMTP] = None
        self.queue: asyncio.Queue = asyncio.Queue()
        
        # Update health details with initial configuration
        self.update_health_details({
            "enabled": self.config.notifications.email.enabled,
            "smtp_host": self.config.notifications.email.smtp_host,
            "smtp_port": self.config.notifications.email.smtp_port,
            "use_tls": self.config.notifications.email.use_tls,
            "queue_size": 0,
            "connected": False
        })
        
    async def _do_initialize(self) -> None:
        """Initialize email service."""
        if not self.config.notifications.email.enabled:
            self.update_health_details({"status": "disabled"})
            raise ValueError("Email service is disabled")
            
        # Initialize SMTP client
        self.smtp_client = aiosmtplib.SMTP(
            hostname=self.config.notifications.email.smtp_host,
            port=self.config.notifications.email.smtp_port,
            use_tls=self.config.notifications.email.use_tls
        )
        
    async def _do_start(self) -> None:
        """Start email service."""
        try:
            # Connect to SMTP server
            await self.smtp_client.connect()
            await self.smtp_client.login(
                username=self.config.notifications.email.smtp_user,
                password=self.config.notifications.email.smtp_pass
            )
            
            # Update health status after successful connection
            self.update_health_details({
                "connected": True,
                "last_connected": datetime.now().isoformat()
            })
            
            # Start processing queue
            self.process_task = asyncio.create_task(self._process_queue())
            
        except Exception as e:
            self.update_health_details({
                "connected": False,
                "last_error": str(e)
            })
            raise
        
    async def _do_stop(self) -> None:
        """Stop email service."""
        # Cancel queue processing
        if hasattr(self, 'process_task'):
            self.process_task.cancel()
            
        # Close SMTP connection
        if self.smtp_client:
            await self.smtp_client.quit()
            self.update_health_details({
                "connected": False,
                "last_disconnected": datetime.now().isoformat()
            })
            
    async def send_email(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        html: bool = False
    ) -> None:
        """Send an email.
        
        Args:
            subject: Email subject
            body: Email body
            recipients: List of recipient email addresses
            html: Whether body is HTML
        """
        message = MIMEMultipart()
        message["From"] = self.config.notifications.email.sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        
        # Add body
        content_type = "html" if html else "plain"
        message.attach(MIMEText(body, content_type))
        
        # Queue for sending
        await self.queue.put({
            "message": message,
            "recipients": recipients
        })
        
        self.logger.info(
            "email_queued",
            context="email",
            recipients=len(recipients)
        )
        
    async def _process_queue(self) -> None:
        """Process email queue."""
        while True:
            try:
                # Get next email
                email = await self.queue.get()
                
                # Send email
                await self.smtp_client.send_message(email["message"])
                
                # Update metrics
                self.metrics["emails_sent"] = self.metrics.get("emails_sent", 0) + 1
                self.metrics["recipients"] = self.metrics.get("recipients", 0) + len(email["recipients"])
                
                self.logger.info(
                    "email_sent",
                    context="email",
                    recipients=len(email["recipients"])
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.metrics["send_errors"] = self.metrics.get("send_errors", 0) + 1
                
                self.logger.error(
                    "email_send_failed",
                    context="email",
                    error=str(e)
                ) 