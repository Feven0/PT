"""Session API routes."""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File

from core.types.session import SessionState, SessionType
from core.types.interview import InterviewSession, InterviewResponse
from services.llm.chat.service import ChatLLMService

from ..models.session import (
    CreateSessionRequest,
    ClarificationRequest,
    SessionResponse,
    SessionProgressResponse,
    ChatHistoryResponse,
    UserSessionsResponse,
    AdminOverviewResponse,
    UserPerformanceResponse,
    JobStatisticsResponse
)
from ..models.analysis import (
    RealtimeAnalysisResponse,
    SentimentAnalysisResponse,
    TopicAnalysisResponse,
    EngagementAnalysisResponse,
    PerformanceAnalysisResponse,
    SessionSummaryResponse,
    RecommendationsResponse
)
from ..dependencies import (
    get_session_service,
    get_interview_service,
    get_audio_manager,
    get_llm_manager,
    get_prompt_manager,
    get_cache_manager,
    get_chat_llm_service
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    session_service = Depends(get_session_service),
    interview_service = Depends(get_interview_service),
    prompt_manager = Depends(get_prompt_manager),
    llm_manager = Depends(get_llm_manager)
):
    """Create a new session."""
    try:
        # Get session initialization prompt
        prompt = await prompt_manager.get_prompt("session_init")
        
        # Generate initial context
        init_response = await llm_manager.generate_response(
            prompt=prompt,
            messages=[],
            config={"temperature": 0.7, "max_tokens": 500}
        )
        
        # Create session based on type
        if request.session_type == SessionType.INTERVIEW:
            if not request.flow_id:
                raise HTTPException(
                    status_code=400,
                    detail="flow_id is required for interview sessions"
                )
            session = await interview_service.create_session(
                trainee_id=request.user_id,
                flow_id=request.flow_id,
                metadata={
                    **(request.metadata or {}),
                    "init_context": init_response.dict()
                }
            )
        else:
            session = await session_service.create_session(
                user_id=request.user_id,
                session_type=request.session_type,
                metadata={
                    **(request.metadata or {}),
                    "init_context": init_response.dict()
                }
            )
        
        return SessionResponse(
            session_id=session.id,
            user_id=session.user_id,
            state=session.state.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session.metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    session_service = Depends(get_session_service),
    interview_service = Depends(get_interview_service)
):
    """Get session details."""
    try:
        # Try getting from session service first
        session = await session_service.get_session(session_id)
        if not session:
            # Try interview service
            session = await interview_service.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            session_id=session.id,
            user_id=session.user_id,
            state=session.state.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/state", response_model=SessionResponse)
async def update_session_state(
    session_id: str,
    state: SessionState,
    session_service = Depends(get_session_service),
    interview_service = Depends(get_interview_service)
):
    """Update session state (pause, resume, complete, etc.)."""
    try:
        # Try getting from session service first
        session = await session_service.get_session(session_id)
        if session:
            success = await session_service.update_session_state(
                session_id=session_id,
                state=state
            )
        else:
            # Try interview service
            session = await interview_service.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            success = await interview_service.update_session_state(
                session_id=session_id,
                state=state
            )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to update session state"
            )
            
        # Get updated session
        updated_session = await get_session(
            session_id,
            session_service,
            interview_service
        )
        return updated_session
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/speech-to-text")
async def speech_to_text(
    session_id: str,
    audio_file: UploadFile = File(...),
    audio_manager = Depends(get_audio_manager),
    session_service = Depends(get_session_service)
):
    """Convert speech audio to text."""
    try:
        # Validate session
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
            
        # Read audio data
        audio_data = await audio_file.read()
        
        # Configure audio processing
        audio_config = dict(
            sample_rate=16000,  # Default values
            channels=1,
            format="wav",
            language="en"
        )
        
        # Process audio
        result = await audio_manager.transcribe(
            audio_data=audio_data,
            #config=audio_config
        )
        
        return {
            "text": result.text,
            "confidence": result.confidence,
            "metadata": result.metadata
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process audio: {str(e)}"
        )

