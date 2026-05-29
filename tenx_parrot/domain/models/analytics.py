"""Analytics domain models."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID
from pydantic import Field, field_validator

from .base import BaseDomainModel


class TimeRange(str, Enum):
    """Time range for analytics."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"


class UserPerformance(BaseDomainModel):
    """User performance model."""
    user_id: UUID = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    total_sessions: int = Field(..., description="Total number of sessions")
    completed_sessions: int = Field(..., description="Number of completed sessions")
    average_score: float = Field(..., description="Average score across all sessions")
    total_duration: float = Field(..., description="Total time spent in sessions")
    strengths: List[str] = Field(default_factory=list, description="Areas of strength")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas needing improvement")
    job_performance: Dict[str, float] = Field(default_factory=dict, description="Performance by job type")

    @classmethod
    @field_validator('average_score', mode='before')
    def validate_score(cls, v):
        if not (0 <= v <= 100):
            raise ValueError('Score must be between 0 and 100')
        return v

    @classmethod
    @field_validator('completed_sessions', mode='before')
    def validate_completed(cls, v, values):
        if 'total_sessions' in values and v > values['total_sessions']:
            raise ValueError('Completed sessions cannot exceed total sessions')
        return v


class JobStatistics(BaseDomainModel):
    """Job statistics model."""
    job_id: UUID = Field(..., description="Job ID")
    title: str = Field(..., description="Job title")
    total_interviews: int = Field(..., description="Total interviews conducted")
    completed_interviews: int = Field(..., description="Completed interviews")
    average_duration: float = Field(..., description="Average interview duration")
    average_score: float = Field(..., description="Average interview score")
    completion_rate: float = Field(..., description="Interview completion rate")
    skill_distribution: Dict[str, float] = Field(default_factory=dict, description="Distribution of skills tested")
    difficulty_rating: float = Field(..., description="Average difficulty rating")

    @classmethod
    @field_validator('completion_rate', mode='before')
    def validate_rate(cls, v):
        if not (0 <= v <= 1):
            raise ValueError('Rate must be between 0 and 1')
        return v

    @classmethod
    @field_validator('difficulty_rating', mode='before')
    def validate_difficulty(cls, v):
        if not (1 <= v <= 5):
            raise ValueError('Difficulty must be between 1 and 5')
        return v

    @classmethod
    @field_validator('skill_distribution', mode='before')
    def validate_distribution(cls, v):
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # Allow for floating point imprecision
            raise ValueError('Skill distribution must sum to 1')
        return v


class EngagementMetrics(BaseDomainModel):
    """Engagement metrics model."""
    total_users: int = Field(..., description="Total registered users")
    active_users: int = Field(..., description="Active users in period")
    total_sessions: int = Field(..., description="Total sessions conducted")
    average_sessions_per_user: float = Field(..., description="Average sessions per user")
    completion_rate: float = Field(..., description="Overall completion rate")
    average_duration: float = Field(..., description="Average session duration")
    engagement_by_job: Dict[str, float] = Field(default_factory=dict, description="Engagement metrics by job")
    user_retention: float = Field(..., description="User retention rate")

    @classmethod
    @field_validator('active_users', mode='before')
    def validate_active(cls, v, values):
        if 'total_users' in values and v > values['total_users']:
            raise ValueError('Active users cannot exceed total users')
        return v

    @classmethod
    @field_validator('user_retention', mode='before')
    def validate_retention(cls, v):
        if not (0 <= v <= 1):
            raise ValueError('Retention rate must be between 0 and 1')
        return v


class AdminAnalytics(BaseDomainModel):
    """Administrative analytics model."""
    time_range: TimeRange = Field(..., description="Time range for analytics")
    period_start: datetime = Field(..., description="Start of analysis period")
    period_end: datetime = Field(..., description="End of analysis period")
    total_users: int = Field(..., description="Total users in system")
    active_users: int = Field(..., description="Currently active users")
    total_sessions: int = Field(..., description="Total sessions")
    completed_sessions: int = Field(..., description="Completed sessions")
    average_completion_rate: float = Field(..., description="Average completion rate")
    average_score: float = Field(..., description="Average score across all sessions")
    total_duration: float = Field(..., description="Total time in system")
    job_statistics: Dict[UUID, JobStatistics] = Field(default_factory=dict, description="Statistics by job")
    user_statistics: Dict[UUID, UserPerformance] = Field(default_factory=dict, description="Statistics by user")
    engagement_metrics: EngagementMetrics = Field(..., description="Overall engagement metrics")

    @classmethod
    @field_validator('period_end', mode='before')
    def validate_period(cls, v, values):
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError('End period must be after start period')
        return v

    def is_period_valid(self) -> bool:
        """Check if the analysis period is valid."""
        if self.time_range == TimeRange.CUSTOM:
            return True
            
        max_durations = {
            TimeRange.DAY: timedelta(days=1),
            TimeRange.WEEK: timedelta(days=7),
            TimeRange.MONTH: timedelta(days=31),
            TimeRange.QUARTER: timedelta(days=92),
            TimeRange.YEAR: timedelta(days=366)
        }
        
        return (self.period_end - self.period_start) <= max_durations[self.time_range] 