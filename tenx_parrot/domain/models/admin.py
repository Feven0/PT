from typing import Dict, List, Optional
from datetime import datetime, timezone
from uuid import UUID
from pydantic import Field

from .base import BaseDomainModel


class InterviewMetrics(BaseDomainModel):
    """Interview metrics for admin overview."""
    total_interviews: int = Field(default=0, description="Total number of interviews")
    completed_interviews: int = Field(default=0, description="Number of completed interviews")
    active_interviews: int = Field(default=0, description="Number of active interviews")
    average_duration_minutes: float = Field(default=0.0, description="Average interview duration in minutes")
    completion_rate: float = Field(default=0.0, description="Interview completion rate")


class UserMetrics(BaseDomainModel):
    """User metrics for admin overview."""
    total_users: int = Field(default=0, description="Total number of users")
    active_users: int = Field(default=0, description="Number of active users")
    new_users_last_30_days: int = Field(default=0, description="New users in last 30 days")


class SystemMetrics(BaseDomainModel):
    """System performance metrics."""
    average_response_time_ms: float = Field(default=0.0, description="Average API response time in milliseconds")
    error_rate: float = Field(default=0.0, description="System error rate")
    system_uptime_hours: float = Field(default=0.0, description="System uptime in hours")


class AdminOverview(BaseDomainModel):
    """Admin dashboard overview model."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the overview")
    interview_metrics: InterviewMetrics = Field(default_factory=InterviewMetrics, description="Interview-related metrics")
    user_metrics: UserMetrics = Field(default_factory=UserMetrics, description="User-related metrics")
    system_metrics: SystemMetrics = Field(default_factory=SystemMetrics, description="System performance metrics")
    recent_activities: List[Dict] = Field(default_factory=list, description="Recent system activities")
    alerts: List[Dict] = Field(default_factory=list, description="System alerts and notifications") 