"""Notification service."""
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from core.base.service import BaseService
from core.telemetry.metrics import MetricsManager
from core.config import AppConfig
from core.logging import BackendLogger
from infrastructure.notification.client import (
    NotificationInfrastructureClient,
    NotificationPriority,
    NotificationError
)

class NotificationService(BaseService):
    """Service for managing notifications."""
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        notification_client: NotificationInfrastructureClient,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None
    ):
        """Initialize notification service.
        
        Args:
            name: Service name
            config: Application configuration
            notification_client: Notification infrastructure client
            metrics: Optional metrics manager
            logger: Optional logger instance
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger
        )
        
        self.notification_client = notification_client
        
    def _get_template(
        self,
        template_name: str,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Get notification template with variables filled.
        
        Args:
            template_name: Template name
            template_vars: Optional template variables
            
        Returns:
            Template with subject and message
            
        Raises:
            ValueError: If template not found
        """
        template = self.config.notification.templates.get(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
            
        if template_vars:
            return {
                "subject": template["subject"].format(**template_vars),
                "message": template["message"].format(**template_vars)
            }
            
        return template
        
    async def notify_interview_complete(
        self,
        interview_id: str,
        duration: Union[int, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send interview completion notification.
        
        Args:
            interview_id: Interview ID
            duration: Interview duration in seconds
            metadata: Optional additional metadata
            
        Raises:
            NotificationError: If sending fails
        """
        try:
            template = self._get_template(
                "interview_complete",
                {
                    "interview_id": interview_id,
                    "duration": f"{duration:.1f}s"
                }
            )
            
            await self.notification_client.send_notification(
                message=template["message"],
                subject=template["subject"],
                priority=NotificationPriority.MEDIUM,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(
                "interview_complete_notification_failed",
                error=str(e),
                interview_id=interview_id
            )
            raise NotificationError(f"Failed to send interview completion notification: {str(e)}")
            
    async def notify_interview_failed(
        self,
        interview_id: str,
        error: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send interview failure notification.
        
        Args:
            interview_id: Interview ID
            error: Error message
            metadata: Optional additional metadata
            
        Raises:
            NotificationError: If sending fails
        """
        try:
            template = self._get_template(
                "interview_failed",
                {
                    "interview_id": interview_id,
                    "error": error
                }
            )
            
            await self.notification_client.send_notification(
                message=template["message"],
                subject=template["subject"],
                priority=NotificationPriority.HIGH,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(
                "interview_failed_notification_failed",
                error=str(e),
                interview_id=interview_id
            )
            raise NotificationError(f"Failed to send interview failure notification: {str(e)}")
            
    async def notify_system_error(
        self,
        error: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send system error notification.
        
        Args:
            error: Error message
            metadata: Optional additional metadata
            
        Raises:
            NotificationError: If sending fails
        """
        try:
            template = self._get_template(
                "system_error",
                {"error": error}
            )
            
            await self.notification_client.send_notification(
                message=template["message"],
                subject=template["subject"],
                priority=NotificationPriority.CRITICAL,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(
                "system_error_notification_failed",
                error=str(e)
            )
            raise NotificationError(f"Failed to send system error notification: {str(e)}")
            
    async def send_custom_notification(
        self,
        message: str,
        subject: Optional[str] = None,
        priority: str = NotificationPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        providers: Optional[List[str]] = None
    ) -> None:
        """Send custom notification.
        
        Args:
            message: Notification message
            subject: Optional subject line
            priority: Notification priority
            metadata: Optional metadata
            providers: Optional list of specific providers
            
        Raises:
            NotificationError: If sending fails
        """
        try:
            await self.notification_client.send_notification(
                message=message,
                subject=subject,
                priority=priority,
                metadata=metadata,
                providers=providers
            )
            
        except Exception as e:
            self.logger.error(
                "custom_notification_failed",
                error=str(e),
                subject=subject
            )
            raise NotificationError(f"Failed to send custom notification: {str(e)}")
            
    async def check_notification_status(
        self,
        provider: Optional[str] = None
    ) -> Dict[str, bool]:
        """Check notification provider status.
        
        Args:
            provider: Optional specific provider to check
            
        Returns:
            Dictionary of provider status
        """
        try:
            return await self.notification_client.check_provider_status(provider)
            
        except Exception as e:
            self.logger.error(
                "notification_status_check_failed",
                error=str(e),
                provider=provider
            )
            raise NotificationError(f"Failed to check notification status: {str(e)}") 