from pydantic import BaseModel, Field
from typing import List, Union, Any, Dict

class UpdateSessionModeResponse(BaseModel):
    sessionId: int = Field(..., description="Session ID")
    mode: str = Field(..., description="Session mode")
    status: int = Field(..., description="Status of the update")
    message: str = Field(..., description="Result message")
    class Config:
        schema_extra = {
            "example": {
                "sessionId": 1942,
                "mode": "Chat",
                "status": 200,
                "message": "Session mode updated successfully."
            }
        }

class ErrorResponse(BaseModel):
    error: str = Field(..., example="Health check failed: ...")

class CreateUserSessionResponse(BaseModel):
    id: int | str = Field(..., description="Session ID")
    status: str = Field(..., description="Session status")
    mode: str = Field(..., description="Session mode")
    user_profile_id: int | str = Field(..., description="User profile ID")
    job_profile_id: int | str = Field(..., description="Job profile ID")
    template_id: int | str = Field(..., description="Template ID")
    challenge_id: int | str = Field(..., description="Challenge ID")
    exist: bool = Field(..., description="Whether the session already exists")
    class Config:
        schema_extra = {
            "example": {
                "id": 1234,
                "status": "Incomplete",
                "mode": "Chat",
                "user_profile_id": 5678,
                "job_profile_id": 91011,
                "template_id": 1213,
                "challenge_id": 1415,
                "exist": False
            }
        }

class ClarifyResponse(BaseModel):
    clarification: str = Field(..., description="The clarified question or answer.")
    class Config:
        schema_extra = {
            "example": {
                "clarification": "Can you explain what you mean by 'project scope'?"
            }
        }

class DeleteSessionResponse(BaseModel):
    success: str = Field(..., description="Success message for session deletion.")
    class Config:
        schema_extra = {
            "example": {
                "success": "Session deleted successfully"
            }
        }

class CloseSessionResponse(BaseModel):
    success: str | dict = Field(..., description="Success message or evaluation results for session closure.")
    class Config:
        schema_extra = {
            "example": {
                "success": {
                    "evaluation": "Session closed and evaluated successfully.",
                    "metrics": {"score": 95, "feedback": "Excellent performance."}
                }
            }
        }

class SessionOverallProgressResponse(BaseModel):
    progress: dict = Field(..., description="Overall progress metrics for the session/job.")
    class Config:
        schema_extra = {
            "example": {
                "progress": {
                    "score": 87,
                    "completed_questions": 10,
                    "total_questions": 12,
                    "feedback": "Good progress, keep going!"
                }
            }
        }

class AllStatProgressResponse(BaseModel):
    progress: dict = Field(..., description="Overall progress metrics for all jobs for a user.")
    class Config:
        schema_extra = {
            "example": {
                "progress": {
                    "average_score": 85,
                    "completed_jobs": 5,
                    "total_jobs": 7,
                    "feedback": "Great progress across all jobs!"
                }
            }
        }

class EngagementJobsStatusResponse(BaseModel):
    all_user_id: Union[int, str] = Field(..., description="User identifier")
    jobs: List[Any] = Field(..., description="List of job engagement summaries")
    cursor: List[Any] = Field(..., description="Pagination cursor")
    status: int = Field(..., description="Status code")
    message: str = Field(..., description="Status or error message")
    class Config:
        schema_extra = {
            "example": {
                "all_user_id": 123,
                "jobs": [
                    {"job_id": 1, "engagement": "active"},
                    {"job_id": 2, "engagement": "inactive"}
                ],
                "cursor": [],
                "status": 200,
                "message": ""
            }
        }

class EngagementStatusResponse(BaseModel):
    all_user_id: Union[int, str] = Field(..., description="User identifier")
    jobs: List[Any] = Field(..., description="List of job engagement summaries")
    cursor: List[Any] = Field(..., description="Pagination cursor")
    status: int = Field(..., description="Status code")
    message: str = Field(..., description="Status or error message")
    class Config:
        schema_extra = {
            "example": {
                "all_user_id": 123,
                "jobs": [
                    {"job_id": 1, "engagement": "active"},
                    {"job_id": 2, "engagement": "inactive"}
                ],
                "cursor": [],
                "status": 200,
                "message": ""
            }
        }

