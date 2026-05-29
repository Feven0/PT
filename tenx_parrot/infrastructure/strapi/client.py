"""Strapi API client implementation."""
from typing import Dict, Any, Optional, Set, List, Union, BinaryIO
import aiohttp
from datetime import datetime, timedelta, timezone
import asyncio
import json

from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.config import AppConfig
from core.base.infrastructure import BaseInfrastructureClient
from core.base.registry import LifecycleRegistry
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker
from core.resilience.rate_limiter import RateLimiter
from core.alert.manager import AlertManager
from core.cache.manager import CacheManager
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation
from core.types.components import ComponentState, HealthStatus


class StrapiError(Exception):
    """Base class for Strapi-related errors."""
    pass


class StrapiAuthenticationError(StrapiError):
    """Raised when authentication fails."""
    pass


class StrapiConnectionError(StrapiError):
    """Raised when connection fails."""
    pass


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class StrapiClient(BaseInfrastructureClient):
    """Strapi API client."""

    REQUIRED_CONFIG = {
        'api_url': str,
        'api_key': str,
        'stage': str,
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
        cache: Optional[CacheManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize Strapi client.
        
        Args:
            name: Client name
            config: Application configuration containing:
                - api_url: Strapi API base URL
                - api_key: Authentication token
                - stage: API stage (default: dev)
                - version: API version (default: v4)
                - timeout: Request timeout (default: 30.0)
            metrics: Optional metrics manager
            retry: Optional retry manager
            circuit_breaker: Optional circuit breaker
            rate_limiter: Optional rate limiter
            alert_manager: Optional alert manager
            cache: Optional cache manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(name, 
                         config=config, 
                         metrics=metrics, 
                         logger=logger or BackendLogger("strapi"),
                         dependencies=dependencies)
        

        self._session: Optional[aiohttp.ClientSession] = None
        self._client_config = self._get_client_config()
        
        # Initialize resilience components
        self._retry = retry
        self._circuit_breaker = circuit_breaker
        self._rate_limiter = rate_limiter
        self._alert_manager = alert_manager
        self._cache = cache
    
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
                'api_url': self._config.get('api_url', ''),
                'api_key': self._config.get('api_key', ''),
                'max_page_size': self._config.get('max_page_size', 100),
                'stage': self._config.get('stage', 'dev'),
                'version': self._config.get('version', 'v4'),
                'timeout': self._config.get('timeout', 30.0)
            }
            
            # Validate fields and log warnings for missing or invalid types
            for field, field_type in self.REQUIRED_CONFIG.items():
                if not config.get(field):
                    if self.logger:
                        self.logger.warning(
                            f"Missing config field: {field}, using default value",
                            context="strapi_client",
                            field=field,
                            default_value=config[field]
                        )
                elif not isinstance(config[field], field_type):
                    if self.logger:
                        self.logger.warning(
                            f"Invalid type for config field {field}. Expected {field_type}, got {type(config[field])}. Attempting conversion.",
                            context="strapi_client",
                            field=field,
                            expected_type=str(field_type),
                            actual_type=str(type(config[field]))
                        )
                    try:
                        # Attempt type conversion
                        config[field] = field_type(config[field])
                    except (ValueError, TypeError):
                        if self.logger:
                            self.logger.warning(
                                f"Could not convert {field} to {field_type}, using default value",
                                context="strapi_client",
                                field=field,
                                value=config[field]
                            )
                            
            # Validate URL format and log warning if invalid
            if config.get('api_url') and not config.get('api_url').startswith(('http://', 'https://')):
                if self.logger:
                    self.logger.warning(
                        "Invalid base URL format. Should start with http:// or https://",
                        context="strapi_client",
                        api_url=config['api_url']
                    )
                            
            # Update health status with config details
            self._health_status.update(details={
                'api_url': config['api_url'],
                'version': config['version'],
                'stage': config['stage'],
                'max_page_size': config['max_page_size'],
                'timeout': config['timeout']
            })
            
            return config
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to get client config: {str(e)}",
                    context="strapi_client",
                    error=str(e)
                )
            # Return default configuration
            return {
                'api_url': '',
                'api_key': '',
                'stage': 'dev',
                'version': 'v4',
                'max_page_size': 100,
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
        
        # API Metrics
        self.metrics.register_metric(
            f"{self.name}_api_requests_total",
            MetricType.COUNTER,
            f"Total number of API requests in {self.name}",
            labels={"method": "", "path": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_api_request_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of API requests in {self.name}",
            labels={"method": "", "path": "", "status": ""}
        )
        
        # Query Metrics
        self.metrics.register_metric(
            f"{self.name}_query_results_total",
            MetricType.COUNTER,
            f"Total number of query results in {self.name}",
            labels={"collection": "", "operation": "", "status": ""}
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
        
        # Rate Limit Metrics
        self.metrics.register_metric(
            f"{self.name}_rate_limit_hits_total",
            MetricType.COUNTER,
            f"Total number of rate limit hits in {self.name}",
            labels={"operation": ""}
        )

    @track_component_operation("initialize")
    async def _initialize_impl(self) -> None:
        """Initialize Strapi client."""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Create session with default headers and timeout
            timeout = aiohttp.ClientTimeout(
                total=self._client_config['timeout']
            )
            self._session = aiohttp.ClientSession(
                base_url=self._client_config['api_url'],
                headers={
                    "Authorization": f"Bearer {self._client_config['api_key']}",
                    "Content-Type": "application/json"
                },
                timeout=timeout
            )
            
            # Validate connection
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
            raise StrapiConnectionError(f"Failed to initialize Strapi client: {str(e)}")

    @track_component_operation("start")
    async def _start_impl(self) -> None:
        """Start Strapi client."""
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
        """Stop Strapi client."""
        try:
            if self._session:
                await self._session.close()
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
        """Validate Strapi connection.
        
        Raises:
            StrapiAuthenticationError: If authentication fails
            StrapiConnectionError: If connection fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Test connection with health check
            async with self._session.get("/_health") as response:
                if response.status == 401:
                    if self.metrics:
                        self.metrics.record(
                            f"{self.name}_errors_total",
                            1,
                            labels={"error_type": "authentication", "operation": "validate"}
                        )
                    raise StrapiAuthenticationError("Invalid API token")
                elif response.status == 204:
                    # 204 No Content is a valid health check response
                    try:
                        self._health_status.update(
                            status=HealthStatus.HEALTHY,
                            details={
                            "status": "healthy",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                        )
                    except:
                        if self.logger:
                            self.logger.error(
                                f"Failed to update health status: {str(e)}",
                                context="strapi_client",
                                error=str(e)
                            )
                        pass
                elif response.status > 299:
                    if self.metrics:
                        self.metrics.record(
                            f"{self.name}_errors_total",
                            1,
                            labels={"error_type": "connection", "operation": "validate"}
                        )
                    raise StrapiConnectionError(
                        f"Health check failed with status {response.status}"
                    )
                else:
                    # Try to parse JSON response if available
                    try:
                        data = await response.json()
                        self._health_status.update(
                            status=HealthStatus.HEALTHY,
                            details={
                                "status": data.get("status", "healthy"),
                                "version": data.get("version", "unknown"),
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                        )
                    except:
                        # If JSON parsing fails, still mark as healthy since status code is ok
                        self._health_status.update(
                            status=HealthStatus.HEALTHY,
                            details={
                                "status": "healthy",
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                        )
                
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_api_requests_total",
                        1,
                        labels={"method": "GET", "path": "/_health", "status": "success"}
                    )
                    self.metrics.record(
                        f"{self.name}_api_request_duration_seconds",
                        (datetime.now(timezone.utc) - start_time).total_seconds(),
                        labels={"method": "GET", "path": "/_health", "status": "success"}
                    )
                
        except aiohttp.ClientError as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_connection_errors_total",
                    1,
                    labels={"error_type": type(e).__name__}
                )
                self.metrics.record(
                    f"{self.name}_api_requests_total",
                    1,
                    labels={"method": "GET", "path": "/healthcheck", "status": "error"}
                )
            self._health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            raise StrapiConnectionError(f"Connection validation failed: {str(e)}")

    async def _execute_request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute HTTP request with resilience patterns.
        
        Args:
            method: HTTP method
            path: Request path
            kwargs: Request arguments
            
        Returns:
            Response data
            
        Raises:
            StrapiError: If request fails
        """
        return await self._execute_with_resilience(
            operation=f"{method.lower()}_{path}",
            func=self._do_execute_request,
            method=method,
            path=path,
            **kwargs
        )

    async def _do_execute_request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Internal method to execute HTTP request.
        
        Args:
            method: HTTP method
            path: Request path
            kwargs: Request arguments
            
        Returns:
            Response data
            
        Raises:
            StrapiError: If request fails
        """
        if not self._session:
            raise StrapiError("Client not initialized")

        async with getattr(self._session, method.lower())(
            path,
            **kwargs
        ) as response:
            if response.status == 401:
                raise StrapiAuthenticationError("Invalid API token")
            elif response.status == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise StrapiError(
                    f"Rate limit exceeded, retry after {retry_after}s"
                )
            elif response.status >= 500:
                raise StrapiError(
                    f"Server error: {response.status}"
                )
            elif response.status != 200:
                raise StrapiError(
                    f"Request failed with status {response.status}"
                )
                
            return await response.json()

    async def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute GraphQL query.
        
        Args:
            query: GraphQL query
            variables: Optional query variables
            
        Returns:
            Query response data
            
        Raises:
            StrapiError: If query fails
        """
        return await self._execute_with_resilience(
            operation="execute_query",
            func=self._do_execute_query,
            query=query,
            variables=variables
        )

    async def _do_execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Internal method to execute GraphQL query.
        
        Args:
            query: GraphQL query
            variables: Optional query variables
            
        Returns:
            Query response data
            
        Raises:
            StrapiError: If query fails
        """
        result = await self._execute_request(
            "POST",
            "/graphql",
            json={
                "query": query,
                "variables": variables or {}
            }
        )
        
        if "errors" in result:
            raise StrapiError(f"GraphQL errors: {result['errors']}")
            
        return result.get("data", {})

    async def execute_mutation(
        self,
        mutation: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute GraphQL mutation.
        
        Args:
            mutation: GraphQL mutation
            variables: Optional mutation variables
            
        Returns:
            Mutation response data
            
        Raises:
            StrapiError: If mutation fails
        """
        return await self._execute_with_resilience(
            operation="execute_mutation",
            func=self._do_execute_mutation,
            mutation=mutation,
            variables=variables
        )

    async def _do_execute_mutation(
        self,
        mutation: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Internal method to execute GraphQL mutation.
        
        Args:
            mutation: GraphQL mutation
            variables: Optional mutation variables
            
        Returns:
            Mutation response data
            
        Raises:
            StrapiError: If mutation fails
        """
        result = await self._execute_request(
            "POST",
            "/graphql",
            json={
                "query": mutation,
                "variables": variables or {}
            }
        )
        
        if "errors" in result:
            raise StrapiError(f"GraphQL errors: {result['errors']}")
            
        return result.get("data", {})

    async def check_health(self) -> Dict[str, Any]:
        """Check client health.
        
        Returns:
            Health check results
        """
        results = await super().check_health()
        
        try:
            # Add client-specific health details
            if self._session:
                await self._validate_connection()
                results.update(details={
                    "connected": True,
                    "api_url": self._client_config['api_url'],
                    "circuit_breaker": self._circuit_breaker.get_status() if self._circuit_breaker else None,
                    "rate_limiter": self._rate_limiter.get_status() if self._rate_limiter else None,
                    "metrics": self.metrics.get_all() if self.metrics else {}
                })
                
        except Exception as e:
            results.update(details={
                "error": str(e),
                "connected": False
            })
            
        return results 