"""Unified storage infrastructure client."""
from typing import Optional, Dict, Any, BinaryIO, Union, List, Set
from datetime import datetime, timezone
import mimetypes
import os
from pathlib import Path
from contextlib import nullcontext
import asyncio

from core.base.component import BaseComponent
from core.telemetry.metrics import MetricsManager
from core.config import AppConfig
from core.logging import BackendLogger
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker
from core.resilience.rate_limiter import RateLimiter
from core.types.metrics import MetricType

class StorageError(Exception):
    """Base storage error."""
    pass

class StorageProviderError(StorageError):
    """Storage provider specific error."""
    pass

class StorageInfrastructureClient(BaseComponent):
    """Unified storage infrastructure client."""
    
    REQUIRED_CONFIG = {
        'primary_provider': str,
        'sync_providers': bool,
        'max_file_size': int,
        'path_prefix': str,
        'allowed_extensions': (list, type(None)),
        'routing_rules': dict
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        retry: Optional[RetryManager] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        rate_limiter: Optional[RateLimiter] = None,
        s3_client: Optional[Any] = None,
        gdrive_client: Optional[Any] = None,
        strapi_client: Optional[Any] = None,
        weaviate_client: Optional[Any] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize storage client.
        
        Args:
            name: Client name
            config: Application configuration
            metrics: Optional metrics manager
            logger: Optional logger instance
            retry: Optional retry manager
            circuit_breaker: Optional circuit breaker
            rate_limiter: Optional rate limiter
            s3_client: Optional S3 client
            gdrive_client: Optional Google Drive client
            strapi_client: Optional Strapi client
            weaviate_client: Optional Weaviate client
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        
        # for k in ['aws','gdrive','strapi','weaviate']:
        #     print(k,self._config[k])
            
        # Get validated config
        self.storage_config = self._get_client_config()
        self._retry = retry
        self._circuit_breaker = circuit_breaker
        self._rate_limiter = rate_limiter
        
        # Initialize storage providers
        self._providers: Dict[str, Any] = {}
        self._primary_provider = self.storage_config['primary_provider']
        self._sync_providers = self.storage_config['sync_providers']
        
        # Initialize enabled providers
        if s3_client and self.storage_config['aws']['enabled']:
            self._providers["s3"] = s3_client
            
        if gdrive_client and self.storage_config['gdrive']['enabled']:
            self._providers["gdrive"] = gdrive_client
            
        if strapi_client and self.storage_config['strapi']['enabled']:
            self._providers["strapi"] = strapi_client
            
        if weaviate_client and self.storage_config['weaviate']['enabled']:
            self._providers["weaviate"] = weaviate_client
            
        if not self._providers:
            raise StorageError("No storage providers configured")
            
        if self._primary_provider not in self._providers:
            raise StorageError(f"Primary provider {self._primary_provider} not available")
            
        # Register metrics
        if self.metrics:
            self._register_metrics()

    def _get_client_config(self) -> Dict[str, Any]:
        """Get and validate client configuration.
        
        Returns:
            Dict containing validated configuration with defaults
        """
        try:
            # Extract config with defaults
            config = {
                'primary_provider': self._config.get('primary_provider', 'strapi'),
                'sync_providers': self._config.get('sync_providers', False),
                'max_file_size': self._config.get('max_file_size', 10485760),  # 10MB
                'path_prefix': self._config.get('path_prefix', ''),
                'allowed_extensions': self._config.get('allowed_extensions', None),
                'routing_rules': self._config.get('routing_rules', {}),
                # Provider configs
                'aws': self._config.get('aws', {'enabled': False}),
                'gdrive': self._config.get('gdrive', {'enabled': False}),
                'strapi': self._config.get('strapi', {'enabled': False}),
                'weaviate': self._config.get('weaviate', {'enabled': False})
            }

            # Validate fields and types
            for field, field_type in self.REQUIRED_CONFIG.items():
                value = config.get(field)
                if isinstance(field_type, tuple):
                    valid = any(isinstance(value, t) for t in field_type)
                else:
                    valid = isinstance(value, field_type)
                
                if not valid:
                    if self.logger:
                        self.logger.warning(
                            f"Invalid type for {field}, attempting conversion",
                            field=field,
                            expected=str(field_type),
                            actual=type(value).__name__
                        )
                    try:
                        if isinstance(field_type, tuple):
                            # Try each type in order
                            for t in field_type:
                                try:
                                    config[field] = t(value) if value is not None else None
                                    break
                                except (ValueError, TypeError):
                                    continue
                        else:
                            config[field] = field_type(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid type for {field}")

            # Update health status
            self._health_status.update(details={
                'primary_provider': config['primary_provider'],
                'sync_providers': config['sync_providers'],
                'max_file_size': config['max_file_size'],
                'path_prefix': config['path_prefix'],
                'allowed_extensions': config['allowed_extensions'],
                'routing_rules': config['routing_rules']
            })

            return config

        except Exception as e:
            if self.logger:
                self.logger.error(
                    "Failed to validate storage config",
                    error=str(e)
                )
            # Return safe defaults
            return {
                'primary_provider': 'strapi',
                'sync_providers': False,
                'max_file_size': 10485760,
                'path_prefix': '',
                'allowed_extensions': None,
                'routing_rules': {},
                'aws': {'enabled': False},
                'gdrive': {'enabled': False},
                'strapi': {'enabled': False},
                'weaviate': {'enabled': False}
            }

    def _register_metrics(self) -> None:
        """Register storage metrics."""
        # Operation metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            "Total number of storage operations",
            labels={"operation": "", "provider": "", "status": ""}
        )
        
        # Transfer metrics
        self.metrics.register_metric(
            f"{self.name}_bytes_transferred",
            MetricType.COUNTER,
            "Number of bytes transferred",
            labels={"operation": "", "provider": ""}
        )
        
        # Duration metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            "Duration of storage operations",
            labels={"operation": "", "provider": ""}
        )
        
        # Error metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            "Total number of storage errors",
            labels={"operation": "", "provider": "", "error_type": ""}
        )
            
    def _get_provider_for_file(self, file_path: str, mime_type: Optional[str] = None) -> str:
        """Get appropriate storage provider for file.
        
        Args:
            file_path: File path
            mime_type: Optional MIME type
            
        Returns:
            Provider name
            
        Raises:
            StorageError: If no suitable provider found
        """
        # Check file extension against allowed extensions
        if self.storage_config['allowed_extensions']:
            ext = os.path.splitext(file_path)[1].lower()
            if ext and ext[1:] not in self.storage_config['allowed_extensions']:
                raise StorageError(f"File extension {ext} not allowed")
                
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
            
        if not mime_type:
            return self._primary_provider
            
        # Check routing rules
        if self.storage_config['routing_rules']:
            for pattern, provider in self.storage_config['routing_rules'].items():
                if pattern.endswith("/*"):
                    if mime_type.startswith(pattern[:-2]):
                        return provider
                elif mime_type == pattern:
                    return provider
                
        return self._primary_provider
        
    async def _sync_operation(self, operation_name: str, provider: str, operation_func: Any, *args, **kwargs) -> Any:
        """Execute operation with provider sync if enabled.
        
        Args:
            operation_name: Operation name
            provider: Provider name
            operation_func: Operation function
            args: Operation arguments
            kwargs: Operation keyword arguments
            
        Returns:
            Operation result
            
        Raises:
            StorageError: If operation fails
        """
        # Execute on primary provider first
        result = await operation_func(*args, **kwargs)
        
        # Sync to other providers if enabled
        if self._sync_providers and provider == self._primary_provider:
            sync_tasks = []
            for sync_provider in self._providers:
                if sync_provider != provider:
                    sync_tasks.append(
                        operation_func(*args, provider=sync_provider, **kwargs)
                    )
                    
            if sync_tasks:
                try:
                    await asyncio.gather(*sync_tasks)
                except Exception as e:
                    self.logger.error(
                        "sync_operation_failed",
                        operation=operation_name,
                        error=str(e)
                    )
                    
        return result
        
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
            file_path: Target file path
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
        start_time = datetime.now()
        
        try:
            # Validate file size
            if isinstance(data, bytes):
                size = len(data)
            else:
                data.seek(0, os.SEEK_END)
                size = data.tell()
                data.seek(0)
                
            if size > self.storage_config['max_file_size']:
                raise StorageError(f"File size {size} exceeds maximum {self.storage_config['max_file_size']}")
                
            # Get provider
            provider_name = provider or self._get_provider_for_file(str(file_path), mime_type)
            provider_client = self._providers.get(provider_name)
            if not provider_client:
                raise StorageError(f"Storage provider {provider_name} not available")
                
            # Prepare path
            full_path = f"{self.storage_config['path_prefix']}/{file_path}"
            
            # Add standard metadata
            full_metadata = {
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "size": size,
                "mime_type": mime_type or mimetypes.guess_type(str(file_path))[0],
                "provider": provider_name
            }
            if metadata:
                full_metadata.update(metadata)
                
            # Upload with resilience patterns and sync
            async with self._circuit_breaker.context() if self._circuit_breaker else nullcontext():
                if self._rate_limiter:
                    await self._rate_limiter.acquire(f"upload:{provider_name}")
                    
                if self._retry:
                    result = await self._sync_operation(
                        operation,
                        provider_name,
                        self._retry.execute,
                        lambda: provider_client.upload_file(full_path, data, full_metadata)
                    )
                else:
                    result = await self._sync_operation(
                        operation,
                        provider_name,
                        provider_client.upload_file,
                        full_path,
                        data,
                        full_metadata
                    )
                    
            # Record metrics
            if self.metrics:
                duration = (datetime.now() - start_time).total_seconds()
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name, "status": "success"}
                )
                
                self.metrics.record(
                    f"{self.name}_bytes_transferred",
                    size,
                    labels={"operation": operation, "provider": provider_name}
                )
                
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider_name}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "error_type": type(e).__name__}
                )
                
            self.logger.error(
                "upload_failed",
                error=str(e),
                file_path=file_path,
                provider=provider_name if 'provider_name' in locals() else "unknown"
            )
            raise StorageError(f"Failed to upload file: {str(e)}")
            
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
        """
        operation = "download_file"
        start_time = datetime.now()
        
        try:
            # Get provider
            provider_name = provider or self._get_provider_for_file(str(file_path))
            provider_client = self._providers.get(provider_name)
            if not provider_client:
                raise StorageError(f"Storage provider {provider_name} not available")
                
            # Prepare path
            full_path = f"{self.storage_config['path_prefix']}/{file_path}"
            
            # Download with resilience patterns
            async with self._circuit_breaker.context() if self._circuit_breaker else nullcontext():
                if self._rate_limiter:
                    await self._rate_limiter.acquire(f"download:{provider_name}")
                    
                if self._retry:
                    result = await self._retry.execute(
                        lambda: provider_client.download_file(full_path)
                    )
                else:
                    result = await provider_client.download_file(full_path)
                    
            # Record metrics
            if self.metrics:
                duration = (datetime.now() - start_time).total_seconds()
                size = len(result) if isinstance(result, bytes) else 0
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name, "status": "success"}
                )
                
                self.metrics.record(
                    f"{self.name}_bytes_transferred",
                    size,
                    labels={"operation": operation, "provider": provider_name}
                )
                
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider_name}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "error_type": type(e).__name__}
                )
                
            self.logger.error(
                "download_failed",
                error=str(e),
                file_path=file_path,
                provider=provider_name if 'provider_name' in locals() else "unknown"
            )
            raise StorageError(f"Failed to download file: {str(e)}")
            
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
        start_time = datetime.now()
        
        try:
            # Get provider
            provider_name = provider or self._get_provider_for_file(str(file_path))
            provider_client = self._providers.get(provider_name)
            if not provider_client:
                raise StorageError(f"Storage provider {provider_name} not available")
                
            # Prepare path
            full_path = f"{self.storage_config['path_prefix']}/{file_path}"
            
            # Delete with resilience patterns and sync
            async with self._circuit_breaker.context() if self._circuit_breaker else nullcontext():
                if self._rate_limiter:
                    await self._rate_limiter.acquire(f"delete:{provider_name}")
                    
                if self._retry:
                    await self._sync_operation(
                        operation,
                        provider_name,
                        self._retry.execute,
                        lambda: provider_client.delete_file(full_path)
                    )
                else:
                    await self._sync_operation(
                        operation,
                        provider_name,
                        provider_client.delete_file,
                        full_path
                    )
                    
            # Record metrics
            if self.metrics:
                duration = (datetime.now() - start_time).total_seconds()
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name, "status": "success"}
                )
                
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider_name}
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "error_type": type(e).__name__}
                )
                
            self.logger.error(
                "delete_failed",
                error=str(e),
                file_path=file_path,
                provider=provider_name if 'provider_name' in locals() else "unknown"
            )
            raise StorageError(f"Failed to delete file: {str(e)}")
            
    async def list_files(
        self,
        directory: Union[str, Path],
        provider: Optional[str] = None,
        recursive: bool = False
    ) -> List[str]:
        """List files in directory.
        
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
        start_time = datetime.now()
        
        try:
            # Get provider
            provider_name = provider or self._primary_provider
            provider_client = self._providers.get(provider_name)
            if not provider_client:
                raise StorageError(f"Storage provider {provider_name} not available")
                
            # Prepare path
            full_path = f"{self.storage_config['path_prefix']}/{directory}"
            
            # List with resilience patterns
            async with self._circuit_breaker.context() if self._circuit_breaker else nullcontext():
                if self._rate_limiter:
                    await self._rate_limiter.acquire(f"list:{provider_name}")
                    
                if self._retry:
                    result = await self._retry.execute(
                        lambda: provider_client.list_files(full_path, recursive)
                    )
                else:
                    result = await provider_client.list_files(full_path, recursive)
                    
            # Record metrics
            if self.metrics:
                duration = (datetime.now() - start_time).total_seconds()
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name, "status": "success"}
                )
                
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider_name}
                )
                
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "error_type": type(e).__name__}
                )
                
            self.logger.error(
                "list_failed",
                error=str(e),
                directory=directory,
                provider=provider_name if 'provider_name' in locals() else "unknown"
            )
            raise StorageError(f"Failed to list files: {str(e)}")
            
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
        start_time = datetime.now()
        
        try:
            # Get provider
            provider_name = provider or self._get_provider_for_file(str(source_path))
            provider_client = self._providers.get(provider_name)
            if not provider_client:
                raise StorageError(f"Storage provider {provider_name} not available")
                
            # Prepare paths
            full_source = f"{self.storage_config['path_prefix']}/{source_path}"
            full_dest = f"{self.storage_config['path_prefix']}/{destination_path}"
            
            # Move with resilience patterns and sync
            async with self._circuit_breaker.context() if self._circuit_breaker else nullcontext():
                if self._rate_limiter:
                    await self._rate_limiter.acquire(f"move:{provider_name}")
                    
                if self._retry:
                    await self._sync_operation(
                        operation,
                        provider_name,
                        self._retry.execute,
                        lambda: provider_client.move_file(full_source, full_dest)
                    )
                else:
                    await self._sync_operation(
                        operation,
                        provider_name,
                        provider_client.move_file,
                        full_source,
                        full_dest
                    )
                    
            # Record metrics
            if self.metrics:
                duration = (datetime.now() - start_time).total_seconds()
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name, "status": "success"}
                )
                
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    duration,
                    labels={"operation": operation, "provider": provider_name}
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"operation": operation, "provider": provider_name if 'provider_name' in locals() else "unknown", "error_type": type(e).__name__}
                )
                
            self.logger.error(
                "move_failed",
                error=str(e),
                source=source_path,
                destination=destination_path,
                provider=provider_name if 'provider_name' in locals() else "unknown"
            )
            raise StorageError(f"Failed to move file: {str(e)}")
            
    async def check_health(self) -> Dict[str, Any]:
        """Check health of storage providers.
        
        Returns:
            Health check results
        """
        results = {}
        
        for provider_name, provider in self._providers.items():
            try:
                await provider.check_health()
                results[provider_name] = {
                    "status": "healthy",
                    "is_primary": provider_name == self._primary_provider
                }
            except Exception as e:
                results[provider_name] = {
                    "status": "unhealthy",
                    "is_primary": provider_name == self._primary_provider,
                    "error": str(e)
                }
                
        return results
            
    async def _cleanup_impl(self) -> None:
        """Clean up storage infrastructure client resources."""
        try:
            # Clean up all providers
            for provider_name, provider in self._providers.items():
                try:
                    await provider.cleanup()
                except Exception as e:
                    if self.logger:
                        self.logger.error(
                            "provider_cleanup_failed",
                            provider=provider_name,
                            error=str(e)
                        )
            
            # Clear providers
            self._providers.clear()
            
            if self.logger:
                self.logger.info(
                    "storage_infrastructure_cleaned_up",
                    client=self.name
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(
                    "storage_cleanup_failed",
                    error=str(e),
                    client=self.name
                )
            raise 
