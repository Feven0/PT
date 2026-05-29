"""Consolidated analysis API endpoints."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path, WebSocket
from pydantic import BaseModel

from core.types.websocket import SocketEvent
from core.types.model import CoreBaseModel
from services.session.service import SessionManagementService
from services.interview.service import InterviewService
from services.analysis.service import AnalysisService
from ..dependencies import (
    get_session_service,
    get_interview_service,
    get_analysis_service,    
)
from ..models.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisMetricResponse,
    QuestionAnalysisResponse,
    SessionAnalysisResponse,
    AnalysisResultResponse,
    RealtimeAnalysisResponse,
    SentimentAnalysisResponse,
    TopicAnalysisResponse,
    EngagementAnalysisResponse,
    PerformanceAnalysisResponse,
    SessionSummaryResponse,
    RecommendationsResponse
)

router = APIRouter(prefix="/analysis", tags=["analysis"])

# REST Endpoints

@router.post("/sessions/{session_id}/analyze", response_model=AnalysisResponse)
async def analyze_session(
    session_id: str = Path(..., description="Session ID"),
    request: AnalysisRequest = None,
    session_service: SessionManagementService = Depends(get_session_service),
    interview_service: InterviewService = Depends(get_interview_service),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> AnalysisResponse:
    """Analyze a session."""
    try:
        # Get session type
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Process analysis based on session type
        if session.type == "interview":
            analysis = await interview_service.analyze_session(
                session_id=session_id,
                start_time=request.start_time if request else None,
                end_time=request.end_time if request else None
            )
        else:
            analysis = await session_service.analyze_session(
                session_id=session_id,
                start_time=request.start_time if request else None,
                end_time=request.end_time if request else None,
                analysis_type=request.analysis_type if request else "conversation"
            )
            
        return AnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}/analyses", response_model=List[AnalysisResponse])
async def get_session_analyses(
    session_id: str = Path(..., description="Session ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session_service: SessionManagementService = Depends(get_session_service),
    interview_service: InterviewService = Depends(get_interview_service),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> List[AnalysisResponse]:
    """Get analyses for a session."""
    try:
        # Get session type
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Get analyses based on session type
        if session.type == "interview":
            analyses = await interview_service.get_session_analyses(
                session_id=session_id,
                limit=limit,
                offset=offset
            )
        else:
            analyses = await session_service.get_session_analyses(
                session_id=session_id,
                limit=limit,
                offset=offset
            )
            
        return [AnalysisResponse(**analysis) for analysis in analyses]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}/analysis/realtime", response_model=RealtimeAnalysisResponse)
async def get_realtime_analysis(
    session_id: str = Path(..., description="Session ID"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> RealtimeAnalysisResponse:
    """Get real-time analysis of the session."""
    try:
        analysis = await analysis_service.get_realtime_analysis(session_id)
        return RealtimeAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/analysis/sentiment", response_model=SentimentAnalysisResponse)
async def get_sentiment_analysis(
    session_id: str = Path(..., description="Session ID"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> SentimentAnalysisResponse:
    """Get sentiment analysis of the session."""
    try:
        analysis = await analysis_service.get_sentiment_analysis(session_id)
        return SentimentAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/analysis/topics", response_model=TopicAnalysisResponse)
async def get_topic_analysis(
    session_id: str = Path(..., description="Session ID"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> TopicAnalysisResponse:
    """Get topic analysis of the session."""
    try:
        analysis = await analysis_service.get_topic_analysis(session_id)
        return TopicAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/analysis/engagement", response_model=EngagementAnalysisResponse)
async def get_engagement_analysis(
    session_id: str = Path(..., description="Session ID"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> EngagementAnalysisResponse:
    """Get engagement analysis of the session."""
    try:
        analysis = await analysis_service.get_engagement_analysis(session_id)
        return EngagementAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/analysis/performance", response_model=PerformanceAnalysisResponse)
async def get_performance_analysis(
    session_id: str = Path(..., description="Session ID"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> PerformanceAnalysisResponse:
    """Get performance analysis of the session."""
    try:
        analysis = await analysis_service.get_performance_analysis(session_id)
        return PerformanceAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/overview", response_model=Dict[str, Any])
async def get_admin_overview(
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Get administrative overview of all interviews."""
    try:
        return await analysis_service.get_admin_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

