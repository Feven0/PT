"""WebSocket endpoints for interview functionality."""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import asyncio

from fastapi import APIRouter
from core.logging import BackendLogger
from core.types.websocket import (
    MessageEvent,
    SocketEvent,
    SocketEventData
)
from core.websocket.socketio_manager import SocketIOManager

from ..models.websocket import (
    InterviewChatRequest,
    InterviewChatResponse,
    AudioTranscriptionRequest,
    AudioTranscriptionResponse,
    AudioChatRequest,
    AudioChatResponse,
    SessionData
)
from ..dependencies import (
    get_session_service,
    get_audio_manager,
    get_llm_manager,
    get_prompt_manager,
    get_cache_manager
)

logger = BackendLogger(__name__).get_logger()

# Get SocketIO manager instance
socketio_manager = SocketIOManager.get_instance()

@socketio_manager.server.on("interview chat")
async def handle_interview_chat(sid: str, data: Dict[str, Any]):
    """Handle text-based interview chat."""
    try:
        # Validate request data
        request = InterviewChatRequest(
            session_id=data.get('session_id'),
            response=data.get('response'),
            time_taken=data.get('time_taken'),
            job_profile_id=data.get('job_profile_id'),
            all_user_id=data.get('all_user_id')
        )
        
        # Get session
        session = socketio_manager.get_session_data(sid)
        if not session:
            return
            
        # Get services
        llm_manager = get_llm_manager()
        session_service = get_session_service()
        
        # Store user response if provided
        if request.response:
            await session_service.store_message(
                request.session_id,
                {
                    "type": "text",
                    "direction": "incoming",
                    "content": request.response,
                    "metadata": {
                        "time_taken": request.time_taken
                    }
                }
            )
        
        # Generate next question
        response = await llm_manager.process_message(
            request.response or '',
            request.session_id,
            context={
                "job_profile_id": request.job_profile_id,
                "user_id": request.all_user_id
            }
        )
        
        # Stream response chunks
        accumulated_message = ""
        for chunk in response.get("content", "").split():
            accumulated_message += chunk + " "
            await socketio_manager.emit(
                SocketEvent.INTERVIEW_CHAT,
                InterviewChatResponse(
                    content={"chunk_response": chunk},
                    status=None,
                    realtime_evaluation=None
                ).model_dump(),
                room=session["session_id"]
            )
            
        # Store assistant response
        await session_service.store_message(
            request.session_id,
            {
                "type": "text",
                "direction": "outgoing",
                "content": accumulated_message,
                "metadata": {
                    "processed_by": "llm"
                }
            }
        )
        
        # Generate and emit real-time evaluation
        if request.response:
            evaluation = await llm_manager.analyze_response(
                request.response,
                request.session_id
            )
            await socketio_manager.emit(
                SocketEvent.REALTIME,
                InterviewChatResponse(
                    content={
                        "realtime_evaluation": evaluation,
                        "full_response": accumulated_message
                    },
                    status=None,
                    realtime_evaluation=evaluation
                ).model_dump(),
                room=session["session_id"]
            )
            
    except Exception as e:
        logger.error(f"Error in interview chat: {str(e)}")
        await socketio_manager.emit(
            SocketEvent.ERROR,
            {"message": f"Error processing chat: {str(e)}"},
            room=session["session_id"] if session else None
        )

@socketio_manager.server.on("audio transcribe")
async def handle_audio_transcribe(sid: str, data: Dict[str, Any]):
    """Handle audio transcription."""
    try:
        # Validate request data
        request = AudioTranscriptionRequest(
            session_id=data.get('session_id'),
            audioblob=data.get('audioblob'),
            format=data.get('format', 'wav')
        )
        
        # Get session
        session = socketio_manager.get_session_data(sid)
        if not session:
            return
            
        # Get services
        audio_manager = get_audio_manager()
        
        # Transcribe audio
        transcription = await audio_manager.transcribe(
            request.audioblob,
            format=request.format
        )
        
        # Emit transcription result
        await socketio_manager.emit(
            SocketEvent.AUDIO_TRANSCRIBE,
            AudioTranscriptionResponse(
                query=transcription.get('text', ''),
                confidence=transcription.get('confidence', 1.0)
            ).model_dump(),
            room=session["session_id"]
        )
        
    except Exception as e:
        logger.error(f"Error in audio transcription: {str(e)}")
        await socketio_manager.emit(
            SocketEvent.ERROR,
            {"message": f"Error transcribing audio: {str(e)}"},
            room=session["session_id"] if session else None
        )

