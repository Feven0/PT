"""Alert configuration."""
from typing import Dict, Optional, List
from pydantic import Field

from core.types.model import CoreBaseModel


class EmailConfig(CoreBaseModel):
    """Email alert configuration."""
    enabled: bool = Field(default=False)
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    from_address: Optional[str] = Field(default=None)
    default_recipients: List[str] = Field(default_factory=list)
    use_tls: bool = Field(default=True)
    timeout: int = Field(default=30)
    retry_count: int = Field(default=3)
    retry_delay: int = Field(default=5)
    template_dir: Optional[str] = Field(default=None)


class SlackConfig(CoreBaseModel):
    """Slack alert configuration."""
    enabled: bool = Field(default=False)
    webhook_url: Optional[str] = Field(default=None)
    bot_token: Optional[str] = Field(default=None)
    default_channel: str = Field(default="#alerts")
    username: str = Field(default="Alert Bot")
    icon_emoji: str = Field(default=":warning:")
    timeout: int = Field(default=30)
    retry_count: int = Field(default=3)
    retry_delay: int = Field(default=5)


class TelegramConfig(CoreBaseModel):
    """Telegram alert configuration."""
    enabled: bool = Field(default=False)
    bot_token: Optional[str] = Field(default=None)
    chat_id: Optional[str] = Field(default=None)
    parse_mode: str = Field(default="HTML")
    disable_web_page_preview: bool = Field(default=False)
    timeout: int = Field(default=30)
    retry_count: int = Field(default=3)
    retry_delay: int = Field(default=5)


class AlertProviderConfig(CoreBaseModel):
    """Alert provider configuration."""
    email: EmailConfig = Field(default_factory=EmailConfig)
    slack: SlackConfig = Field(default_factory=SlackConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)


class AlertConfig(CoreBaseModel):
    """Alert configuration."""
    enabled: bool = Field(default=True)
    notification_strategy: str = Field(default="priority")  # all/fallback/priority
    default_provider: str = Field(default="email")
    rate_limit: int = Field(default=100)  # alerts per minute
    circuit_breaker_threshold: int = Field(default=5)
    circuit_breaker_timeout: int = Field(default=60)
    
    # Provider configurations
    providers: AlertProviderConfig = Field(default_factory=AlertProviderConfig)
    
    # Priority routing
    priority_routes: Dict[str, List[str]] = Field(default_factory=lambda: {
        "critical": ["email", "slack", "telegram"],
        "high": ["email", "slack"],
        "medium": ["slack"],
        "low": ["slack"]
    })
    
    # Alert templates
    templates: Dict[str, Dict[str, str]] = Field(default_factory=lambda: {
        "interview_complete": {
            "subject": "Interview {interview_id} Complete",
            "message": "Interview {interview_id} has been completed. Duration: {duration}."
        },
        "interview_failed": {
            "subject": "Interview {interview_id} Failed",
            "message": "Interview {interview_id} failed: {error}."
        },
        "system_error": {
            "subject": "System Error",
            "message": "A system error occurred: {error}."
        }
    }) 