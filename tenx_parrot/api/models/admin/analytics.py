"""Admin analytics API models."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import Field
from uuid import UUID

from core.types.model import CoreBaseModel


class UserPerformanceDTO(CoreBaseModel):
    """User performance data transfer object."""
    user_id: UUID = Field(description="User ID")
    name: str = Field(description="User name")
    total_sessions: int = Field(description="Total number of sessions")
    completed_sessions: int = Field(description="Number of completed sessions")
    average_score: float = Field(description="Average score across all sessions")
    total_duration: float = Field(description="Total time spent in sessions")
    strengths: List[str] = Field(description="Areas of strength")
    areas_for_improvement: List[str] = Field(description="Areas needing improvement")
    job_performance: Dict[str, float] = Field(description="Performance by job type")


class JobStatisticsDTO(CoreBaseModel):
    """Job statistics data transfer object."""
    job_id: UUID = Field(description="Job ID")
    title: str = Field(description="Job title")
    total_interviews: int = Field(description="Total interviews conducted")
    completed_interviews: int = Field(description="Completed interviews")
    average_duration: float = Field(description="Average interview duration")
    average_score: float = Field(description="Average interview score")
    completion_rate: float = Field(description="Interview completion rate")
    skill_distribution: Dict[str, float] = Field(description="Distribution of skills tested")
    difficulty_rating: float = Field(description="Average difficulty rating")


class EngagementMetricsDTO(CoreBaseModel):
    """Engagement metrics data transfer object."""
    total_users: int = Field(description="Total registered users")
    active_users: int = Field(description="Active users in period")
    total_sessions: int = Field(description="Total sessions conducted")
    average_sessions_per_user: float = Field(description="Average sessions per user")
    completion_rate: float = Field(description="Overall completion rate")
    average_duration: float = Field(description="Average session duration")
    engagement_by_job: Dict[str, float] = Field(description="Engagement metrics by job")
    user_retention: float = Field(description="User retention rate")


class AdminOverviewDTO(CoreBaseModel):
    """Administrative overview data transfer object."""
    total_users: int = Field(description="Total users in system")
    active_users: int = Field(description="Currently active users")
    total_sessions: int = Field(description="Total sessions")
    completed_sessions: int = Field(description="Completed sessions")
    average_completion_rate: float = Field(description="Average completion rate")
    average_score: float = Field(description="Average score across all sessions")
    total_duration: float = Field(description="Total time in system")
    job_statistics: Dict[UUID, JobStatisticsDTO] = Field(description="Statistics by job")
    user_statistics: Dict[UUID, UserPerformanceDTO] = Field(description="Statistics by user")
    engagement_metrics: EngagementMetricsDTO = Field(description="Overall engagement metrics")
    period_start: datetime = Field(description="Start of reporting period")
    period_end: datetime = Field(description="End of reporting period") 