@router.post("/{session_id}/clarify")
async def clarify_question(
    session_id: str,
    request: ClarificationRequest,
    prompt_manager = Depends(get_prompt_manager),
    llm_manager = Depends(get_llm_manager),
    session_service = Depends(get_session_service)
):
    """Get clarification for a question."""
    try:
        # Validate session
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
            
        # Get clarification prompt
        prompt = await prompt_manager.get_prompt("question_clarification")
        
        llm_config = dict(
            temperature=0.7,
            max_tokens=500
        )

        # Generate clarification
        response = await llm_manager.generate_response(
            prompt=prompt,
            messages=[{"role": "user", "content": request.question}],
            context=request.context,
            #config=llm_config
        )
        
        return {
            "clarification": response.text,
            "confidence": response.confidence,
            "metadata": response.metadata
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clarify question: {str(e)}"
        )

@router.post("/{session_id}/close")
async def close_session(
    session_id: str,
    session_service = Depends(get_session_service),
    prompt_manager = Depends(get_prompt_manager),
    llm_manager = Depends(get_llm_manager)
):
    """Close an interview session."""
    try:
        # Get session
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
            
        # Get session summary prompt
        prompt = await prompt_manager.get_prompt("session_summary")
        
        llm_config = dict(
            temperature=0.7,
            max_tokens=1000
        )

        # Generate session summary
        summary = await llm_manager.generate_response(
            prompt=prompt,
            messages=[],  # Add relevant session history here
            #config=llm_config
        )
        
        # Update session state
        session.state.status = SessionState.CLOSED
        session.state.progress = 1.0
        session.state.last_activity = datetime.now(timezone.utc)
        session.updated_at = datetime.now(timezone.utc)
        session.metadata["summary"] = summary.dict()
        
        # Store updated session
        await session_service.update_session(session_id, session)
        
        return SessionResponse(
            session_id=session.id,
            user_id=session.user_id,
            state=session.state.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session.metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to close session: {str(e)}"
        )

@router.get("/{session_id}/progress", response_model=SessionProgressResponse)
async def get_session_progress(
    session_id: str,
    session_service = Depends(get_session_service)
):
    """Get session progress."""
    try:
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
            
        return SessionProgressResponse(
            session_id=session.id,
            progress=session.state.progress,
            state=session.state.status,
            last_activity=session.state.last_activity,
            metrics=session.data.get("metrics", {})
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session progress: {str(e)}"
        )


# # Update route handlers to use the new service
# @router.post("/{session_id}/generate")
# async def generate_chat_response(
#     session_id: str,
#     request: GenerateRequest,
#     chat_service: ChatLLMService = Depends(get_chat_llm_service)
# ):
#     """Generate chat response."""
#     response = await chat_service.generate_chat_response(
#         session_id=session_id,
#         user_message=request.message,
#         context=request.context
#     )
#     return response

@router.get("/{session_id}/chat-history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    cache_manager = Depends(get_cache_manager)
):
    """Get session chat history."""
    try:
        # Get chat history from cache
        history = await cache_manager.get(f"chat_context:{session_id}")
        if not history:
            return ChatHistoryResponse()
            
        return ChatHistoryResponse(**history)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get chat history: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=UserSessionsResponse)
async def get_user_sessions(
    user_id: str,
    session_service = Depends(get_session_service)
):
    """Get user's sessions."""
    try:
        sessions = await session_service.get_user_sessions(user_id)
        
        return UserSessionsResponse(
            sessions=[
                SessionResponse(
                    session_id=session.id,
                    user_id=session.user_id,
                    state=session.state.status,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    metadata=session.metadata
                )
                for session in sessions
            ],
            total=len(sessions),
            has_more=False  # Implement pagination if needed
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user sessions: {str(e)}"
        )

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    session_service = Depends(get_session_service)
) -> Dict[str, str]:
    """Delete an interview session."""
    try:
        await session_service.delete_session(session_id)
        return {"status": "success", "message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/overview", response_model=AdminOverviewResponse)
