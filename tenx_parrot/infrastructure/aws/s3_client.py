"""AWS S3 client implementation."""
from typing import Optional, Dict, Any, List, Set, Union, BinaryIO
import os
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import aioboto3
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from core.base.infrastructure import BaseInfrastructureClient
from core.types.storage import StorageProviderProtocol, StoragePath
from core.config import AppConfig
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker
from core.resilience.rate_limiter import RateLimiter
from core.logging import BackendLogger
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation


class S3Error(Exception):
    """Base class for S3-related errors."""
    pass


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class S3Client(BaseInfrastructureClient, StorageProviderProtocol):
    """AWS S3 client implementation."""

    REQUIRED_CONFIG = {
        'region_name': str,        
        'aws_access_key_id': str,
        'aws_secret_access_key': str,
        'bucket_name': str,
        's3_prefix': str,
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        retry: Optional[RetryManager] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        rate_limiter: Optional[RateLimiter] = None,
        alert_manager: Optional[AlertManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize S3 client.
        
        Args:
            name: Client name
            config: Application configuration containing:
                - bucket: S3 bucket name
                - region: AWS region
                - access_key: AWS access key
                - secret_key: AWS secret key
                - endpoint_url: Optional custom endpoint URL
                - max_pool_connections: Max number of connections (default: 10)
                - connect_timeout: Connection timeout in seconds (default: 5)
                - read_timeout: Read timeout in seconds (default: 60)
            metrics: Optional metrics manager
            retry: Optional retry manager
            circuit_breaker: Optional circuit breaker
            rate_limiter: Optional rate limiter
            alert_manager: Optional alert manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        
        self._retry = retry
        self._circuit_breaker = circuit_breaker
        self._rate_limiter = rate_limiter
        self._alert_manager = alert_manager
        
        self._client_config = self._get_client_config()
        self._session = None
        self._client = None
        self._client_cm = None  # Context manager for client

        # Register metrics if available
        if self.metrics:
            self._register_metrics()

    def _get_client_config(self) -> Dict[str, Any]:
        """Extract and validate client configuration.
        
        Returns:
            Dict containing validated configuration with defaults
        """
        try:
            config = {
                'region_name': self._config.get('region_name', 'us-east-1'),
                'bucket_name': self._config.get('bucket_name', ''),
                'aws_access_key_id': self._config.get('aws_access_key_id', ''),
                'aws_secret_access_key': self._config.get('aws_secret_access_key', ''),
                's3_prefix': self._config.get('s3_prefix', ''),
                's3_acl': self._config.get('s3_acl', 'private'),
                'upload_chunk_size': self._config.get('upload_chunk_size', 5242880),  # 5MB default
                'use_ssl': self._config.get('use_ssl', True),
                'max_pool_connections': self._config.get('max_pool_connections', 10),
                'timeout': self._config.get('timeout', 30.0)
            }
            
            # Validate fields and log warnings for missing or invalid types
            for field, field_type in self.REQUIRED_CONFIG.items():
                if not config.get(field):
                    if self.logger:
                        self.logger.warning(
                            f"Missing config field: {field}, using default value",
                            context="s3_client",
                            field=field,
                            default_value=config[field]
                        )
                elif not isinstance(config.get(field), field_type):
                    if self.logger:
                        self.logger.warning(
                            f"Invalid type for config field {field}. Expected {field_type}, got {type(config[field])}. Attempting conversion.",
                            context="s3_client",
                            field=field,
                            expected_type=str(field_type),
                            actual_type=str(type(config[field]))
                        )
                    try:
                        # Attempt type conversion
                        config[field] = field_type(config.get(field))
                    except (ValueError, TypeError):
                        if self.logger:
                            self.logger.warning(
                                f"Could not convert {field} to {field_type}, using default value",
                                context="s3_client",
                                field=field,
                                value=config.get(field)
                            )
                            
            # Update health status with config details
            self._health_status.update({
                'region_name': config['region_name'],
                'bucket_name': config['bucket_name'],
                's3_prefix': config['s3_prefix'],
                'use_ssl': config['use_ssl'],
                'max_pool_connections': config['max_pool_connections'],
                'timeout': config['timeout']
            })
            
            return config
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to get client config: {str(e)}",
                    context="s3_client",
                    error=str(e)
                )
            # Return default configuration
            return {
                'region_name': 'us-east-1',
                'bucket_name': '',
                'aws_access_key_id': '',
                'aws_secret_access_key': '',
                's3_prefix': '',
                's3_acl': 'private',
                'upload_chunk_size': 5242880,
                'use_ssl': True,
                'max_pool_connections': 10,
                'timeout': 30.0
            }

    def _register_metrics(self) -> None:
        """Register infrastructure metrics."""
        # Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Storage Metrics
        self.metrics.register_metric(
            f"{self.name}_storage_usage_bytes",
            MetricType.GAUGE,
            f"Storage usage in bytes in {self.name}",
            labels={"bucket": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_objects_total",
            MetricType.GAUGE,
            f"Total number of objects in {self.name}",
            labels={"bucket": "", "type": ""}
        )
        
        # Transfer Metrics
        self.metrics.register_metric(
            f"{self.name}_transfer_bytes",
            MetricType.COUNTER,
            f"Number of bytes transferred in {self.name}",
            labels={"operation": "", "bucket": "", "direction": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_transfer_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of transfer operations in {self.name}",
            labels={"operation": "", "bucket": ""}
        )
        
        # Connection Metrics
        self.metrics.register_metric(
            f"{self.name}_connection_errors_total",
            MetricType.COUNTER,
            f"Total number of connection errors in {self.name}",
            labels={"error_type": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_connection_status",
            MetricType.GAUGE,
            f"Current connection status in {self.name}",
            labels={"status": ""}
        )
        
        # Performance Metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )

    async def _get_client(self):
        """Get S3 client using context manager pattern.
        
        Returns:
            S3 client instance
        """
        if not self._session:
            session_kw = {
                'aws_access_key_id': self._client_config.get('aws_access_key_id', ''),
                'aws_secret_access_key': self._client_config.get('aws_secret_access_key', ''),
                'region_name': self._client_config.get('region_name', 'us-east-1')
            }
            if not session_kw['aws_access_key_id'] or not session_kw['aws_secret_access_key']:
                session_kw.pop('aws_access_key_id', None)
                session_kw.pop('aws_secret_access_key', None)
            
            self._session = aioboto3.Session(**session_kw)

        # Configure client with timeouts and connection settings
        client_config = Config(
            connect_timeout=self._client_config.get('connect_timeout', 5),
            read_timeout=self._client_config.get('read_timeout', 60),
            max_pool_connections=self._client_config.get('max_pool_connections', 10),
            retries={'max_attempts': self._client_config.get('retries', 3)}
        )
        
        kw = {}             
        if self._client_config.get('endpoint_url'):
            kw['endpoint_url'] = self._client_config.get('endpoint_url', '')
        kw['config'] = client_config

        if not self._client_cm:
            self._client_cm = self._session.client('s3', **kw)
            self._client = await self._client_cm.__aenter__()
        
        return self._client

    @track_component_operation("initialize")
    async def _do_initialize(self) -> None:
        """Initialize S3 client."""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Initialize client and validate connection
            await self._get_client()
            await self._validate_connection()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_connection_status",
                    1,
                    labels={"status": "connected"}
                )
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds(),
                    labels={"operation": "initialize", "status": "success"}
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_connection_errors_total",
                    1,
                    labels={"error_type": type(e).__name__}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_connection_status",
                    0,
                    labels={"status": "disconnected"}
                )
            raise S3Error(f"Failed to initialize S3 client: {str(e)}")

    @track_component_operation("start")
    async def _do_start(self) -> None:
        """Start S3 client."""
        try:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "start"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "error"}
                )
            raise

    @track_component_operation("stop")
    async def _do_stop(self) -> None:
        """Stop S3 client."""
        try:
            if self._client_cm:
                await self._client_cm.__aexit__(None, None, None)
                self._client_cm = None
                self._client = None
                
            if self._session:
                self._session = None
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_connection_status",
                    0,
                    labels={"status": "disconnected"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "stop"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "error"}
                )
            raise

    async def _validate_connection(self) -> None:
        """Validate S3 connection.
        
        Raises:
            S3Error: If connection validation fails
        """
        try:
            client = await self._get_client()
            await client.list_buckets()
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_connection_errors_total",
                    1,
                    labels={"error_type": type(e).__name__}
                )
            raise S3Error(f"Connection validation failed: {str(e)}")

    async def upload_file(
        self,
        local_path: Union[str, Path],
        s3_path: Union[str, StoragePath],
        bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload file to S3.
        
        Args:
            local_path: Local file path
            s3_path: S3 object path
            bucket: Optional bucket name (defaults to configured bucket)
            
        Returns:
            Upload result info
            
        Raises:
            S3Error: If upload fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            bucket = bucket or self._bucket
            
            # Upload file
            result = await self._client.upload_file(
                str(local_path),
                bucket,
                str(s3_path)
            )
            
            if self.metrics:
                file_size = Path(local_path).stat().st_size
                self.metrics.record(
                    f"{self.name}_transfer_bytes",
                    file_size,
                    labels={
                        "operation": "upload",
                        "bucket": bucket,
                        "direction": "outbound"
                    }
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "upload", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_transfer_duration_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds(),
                    labels={"operation": "upload", "bucket": bucket}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "upload"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "upload", "status": "error"}
                )
            raise S3Error(f"Failed to upload file: {str(e)}")

    async def download_file(
        self,
        s3_path: Union[str, StoragePath],
        local_path: Optional[Union[str, Path]] = None,
        bucket: Optional[str] = None
    ) -> BinaryIO:
        """Download file from S3.
        
        Args:
            s3_path: S3 object path
            local_path: Optional local file path
            bucket: Optional bucket name (defaults to configured bucket)
            
        Returns:
            File contents
            
        Raises:
            S3Error: If download fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            bucket = bucket or self._bucket
            
            # Download file
            result = await self._client.download_file(
                bucket,
                str(s3_path),
                str(local_path) if local_path else None
            )
            
            if self.metrics:
                file_size = (await self._client.head_object(
                    Bucket=bucket,
                    Key=str(s3_path)
                ))['ContentLength']
                
                self.metrics.record(
                    f"{self.name}_transfer_bytes",
                    file_size,
                    labels={
                        "operation": "download",
                        "bucket": bucket,
                        "direction": "inbound"
                    }
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "download", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_transfer_duration_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds(),
                    labels={"operation": "download", "bucket": bucket}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "download"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "download", "status": "error"}
                )
            raise S3Error(f"Failed to download file: {str(e)}")

    async def delete_file(
        self,
        s3_path: Union[str, StoragePath],
        bucket: Optional[str] = None
    ) -> None:
        """Delete file from S3.
        
        Args:
            s3_path: S3 object path
            bucket: Optional bucket name (defaults to configured bucket)
            
        Raises:
            S3Error: If deletion fails
        """
        try:
            bucket = bucket or self._bucket
            
            # Delete file
            await self._client.delete_object(
                Bucket=bucket,
                Key=str(s3_path)
            )
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "delete", "status": "success"}
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "delete"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "delete", "status": "error"}
                )
            raise S3Error(f"Failed to delete file: {str(e)}")

    async def list_files(
        self,
        prefix: Optional[str] = None,
        bucket: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in S3 bucket.
        
        Args:
            prefix: Optional key prefix
            bucket: Optional bucket name (defaults to configured bucket)
            
        Returns:
            List of file information
            
        Raises:
            S3Error: If listing fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            bucket = bucket or self._bucket
            
            # List objects
            result = await self._client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix or ""
            )
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "list", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds(),
                    labels={"operation": "list", "status": "success"}
                )
                
            return result.get('Contents', [])
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "list"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "list", "status": "error"}
                )
            raise S3Error(f"Failed to list files: {str(e)}")

    async def get_file_metadata(
        self,
        s3_path: Union[str, StoragePath],
        bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get file metadata from S3.
        
        Args:
            s3_path: S3 object path
            bucket: Optional bucket name (defaults to configured bucket)
            
        Returns:
            File metadata
            
        Raises:
            S3Error: If metadata retrieval fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            bucket = bucket or self._bucket
            
            # Get object metadata
            result = await self._client.head_object(
                Bucket=bucket,
                Key=str(s3_path)
            )
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "metadata", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds(),
                    labels={"operation": "metadata", "status": "success"}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "metadata"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "metadata", "status": "error"}
                )
            raise S3Error(f"Failed to get file metadata: {str(e)}")

    async def check_health(self) -> Dict[str, Any]:
        """Check client health.
        
        Returns:
            Health check results
        """
        results = await super().check_health()
        
        try:
            # Add client-specific health details
            if self._client:
                await self._validate_connection()
                self.update_health_details({
                    "connected": True,
                    "bucket": self._bucket,
                    "region": self._region
                })
                
        except Exception as e:
            self.update_health_details({
                "error": str(e),
                "connected": False
            })
            
        return results 