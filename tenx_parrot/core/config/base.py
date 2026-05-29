"""Base configuration management."""
import os
import json
from typing import Any, Dict, Optional, TypeVar, Type, Union, List, Tuple
from pathlib import Path
from pydantic import Field, ConfigDict

from core.types.model import CoreBaseModel
from core.types.base import ComponentNames as CN
from core.logging import BackendLogger

# Prompt Manager
from .prompt_config import PromptConfig

# LLM configurations
from .llm_config import (
    LLMConfig, 
    AssemblyAIConfig,
    OpenAIConfig,
    AnthropicConfig
)
from .audio_config import AudioConfig

# Resilience configurations
from .resilience_config import (
    RetryConfig,
    RateLimiterConfig,
    CircuitBreakerConfig,
    RecoveryConfig,
    ResilienceConfig
)

# Repository configurations
from .repository_config import (
    BaseRepositoryConfig,
    StorageRepositoryConfig,
    UserRepositoryConfig,
    InterviewRepositoryConfig,
    SessionRepositoryConfig,
    AdminRepositoryConfig,
    AnalysisRepositoryConfig
)

# Service configurations
from .service_config import (
    BaseServiceConfig,
    WebSocketConfig,
    WebRTCConfig,
    CORSConfig,
    ServerConfig,
    ChatServiceConfig,
    InterviewServiceConfig,
    AnalysisServiceConfig,
    AdminServiceConfig,
    StorageServiceConfig,
    SessionServiceConfig
)

# Infrastructure configurations
from .infrastructure_config import (
    AWSConfig,
    GDriveConfig,
    StrapiConfig,
    WeaviateConfig,
    CacheConfig,
    QueueConfig,
    RedisConfig,
    StorageInfrastructureConfig
)

# Session configurations
from .session_config import CoreSessionConfig
from .metrics_config import MetricsConfig

# Alert configurations
from .alert_config import (
    AlertConfig,
    AlertProviderConfig,
    EmailConfig,
    SlackConfig,
    TelegramConfig
)


# Middleware configurations
from .middleware_config import (
    ErrorHandlerConfig,
    RequestProcessorConfig,
    HealthCheckConfig
)

logger = BackendLogger(__name__).get_logger()


def load_env_file(env_filename: str = ".env") -> None:
    """Load environment variables from .env file."""
    env_file = Path(env_filename)
    if not env_file.exists():
        logger.warning(
            "env_file_not_found",
            context="env",
            file=str(env_file)
        )
        return
        
    with env_file.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()


