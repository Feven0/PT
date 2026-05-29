"""Mock configuration for testing."""
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import (
    AppConfig,
    LLMConfig,
    AssemblyAIConfig,
    StrapiConfig,
    WeaviateConfig,
    GDriveConfig,
    AWSConfig,
    WebSocketConfig,
    WebRTCConfig,
    CORSConfig,
    ServerConfig,    
    AlertConfig,
    StorageInfrastructureConfig,
    QueueConfig,
    CacheConfig,
    MetricsConfig,
    RedisConfig,
    ResilienceConfig,
    RetryConfig,
    RateLimiterConfig,
    CircuitBreakerConfig,
    StorageRepositoryConfig,
    UserRepositoryConfig,
    EmailConfig,
    SlackConfig,
    TelegramConfig,
    OpenAIConfig,
    AnthropicConfig,
    ChatServiceConfig,
    InterviewServiceConfig,
    AnalysisServiceConfig,
    AdminServiceConfig,
    StorageServiceConfig,
    SessionServiceConfig,
    InterviewRepositoryConfig,
    SessionRepositoryConfig,
    AdminRepositoryConfig,
    AnalysisRepositoryConfig,
    CoreSessionConfig
)

# Import actual exception classes
from requests.exceptions import ConnectionError, Timeout

# Import Logger
from core.logging import BackendLogger

logger = BackendLogger(name="mock_config").get_logger()

# Core
metrics_config = MetricsConfig(
    enabled=True,
    namespace="test",
    subsystem="core",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0)
)

logger.info("Preparing mock configuration", 
            context="test")

# Infrastructure configs
aws_config = AWSConfig(
    enabled=True,
    api_url="http://localhost:4566",
    api_key="test-aws-key",
    credentials="test-credentials",
    max_retries=3,
    retry_delay=1.0,
    timeout=10.0,
    region_name="us-east-1",
    bucket_name="test-bucket",
    s3_prefix="test",
    s3_acl="private",
    upload_chunk_size=5242880,
    use_ssl=False
)

gdrive_config = GDriveConfig(
    enabled=True,
    api_url="http://localhost:8081",
    api_key="test-gdrive-key",
    credentials="test-credentials",
    max_retries=3,
    retry_delay=1.0,
    timeout=10.0,
    folder_id="test-folder",
    max_page_size=100,
    upload_chunk_size=5242880
)

strapi_config = StrapiConfig(
    stage="test",
    enabled=True,
    base_url="http://localhost:1337",
    api_key="test-strapi-token",
    max_retries=3,
    retry_delay=1.0,
    timeout=10.0,
    version="v4",
    verify_ssl=False,
    max_page_size=100,
    upload_chunk_size=5242880
)

weaviate_config = WeaviateConfig(
    enabled=True,
    api_url="http://localhost:8080",
    api_key="test-weaviate-key",
    max_retries=3,
    retry_delay=1.0,
    timeout=10.0,
    batch_size=100,
    vector_index_type="hnsw",
    vector_cache_size=100000
)

cache_config = CacheConfig(
    enabled=True,
    provider="redis",
    url="redis://localhost:6379/0",
    ttl=3600,
    max_size=1000,
    cleanup_interval=300,
    max_memory_mb=512
)

redis_config = RedisConfig(
    host="localhost",
    port=6379,
    db=0,
    password="",
    ssl=False,
    timeout=10,
    pool_size=10,
    encoding="utf-8"
)

queue_config = QueueConfig(
    enabled=True,
    min_workers=1,
    max_workers=5,
    queue_url="redis://localhost:6379/1"
)

# Storage infrastructure configuration
storage_infrastructure_config = StorageInfrastructureConfig(
    enabled=True,
    primary_provider="strapi",
    sync_providers=False,
    max_file_size=10485760,
    path_prefix="test",
    allowed_extensions=[".txt", ".pdf", ".doc", ".docx", ".mp3", ".wav", ".mp4"],
    routing_rules={
        "application/pdf": "s3",
        "audio/*": "gdrive",
        "application/json": "strapi",
        "application/weaviate": "weaviate"
    },
    max_concurrent_uploads=5,
    max_concurrent_downloads=10,
    upload_chunk_size=5242880,
    download_chunk_size=5242880,
    providers={
        "aws": aws_config,
        "gdrive": gdrive_config,
        "strapi": strapi_config,
        "weaviate": weaviate_config
    },
    cache=cache_config,
    queue=queue_config
)

# Repository configurations
storage_repository_config = StorageRepositoryConfig(
    enabled=True,
    infrastructure=storage_infrastructure_config,
    max_file_size=10485760,
    allowed_extensions=[".txt", ".pdf", ".doc", ".docx", ".mp3", ".wav", ".mp4"],
    path_prefix="test/storage"
)

