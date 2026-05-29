"""WebRTC routes."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from core.di import get_container
from services.webrtc import WebRTCService


router = APIRouter(prefix="/webrtc", tags=["WebRTC"])


def get_webrtc_service() -> WebRTCService:
    """Get WebRTC service instance."""
    container = get_container()
    return container.webrtc_service


@router.post("/offer")
async def create_webrtc_offer(
    session_id: str,
    service: WebRTCService = Depends(get_webrtc_service)
) -> Dict[str, Any]:
    """Create WebRTC offer for session."""
    try:
        return await service.create_connection(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ice-candidate")
async def handle_ice_candidate(
    session_id: str,
    candidate: Dict[str, Any],
    service: WebRTCService = Depends(get_webrtc_service)
):
    """Handle ICE candidate from peer."""
    try:
        await service.handle_ice_candidate(session_id, candidate)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connection-state")
async def handle_connection_state(
    session_id: str,
    state: str,
    service: WebRTCService = Depends(get_webrtc_service)
):
    """Handle connection state change."""
    try:
        await service.handle_connection_state(session_id, state)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ice-candidates/{session_id}")
async def get_ice_candidates(
    session_id: str,
    service: WebRTCService = Depends(get_webrtc_service)
) -> Dict[str, Any]:
    """Get gathered ICE candidates for session."""
    try:
        candidates = await service.get_ice_candidates(session_id)
        return {"candidates": list(candidates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/connection/{session_id}")
async def close_webrtc_connection(
    session_id: str,
    service: WebRTCService = Depends(get_webrtc_service)
):
    """Close WebRTC connection."""
    try:
        await service.close_connection(session_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 