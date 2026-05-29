"""Infrastructure configuration."""
from typing import Optional, Dict, Any, List
from pydantic import Field

from core.types.model import CoreBaseModel


class BaseProviderConfig(CoreBaseModel):
    """Base provider configuration."""
    enabled: bool = Field(default=True, description="Enable provider")
    api_url: str = Field(default="", description="API URL")
    api_key: str = Field(default="", description="API key")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")


class AWSConfig(BaseProviderConfig):
    """AWS configuration."""
    region_name: str = Field(default="us-east-1", description="AWS region name")
    aws_access_key_id: str = Field(default="", description="AWS access key ID")
    aws_secret_access_key: str = Field(default="", description="AWS secret access key")
    bucket_name: str = Field(default="", description="S3 bucket name")
    s3_prefix: str = Field(default="", description="S3 key prefix")
    s3_acl: str = Field(default="private", description="S3 ACL")
    upload_chunk_size: int = Field(default=5242880, description="Upload chunk size in bytes")
    use_ssl: bool = Field(default=True, description="Use SSL for connections")
    max_pool_connections: int = Field(default=10, description="Maximum connection pool size")


class GDriveConfig(BaseProviderConfig):
    """Google Drive configuration."""
    credentials: str = Field(default="", description="Service account credentials")
    folder_id: str = Field(default="", description="Root folder ID")
    max_page_size: int = Field(default=100, description="Maximum page size for listing")
    upload_chunk_size: int = Field(default=5242880, description="Upload chunk size in bytes")


class StrapiConfig(BaseProviderConfig):
    """Strapi configuration."""
    stage: str = Field(default="dev", description="Strapi stage")
    version: str = Field(default="v4", description="API version")
    max_page_size: int = Field(default=100, description="Maximum page size for listing")



class WeaviateConfig(BaseProviderConfig):
    """Weaviate configuration."""
    batch_size: int = Field(default=100, description="Batch size for operations")
    vector_index_type: str = Field(default="hnsw", description="Vector index type")
    vector_cache_size: int = Field(default=100000, description="Vector cache size")


class CacheConfig(CoreBaseModel):
    """Cache configuration."""
    enabled: bool = Field(default=True, description="Enable caching")
    provider: str = Field(default="memory", description="Cache provider type")
    url: str = Field(default="redis://localhost:6379", description="Cache URL")
    ttl: int = Field(default=3600, description="Cache TTL in seconds")
    max_size: int = Field(default=1000, description="Maximum number of items")
    cleanup_interval: int = Field(default=300, description="Cleanup interval in seconds")
    max_memory_mb: int = Field(default=512, description="Maximum memory in MB")


class QueueConfig(CoreBaseModel):
    """Queue configuration."""
    enabled: bool = Field(default=False, description="Enable queue")
    url: Optional[str] = Field(default=None, description="Queue URL")
    min_workers: int = Field(default=1, description="Minimum number of workers")
    max_workers: int = Field(default=5, description="Maximum number of workers")
    batch_size: int = Field(default=100, description="Batch size")
    visibility_timeout: int = Field(default=300, description="Message visibility timeout")


class RedisConfig(CoreBaseModel):
    """Redis configuration."""
    enabled: bool = Field(default=False, description="Enable Redis")
    url: str = Field(default="redis://localhost:6379", description="Redis URL")
    max_connections: int = Field(default=10, description="Maximum connections")
    socket_timeout: float = Field(default=5.0, description="Socket timeout")
    socket_connect_timeout: float = Field(default=2.0, description="Socket connect timeout")


class StorageInfrastructureConfig(CoreBaseModel):
    """Storage configuration."""
    enabled: bool = Field(default=True, description="Enable storage")
    primary_provider: str = Field(default="strapi", description="Primary storage provider")
    sync_providers: bool = Field(default=False, description="Sync between providers")
    max_file_size: int = Field(default=10485760, description="Maximum file size in bytes")
    path_prefix: str = Field(default="", description="Storage path prefix")
    allowed_extensions: Optional[List[str]] = Field(default=None, description="Allowed file extensions")
    routing_rules: Optional[Dict[str, str]] = Field(default=None, description="MIME type routing rules")
    max_concurrent_uploads: int = Field(default=5, description="Maximum concurrent uploads")
    max_concurrent_downloads: int = Field(default=10, description="Maximum concurrent downloads")
    upload_chunk_size: int = Field(default=5242880, description="Default upload chunk size")
    download_chunk_size: int = Field(default=5242880, description="Default download chunk size")
    aws: AWSConfig = Field(default_factory=AWSConfig)
    gdrive: GDriveConfig = Field(default_factory=GDriveConfig)
    strapi: StrapiConfig = Field(default_factory=StrapiConfig)
    weaviate: WeaviateConfig = Field(default_factory=WeaviateConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    queue: QueueConfig = Field(default_factory=QueueConfig)