user_repository_config = UserRepositoryConfig(
    enabled=True,
    infrastructure=storage_infrastructure_config,
    max_file_size=5242880,
    allowed_extensions=[".json"],
    path_prefix="test/users"
)

interview_repository_config = InterviewRepositoryConfig(
    enabled=True,
    infrastructure=storage_infrastructure_config,
    max_file_size=10485760,
    allowed_extensions=[".json", ".mp3", ".wav"],
    path_prefix="test/interviews",
    max_interviews=1000,
    max_duration=3600,
    max_questions=50
)

session_repository_config = SessionRepositoryConfig(
    enabled=True,
    infrastructure=storage_infrastructure_config,
    max_file_size=1048576,
    allowed_extensions=[".json"],
    path_prefix="test/sessions",
    max_sessions=1000,
    cleanup_interval=300,
    max_inactive_time=1800
)

admin_repository_config = AdminRepositoryConfig(
    enabled=True,
    infrastructure=storage_infrastructure_config,
    max_file_size=5242880,
    allowed_extensions=[".json"],
    path_prefix="test/admin",
    max_admins=100,
    max_operations=1000
)

analysis_repository_config = AnalysisRepositoryConfig(
    enabled=True,
    infrastructure=storage_infrastructure_config,
    max_file_size=10485760,
    allowed_extensions=[".json", ".csv", ".xlsx"],
    path_prefix="test/analysis",
    storage_path="test/analysis/results"
)

# Service configurations
chat_service_config = ChatServiceConfig(
    enabled=True,
    max_message_length=4096,
    history_size=100,
    typing_timeout=5.0,
    presence_update_interval=30.0
)

interview_service_config = InterviewServiceConfig(
    enabled=True,
    max_duration=3600,
    min_duration=300,
    recording_enabled=True,
    transcription_enabled=True,
    max_participants=2
)

analysis_service_config = AnalysisServiceConfig(
    enabled=True,
    batch_size=100,
    max_concurrent_analyses=5,
    result_ttl=86400,
    min_confidence=0.7
)

admin_service_config = AdminServiceConfig(
    enabled=True,
    audit_enabled=True,
    audit_retention_days=90,
    max_bulk_operations=1000,
    require_2fa=True
)

storage_service_config = StorageServiceConfig(
    enabled=True,
    max_file_size=10485760,
    allowed_extensions=["*"],
    compression_enabled=True,
    compression_level=6,
    chunk_size=8192
)

session_service_config = SessionServiceConfig(
    enabled=True,
    session_timeout=3600,
    max_sessions_per_user=5,
    cleanup_interval=300,
    heartbeat_interval=30
)

# Alert configurations
email_config = EmailConfig(
    enabled=True,
    sender="test@example.com",
    recipients=["test@example.com"],
    smtp_host="localhost",
    smtp_port=1025,
    smtp_username="test",
    smtp_password="test",
    use_tls=False,
    templates={
        "alert": "templates/email/alert.html",
        "notification": "templates/email/notification.html"
    }
)

slack_config = SlackConfig(
    enabled=True,
    webhook_url="http://localhost:8082/webhook",
    default_channel="#alerts",
    username="Alert Bot",
    icon_emoji=":warning:",
    templates={
        "alert": "templates/slack/alert.json",
        "notification": "templates/slack/notification.json"
    }
)

telegram_config = TelegramConfig(
    enabled=True,
    bot_token="test-bot-token",
    chat_id="test-chat-id",
    templates={
        "alert": "templates/telegram/alert.txt",
        "notification": "templates/telegram/notification.txt"
    }
)

alert_config = AlertConfig(
    enabled=True,
    notification_strategy="priority",
    default_provider="email",
    rate_limit=100,
    circuit_breaker_threshold=5,
    circuit_breaker_timeout=60,
    providers={
        "email": email_config,
        "slack": slack_config,
        "telegram": telegram_config
    },
    priority_routes={
        "high": ["slack", "email"],
        "medium": ["email"],
        "low": ["telegram"]
    },
    templates={
        "alert": {
            "subject": "Test Alert",
            "body": "This is a test alert"
        },
        "notification": {
            "subject": "Test Notification",
            "body": "This is a test notification"
        }
    }
)

