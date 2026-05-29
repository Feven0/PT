"""Interview management API endpoints."""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel

from core.types.interview import (
    InterviewFlow,
    InterviewSession,
    InterviewResponse,
    InterviewState,
    InterviewType
)
from services.interview.service import InterviewService
from services.llm.interview.service import InterviewLLMService
from ..dependencies import get_interview_service, get_interview_llm_service

router = APIRouter(prefix="/interviews", tags=["interviews"])

class CreateFlowRequest(BaseModel):
    """Request model for creating an interview flow."""
    title: str
    description: str
    type: InterviewType
    steps: List[Dict[str, Any]]
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

# Flow Management Endpoints
@router.post("/flows", response_model=InterviewFlow)
async def create_flow(
    request: CreateFlowRequest,
    interview_service: InterviewService = Depends(get_interview_service)
) -> InterviewFlow:
    """Create a new interview flow."""
    try:
        return await interview_service.create_flow(
            title=request.title,
            description=request.description,
            type=request.type,
            steps=request.steps,
            settings=request.settings,
            metadata=request.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/flows", response_model=List[InterviewFlow])
async def list_flows(
    type: Optional[InterviewType] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    interview_service: InterviewService = Depends(get_interview_service)
) -> List[InterviewFlow]:
    """List interview flows."""
    try:
        return await interview_service.list_flows(
            type=type,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/flows/{flow_id}", response_model=InterviewFlow)
async def get_flow(
    flow_id: str = Path(..., description="Interview flow ID"),
    interview_service: InterviewService = Depends(get_interview_service)
) -> InterviewFlow:
    """Get interview flow by ID."""
    try:
        flow = await interview_service.get_flow(flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        return flow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Interview-specific Session Endpoints
@router.get("/sessions/{session_id}/responses", response_model=List[InterviewResponse])
async def list_responses(
    session_id: str = Path(..., description="Interview session ID"),
    interview_service: InterviewService = Depends(get_interview_service)
) -> List[InterviewResponse]:
    """List responses for an interview session."""
    try:
        return await interview_service.list_responses(session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Note: Session management endpoints have been moved to /v2/sessions
# Use the following endpoints for session management:
# - POST /v2/sessions - Create new session (including interview sessions)
# - GET /v2/sessions/{session_id} - Get session details
# - POST /v2/sessions/{session_id}/state - Update session state
# - GET /v2/sessions/{session_id}/progress - Get session progress



# @router.post("/{session_id}/observers")
# async def create_session_observer(
#     session_id: str,
#     request: CreateObserverRequest,
#     interview_service: InterviewLLMService = Depends(get_interview_llm_service)
# ):
#     """Create session observer."""
#     observer = await interview_service.create_session_observer(
#         session_id=session_id,
#         observer_type=request.type,
#         config=request.config
#     )
#     return observer

# @router.get("/{session_id}/observations")
# async def get_session_observations(
#     session_id: str,
#     observer_id: Optional[str] = None,
#     limit: Optional[int] = None,
#     offset: Optional[int] = None,
#     interview_service: InterviewLLMService = Depends(get_interview_llm_service)
# ):
#     """Get session observations."""
#     observations = await interview_service.get_session_observations(
#         session_id=session_id,
#         observer_id=observer_id,
#         limit=limit,
#         offset=offset
#     )
#     return observations

# @router.post("/{session_id}/summary")
# async def generate_session_summary(
#     session_id: str,
#     request: GenerateSummaryRequest,
#     interview_service: InterviewLLMService = Depends(get_interview_llm_service)
# ):
#     """Generate session summary."""
#     summary = await interview_service.generate_session_summary(
#         session_id=session_id,
#         summary_type=request.type
#     )
#     return summary 

# @router.post("/{session_id}/generate")
# async def generate_interview_response(
#     session_id: str,
#     request: GenerateRequest,
#     interview_service: InterviewLLMService = Depends(get_interview_llm_service)
# ):
#     """Generate interview response."""
#     response = await interview_service.generate_interview_response(
#         session_id=session_id,
#         user_message=request.message,
#         context=request.context
#     )
#     return response