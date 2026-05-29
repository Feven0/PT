"""V2 API dependencies."""
from typing import Optional, Dict, Any
from fastapi import Depends

from core.di import get_container
from services.session.service import SessionManagementService
from core.llm.audio.manager import AudioManager
from core.llm.client import LLMClient as LLMManager
from core.prompt.manager import PromptManager
from core.cache.manager import CacheManager
from services.analysis import AnalysisService
from repositories.prompt import PromptRepository

from core.alert.manager import AlertManager
from core.session.manager import SessionManager as CoreSessionManager
from core.cache.manager import CacheManager

from core.llm.audio.manager import AudioManager
from core.llm.chain.manager import ChainManager
from core.prompt.manager import PromptManager

from core.llm.client import LLMClient
from infrastructure.strapi.client import StrapiClient
from infrastructure.weaviate.client import WeaviateInfrastructureClient
from infrastructure.gdrive.client import GDriveClient
from infrastructure.aws.s3_client import S3Client
from infrastructure.storage.client import StorageInfrastructureClient

from repositories.user import UserRepository
from repositories.interview import InterviewRepository
from repositories.session import SessionRepository
from repositories.storage import StorageRepository
from repositories.analysis import AnalysisRepository
from repositories.admin import AdminRepository
from repositories.observer import ObserverRepository
from repositories.overall_observer import OverallObserverRepository
from repositories.prompt import PromptRepository
from repositories.llm_metrics import LLMMetricsRepository

from services.user import UserService
from services.chat.service import ChatService
from services.interview.service import InterviewService
from services.storage import StorageService
from services.analysis import AnalysisService
from services.webrtc import WebRTCService
from services.session.service import SessionManagementService
from services.llm.interview.service import InterviewLLMService
from services.llm.chat.service import ChatLLMService
from services.admin.service import AdminService
from services.llm_metrics import LLMMetricsService
from core.websocket.socketio_manager import SocketIOManager

def get_session_service() -> SessionManagementService:
    """Get session service instance.
    
    Returns:
        Session management service instance
    """
    container = get_container()
    return container.session_service

def get_audio_manager() -> AudioManager:
    """Get audio manager instance."""
    container = get_container()
    return container.audio_manager

def get_llm_manager() -> LLMManager:
    """Get LLM manager instance."""
    container = get_container()
    return container.llm_manager

def get_prompt_manager() -> PromptManager:
    """Get prompt manager instance."""
    container = get_container()
    return container.prompt_manager


def get_chain_manager() -> ChainManager:
    """Get chain manager instance."""
    container = get_container()
    return container.chain_manager


def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    container = get_container()
    return container.cache_manager

def get_analysis_service() -> AnalysisService:
    """Get analysis service instance."""
    container = get_container()
    return container.analysis_service

def get_prompt_repository() -> PromptRepository:
    """Get prompt repository instance."""
    container = get_container()
    return container.prompt_repository


def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    container = get_container()
    return container.user_repository

def get_interview_repository() -> InterviewRepository:
    """Get interview repository instance."""
    container = get_container()
    return container.interview_repository

def get_session_repository() -> SessionRepository:
    """Get session repository instance."""
    container = get_container()
    return container.session_repository

def get_storage_repository() -> StorageRepository:
    """Get storage repository instance."""
    container = get_container()
    return container.storage_repository

def get_analysis_repository() -> AnalysisRepository:
    """Get analysis repository instance."""
    container = get_container()
    return container.analysis_repository

def get_admin_repository() -> AdminRepository:
    """Get admin repository instance."""
    container = get_container()
    return container.admin_repository

def get_observer_repository() -> ObserverRepository:
    """Get observer repository instance."""
    container = get_container()
    return container.observer_repository

def get_overall_observer_repository() -> OverallObserverRepository:
    """Get overall observer repository instance."""
    container = get_container()
    return container.overall_observer_repository

def get_storage_service() -> StorageService:
    """Get storage service instance."""
    container = get_container()
    return container.storage_service

def get_socketio_application() -> SocketIOManager:
    """Get socketio application instance."""
    container = get_container()
    return container.socketio_manager


def get_interview_service() -> InterviewService:
    """Get interview service instance."""
    container = get_container()
    return container.interview_service

def get_chat_service() -> ChatService:
    """Get chat service instance."""
    container = get_container()
    return container.chat_service

def get_interview_llm_service() -> InterviewLLMService:
    """Get interview LLM service instance."""
    container = get_container()
    return container.interview_llm_service

def get_chat_llm_service() -> ChatLLMService:
    """Get chat LLM service instance."""
    container = get_container()
    return container.chat_llm_service



    
    