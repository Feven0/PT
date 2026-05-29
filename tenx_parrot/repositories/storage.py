"""Storage repository implementation."""
from typing import Optional, Dict, Any, List, BinaryIO, Set, Union
from datetime import datetime, timezone
import asyncio
import time
from pathlib import Path

from core.types.base import ComponentNames as CN
from core.base import BaseRepository
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.errors.exceptions import StorageError, NotFoundError
from core.resilience.rate_limiter import RateLimiter
from core.resilience.retry import RetryWithBackoff
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation
from infrastructure.storage.client import StorageInfrastructureClient
from core.types.components import HealthStatus


class StorageRepository(BaseRepository):
    """Storage repository."""

    REQUIRED_CONFIG = {
        'primary_provider': str,
        'sync_providers': bool,
        'max_file_size': int,
        'path_prefix': str,
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        dependencies: Optional[Set[str]] = None,
        storage_client: Optional[StorageInfrastructureClient] = None
    ):
        """Initialize storage repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Optional metrics manager
            dependencies: Optional set of dependency names
            storage_client: Storage infrastructure client
        """
        # Initialize base repository
        required_deps = {CN.metrics_manager, 
                         CN.storage_infrastructure_client}
        if dependencies:
            required_deps.update(dependencies)
            
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            dependencies=required_deps
        )
        
        self._storage = storage_client
        if not self._storage:
            raise ValueError("Storage client is required")
            
        # Get validated repository config
        self._repository_config = self._get_repository_config()
        
        # Initialize storage repository settings from validated config
        self._cache_ttl = self._repository_config['cache_ttl']
        self._batch_size = self._repository_config['batch_size']
        self._max_retries = self._repository_config['max_retries']
        self._max_file_size = self._repository_config['max_file_size']
        self._allowed_extensions = self._repository_config.get('allowed_extensions')
        
        # Update health status with storage repository specific details
        self.update_health_details({
            "config": {
                "cache_ttl": self._cache_ttl,
                "batch_size": self._batch_size,
                "max_retries": self._max_retries,
                "max_file_size": self._max_file_size,
                "allowed_extensions": self._allowed_extensions,
                "primary_provider": self._repository_config['primary_provider'],
                "sync_providers": self._repository_config['sync_providers']
            }
        })
        
        # Register metrics if available
        if self.metrics:
            self._register_metrics()

    def _get_repository_config(self) -> Dict[str, Any]:
        """Extract and validate repository configuration.
        
        Returns:
            Dict containing validated configuration with defaults
        """
        try:
            # Get storage config section
            storage_config = self._config
            
            config = {
                'primary_provider': storage_config.get('primary_provider', 'gdrive'),
                'sync_providers': storage_config.get('sync_providers', False),
                'max_file_size': storage_config.get('max_file_size', 10485760),  # 10MB default
                'path_prefix': storage_config.get('path_prefix', ''),
                'allowed_extensions': storage_config.get('allowed_extensions', ['*']),
                'routing_rules': storage_config.get('routing_rules', {'s3/*': 's3', 'gdrive/*': 'gdrive', 'strapi/*': 'strapi', 'aws/*': 'aws'}),
                'cache_ttl': storage_config.get('cache_ttl', 3600),
                'batch_size': storage_config.get('batch_size', 100),
                'max_retries': storage_config.get('max_retries', 3)
            }
            
            # Validate fields and log warnings for missing or invalid types
            for field, field_type in self.REQUIRED_CONFIG.items():
                if not config.get(field):
                    if self.logger:
                        self.logger.warning(
                            f"Missing config field: {field}, using default value",
                            context="storage_repository",
                            field=field,
                            default_value=config[field]
                        )
                elif not isinstance(config.get(field), field_type):
                    if self.logger:
                        self.logger.warning(
                            f"Invalid type for config field {field}. Expected {field_type}, got {type(config[field])}. Attempting conversion.",
                            context="storage_repository",
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
                                context="storage_repository",
                                field=field,
                                value=config.get(field)
                            )
            
            return config
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to get repository config: {str(e)}",
                    context="storage_repository",
                    error=str(e)
                )
            # Return default configuration
            return {
                'primary_provider': 'strapi',
                'sync_providers': False,
                'max_file_size': 10485760,
                'path_prefix': '',
                'allowed_extensions': None,
                'routing_rules': {},
                'cache_ttl': 3600,
                'batch_size': 100,
                'max_retries': 3
            }

    def _register_metrics(self) -> None:
        """Register repository metrics."""
        # Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": "", "provider": ""}
        )
        
        # Storage Metrics
        self.metrics.register_metric(
            f"{self.name}_storage_usage_bytes",
            MetricType.GAUGE,
            f"Storage usage in bytes in {self.name}",
            labels={"provider": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_files_total",
            MetricType.GAUGE,
            f"Total number of files in {self.name}",
            labels={"provider": "", "type": ""}
        )
        
        # Transfer Metrics
        self.metrics.register_metric(
            f"{self.name}_transfer_bytes",
            MetricType.COUNTER,
            f"Number of bytes transferred in {self.name}",
            labels={"operation": "", "provider": "", "direction": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_transfer_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of transfer operations in {self.name}",
            labels={"operation": "", "provider": ""}
        )
        
        # Performance Metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of operations in {self.name}",
            labels={"operation": "", "provider": "", "status": ""}
        )
        
        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": "", "provider": ""}
        )
            
    @track_component_operation("initialize")
    async def _initialize_impl(self) -> None:
        """Initialize storage repository."""
        try:
            # Initialize storage client
            if self._storage:
                await self._storage.initialize()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "success", "provider": "all"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "initialize", "provider": "all"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "error", "provider": "all"}
                )
            raise
            
    @track_component_operation("start")
    async def _start_impl(self) -> None:
        """Start storage repository."""
        try:
            # Start storage client
            if self._storage:
                await self._storage.start()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "success", "provider": "all"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "start", "provider": "all"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "error", "provider": "all"}
                )
            raise
            
    @track_component_operation("stop")
    async def _stop_impl(self) -> None:
        """Stop storage repository."""
        try:
            # Stop storage client
            if self._storage:
                await self._storage.stop()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "success", "provider": "all"}
                )
                self.metrics.record(
                    f"{self.name}_storage_usage_bytes",
                    0,
                    labels={"provider": "all"}
                )
                self.metrics.record(
                    f"{self.name}_files_total",
                    0,
                    labels={"provider": "all", "type": "total"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "stop", "provider": "all"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "error", "provider": "all"}
                )
            raise
            
    async def upload_file(
        self,
        file_path: Union[str, Path],
        data: Union[bytes, BinaryIO],
        mime_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None
    ) -> str:
        """Upload file to storage.
        
        Args:
            file_path: File path
            data: File data or file-like object
            mime_type: Optional MIME type
            metadata: Optional metadata
            provider: Optional provider override
            
        Returns:
            Storage path
            
        Raises:
            StorageError: If upload fails
        """
        operation = "upload_file"
        start_time = time.time()
        
        try:
            result = await self._storage.upload_file(
                file_path=file_path,
                data=data,
                mime_type=mime_type,
                metadata=metadata,
                provider=provider
            )
            
            if self.metrics:
                if isinstance(data, bytes):
                    size = len(data)
                else:
                    data.seek(0, os.SEEK_END)
                    size = data.tell()
                    data.seek(0)
                    
                self.metrics.record(
                    f"{self.name}_transfer_bytes",
                    size,
                    labels={"operation": operation, "provider": provider or "default", "direction": "upload"}
                )
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "success", "provider": provider or "default"}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": operation, "provider": provider or "default"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "error", "provider": provider or "default"}
                )
                
            if isinstance(e, StorageError):
                raise
            raise StorageError(f"Failed to upload file: {str(e)}") from e
            
        finally:
            if self.metrics:
                duration = time.time() - start_time
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider or "default"}
                )
                
    async def download_file(
        self,
        file_path: Union[str, Path],
        provider: Optional[str] = None
    ) -> bytes:
        """Download file from storage.
        
        Args:
            file_path: File path
            provider: Optional provider override
            
        Returns:
            File data
            
        Raises:
            StorageError: If download fails
            NotFoundError: If file not found
        """
        operation = "download_file"
        start_time = time.time()
        
        try:
            result = await self._storage.download_file(
                file_path=file_path,
                provider=provider
            )
            
            if self.metrics:
                size = len(result)
                self.metrics.record(
                    f"{self.name}_transfer_bytes",
                    size,
                    labels={"operation": operation, "provider": provider or "default", "direction": "download"}
                )
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "success", "provider": provider or "default"}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": operation, "provider": provider or "default"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "error", "provider": provider or "default"}
                )
                
            if isinstance(e, NotFoundError):
                raise
            if isinstance(e, StorageError):
                raise
            raise StorageError(f"Failed to download file: {str(e)}") from e
            
        finally:
            if self.metrics:
                duration = time.time() - start_time
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider or "default"}
                )
                
    async def delete_file(
        self,
        file_path: Union[str, Path],
        provider: Optional[str] = None
    ) -> None:
        """Delete file from storage.
        
        Args:
            file_path: File path
            provider: Optional provider override
            
        Raises:
            StorageError: If deletion fails
        """
        operation = "delete_file"
        start_time = time.time()
        
        try:
            await self._storage.delete_file(
                file_path=file_path,
                provider=provider
            )
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "success", "provider": provider or "default"}
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": operation, "provider": provider or "default"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "error", "provider": provider or "default"}
                )
                
            if isinstance(e, StorageError):
                raise
            raise StorageError(f"Failed to delete file: {str(e)}") from e
            
        finally:
            if self.metrics:
                duration = time.time() - start_time
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider or "default"}
                )
                
    async def list_files(
        self,
        directory: Union[str, Path] = "",
        provider: Optional[str] = None,
        recursive: bool = False
    ) -> List[str]:
        """List files in storage.
        
        Args:
            directory: Directory path
            provider: Optional provider override
            recursive: Whether to list recursively
            
        Returns:
            List of file paths
            
        Raises:
            StorageError: If listing fails
        """
        operation = "list_files"
        start_time = time.time()
        
        try:
            result = await self._storage.list_files(
                directory=directory,
                provider=provider,
                recursive=recursive
            )
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "success", "provider": provider or "default"}
                )
                
                self.metrics.record(
                    f"{self.name}_files_total",
                    len(result),
                    labels={"provider": provider or "default", "type": "total"}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": operation, "provider": provider or "default"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "error", "provider": provider or "default"}
                )
                
            if isinstance(e, StorageError):
                raise
            raise StorageError(f"Failed to list files: {str(e)}") from e
            
        finally:
            if self.metrics:
                duration = time.time() - start_time
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider or "default"}
                )
                
    async def move_file(
        self,
        source_path: Union[str, Path],
        destination_path: Union[str, Path],
        provider: Optional[str] = None
    ) -> None:
        """Move file in storage.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            provider: Optional provider override
            
        Raises:
            StorageError: If move fails
        """
        operation = "move_file"
        start_time = time.time()
        
        try:
            await self._storage.move_file(
                source_path=source_path,
                destination_path=destination_path,
                provider=provider
            )
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "success", "provider": provider or "default"}
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": operation, "provider": provider or "default"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "error", "provider": provider or "default"}
                )
                
            if isinstance(e, StorageError):
                raise
            raise StorageError(f"Failed to move file: {str(e)}") from e
            
        finally:
            if self.metrics:
                duration = time.time() - start_time
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider or "default"}
                )
                
    async def check_health(self) -> Dict[str, Any]:
        """Check repository health.
        
        Returns:
            Health check results
        """
        health_status = await super().check_health()
        results = health_status.details
        
        # Check storage client health
        if self._storage:
            storage_health = await self._storage.check_health()
            results.update({'storage': storage_health})
            
        return results 