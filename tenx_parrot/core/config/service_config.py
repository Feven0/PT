"""Service configuration."""
from typing import Optional, List, Dict, Any
from pydantic import Field, model_validator

from core.types.model import CoreBaseModel

class BaseServiceConfig(CoreBaseModel):
    """Base service configuration."""
    enabled: bool = Field(default=True, description="Enable service")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    timeout: float = Field(default=30.0, description="Operation timeout in seconds")
    max_concurrent_operations: int = Field(default=10, description="Maximum concurrent operations")
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")

    @model_validator(mode="after")
    def validate_base_config(self) -> "BaseServiceConfig":
        """Validate base configuration."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay <= 0:
            raise ValueError("retry_delay must be positive")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_concurrent_operations <= 0:
            raise ValueError("max_concurrent_operations must be positive")
        if self.cache_ttl <= 0:
            raise ValueError("cache_ttl must be positive")
        return self

class StorageServiceConfig(BaseServiceConfig):
    """Storage service configuration."""
    max_file_size: int = Field(default=10485760, description="Maximum file size in bytes")
    allowed_extensions: List[str] = Field(default=["*"], description="Allowed file extensions")
    compression_enabled: bool = Field(default=True, description="Enable file compression")
    compression_level: int = Field(default=6, description="Compression level")
    chunk_size: int = Field(default=8192, description="Upload/download chunk size")

    @model_validator(mode="after")
    def validate_storage_config(self) -> "StorageServiceConfig":
        """Validate storage configuration."""
        if self.max_file_size <= 0:
            raise ValueError("max_file_size must be positive")
        if not 0 <= self.compression_level <= 9:
            raise ValueError("compression_level must be between 0 and 9")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        return self

class SessionServiceConfig(BaseServiceConfig):
    """Session service configuration."""
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    max_sessions_per_user: int = Field(default=5, description="Maximum concurrent sessions per user")
    cleanup_interval: int = Field(default=300, description="Session cleanup interval in seconds")
    heartbeat_interval: int = Field(default=30, description="Session heartbeat interval in seconds")

    @model_validator(mode="after")
    def validate_session_config(self) -> "SessionServiceConfig":
        """Validate session configuration."""
        if self.session_timeout <= 0:
            raise ValueError("session_timeout must be positive")
        if self.max_sessions_per_user <= 0:
            raise ValueError("max_sessions_per_user must be positive")
        if self.cleanup_interval <= 0:
            raise ValueError("cleanup_interval must be positive")
        if self.heartbeat_interval <= 0:
            raise ValueError("heartbeat_interval must be positive")
        if self.heartbeat_interval >= self.session_timeout:
            raise ValueError("heartbeat_interval must be less than session_timeout")
        return self

class ChatServiceConfig(BaseServiceConfig):
    """Chat service configuration."""
    max_message_length: int = Field(default=4096, description="Maximum message length")
    history_size: int = Field(default=100, description="Maximum chat history size")
    typing_timeout: float = Field(default=5.0, description="Typing indicator timeout")
    presence_update_interval: float = Field(default=30.0, description="Presence update interval")

    @model_validator(mode="after")
    def validate_chat_config(self) -> "ChatServiceConfig":
        """Validate chat configuration."""
        if self.max_message_length <= 0:
            raise ValueError("max_message_length must be positive")
        if self.history_size <= 0:
            raise ValueError("history_size must be positive")
        if self.typing_timeout <= 0:
            raise ValueError("typing_timeout must be positive")
        if self.presence_update_interval <= 0:
            raise ValueError("presence_update_interval must be positive")
        return self

class InterviewServiceConfig(BaseServiceConfig):
    """Interview service configuration."""
    max_duration: int = Field(default=3600, description="Maximum interview duration in seconds")
    min_duration: int = Field(default=300, description="Minimum interview duration in seconds")
    recording_enabled: bool = Field(default=True, description="Enable interview recording")
    transcription_enabled: bool = Field(default=True, description="Enable interview transcription")
    max_participants: int = Field(default=2, description="Maximum number of participants")

    @model_validator(mode="after")
    def validate_interview_config(self) -> "InterviewServiceConfig":
        """Validate interview configuration."""
        if self.max_duration <= 0:
            raise ValueError("max_duration must be positive")
        if self.min_duration <= 0:
            raise ValueError("min_duration must be positive")
        if self.min_duration >= self.max_duration:
            raise ValueError("min_duration must be less than max_duration")
        if self.max_participants <= 1:
            raise ValueError("max_participants must be greater than 1")
        return self

class AnalysisServiceConfig(BaseServiceConfig):
    """Analysis service configuration."""
    batch_size: int = Field(default=100, description="Analysis batch size")
    max_concurrent_analyses: int = Field(default=5, description="Maximum concurrent analyses")
    result_ttl: int = Field(default=86400, description="Analysis result TTL in seconds")
    min_confidence: float = Field(default=0.7, description="Minimum confidence threshold")

    @model_validator(mode="after")
    def validate_analysis_config(self) -> "AnalysisServiceConfig":
        """Validate analysis configuration."""
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.max_concurrent_analyses <= 0:
            raise ValueError("max_concurrent_analyses must be positive")
        if self.result_ttl <= 0:
            raise ValueError("result_ttl must be positive")
        if not 0 <= self.min_confidence <= 1:
            raise ValueError("min_confidence must be between 0 and 1")
        return self

class AdminServiceConfig(BaseServiceConfig):
    """Admin service configuration."""
    audit_enabled: bool = Field(default=True, description="Enable audit logging")
    audit_retention_days: int = Field(default=90, description="Audit log retention in days")
    max_bulk_operations: int = Field(default=1000, description="Maximum bulk operation size")
    require_2fa: bool = Field(default=True, description="Require two-factor authentication")

    @model_validator(mode="after")
    def validate_admin_config(self) -> "AdminServiceConfig":
        """Validate admin configuration."""
        if self.audit_retention_days <= 0:
            raise ValueError("audit_retention_days must be positive")
        if self.max_bulk_operations <= 0:
            raise ValueError("max_bulk_operations must be positive")
        return self

class WebRTCConfig(BaseServiceConfig):
    """WebRTC service configuration."""
    ice_servers: List[Dict[str, Any]] = Field(
        default=[{"urls": ["stun:stun.l.google.com:19302"]}],
        description="ICE server configuration"
    )
    max_bandwidth: int = Field(default=1000000, description="Maximum bandwidth in bits per second")
    max_participants: int = Field(default=10, description="Maximum participants per session")
    connection_timeout: float = Field(default=30.0, description="Connection timeout in seconds")
    reconnect_attempts: int = Field(default=3, description="Number of reconnection attempts")
    dtls_role: str = Field(default="auto", description="DTLS role")
    ice_transport_policy: str = Field(default="all", description="ICE transport policy")
    max_packet_size: int = Field(default=1200, description="Maximum packet size in bytes")

    @model_validator(mode="after")
    def validate_webrtc_config(self) -> "WebRTCConfig":
        """Validate WebRTC configuration."""
        if not self.ice_servers:
            raise ValueError("At least one ICE server must be configured")
        if self.max_bandwidth <= 0:
            raise ValueError("max_bandwidth must be positive")
        if self.max_participants <= 0:
            raise ValueError("max_participants must be positive")
        if self.connection_timeout <= 0:
            raise ValueError("connection_timeout must be positive")
        if self.reconnect_attempts < 0:
            raise ValueError("reconnect_attempts must be non-negative")
        if self.dtls_role not in ["auto", "client", "server"]:
            raise ValueError("dtls_role must be one of: auto, client, server")
        if self.ice_transport_policy not in ["all", "relay"]:
            raise ValueError("ice_transport_policy must be one of: all, relay")
        if self.max_packet_size <= 0:
            raise ValueError("max_packet_size must be positive")
        return self

class WebSocketConfig(BaseServiceConfig):
    """WebSocket service configuration."""
    path: str = Field(default="/socket.io", description="WebSocket path")
    ping_interval: float = Field(default=30.0, description="Ping interval in seconds")
    ping_timeout: float = Field(default=10.0, description="Ping timeout in seconds")
    max_message_size: int = Field(default=1048576, description="Maximum message size in bytes")
    compression_level: int = Field(default=6, description="Compression level")
    max_connections: int = Field(default=1000, description="Maximum concurrent connections")
    connection_timeout: float = Field(default=30.0, description="Connection timeout in seconds")
    max_reconnect_attempts: int = Field(default=3, description="Number of reconnection attempts")    
    reconnect_delay: float = Field(default=1.0, description="Reconnection delay in seconds")
    heartbeat_interval: float = Field(default=30.0, description="Heartbeat interval in seconds")

    @model_validator(mode="after")
    def validate_websocket_config(self) -> "WebSocketConfig":
        """Validate WebSocket configuration."""
        if self.ping_interval <= 0:
            raise ValueError("ping_interval must be positive")
        if self.ping_timeout <= 0:
            raise ValueError("ping_timeout must be positive")
        if self.ping_timeout >= self.ping_interval:
            raise ValueError(f"ping_timeout={self.ping_timeout} must be less than ping_interval={self.ping_interval}")
        if self.max_message_size <= 0:
            raise ValueError("max_message_size must be positive")
        if self.connection_timeout <= 0:
            raise ValueError("connection_timeout must be positive")
        if self.max_reconnect_attempts < 0:
            raise ValueError("max_reconnect_attempts must be non-negative")  
        if self.reconnect_delay <= 0:
            raise ValueError("reconnect_delay must be positive")
        if not 0 <= self.compression_level <= 9:
            raise ValueError("compression_level must be between 0 and 9")
        if self.max_connections <= 0:
            raise ValueError("max_connections must be positive")
        if self.heartbeat_interval <= 0:
            raise ValueError("heartbeat_interval must be positive")
        return self

class CORSConfig(CoreBaseModel):
    """CORS configuration."""
    enabled: bool = Field(default=True, description="Enable CORS")
    allow_origins: List[str] = Field(
        default=["*"], 
        description="Allowed origins"
        )
    allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed methods"
    )
    allow_headers: List[str] = Field(
        default=["*"],
        description="Allowed headers"
    )
    allow_credentials: bool = Field(default=True, description="Allow credentials")
    max_age: int = Field(default=36000, description="Maximum age in seconds")

    def to_dict(self, core: bool = True) -> Dict[str, Any]:
        """Convert CORS configuration to dictionary."""
        output = {k: v for k, v in self.model_dump(core=core).items() if k in ['allow_origins', 'allow_methods', 'allow_headers', 'allow_credentials', 'max_age']}
        return output

    @model_validator(mode="after")
    def validate_cors_config(self) -> "CORSConfig":
        """Validate CORS configuration."""
        if not self.allow_origins:
            raise ValueError("At least one origin must be allowed")
        if not self.allow_methods:
            raise ValueError("At least one method must be allowed")
        if not self.allow_headers:
            raise ValueError("At least one header must be allowed")
        if self.max_age < 0:
            raise ValueError("max_age must be non-negative")
        return self

class ServerConfig(CoreBaseModel):
    """Server configuration."""
    name: str = Field(default="Core", description="Server name")
    description: str = Field(default="Core server", description="Server description")
    version: str = Field(default="0.1.0", description="Server version")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=4, description="Number of worker processes")
    keepalive: int = Field(default=5, description="Keepalive timeout in seconds")
    timeout: int = Field(default=10, description="Worker timeout in seconds")
    max_requests: int = Field(default=1000, description="Maximum requests per worker")
    max_requests_jitter: int = Field(default=50, description="Maximum requests jitter")
    graceful_timeout: int = Field(default=1, description="Graceful shutdown timeout")
    ssl_enabled: bool = Field(default=False, description="Enable SSL")
    ssl_keyfile: Optional[str] = Field(default=None, description="SSL key file path")
    ssl_certfile: Optional[str] = Field(default=None, description="SSL certificate file path")

    @model_validator(mode="after")
    def validate_server_config(self) -> "ServerConfig":
        """Validate server configuration."""
        if self.port <= 0 or self.port > 65535:
            raise ValueError("port must be between 1 and 65535")
        if self.workers <= 0:
            raise ValueError("workers must be positive")
        if self.keepalive <= 0:
            raise ValueError("keepalive must be positive")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if self.max_requests_jitter < 0:
            raise ValueError("max_requests_jitter must be non-negative")
        if self.graceful_timeout <= 0:
            raise ValueError("graceful_timeout must be positive")
        if self.ssl_enabled and (not self.ssl_keyfile or not self.ssl_certfile):
            raise ValueError("SSL key file and certificate file are required when SSL is enabled")
        return self