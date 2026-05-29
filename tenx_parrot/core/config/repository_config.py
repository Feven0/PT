"""Repository configuration."""
from typing import Optional, Dict, Any
from pydantic import Field

from core.types.model import CoreBaseModel
from core.config.infrastructure_config import StorageInfrastructureConfig

class BaseRepositoryConfig(CoreBaseModel):
    """Base repository configuration."""
    enabled: bool = Field(default=True, description="Enable repository")
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    max_batch_size: int = Field(default=100, description="Maximum batch size")
    max_concurrent_operations: int = Field(default=10, description="Maximum concurrent operations")

class StorageRepositoryConfig(BaseRepositoryConfig):
    """Storage repository configuration."""
    infrastructure: Any = Field(default=None, description="Storage infrastructure configuration")
    primary_storage: str = Field(default="strapi", description="Primary storage provider")
    sync_storages: bool = Field(default=False, description="Sync between storage providers")
    max_file_size: int = Field(default=10485760, description="Maximum file size in bytes")
    allowed_extensions: Optional[list] = Field(default=None, description="Allowed file extensions")

class UserRepositoryConfig(BaseRepositoryConfig):
    """User repository configuration."""
    infrastructure: StorageInfrastructureConfig = Field(
        default_factory=StorageInfrastructureConfig,
        description="Storage configuration"
    )
    max_users: int = Field(default=1000, description="Maximum number of users")
    max_sessions_per_user: int = Field(default=5, description="Maximum sessions per user")
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")

class InterviewRepositoryConfig(BaseRepositoryConfig):
    """Interview repository configuration."""
    infrastructure: StorageInfrastructureConfig = Field(
        default_factory=StorageInfrastructureConfig,
        description="Storage configuration"
    )
    max_interviews: int = Field(default=1000, description="Maximum number of interviews")
    max_duration: int = Field(default=3600, description="Maximum interview duration in seconds")
    max_questions: int = Field(default=50, description="Maximum number of questions")
    recording_enabled: bool = Field(default=True, description="Enable interview recording")
    transcription_enabled: bool = Field(default=True, description="Enable interview transcription")
    storage_path: str = Field(default="interviews", description="Storage path for interviews")

class SessionRepositoryConfig(BaseRepositoryConfig):
    """Session repository configuration."""
    infrastructure: StorageInfrastructureConfig = Field(
        default_factory=StorageInfrastructureConfig,
        description="Storage configuration"
    )
    max_sessions: int = Field(default=1000, description="Maximum number of sessions")
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    cleanup_interval: int = Field(default=300, description="Cleanup interval in seconds")
    max_inactive_time: int = Field(default=1800, description="Maximum inactive time in seconds")
    storage_path: str = Field(default="sessions", description="Storage path for sessions")

class AdminRepositoryConfig(BaseRepositoryConfig):
    """Admin repository configuration."""
    infrastructure: StorageInfrastructureConfig = Field(
        default_factory=StorageInfrastructureConfig,
        description="Storage configuration"
    )
    max_admins: int = Field(default=100, description="Maximum number of admins")
    max_operations: int = Field(default=1000, description="Maximum number of operations")
    audit_enabled: bool = Field(default=True, description="Enable audit logging")
    audit_retention_days: int = Field(default=90, description="Audit log retention in days")
    storage_path: str = Field(default="admin", description="Storage path for admin data")

class AnalysisRepositoryConfig(BaseRepositoryConfig):
    """Analysis repository configuration."""
    infrastructure: StorageInfrastructureConfig = Field(
        default_factory=StorageInfrastructureConfig,
        description="Storage configuration"
    )
    max_analyses: int = Field(default=1000, description="Maximum number of analyses")
    max_batch_size: int = Field(default=100, description="Maximum batch size")
    storage_path: str = Field(default="analyses", description="Storage path for analyses")
    result_ttl: int = Field(default=86400, description="Result TTL in seconds")
    min_confidence: float = Field(default=0.7, description="Minimum confidence threshold") 