class AppConfig(CoreBaseModel):
    """Application configuration."""
    
    name: str = Field(default="tenx-ipersona")
    strapi_stage: str = Field(default="dev")
    stage: str = Field(default="dev")
    debug: bool = Field(default=False)
    version: str = Field(default="0.0.1")
    
    # Service configurations
    llm_manager: LLMConfig = Field(default_factory=LLMConfig)
    prompt_manager: PromptConfig = Field(default_factory=PromptConfig)
    audio_manager: AudioConfig = Field(default_factory=AudioConfig)
    assembly_ai: AssemblyAIConfig = Field(default_factory=AssemblyAIConfig)
    websocket: WebSocketConfig = Field(default_factory=WebSocketConfig)
    webrtc: WebRTCConfig = Field(default_factory=WebRTCConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    # Infrastructure configurations
    alert: AlertConfig = Field(default_factory=AlertConfig)
    queue: QueueConfig = Field(default_factory=QueueConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    strapi: StrapiConfig = Field(default_factory=StrapiConfig)
    weaviate: WeaviateConfig = Field(default_factory=WeaviateConfig)
    gdrive: GDriveConfig = Field(default_factory=GDriveConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)    
    storage_infrastructure: StorageInfrastructureConfig = Field(default_factory=StorageInfrastructureConfig)
    
    # Resilience configurations
    retry: RetryConfig = Field(default_factory=RetryConfig)
    rate_limiter: RateLimiterConfig = Field(default_factory=RateLimiterConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    recovery: RecoveryConfig = Field(default_factory=RecoveryConfig)

    # Session configurations
    core_session: CoreSessionConfig = Field(default_factory=CoreSessionConfig)
    
    # Repository configurations
    storage_repository: StorageRepositoryConfig = Field(default_factory=StorageRepositoryConfig)
    user_repository: UserRepositoryConfig = Field(default_factory=UserRepositoryConfig)
    interview_repository: InterviewRepositoryConfig = Field(default_factory=InterviewRepositoryConfig)
    session_repository: SessionRepositoryConfig = Field(default_factory=SessionRepositoryConfig)
    admin_repository: AdminRepositoryConfig = Field(default_factory=AdminRepositoryConfig)
    analysis_repository: AnalysisRepositoryConfig = Field(default_factory=AnalysisRepositoryConfig)
    
    # Service configurations
    webrtc_service: WebRTCConfig = Field(default_factory=WebRTCConfig)
    chat_service: ChatServiceConfig = Field(default_factory=ChatServiceConfig)
    interview_service: InterviewServiceConfig = Field(default_factory=InterviewServiceConfig)
    analysis_service: AnalysisServiceConfig = Field(default_factory=AnalysisServiceConfig)
    admin_service: AdminServiceConfig = Field(default_factory=AdminServiceConfig)
    storage_service: StorageServiceConfig = Field(default_factory=StorageServiceConfig)
    session_service: SessionServiceConfig = Field(default_factory=SessionServiceConfig)
    websocket_service: WebSocketConfig = Field(default_factory=WebSocketConfig)
    
    # Middleware configurations
    error_handler: ErrorHandlerConfig = Field(default_factory=ErrorHandlerConfig)
    request_processor: RequestProcessorConfig = Field(default_factory=RequestProcessorConfig)
    health_check: HealthCheckConfig = Field(default_factory=HealthCheckConfig)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="allow",
        validate_default=True
    )

    @classmethod
    def from_env(cls, stage: Optional[str] = None) -> "AppConfig":
        """Create configuration from environment variables.
        
        Args:
            stage: Optional environment stage
            
        Returns:
            Application configuration
        """
        # Load environment variables
        load_env_file()
        
        try:
            # Initialize LLM config
            providers={
                "openai": OpenAIConfig(
                    enabled=True,
                    name=os.getenv("OPENAI_NAME", "openai"),
                    api_key=os.getenv("OPENAI_API_KEY", ""),
                    api_base=os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
                    model=os.getenv("OPENAI_MODEL", "gpt-4"),
                    audio_model=os.getenv("OPENAI_AUDIO_MODEL", "gpt-4o-audio-preview"),
                    temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                    max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
                    streaming=os.getenv("OPENAI_STREAMING", "true").lower() == "true",
                    provider_config=json.loads(os.getenv("OPENAI_CONFIG", "{}"))
                ),
                "assemblyai": AssemblyAIConfig(
                    enabled=True,
                    name=os.getenv("ASSEMBLYAI_NAME", "assemblyai"),
                    api_key=os.getenv("ASSEMBLYAI_API_KEY", ""),
                    api_base=os.getenv("ASSEMBLYAI_API_URL", "https://api.assemblyai.com/v2"),
                    streaming=os.getenv("ASSEMBLYAI_STREAMING", "true").lower() == "true"
                )
            }                       
            llm_manager_config = LLMConfig(
                providers=providers,
                default_provider=os.getenv("LLM_PROVIDER", "openai"),
            )
            
            audio_manager_config = AudioConfig(
                enabled=os.getenv("AUDIO_ENABLED", "true").lower() == "true",
                default_provider=os.getenv("AUDIO_PROVIDER", "openai"),
                providers=providers
            )
            
            prompt_manager_config = PromptConfig(
                enabled=os.getenv("PROMPT_ENABLED", "true").lower() == "true",
                template_paths=os.getenv("PROMPT_TEMPLATE_PATHS", "").split(",") if os.getenv("PROMPT_TEMPLATE_PATHS", "") else None,
                cache_templates=os.getenv("PROMPT_CACHE_TEMPLATES", "true").lower() == "true",
                cache_ttl=int(os.getenv("PROMPT_CACHE_TTL", "3600")),
                max_retries=int(os.getenv("PROMPT_MAX_RETRIES", "3")),
                timeout=int(os.getenv("PROMPT_TIMEOUT", "30"))
            )
            
            # Define provider configs first
            aws_config = AWSConfig(
                enabled=os.getenv("AWS_S3_ENABLED", "true").lower() == "true",
                region_name=os.getenv("AWS_REGION_NAME", "us-east-1"),
                aws_access_key_id=os.getenv("AWS_S3_API_KEY", ""),
                aws_secret_access_key=os.getenv("AWS_S3_CREDENTIALS", ""),
                max_retries=int(os.getenv("AWS_S3_MAX_RETRIES", "3")),
                retry_delay=float(os.getenv("AWS_S3_RETRY_DELAY", "1.0")),
                timeout=float(os.getenv("AWS_S3_TIMEOUT", "10.0")),
                bucket_name=os.getenv("AWS_S3_BUCKET_NAME", ""),
                s3_prefix=os.getenv("AWS_S3_PREFIX", ""),
                s3_acl=os.getenv("AWS_S3_ACL", "private"),
                upload_chunk_size=int(os.getenv("AWS_S3_UPLOAD_CHUNK_SIZE", "5242880")),
                use_ssl=os.getenv("AWS_S3_USE_SSL", "true").lower() == "true"
            )
            
            gdrive_config = GDriveConfig(
                enabled=os.getenv("GDRIVE_ENABLED", "true").lower() == "true",
                folder_id=os.getenv("GDRIVE_FOLDER_ID", ""),
                credential_file=os.getenv("GDRIVE_CREDENTIALS", ""),
                credential_user_email=os.getenv("GDRIVE_CREDENTIAL_USER_EMAIL", ""),
                credential_type=os.getenv("GDRIVE_CREDENTIAL_TYPE", "service_account"),
                max_page_size=int(os.getenv("GDRIVE_MAX_PAGE_SIZE", "100")),
                upload_chunk_size=int(os.getenv("GDRIVE_UPLOAD_CHUNK_SIZE", "5242880")),
                timeout=float(os.getenv("GDRIVE_TIMEOUT", "30.0"))
            )
            
            strapi_config = StrapiConfig(                
                enabled=os.getenv("STRAPI_ENABLED", "true").lower() == "true",    
                stage = os.getenv("STRAPI_STAGE", "dev"),  
                api_url=os.getenv("STRAPI_URL", ""),
                api_key=os.getenv("STRAPI_AUTH_TOKEN", ""),
                version=os.getenv("STRAPI_VERSION", "v4"),
                max_retries=int(os.getenv("STRAPI_MAX_RETRIES", "3")),
                retry_delay=float(os.getenv("STRAPI_RETRY_DELAY", "1.0")),
                timeout=float(os.getenv("STRAPI_TIMEOUT", "10.0")),                
            )
            
            weaviate_config = WeaviateConfig(
                enabled=os.getenv("WEAVIATE_ENABLED", "true").lower() == "true",
                api_url=os.getenv("WEAVIATE_URL", ""),
                api_key=os.getenv("WEAVIATE_API_KEY", ""),
                batch_size=int(os.getenv("WEAVIATE_BATCH_SIZE", "100")),
                vector_index_type=os.getenv("WEAVIATE_VECTOR_INDEX_TYPE", "hnsw"),
                vector_cache_size=int(os.getenv("WEAVIATE_VECTOR_CACHE_SIZE", "100000")),                
                max_retries=int(os.getenv("WEAVIATE_MAX_RETRIES", "3")),
                retry_delay=float(os.getenv("WEAVIATE_RETRY_DELAY", "1.0")),
                timeout=float(os.getenv("WEAVIATE_TIMEOUT", "10.0"))
            )
            
            cache_config = CacheConfig(
                enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
                provider=os.getenv("CACHE_PROVIDER", "memory"),
                url=os.getenv("CACHE_URL", "redis://localhost:6379"),
                ttl=int(os.getenv("CACHE_TTL", "3600")),
                max_size=int(os.getenv("CACHE_MAX_SIZE", "1000")),
                cleanup_interval=int(os.getenv("CACHE_CLEANUP_INTERVAL", "300")),
                max_memory_mb=int(os.getenv("CACHE_MAX_MEMORY_MB", "512"))
            )
            
            queue_config = QueueConfig(
                enabled=os.getenv("QUEUE_ENABLED", "false").lower() == "true",
                min_workers=int(os.getenv("QUEUE_MIN_WORKERS", "1")),
                max_workers=int(os.getenv("QUEUE_MAX_WORKERS", "5")),
                queue_url=os.getenv("QUEUE_URL")
            )

            storage_infrastructure = StorageInfrastructureConfig(
                enabled=os.getenv("STORAGE_ENABLED", "true").lower() == "true",
                primary_provider=os.getenv("STORAGE_PRIMARY_PROVIDER", "strapi"),
                sync_providers=os.getenv("STORAGE_SYNC_PROVIDERS", "false").lower() == "true",
                max_file_size=int(os.getenv("STORAGE_MAX_FILE_SIZE", "10485760")),
                path_prefix=os.getenv("STORAGE_PATH_PREFIX", ""),
                allowed_extensions=os.getenv("STORAGE_ALLOWED_EXTENSIONS", "").split(",") if os.getenv("STORAGE_ALLOWED_EXTENSIONS", "") else None,
                routing_rules=json.loads(os.getenv("STORAGE_ROUTING_RULES", "{}")) if os.getenv("STORAGE_ROUTING_RULES", "") else None,
                aws=aws_config,
                gdrive=gdrive_config,
                strapi=strapi_config,
                weaviate=weaviate_config,
                cache=cache_config,
                queue=queue_config
            )
            
            # Now initialize the main config
            config = cls(
                stage=stage or os.getenv("STAGE", "dev"),
                strapi_stage=os.getenv("STRAPI_STAGE", "dev"),
                debug=os.getenv("DEBUG", "false").lower() == "true",                

                # LLM configurations
                llm_manager=llm_manager_config,
                audio_manager=audio_manager_config,
                prompt_manager=prompt_manager_config,
                assembly_ai=AssemblyAIConfig(
                    api_key=os.getenv("ASSEMBLY_AI_API_KEY", ""),
                    streaming=os.getenv("ASSEMBLY_AI_STREAMING", "true").lower() == "true"
                ),
                core_session=CoreSessionConfig(
                    enabled=os.getenv("CORE_SESSION_ENABLED", "true").lower() == "true",
                    timeout_seconds=int(os.getenv("CORE_SESSION_TIMEOUT_SECONDS", "3600")),
                    cleanup_interval_seconds=int(os.getenv("CORE_SESSION_CLEANUP_INTERVAL_SECONDS", "300")),
                    max_inactive_seconds=int(os.getenv("CORE_SESSION_MAX_INACTIVE_SECONDS", "1800")),
                    max_sessions_per_user=int(os.getenv("CORE_SESSION_MAX_SESSIONS_PER_USER", "1"))
                ),
                # Resilience configurations
                retry_manager=RetryConfig(
                    enabled=os.getenv("RETRY_ENABLED", "true").lower() == "true",
                    initial_delay=float(os.getenv("RETRY_INITIAL_DELAY", "1.0")),
                    max_delay=float(os.getenv("RETRY_MAX_DELAY", "30.0")),
                    exponential_base=float(os.getenv("RETRY_EXPONENTIAL_BASE", "2.0")),
                    jitter=os.getenv("RETRY_JITTER", "true").lower() == "true",
                    retry_on_exceptions=os.getenv("RETRY_ON_EXCEPTIONS", "").split(",") if os.getenv("RETRY_ON_EXCEPTIONS", "") else None
                ),
                rate_limiter=RateLimiterConfig(
                    enabled=os.getenv("RATE_LIMITER_ENABLED", "true").lower() == "true",                    
                    name=os.getenv("RATE_LIMITER_NAME", "default"),
                    burst=int(os.getenv("RATE_LIMITER_BURST", "100")),
                    max_requests=int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100")),
                    window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
                ),
                circuit_breaker=CircuitBreakerConfig(
                    name=os.getenv("CIRCUIT_BREAKER_NAME", "default"),
                    enabled=os.getenv("CIRCUIT_BREAKER_ENABLED", "true").lower() == "true",                    
                    failure_threshold=int(os.getenv("CIRCUIT_BREAKER_MAX_FAILURES", "5")),
                    reset_timeout=int(os.getenv("CIRCUIT_BREAKER_WINDOW_SECONDS", "60")),
                    half_open_timeout=int(os.getenv("CIRCUIT_BREAKER_HALF_OPEN_TIMEOUT", "30")),
                    monitored_exceptions=os.getenv("CIRCUIT_BREAKER_MONITORED_EXCEPTIONS", "").split(",") if os.getenv("CIRCUIT_BREAKER_MONITORED_EXCEPTIONS", "") else None,
                    exclude_exceptions=os.getenv("CIRCUIT_BREAKER_EXCLUDE_EXCEPTIONS", "").split(",") if os.getenv("CIRCUIT_BREAKER_EXCLUDE_EXCEPTIONS", "") else None
                ),
                recovery=RecoveryConfig(
                    enabled=os.getenv("RECOVERY_ENABLED", "true").lower() == "true",
                    cleanup_interval=int(os.getenv("RECOVERY_CLEANUP_INTERVAL", "300")),
                    attempt_expiry=int(os.getenv("RECOVERY_ATTEMPT_EXPIRY", "3600")),
                    cooldown_period=int(os.getenv("RECOVERY_COOLDOWN_PERIOD", "300")),
                    thresholds=json.loads(os.getenv("RECOVERY_THRESHOLDS", "{}")) if os.getenv("RECOVERY_THRESHOLDS", "") else None,
                    default_threshold=int(os.getenv("RECOVERY_DEFAULT_THRESHOLD", "3"))
                ),

                cors=CORSConfig(
                    enabled=os.getenv("CORS_ENABLED", "true").lower() == "true",
                    allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",")],
                    allow_methods=[x.strip() for x in os.getenv("CORS_METHODS", "*").split(",")],
                    allow_headers=[x.strip() for x in os.getenv("CORS_HEADERS", "*").split(",")],
                    allow_credentials=os.getenv("CORS_CREDENTIALS", "true").lower() == "true",
                    max_age=int(os.getenv("CORS_MAX_AGE", "36000"))
                ),
                server=ServerConfig(
                    name=os.getenv("SERVER_NAME", "tenx-ipersona"),
                    description=os.getenv("SERVER_DESCRIPTION", "tenx-ipersona server"),
                    version=os.getenv("SERVER_VERSION", "0.1.0"),
                    host=os.getenv("SERVER_HOST", "0.0.0.0"),
                    port=int(os.getenv("SERVER_PORT", "9900")),
                    workers=int(os.getenv("SERVER_WORKERS", "4")),
                    reload=os.getenv("SERVER_RELOAD", "false").lower() == "true"
                ),
                
                # Infrastructure configurations
                alert=AlertConfig(
                    enabled=os.getenv("ALERT_ENABLED", "true").lower() == "true",
                    notification_strategy=os.getenv("ALERT_STRATEGY", "priority"),
                    default_provider=os.getenv("ALERT_DEFAULT_PROVIDER", "email"),
                    rate_limit=int(os.getenv("ALERT_RATE_LIMIT", "100")),
                    circuit_breaker_threshold=int(os.getenv("ALERT_CB_THRESHOLD", "5")),
                    circuit_breaker_timeout=int(os.getenv("ALERT_CB_TIMEOUT", "60")),
                    providers=AlertProviderConfig(
                        email=EmailConfig(
                            enabled=os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                            smtp_host=os.getenv("SMTP_HOST", ""),
                            smtp_port=int(os.getenv("SMTP_PORT", "587")),
                            smtp_username=os.getenv("SMTP_USER", ""),
                            smtp_password=os.getenv("SMTP_PASS", ""),
                            from_address=os.getenv("EMAIL_SENDER", ""),
                            default_recipients=os.getenv("EMAIL_RECIPIENTS", "").split(","),
                            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
                        ),
                        slack=SlackConfig(
                            enabled=os.getenv("SLACK_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                            webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
                            default_channel=os.getenv("SLACK_DEFAULT_CHANNEL", "#alerts"),
                            username=os.getenv("SLACK_BOT_NAME", "Alert Bot")
                        ),
                        telegram=TelegramConfig(
                            enabled=os.getenv("TELEGRAM_NOTIFICATIONS_ENABLED", "false").lower() == "true",
                            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
                            chat_id=os.getenv("TELEGRAM_CHAT_ID", "")
                        )
                    )
                ),
                metrics=MetricsConfig(
                    enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
                    namespace=os.getenv("METRICS_NAMESPACE", "app"),
                    subsystem=os.getenv("METRICS_SUBSYSTEM", "core"),
                    buckets=tuple(float(bucket) for bucket in os.getenv("METRICS_BUCKETS", "0.005,0.01,0.025,0.05,0.075,0.1,0.25,0.5,0.75,1.0,2.5,5.0,7.5,10.0,25.0,50.0,75.0,100.0").split(","))
                ),
                
                # Define provider configs
                queue=queue_config,
                cache=cache_config,                
                strapi=strapi_config,
                weaviate=weaviate_config,
                gdrive=gdrive_config,
                aws=aws_config,

                # Define provider configs
                storage_infrastructure = storage_infrastructure,

                # Define repositorie configs
                user_repository = UserRepositoryConfig(
                    infrastructure=storage_infrastructure
                ),
                storage_repository = StorageRepositoryConfig(
                    infrastructure=storage_infrastructure
                ),  
                session_repository = SessionRepositoryConfig(
                    infrastructure=storage_infrastructure
                ),
                admin_repository = AdminRepositoryConfig(
                    infrastructure=storage_infrastructure
                ),
                analysis_repository = AnalysisRepositoryConfig(
                    infrastructure=storage_infrastructure
                ),
                interview_repository = InterviewRepositoryConfig(
                    infrastructure=storage_infrastructure
                ),

                # Define service configs                   
                storage_service = StorageServiceConfig(
                    enabled=os.getenv("STORAGE_SERVICE_ENABLED", "true").lower() == "true",
                ),
                websocket_service=WebSocketConfig(
                    path=os.getenv("WEBSOCKET_PATH", "/socket.io"),
                    enabled=os.getenv("WS_ENABLED", "true").lower() == "true",
                    ping_interval=int(os.getenv("WS_PING_INTERVAL", "30")),
                    ping_timeout=int(os.getenv("WS_PING_TIMEOUT", "10")),
                    max_lifetime=int(os.getenv("WS_MAX_LIFETIME", "7200"))
                ),
                webrtc_service=WebRTCConfig(
                    ice_servers=json.loads(os.getenv("WEBRTC_ICE_SERVERS", "[]"))
                ),

                chat_service=ChatServiceConfig(
                    enabled=os.getenv("CHAT_SERVICE_ENABLED", "true").lower() == "true",
                    max_history=int(os.getenv("CHAT_SERVICE_MAX_HISTORY", "10")),
                    max_tokens=int(os.getenv("CHAT_SERVICE_MAX_TOKENS", "2000")),
                    temperature=float(os.getenv("CHAT_SERVICE_TEMPERATURE", "0.7")),
                    model=os.getenv("CHAT_SERVICE_MODEL", "gpt-4-1106-preview")
                ),
                interview_service=InterviewServiceConfig(
                    enabled=os.getenv("INTERVIEW_SERVICE_ENABLED", "true").lower() == "true",
                    max_duration=int(os.getenv("INTERVIEW_SERVICE_MAX_DURATION", "3600")),
                    max_questions=int(os.getenv("INTERVIEW_SERVICE_MAX_QUESTIONS", "20")),
                    model=os.getenv("INTERVIEW_SERVICE_MODEL", "gpt-4-1106-preview")
                ),
                analysis_service=AnalysisServiceConfig(
                    enabled=os.getenv("ANALYSIS_SERVICE_ENABLED", "true").lower() == "true",
                    max_tokens=int(os.getenv("ANALYSIS_SERVICE_MAX_TOKENS", "4000")),
                    model=os.getenv("ANALYSIS_SERVICE_MODEL", "gpt-4-1106-preview")
                ),
                admin_service=AdminServiceConfig(
                    enabled=os.getenv("ADMIN_SERVICE_ENABLED", "true").lower() == "true",
                    max_users=int(os.getenv("ADMIN_SERVICE_MAX_USERS", "1000")),
                    max_sessions=int(os.getenv("ADMIN_SERVICE_MAX_SESSIONS", "100"))
                ),

                # Middleware
                error_handler=ErrorHandlerConfig(
                    enabled=os.getenv("ERROR_HANDLER_ENABLED", "true").lower() == "true",
                    handler=os.getenv("ERROR_HANDLER_HANDLER", ""),
                    threshold=int(os.getenv("ERROR_HANDLER_THRESHOLD", "100"))
                ),
                request_processor=RequestProcessorConfig(
                    enabled=os.getenv("REQUEST_PROCESSOR_ENABLED", "true").lower() == "true",
                    processor=os.getenv("REQUEST_PROCESSOR_PROCESSOR", ""),
                    threshold=int(os.getenv("REQUEST_PROCESSOR_THRESHOLD", "100"))
                ),
                health_check=HealthCheckConfig(
                    enabled=os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true",
                    check=os.getenv("HEALTH_CHECK_CHECK", ""),
                    threshold=int(os.getenv("HEALTH_CHECK_THRESHOLD", "100"))
                )
            )
            
            # Log configuration
            logger.info(
                "config_loaded",
                context="config",
                json_data={
                    "Configuration": {
                        "Stage": config.stage,
                        "Debug": config.debug,
                        "LLM Provider": config.llm_manager.providers,
                        "WebSocket": config.websocket.enabled,
                        "Storage": {
                            "Primary": config.storage_repository.primary_storage,
                            "Sync": config.storage_repository.sync_storages
                        },
                        "Notifications": {
                            "Email": config.alert.providers.email.enabled,
                            "Slack": config.alert.providers.slack.enabled
                        },
                        "Queue": config.queue.enabled,
                        "Cache": config.cache.enabled,
                        "Server": {
                            "Host": config.server.host,
                            "Port": config.server.port
                        },
                        "Circuit Breaker": {
                            "Enabled": config.circuit_breaker.enabled,
                            "Name": config.circuit_breaker.name,
                            "Max Failures": config.circuit_breaker.failure_threshold
                        }
                    }
                },
                print_json=True
            )
            
            return config
            
        except Exception as e:
            logger.error(
                "config_load_failed",
                context="error",
                error=str(e)
            )
            raise

    def get_config(self, name: str) -> Dict[str, Any]:
        """Get configuration for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service configuration
        """
        try:
            config = getattr(self, name)
            return config
        except AttributeError:
            logger.warning(
                f"config_not_found for name={name}",
                context="config",
            )
            return self
            
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service configuration
        """
        try:
            config = getattr(self, service_name)
            return config.model_dump()
        except AttributeError:
            logger.warning(
                "service_config_not_found",
                context="config",
                service=service_name
            )
            return {} 

    @classmethod
    def get_by_component_name(cls, 
                              config: Union[Dict[str, Any], "AppConfig"], 
                              name: str, **kwargs) -> Any:
        """Create configuration for a specific component.
        
        Args:
            name: Component name from ComponentNames
            **kwargs: Additional configuration
            
        Returns:
            Component-specific configuration or full AppConfig if no specific config exists
        """
        
        if not isinstance(config, AppConfig):
            config = AppConfig(**config)
        
        # Map component names to their config attributes
        component_config_map = {
            # Core managers
            CN.metrics_manager: "metrics",
            CN.cache_manager: "cache",
            CN.retry_manager: "retry",
            CN.rate_limiter: "rate_limiter",
            CN.circuit_breaker: "circuit_breaker",
            CN.alert_manager: "alert",
            CN.llm_manager: "llm_manager",
            CN.audio_manager: "audio_manager",
            CN.prompt_manager: "prompt_manager",
            CN.chat_manager: "llm_manager",
            CN.chain_manager: "llm_manager",
            
            # Session managers
            CN.core_session_manager: "core_session",
            
            # Infrastructure clients
            CN.s3_client: "aws",
            CN.gdrive_client: "gdrive",
            CN.storage_infrastructure_client: "storage_infrastructure",
            CN.strapi_client: "strapi",
            CN.weaviate_client: "weaviate",
            
            # Repositories
            CN.storage_repository: "storage_repository",
            CN.user_repository: "user_repository",
            CN.interview_repository: "interview_repository",
            CN.session_repository: "session_repository",
            CN.admin_repository: "admin_repository",
            CN.analysis_repository: "analysis_repository",
            
            # Services            
            CN.storage_service: "storage_service",
            CN.session_service: "session_service",
            CN.websocket_service: "websocket_service",
            CN.webrtc_service: "webrtc_service",
            CN.chat_service: "chat_service",
            CN.interview_service: "interview_service",
            CN.analysis_service: "analysis_service",
            CN.admin_service: "admin_service",
            CN.chat_manager: "chat_service",
            CN.interview_manager: "interview_service",
            
            # Middleware
            CN.error_handler: "error_handler",
            CN.request_processor: "request_processor",
            CN.health_check: "health_check"
        }
        
        # Get the config attribute name for this component
        config_attr = component_config_map.get(name)
        if config_attr:
            try:
                return getattr(config, config_attr).model_dump()
            except AttributeError:
                logger.warning(
                    "config_not_found",
                    component=name,
                    config_attr=config_attr
                )
                return config.model_dump()
        
        return {}
    
    def __repr__(self):
 
        json_data={
            "Configuration": {
                "Stage": self.stage,
                "Debug": self.debug,
                "LLM Provider": self.llm.provider,
                "WebSocket": self.websocket.enabled,
                "Notifications": {
                    "Email": self.alert.email.enabled,
                    "Slack": self.alert.slack.enabled
                },
                "Queue": self.queue.enabled,
                "Cache": self.cache.enabled,
                "Server": {
                    "Host": self.server.host,
                    "Port": self.server.port
                },
                "Circuit Breaker": {
                    "Enabled": self.circuit_breaker.enabled,
                    "Name": self.circuit_breaker.name,
                    "Max Failures": self.circuit_breaker.failure_threshold
                }
            }
        }
            
        return json.dumps(json_data, indent=4)


