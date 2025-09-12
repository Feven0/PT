"""
Task Management Models

This module defines Pydantic models for task management API endpoints,
including enums for task status and type options.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

from api.services.celery.task_tracker import TaskStatus, TaskType


class TaskStatusEnum(str, Enum):
    """Enum for task status options"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskTypeEnum(str, Enum):
    """Enum for task type options"""
    AUDIO_PROCESSING = "audio_processing"
    DUAL_AUDIO_PROCESSING = "dual_audio_processing"
    TRANSCRIPTION = "transcription"
    EVALUATION = "evaluation"
    OVERALL_EVALUATION = "overall_evaluation"


class TargetType(str, Enum):
    """Enum for target types supported by the task tracker"""
    JOB_PROFILE = "job_profile_id"
    CHALLENGE = "challenge_id"
    SESSION = "session_id"
    ALL_USER = "all_user_id"


class MultiTargetRequest(BaseModel):
    """Request model for filtering tasks by multiple targets"""
    targets: Dict[Union[TargetType, str], int] = Field(
        ...,
        description="Dictionary of target types and their IDs. Can use enum values or arbitrary strings.",
        example={
            "job_profile": 123,
            "all_user": 456,
            "custom_target": 789
        }
    )
    
    class Config:
        json_encoders = {
            TargetType: lambda v: v.value
        }


class TaskResponse(BaseModel):
    """Response model for task data"""
    task_type: str
    target_type: str
    target_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    progress: int
    metadata: Dict[str, Any]
    all_targets: Dict[str, Any]


class TaskStatisticsResponse(BaseModel):
    """Response model for task statistics"""
    total_tasks: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_target_type: Dict[str, int]


class TaskStatusOptionsResponse(BaseModel):
    """Response model for available task status options"""
    statuses: List[str]
    descriptions: Dict[str, str]


class TaskTypeOptionsResponse(BaseModel):
    """Response model for available task type options"""
    types: List[str]
    descriptions: Dict[str, str]


# Status descriptions for better API documentation
TASK_STATUS_DESCRIPTIONS = {
    "pending": "Task is registered but not yet started",
    "processing": "Task is currently being executed",
    "completed": "Task has finished successfully",
    "failed": "Task encountered an error and failed",
    "cancelled": "Task was cancelled before completion"
}

# Task type descriptions for better API documentation
TASK_TYPE_DESCRIPTIONS = {
    "audio_processing": "Processing of single audio file uploads",
    "dual_audio_processing": "Processing of question and answer file pairs",
    "transcription": "Audio/video transcription tasks",
    "evaluation": "Interview evaluation and scoring",
    "overall_evaluation": "Overall performance evaluation and metrics"
} 