async def get_admin_overview(
    session_service = Depends(get_session_service)
) -> AdminOverviewResponse:
    """Get admin overview statistics."""
    try:
        return await session_service.get_admin_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/users", response_model=List[UserPerformanceResponse])
async def get_admin_users_data(
    session_service = Depends(get_session_service)
) -> List[UserPerformanceResponse]:
    """Get all users performance data."""
    try:
        return await session_service.get_users_performance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/jobs", response_model=List[JobStatisticsResponse])
async def get_admin_jobs_data(
    session_service = Depends(get_session_service)
) -> List[JobStatisticsResponse]:
    """Get all jobs statistics."""
    try:
        return await session_service.get_jobs_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/performance", response_model=UserPerformanceResponse)
async def get_user_performance(
    user_id: str,
    session_service = Depends(get_session_service)
) -> UserPerformanceResponse:
    """Get user performance metrics."""
    try:
        return await session_service.get_user_performance(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/observers", response_model=List[Dict[str, Any]])
async def get_user_observers(
    user_id: str,
    session_service = Depends(get_session_service)
) -> List[Dict[str, Any]]:
    """Get all observers for a user."""
    try:
        return await session_service.get_user_observers(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/observers", response_model=List[Dict[str, Any]])
async def get_session_observers(
    session_id: str,
    session_service = Depends(get_session_service)
) -> List[Dict[str, Any]]:
    """Get observers for a specific session."""
    try:
        return await session_service.get_session_observers(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job/{job_id}/statistics", response_model=JobStatisticsResponse)
async def get_job_statistics(
    job_id: str,
    session_service = Depends(get_session_service)
) -> JobStatisticsResponse:
    """Get statistics for a specific job."""
    try:
        return await session_service.get_job_statistics(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/engagement/{user_id}", response_model=Dict[str, Any])
async def get_engagement_status(
    user_id: str,
    session_service = Depends(get_session_service)
) -> Dict[str, Any]:
    """Get user engagement status across jobs."""
    try:
        return await session_service.get_engagement_status(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/analysis/realtime", response_model=RealtimeAnalysisResponse)
async def get_realtime_analysis(
    session_id: str,
    session_service = Depends(get_session_service)
) -> RealtimeAnalysisResponse:
    """Get real-time analysis of the session."""
    try:
        return await session_service.get_realtime_analysis(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/analysis/sentiment", response_model=SentimentAnalysisResponse)
async def get_sentiment_analysis(
    session_id: str,
    session_service = Depends(get_session_service)
) -> SentimentAnalysisResponse:
    """Get sentiment analysis of the session."""
    try:
        return await session_service.get_sentiment_analysis(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/analysis/topics", response_model=TopicAnalysisResponse)
async def get_topic_analysis(
    session_id: str,
    session_service = Depends(get_session_service)
) -> TopicAnalysisResponse:
    """Get topic analysis of the session."""
    try:
        return await session_service.get_topic_analysis(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/analysis/engagement", response_model=EngagementAnalysisResponse)
async def get_engagement_analysis(
    session_id: str,
    session_service = Depends(get_session_service)
) -> EngagementAnalysisResponse:
    """Get engagement analysis of the session."""
    try:
        return await session_service.get_engagement_analysis(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/analysis/performance", response_model=PerformanceAnalysisResponse)
async def get_performance_analysis(
    session_id: str,
    session_service = Depends(get_session_service)
) -> PerformanceAnalysisResponse:
    """Get performance analysis of the session."""
    try:
        return await session_service.get_performance_analysis(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/analysis/summary", response_model=SessionSummaryResponse)
async def get_session_summary(
    session_id: str,
    session_service = Depends(get_session_service)
) -> SessionSummaryResponse:
    """Get comprehensive summary of the session."""
    try:
        return await session_service.get_session_summary(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/analysis/recommendations", response_model=RecommendationsResponse)
async def get_session_recommendations(
    session_id: str,
    session_service = Depends(get_session_service)
) -> RecommendationsResponse:
    """Get recommendations based on session analysis."""
    try:
        return await session_service.get_session_recommendations(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 