# Resilience configurations
resilience_config = ResilienceConfig(
    retry=RetryConfig(
        enabled=True,
        max_retries=3,
        initial_delay=1.0,
        max_delay=5.0,
        exponential_base=2.0,
        jitter=True
    ),
    rate_limiter=RateLimiterConfig(
        enabled=True,
        name="test",
        burst=100,
        max_requests=100,
        window_seconds=60
    ),
    circuit_breaker=CircuitBreakerConfig(
        name="test",
        enabled=True,
        failure_threshold=5,
        reset_timeout=60,
        half_open_timeout=30,
        monitored_exceptions=None
    )
)

# Session configurations
core_session_config = CoreSessionConfig(
    enabled=True,
    session_timeout=3600,
    max_sessions_per_user=5,
    cleanup_interval=300,
    heartbeat_interval=30,
    storage_path="test/sessions/core",
    max_session_data_size=1048576
)


logger.info("Mock configuration prepared", 
            context="test")

def create_mock_config(overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    """Create mock configuration for testing.
    
    Args:
        overrides: Optional dictionary of configuration overrides
        
    Returns:
        Mock AppConfig instance with optional overrides
    """
    config = AppConfig(
        name="tenx-ipersona-test",
        strapi_stage="test",
        stage="test",
        debug=True,
        version="0.0.1-test",
        
        # Service configurations
        llm=LLMConfig(
            default_provider="openai",
            providers={
                "openai": OpenAIConfig(
                    enabled=True,
                    api_token="test-openai-token",
                    api_url="https://api.openai.com/v1",
                    model="gpt-4-test",
                    temperature=0.7,
                    max_tokens=2000,
                    streaming=True,
                    provider_config={}
                ),
                "anthropic": AnthropicConfig(
                    enabled=False,
                    api_token="test-anthropic-token",
                    api_url="https://api.anthropic.com",
                    model="claude-2",
                    temperature=0.7,
                    max_tokens=2000,
                    streaming=True,
                    provider_config={}
                )
            }
        ),
        assembly_ai=AssemblyAIConfig(
            enabled=True,
            api_token="test-assembly-ai-token",
            api_url="https://api.assemblyai.com/v2",
            streaming=True,
            provider_config={}
        ),
        websocket=WebSocketConfig(
            enabled=True,
            ping_interval=30,
            ping_timeout=10,
            max_lifetime=7200
        ),
        webrtc=WebRTCConfig(
            ice_servers=[
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "stun:stun1.l.google.com:19302"}
            ]
        ),
        cors=CORSConfig(
            origins=["http://localhost:3000"],
            credentials=True,
            methods="*",
            headers="*"
        ),
        server=ServerConfig(
            host="0.0.0.0",
            port=9900,
            workers=1,
            keepalive=65,
            timeout=120,
            max_requests=1000,
            max_requests_jitter=50,
            graceful_timeout=30,
            ssl_enabled=False
        ),
        
        # Infrastructure configurations
        alert=alert_config,
        storage_infrastructure=storage_infrastructure_config,
        queue=queue_config,
        cache=cache_config,
        metrics=metrics_config,
        redis=redis_config,
        strapi=strapi_config,
        weaviate=weaviate_config,
        gdrive=gdrive_config,
        aws=aws_config,

        # Resilience configurations
        retry=resilience_config.retry,
        rate_limiter=resilience_config.rate_limiter,
        circuit_breaker=resilience_config.circuit_breaker,
        
        # Session configurations
        core_session=core_session_config,
        interview_session=interview_session_config,
        
        # Repository configurations
        storage_repository=storage_repository_config,
        user_repository=user_repository_config,
        interview_repository=interview_repository_config,
        session_repository=session_repository_config,
        admin_repository=admin_repository_config,
        analysis_repository=analysis_repository_config,
        
        # Service configurations
        chat_service=chat_service_config,
        interview_service=interview_service_config,
        analysis_service=analysis_service_config,
        admin_service=admin_service_config,
        storage_service=storage_service_config,
        session_service=session_service_config,
        webrtc_service=WebRTCConfig(
            ice_servers=[
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "stun:stun1.l.google.com:19302"}
            ]
        ),
        websocket_service=WebSocketConfig(
            enabled=True,
            ping_interval=30,
            ping_timeout=10,
            max_lifetime=7200
        )
    )
    
    logger.good("Mock configuration generated", 
                context="test")
    logger.debug(config, 
                context="test",
                fg="pink")

    if overrides:
        # Update config with overrides
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                raise ValueError(f"Invalid configuration override: {key}")
    
    return config

def create_test_container(config: Optional[AppConfig] = None) -> "Container":
    """Create test container with mock configuration.
    
    Args:
        config: Optional custom configuration
        
    Returns:
        Test container instance
    """
    from core.di.container import Container
    
    if not config:
        config = create_mock_config()
        
    return Container(config) 