"""Google Drive client implementation."""
from typing import Any, Dict, List, Optional, BinaryIO, Set, Union
from pathlib import Path
import json
import asyncio
from datetime import datetime, timezone
import os
import pickle

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from core.base.infrastructure import BaseInfrastructureClient
from core.config import AppConfig
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager
from core.base.registry import LifecycleRegistry
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker
from core.resilience.rate_limiter import RateLimiter
from core.logging import BackendLogger
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation
from core.types.storage import StorageProviderProtocol, StoragePath
from infrastructure.aws.secrets_manager_client import SecretsManagerClient


class GDriveError(Exception):
    """Base class for GDrive-related errors."""
    pass


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class GDriveClient(BaseInfrastructureClient, StorageProviderProtocol):
    """Google Drive client implementation."""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    REQUIRED_CONFIG = {
        'secret_id': str,
        'credentials_type': str,  # 'service_account' or 'oauth2'
        'credentials_file': str,  # Path to credentials file
        'folder_id': str,
        'max_page_size': int,
        'timeout': float,
        'user_email': str  # Optional, for service account impersonation
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
        dependencies: Optional[Set[str]] = None,
        secrets_manager: Optional[SecretsManagerClient] = None
    ):
        """Initialize GDrive client.
        
        Args:
            name: Client name
            config: Application configuration
            metrics: Optional metrics manager
            retry: Optional retry manager
            circuit_breaker: Optional circuit breaker
            rate_limiter: Optional rate limiter
            alert_manager: Optional alert manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
            secrets_manager: Optional SecretsManagerClient for retrieving credentials
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies or set()
        )
        self.retry = retry
        self.circuit_breaker = circuit_breaker
        self.rate_limiter = rate_limiter
        self.alert_manager = alert_manager
        self.secrets_manager = secrets_manager
        self._service = None
        self._credentials = None
        self._client_config = self._get_client_config()

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
                'secret_id': self._config.get('secret_id', ''),
                'credentials_file': self._config.get('credential_file', ''),
                'folder_id': self._config.get('folder_id', ''),
                'max_page_size': self._config.get('max_page_size', 100),
                'timeout': self._config.get('timeout', 30.0),
                'user_email': self._config.get('credential_user_email', '')
            }
            
            # Validate fields and log warnings for missing or invalid types
            for field, field_type in self.REQUIRED_CONFIG.items():
                if not config.get(field) and field != 'user_email':  # user_email is optional
                    if self.logger:
                        self.logger.warning(
                            f"Missing config field: {field}, using default value",
                            context="gdrive_client",
                            field=field,
                            default_value=config[field]
                        )
                elif not isinstance(config.get(field), field_type):
                    if self.logger:
                        self.logger.warning(
                            f"Invalid type for config field {field}. Expected {field_type}, got {type(config[field])}. Attempting conversion.",
                            context="gdrive_client",
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
                                context="gdrive_client",
                                field=field,
                                value=config.get(field)
                            )
                            
            # Update health status with config details
            self._health_status.update(details={
                'secret_id': config['secret_id'],
                'credentials_file': config['credentials_file'],
                'folder_id': config['folder_id'],
                'max_page_size': config['max_page_size'],
                'timeout': config['timeout']
            })
            
            return config
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to get client config: {str(e)}",
                    context="gdrive_client",
                    error=str(e)
                )
            # Return default configuration
            return {
                'credentials_file': '',
                'secret_id': '',
                'folder_id': '',
                'max_page_size': 100,
                'timeout': 30.0,
                'user_email': ''
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
            labels={"folder": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_files_total",
            MetricType.GAUGE,
            f"Total number of files in {self.name}",
            labels={"folder": "", "type": ""}
        )
        
        # Transfer Metrics
        self.metrics.register_metric(
            f"{self.name}_transfer_bytes",
            MetricType.COUNTER,
            f"Number of bytes transferred in {self.name}",
            labels={"operation": "", "folder": "", "direction": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_transfer_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of transfer operations in {self.name}",
            labels={"operation": "", "folder": ""}
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

    def _get_credentials_from_file(self) -> Dict[str, Any]:
        """Get credentials from file."""
        with open(self._client_config['credentials_file'], 'r') as f:
            return json.load(f)

    @track_component_operation("initialize")
    async def _initialize_impl(self) -> None:
        """Initialize the client implementation."""
        try:
            if self.secrets_manager:
                # Get credentials from Secrets Manager
                secret_id = self._client_config['secret_id']
                creds_info = await self.secrets_manager.get_google_credentials(secret_id)
            elif self._client_config['credentials_file']:
                # Get credentials from file
                creds_info = self._get_credentials_from_file()
            else:
                raise GDriveError("No credentials source provided")
                
            credentials_type = creds_info['credentials_type']
            credentials_data = creds_info['credentials']

            # Initialize credentials based on type
            if credentials_type == 'service_account':
                self._credentials = service_account.Credentials.from_service_account_info(
                    credentials_data,
                    scopes=self.SCOPES
                )
                
                # Handle service account impersonation
                if self._client_config.get('user_email'):
                    self._credentials = self._credentials.with_subject(
                        self._client_config['user_email']
                    )
                    
            elif credentials_type == 'oauth2':
                # For OAuth2, we need to handle token persistence
                token_path = 'token.pickle'
                
                if os.path.exists(token_path):
                    with open(token_path, 'rb') as token:
                        self._credentials = pickle.load(token)
                        
                if not self._credentials or not self._credentials.valid:
                    if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                        self._credentials.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_info(
                            credentials_data,
                            self.SCOPES
                        )
                        self._credentials = flow.run_local_server(port=0)
                        
                    # Save credentials for future use
                    with open(token_path, 'wb') as token:
                        pickle.dump(self._credentials, token)
            else:
                raise GDriveError(f"Unsupported credentials type: {credentials_type}")

            # Build the Drive service
            self._service = build(
                'drive', 
                'v3',
                credentials=self._credentials,
                cache_discovery=False
            )
            
            await self._validate_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize client: {str(e)}")
            raise

    @track_component_operation("start")
    async def _start_impl(self) -> None:
        """Start GDrive client."""
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
    async def _stop_impl(self) -> None:
        """Stop GDrive client."""
        try:
            if self._service:
                self._service.close()
                self._service = None
                
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
        """Validate GDrive connection.
        
        Raises:
            GDriveError: If connection validation fails
        """
        try:
            # Test connection by listing files
            await self._execute_operation(
                'files',
                'list',
                pageSize=1
            )
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_connection_errors_total",
                    1,
                    labels={"error_type": type(e).__name__}
                )
            raise GDriveError(f"Connection validation failed: {str(e)}")

    async def _execute_operation(self, resource: str, method: str, **kwargs) -> Any:
        """Execute Google Drive API operation with resilience patterns.
        
        Args:
            resource: API resource (e.g., 'files', 'folders')
            method: API method to call
            kwargs: Additional arguments for the API call
            
        Returns:
            Operation result
            
        Raises:
            GDriveError: If operation fails
        """
        return await self._execute_with_resilience(
            operation=f"{resource}_{method}",
            func=self._do_execute_operation,
            resource=resource,
            method=method,
            **kwargs
        )

    async def _do_execute_operation(self, resource: str, method: str, **kwargs) -> Any:
        """Execute single Google Drive API operation.
        
        Args:
            resource: API resource (e.g., 'files', 'folders')
            method: API method to call
            kwargs: Additional arguments for the API call
            
        Returns:
            Operation result
            
        Raises:
            GDriveError: If operation fails
        """
        if not self._service:
            raise GDriveError("Client not initialized")
            
        try:
            # Get resource
            resource_obj = getattr(self._service, resource)()
            if not resource_obj:
                raise GDriveError(f"Unknown resource: {resource}")
                
            # Get method
            method_obj = getattr(resource_obj, method)
            if not method_obj:
                raise GDriveError(f"Unknown method: {method}")
                
            # Execute operation
            request = method_obj(**kwargs)
            return request.execute()
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": f"{resource}_{method}"}
                )
            raise GDriveError(f"Operation {resource}.{method} failed: {str(e)}")

    async def upload_file(
        self,
        local_path: str,
        folder_id: str,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload file to Google Drive.
        
        Args:
            local_path: Local file path
            folder_id: Destination folder ID
            file_name: Optional file name (defaults to local file name)
            
        Returns:
            Upload result info
            
        Raises:
            GDriveError: If upload fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            file_name = file_name or Path(local_path).name
            
            # Create file metadata
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            # Upload file
            media = MediaIoBaseUpload(
                Path(local_path).open('rb'),
                mimetype='application/octet-stream',
                resumable=True
            )
            
            result = await self._execute_operation(
                'files',
                'create',
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, size'
            )
            
            if self.metrics:
                file_size = Path(local_path).stat().st_size
                self.metrics.record(
                    f"{self.name}_transfer_bytes",
                    file_size,
                    labels={
                        "operation": "upload",
                        "folder": folder_id,
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
                    labels={"operation": "upload", "folder": folder_id}
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
            raise GDriveError(f"Failed to upload file: {str(e)}")

    async def download_file(
        self,
        file_id: str,
        local_path: Optional[str] = None
    ) -> BinaryIO:
        """Download file from Google Drive.
        
        Args:
            file_id: File ID
            local_path: Optional local file path
            
        Returns:
            File contents
            
        Raises:
            GDriveError: If download fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Get file metadata
            file = await self._execute_operation(
                'files',
                'get',
                fileId=file_id,
                fields='size'
            )
            
            # Download file
            request = await self._execute_operation(
                'files',
                'get_media',
                fileId=file_id
            )
            
            if local_path:
                with open(local_path, 'wb') as f:
                    f.write(request.execute())
                result = None
            else:
                result = request.execute()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_transfer_bytes",
                    int(file.get('size', 0)),
                    labels={
                        "operation": "download",
                        "folder": file_id,
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
                    labels={"operation": "download", "folder": file_id}
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
            raise GDriveError(f"Failed to download file: {str(e)}")

    async def delete_file(self, file_id: str) -> None:
        """Delete file from Google Drive.
        
        Args:
            file_id: File ID
            
        Raises:
            GDriveError: If deletion fails
        """
        try:
            # Delete file
            await self._execute_operation(
                'files',
                'delete',
                fileId=file_id
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
            raise GDriveError(f"Failed to delete file: {str(e)}")

    async def list_files(
        self,
        folder_id: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in Google Drive folder.
        
        Args:
            folder_id: Optional folder ID
            query: Optional search query
            
        Returns:
            List of file information
            
        Raises:
            GDriveError: If listing fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Build query
            q = []
            if folder_id:
                q.append(f"'{folder_id}' in parents")
            if query:
                q.append(query)
                
            # List files
            result = await self._execute_operation(
                'files',
                'list',
                q=' and '.join(q) if q else None,
                fields='files(id, name, mimeType, size, createdTime, modifiedTime)'
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
                
            return result.get('files', [])
            
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
            raise GDriveError(f"Failed to list files: {str(e)}")

    async def check_health(self) -> Dict[str, Any]:
        """Check client health.
        
        Returns:
            Health check results
        """
        results = {
            "status": "healthy",
            "details": {
                "client": self.name,
                "credentials_type": "service_account" if hasattr(self._credentials, 'service_account_email') else "oauth2",
                "scopes": self.SCOPES,
                "last_check": datetime.now(timezone.utc).isoformat()
            }
        }
        
        try:
            await self._validate_connection()
            
        except Exception as e:
            results.update({
                "status": "unhealthy",
                "error": str(e)
            })
            
        return results 