"""AWS Secrets Manager client implementation."""
from typing import Dict, Any, Optional, Set, Union
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from core.base.infrastructure import BaseInfrastructureClient
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker
from core.resilience.rate_limiter import RateLimiter
from core.alert.manager import AlertManager
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation


class SecretsManagerError(Exception):
    """Base class for Secrets Manager related errors."""
    pass


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class SecretsManagerClient(BaseInfrastructureClient):
    """AWS Secrets Manager client implementation."""

    REQUIRED_CONFIG = {
        'region_name': str,
        'aws_access_key_id': str,  # Optional if using IAM role
        'aws_secret_access_key': str,  # Optional if using IAM role
        'timeout': float
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
        """Initialize Secrets Manager client.
        
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
        self._client = None
        self._client_config = self._get_client_config()

    def _get_client_config(self) -> Dict[str, Any]:
        """Get client configuration.
        
        Returns:
            Client configuration dictionary
            
        Raises:
            ConfigError: If configuration is invalid
        """
        try:
            config = {
                'region_name': self.config.get_string('region_name'),
                'timeout': self.config.get_float('timeout', 30.0)
            }
            
            # Optional AWS credentials
            aws_access_key = self.config.get_string('aws_access_key_id', '')
            aws_secret_key = self.config.get_string('aws_secret_access_key', '')
            
            if aws_access_key and aws_secret_key:
                config.update({
                    'aws_access_key_id': aws_access_key,
                    'aws_secret_access_key': aws_secret_key
                })
                
            return config
            
        except Exception as e:
            raise ConfigError(f"Invalid configuration: {str(e)}")

    def _register_metrics(self) -> None:
        """Register client metrics."""
        if self.metrics:
            self.metrics.register(
                name=f"{self.name}_operations_total",
                type=MetricType.COUNTER,
                description=f"Total {self.name} operations",
                labels=["operation", "status"]
            )
            self.metrics.register(
                name=f"{self.name}_errors_total", 
                type=MetricType.COUNTER,
                description=f"Total {self.name} errors",
                labels=["error_type", "operation"]
            )
            self.metrics.register(
                name=f"{self.name}_operation_duration_seconds",
                type=MetricType.HISTOGRAM,
                description=f"{self.name} operation duration in seconds",
                labels=["operation"]
            )

    @track_component_operation("initialize")
    async def _initialize_impl(self) -> None:
        """Initialize the client implementation."""
        try:
            session = boto3.Session(
                aws_access_key_id=self._client_config.get('aws_access_key_id'),
                aws_secret_access_key=self._client_config.get('aws_secret_access_key'),
                region_name=self._client_config['region_name']
            )
            
            self._client = session.client(
                service_name='secretsmanager',
                region_name=self._client_config['region_name']
            )
            
            await self._validate_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize client: {str(e)}")
            raise

    @track_component_operation("validate")
    async def _validate_connection(self) -> None:
        """Validate AWS Secrets Manager connection.
        
        Raises:
            SecretsManagerError: If connection validation fails
        """
        try:
            # List secrets to validate connection
            self._client.list_secrets(MaxResults=1)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'InvalidSignatureException':
                raise SecretsManagerError(f"Invalid AWS credentials: {error_message}")
            elif error_code == 'UnrecognizedClientException':
                raise SecretsManagerError(f"Invalid AWS configuration: {error_message}")
            else:
                raise SecretsManagerError(f"Failed to validate connection: {error_message}")
                
        except Exception as e:
            raise SecretsManagerError(f"Failed to validate connection: {str(e)}")

    async def get_secret(self, secret_id: str) -> Dict[str, Any]:
        """Get secret value.
        
        Args:
            secret_id: Secret identifier
            
        Returns:
            Secret value as dictionary
            
        Raises:
            SecretsManagerError: If operation fails
        """
        async def _do_get_secret():
            try:
                response = self._client.get_secret_value(SecretId=secret_id)
                
                if 'SecretString' in response:
                    return response['SecretString']
                elif 'SecretBinary' in response:
                    import base64
                    return base64.b64decode(response['SecretBinary'])
                    
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                
                if error_code == 'ResourceNotFoundException':
                    raise SecretsManagerError(f"Secret {secret_id} not found")
                elif error_code == 'InvalidParameterException':
                    raise SecretsManagerError(f"Invalid secret ID: {error_message}")
                elif error_code == 'InvalidRequestException':
                    raise SecretsManagerError(f"Invalid request: {error_message}") 
                else:
                    raise SecretsManagerError(f"Failed to get secret: {error_message}")
                    
            except Exception as e:
                raise SecretsManagerError(f"Failed to get secret: {str(e)}")
                
        return await self._execute_with_resilience(
            "get_secret",
            _do_get_secret
        )

    async def get_google_credentials(self, secret_id: str) -> Dict[str, Any]:
        """Get Google credentials from secret and determine type.
        
        Args:
            secret_id: Secret identifier
            
        Returns:
            Dictionary containing:
                - credentials_type: 'service_account' or 'oauth2'
                - credentials: The credentials data
                
        Raises:
            SecretsManagerError: If operation fails
        """
        try:
            secret_data = await self.get_secret(secret_id)
            
            # Parse secret data
            if isinstance(secret_data, str):
                import json
                credentials = json.loads(secret_data)
            else:
                credentials = secret_data
                
            # Determine credentials type
            if 'type' in credentials and credentials['type'] == 'service_account':
                return {
                    'credentials_type': 'service_account',
                    'credentials': credentials
                }
            elif 'installed' in credentials or 'web' in credentials:
                return {
                    'credentials_type': 'oauth2',
                    'credentials': credentials
                }
            else:
                raise SecretsManagerError(
                    "Unable to determine credentials type - missing required fields"
                )
                
        except Exception as e:
            raise SecretsManagerError(f"Failed to get Google credentials: {str(e)}")

    async def check_health(self) -> Dict[str, Any]:
        """Check client health.
        
        Returns:
            Health check results
        """
        results = {
            "status": "healthy",
            "details": {
                "client": self.name,
                "region": self._client_config['region_name'],
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