class EngagementChallengeStatusResponse(BaseModel):
    all_user_id: Union[int, str] = Field(..., description="User identifier")
    challenges: List[Any] = Field(..., description="List of challenge engagement summaries")
    status: int = Field(..., description="Status code")
    message: str = Field(..., description="Status or error message")
    class Config:
        schema_extra = {
            "example": {
                "all_user_id": 123,
                "challenges": [
                    {"challenge_id": 1, "engagement": "active"},
                    {"challenge_id": 2, "engagement": "inactive"}
                ],
                "status": 200,
                "message": ""
            }
        }

class FetchUserSessionResponse(BaseModel):
    data: Any = Field(..., description="User session data (list or dict)")
    class Config:
        schema_extra = {
            "example": {
                "data": [
                    {"session_id": 1, "status": "active"},
                    {"session_id": 2, "status": "completed"}
                ]
            }
        }

class ChatHistoryMessage(BaseModel):
    content: Dict[str, Any] = Field(..., description="Message content and metadata.")
    # Allow extra fields for flexibility
    class Config:
        extra = "allow"

class FetchChatHistoryDictResponse(BaseModel):
    count: int = Field(..., description="Number of messages.")
    total: List[ChatHistoryMessage] = Field(..., description="List of chat messages.")
    class Config:
        schema_extra = {
            "example": {
                "count": 2,
                "total": [
                    {
                        "content": {
                            "time_limit": "",
                            "time_taken": "null",
                            "full_response": "Tell me a little bit about your self?",
                            "realtime_evaluation": None
                        },
                        "sender": "user",
                        "timestamp": "2024-07-07T12:00:00Z"
                    },
                    {
                        "content": {
                            "time_limit": "",
                            "time_taken": "null",
                            "full_response": "I'm a software engineer...",
                            "realtime_evaluation": None
                        },
                        "sender": "bot",
                        "timestamp": "2024-07-07T12:00:01Z"
                    }
                ]
            }
        }

class FetchUserSessionDictResponse(BaseModel):
    count: int = Field(..., description="Number of sessions.")
    total: List[Dict[str, Any]] = Field(..., description="List of session data objects.")
    class Config:
        extra = "allow"
        schema_extra = {
            "example": {
                "count": 1,
                "total": [
                    {
                        "id": 123,
                        "user_profile_id": 456,
                        "job_profile_id": 789,
                        "status": "active",
                        "created_at": "2024-07-07T12:00:00Z",
                        # ... other session fields ...
                    }
                ]
            }
        }

class UserObserver(BaseModel):
    observer_id: int = Field(..., description="Unique ID of the observer record")
    session_id: int = Field(..., description="ID of the session this observer is linked to")
    observer_type: str = Field(..., description="Type of observer (e.g., 'admin', 'user')")
    created_at: str = Field(..., description="Timestamp when the observer record was created")
    # Add other known fields here, or use extra = 'allow' for flexibility
    class Config:
        extra = "allow"
        schema_extra = {
            "example": {
                "observer_id": 1,
                "session_id": 2070,
                "observer_type": "admin",
                "created_at": "2024-07-07T12:00:00Z"
            }
        }

class FetchUserAllObserverDictResponse(BaseModel):
    count: int = Field(..., description="Number of observer records.")
    total: List[UserObserver] = Field(..., description="List of observer data objects.")
    class Config:
        schema_extra = {
            "example": {
                "count": 2,
                "total": [
                    {
                        "observer_id": 1,
                        "session_id": 2070,
                        "observer_type": "admin",
                        "created_at": "2024-07-07T12:00:00Z"
                    },
                    {
                        "observer_id": 2,
                        "session_id": 2070,
                        "observer_type": "user",
                        "created_at": "2024-07-07T12:05:00Z"
                    }
                ]
            }
        } 


def sanitize_create_user_session_response(data):
    return {
        "id": data.get("id") or "",
        "status": str(data.get("status") or "Incomplete"),
        "mode": str(data.get("mode") or ""),
        "user_profile_id": data.get("user_profile_id") or "",
        "job_profile_id": data.get("job_profile_id") or "",
        "template_id": data.get("template_id") or "",
        "challenge_id": data.get("challenge_id") or "",
    }
