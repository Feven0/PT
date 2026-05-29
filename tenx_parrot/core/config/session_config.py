"""Session configuration."""
from typing import Optional
from pydantic import Field, ConfigDict

from ..types.model import CoreBaseModel


class CoreSessionConfig(CoreBaseModel):
    """Session configuration."""
    timeout_seconds: Optional[int] = Field(default=3600, description="Session timeout in seconds (1 hour)")
    cleanup_interval_seconds: Optional[int] = Field(default=300, description="Cleanup interval in seconds (5 minutes)")
    max_inactive_seconds: Optional[int] = Field(default=1800, description="Max inactive time in seconds (30 minutes)")
    max_sessions_per_user: Optional[int] = Field(default=1, description="Maximum number of concurrent sessions per user")
    enabled: Optional[bool] = Field(default=True, description="Whether session management is enabled")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="allow",
        validate_default=True
    ) 