"""Chat API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from core.di import get_container
from services.chat.service import ChatService
from domain.models import ChatMessage, ChatSession


router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service() -> ChatService:
    """Get chat service instance."""
    container = get_container()
    return container.chat_service


@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatSession:
    """Create a new chat session."""
    return await chat_service.create_session()


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatSession:
    """Get chat session by ID."""
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_chat_messages(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> List[ChatMessage]:
    """Get messages for a chat session."""
    messages = await chat_service.get_messages(session_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return messages


@router.post("/sessions/{session_id}/messages", response_model=ChatMessage)
async def send_chat_message(
    session_id: str,
    message: ChatMessage,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatMessage:
    """Send a message in a chat session."""
    result = await chat_service.send_message(session_id, message)
    if result is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return result


@router.websocket("/ws/{session_id}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> None:
    """WebSocket endpoint for real-time chat."""
    try:
        await chat_service.handle_websocket(websocket, session_id)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        raise 