@socketio_manager.server.on("audio chat")
async def handle_audio_chat(sid: str, data: Dict[str, Any]):
    """Handle audio-based interview chat."""
    try:
        # Validate request data
        request = AudioChatRequest(
            session_id=data.get('session_id'),
            response=data.get('response'),
            time_taken=data.get('time_taken'),
            job_profile_id=data.get('job_profile_id'),
            all_user_id=data.get('all_user_id'),
            format=data.get('format', 'wav')
        )
        
        # Get session
        session = socketio_manager.get_session_data(sid)
        if not session:
            return
            
        # Get services
        audio_manager = get_audio_manager()
        llm_manager = get_llm_manager()
        session_service = get_session_service()
        
        # Process audio response if provided
        transcription = None
        if request.response:
            # Transcribe user audio
            transcription = await audio_manager.transcribe(
                request.response,
                format=request.format
            )
            
            # Store transcribed message
            await session_service.store_message(
                request.session_id,
                {
                    "type": "audio",
                    "direction": "incoming",
                    "audio_data": request.response,
                    "text_content": transcription.get('text', ''),
                    "metadata": {
                        "time_taken": request.time_taken,
                        "confidence": transcription.get('confidence', 1.0)
                    }
                }
            )
        
        # Generate next question
        response = await llm_manager.process_message(
            transcription.get('text', '') if transcription else '',
            request.session_id,
            context={
                "job_profile_id": request.job_profile_id,
                "user_id": request.all_user_id
            }
        )
        
        # Stream text response
        accumulated_message = ""
        for chunk in response.get("content", "").split():
            accumulated_message += chunk + " "
            await socketio_manager.emit(
                SocketEvent.AUDIO_TEXT_CHUNK,
                chunk,
                room=session["session_id"]
            )
            
        await socketio_manager.emit(
            SocketEvent.AUDIO_TEXT_CHUNK_DONE,
            room=session["session_id"]
        )
        
        # Synthesize and stream audio response
        audio_chunks = []
        for sentence in accumulated_message.split('.'):
            if sentence.strip():
                audio_data = await audio_manager.synthesize(
                    sentence.strip() + ".",
                    format=request.format
                )
                audio_chunks.append(audio_data)
                await socketio_manager.emit(
                    SocketEvent.AUDIO_CHUNK,
                    audio_data,
                    room=session["session_id"]
                )
            
        # Store assistant response
        await session_service.store_message(
            request.session_id,
            {
                "type": "audio",
                "direction": "outgoing",
                "audio_data": b"".join(audio_chunks),
                "text_content": accumulated_message,
                "metadata": {
                    "processed_by": "llm"
                }
            }
        )
        
        # Generate and emit real-time evaluation
        if request.response and transcription:
            evaluation = await llm_manager.analyze_response(
                transcription.get('text', ''),
                request.session_id
            )
            await socketio_manager.emit(
                SocketEvent.REALTIME,
                AudioChatResponse(
                    content={
                        "realtime_evaluation": evaluation,
                        "full_response": accumulated_message
                    },
                    status=None,
                    realtime_evaluation=evaluation,
                    audio_chunks=audio_chunks
                ).model_dump(),
                room=session["session_id"]
            )
            
    except Exception as e:
        logger.error(f"Error in audio chat: {str(e)}")
        await socketio_manager.emit(
            SocketEvent.ERROR,
            {"message": f"Error processing audio chat: {str(e)}"},
            room=session["session_id"] if session else None
        )
