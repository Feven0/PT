"""User repository implementation."""
from typing import Dict, Any, Optional, Set, List, Union
from datetime import datetime, timedelta
import time

from core.types.base import ComponentNames as CN
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.cache.manager import CacheManager
from core.base import BaseRepository
from core.config import AppConfig
from core.resilience.rate_limiter import RateLimiter
from core.resilience.retry import RetryWithBackoff
from core.types.metrics import MetricType
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.strapi.schemas import IPersonaAllUser, IPersonaAllUserSchema

class UserError(Exception):
    """Base user error."""
    pass

class ConfigError(UserError):
    """Configuration error."""
    pass

class UserNotFoundError(UserError):
    """Error raised when user is not found."""
    pass

class UserCreationError(UserError):
    """Error raised when user creation fails."""
    pass

class UserUpdateError(UserError):
    """Error raised when user update fails."""
    pass

class UserDeletionError(UserError):
    """Error raised when user deletion fails."""
    pass

class UserRepository(BaseRepository[IPersonaAllUser]):
    """User repository implementation."""

    REQUIRED_CONFIG = {
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int
    }

    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional['MetricsManager'] = None,
        strapi_client: Optional[StrapiClient] = None,
        cache: Optional[CacheManager] = None,
        rate_limiter: Optional[RateLimiter] = None,
        retry_manager: Optional[RetryWithBackoff] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Initialize user repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Optional metrics manager
            strapi_client: Optional Strapi client
            cache: Optional cache manager
            dependencies: Optional set of dependency names
        """
        # Initialize base repository
        required_deps = {CN.metrics_manager, 
                         CN.cache_manager, 
                         CN.strapi_client,
                         CN.rate_limiter,
                         CN.retry_manager
                         }
        if dependencies:
            required_deps.update(dependencies)
            
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            cache=cache,
            dependencies=required_deps,
            required_config=self.REQUIRED_CONFIG
        )
        

        
        # Get validated repository config
        self._repository_config = self._config

        # Initialize user repository settings from validated config
        self._cache_ttl = self._repository_config.get('cache_ttl', 3600)
        self._batch_size = self._repository_config.get('batch_size', 100)
        self._max_retries = self._repository_config.get('max_retries', 3)
        
        # Initialize resilience components
        if metrics:
            self._register_metrics()
            
        # Initialize rate limiter with validated config
        self._rate_limiter = rate_limiter
        self._retry_manager = retry_manager
        
  
        
        # Get Strapi service for users
        self._user_service = (StrapiServiceFactory(strapi_client, metrics)
                               .all_user_service)
        
        # Update health status with config details
        self.update_health_details({
            "config": {
                "cache_ttl": self._cache_ttl,
                "batch_size": self._batch_size,
                "max_retries": self._max_retries
            }
        })
        
    def _register_metrics(self) -> None:
        """Register repository metrics."""
        # Operation metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Performance metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_batch_size",
            MetricType.GAUGE,
            f"Current batch size in {self.name}",
            labels={"operation": ""}
        )
        
        # Cache metrics
        self.metrics.register_metric(
            f"{self.name}_cache_hits_total",
            MetricType.COUNTER,
            f"Total number of cache hits in {self.name}",
            labels={"operation": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_cache_misses_total", 
            MetricType.COUNTER,
            f"Total number of cache misses in {self.name}",
            labels={"operation": ""}
        )
        
        # Error metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"type": "", "operation": ""}
        )
        
        # Rate limit metrics
        self.metrics.register_metric(
            f"{self.name}_rate_limit_hits_total",
            MetricType.COUNTER,
            f"Total number of rate limit hits in {self.name}",
            labels={"operation": ""}
        )
        
        # Retry metrics
        self.metrics.register_metric(
            f"{self.name}_retries_total",
            MetricType.COUNTER,
            f"Total number of retries in {self.name}",
            labels={"operation": ""}
        )
        
    async def get(self, id: str) -> Optional[IPersonaAllUser]:
        """Get user by ID.
        
        Args:
            id: User ID (string)
            
        Returns:
            User data if found, None otherwise
            
        Raises:
            UserNotFoundError: If user is not found
            UserError: If an error occurs during retrieval
        """
        operation = "get_user"
        start_time = time.time()
        
        try:
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Try cache first
                cache_key = f"user:{id}"
                if self._cache:
                    if cached := await self._cache.get(cache_key):
                        if self.metrics:
                            self.metrics.record(
                                f"{self.name}_cache_hits",
                                1
                            )
                        return IPersonaAllUser(**cached)
                
                # Get from Strapi
                user = await self._user_service.find_one(id)
                
                # Cache result
                if user and self._cache:
                    await self._cache.set(cache_key, user.dict(), ttl=self._cache_ttl)
                
                if not user:
                    raise UserNotFoundError(f"User with ID {id} not found")
                    
                return user
                
        except UserNotFoundError:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_not_found",
                    1,
                    labels={"user_id": str(id)}
                )
            raise
        except Exception as e:
            self.logger.error(f"Failed to get user: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_get_error",
                    1,
                    labels={"error": str(e)}
                )
            raise UserError(f"Failed to get user: {str(e)}") from e

    async def list(
        self,
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[IPersonaAllUser]:
        """List users with optional filtering and pagination.
        
        Args:
            filter: Optional filter criteria
            sort: Optional sort criteria
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of users
        """
        operation = "list_users"
        start_time = time.time()
        
        try:
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Build pagination
                pagination = {}
                if limit is not None:
                    pagination["pageSize"] = min(limit, self._batch_size)
                if offset is not None:
                    pagination["page"] = (offset // pagination.get("pageSize", self._batch_size)) + 1
                
                # Get from Strapi
                users = await self._user_service.find_many(
                    filters=filter,
                    sort=sort,
                    pagination=pagination
                )
                
                return users
                
        except Exception as e:
            self.logger.error(f"Failed to list users: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_list_error",
                    1,
                    labels={"error": str(e)}
                )
            raise

    async def create(self, user: IPersonaAllUser) -> IPersonaAllUser:
        """Create new user.
        
        Args:
            user: User data
            
        Returns:
            Created user
            
        Raises:
            UserCreationError: If user creation fails
        """
        operation = "create_user"
        start_time = time.time()
        
        try:
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Create in Strapi
                created = await self._user_service.create(user)
                
                # Cache result
                if created and self._cache:
                    cache_key = f"user:{created.id}"
                    await self._cache.set(cache_key, created.dict(), ttl=self._cache_ttl)
                
                if not created:
                    raise UserCreationError("Failed to create user")
                
                return created
                
        except Exception as e:
            self.logger.error(f"Failed to create user: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_create_error",
                    1,
                    labels={"error": str(e)}
                )
            raise UserCreationError(f"Failed to create user: {str(e)}") from e

    async def update(self, id: str, user: IPersonaAllUser) -> Optional[IPersonaAllUser]:
        """Update existing user.
        
        Args:
            id: User ID (string)
            user: Updated user data
            
        Returns:
            Updated user if found, None otherwise
            
        Raises:
            UserNotFoundError: If user is not found
            UserUpdateError: If user update fails
        """
        operation = "update_user"
        start_time = time.time()
        
        try:
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Check if user exists
                existing = await self.get(id)
                if not existing:
                    raise UserNotFoundError(f"User with ID {id} not found")
                
                # Update in Strapi
                updated = await self._user_service.update(id, user)
                
                # Update cache
                if updated and self._cache:
                    cache_key = f"user:{id}"
                    await self._cache.set(cache_key, updated.dict(), ttl=self._cache_ttl)
                
                if not updated:
                    raise UserUpdateError(f"Failed to update user with ID {id}")
                
                return updated
                
        except UserNotFoundError:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_not_found",
                    1,
                    labels={"user_id": str(id)}
                )
            raise
        except Exception as e:
            self.logger.error(f"Failed to update user: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_update_error",
                    1,
                    labels={"error": str(e)}
                )
            raise UserUpdateError(f"Failed to update user: {str(e)}") from e

    async def delete(self, id: str) -> bool:
        """Delete user.
        
        Args:
            id: User ID (string)
            
        Returns:
            True if user was deleted, False otherwise
            
        Raises:
            UserNotFoundError: If user is not found
            UserDeletionError: If user deletion fails
        """
        operation = "delete_user"
        start_time = time.time()
        
        try:
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Check if user exists
                existing = await self.get(id)
                if not existing:
                    raise UserNotFoundError(f"User with ID {id} not found")
                
                # Delete from Strapi
                result = await self._user_service.delete(id)
                
                # Delete from cache
                if self._cache:
                    await self._cache.delete(f"user:{id}")
                
                if not result:
                    raise UserDeletionError(f"Failed to delete user with ID {id}")
                
                return True
                
        except UserNotFoundError:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_not_found",
                    1,
                    labels={"user_id": str(id)}
                )
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete user: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_delete_error",
                    1,
                    labels={"error": str(e)}
                )
            raise UserDeletionError(f"Failed to delete user: {str(e)}") from e

    async def get_all_users(
        self, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all users with optional pagination.
        
        Args:
            limit: Optional maximum number of users to return
            offset: Optional offset for pagination
            
        Returns:
            List of user objects
            
        Raises:
            UserError: If an error occurs during retrieval
        """
        try:
            # Record operation metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_all_users", "status": "started"}
                )
            
            # Apply cache if available
            cache_key = f"all_users_{limit}_{offset}"
            if self._cache:
                cached_result = await self._cache.get(cache_key)
                if cached_result:
                    if self.metrics:
                        self.metrics.record(
                            f"{self.name}_cache_hits_total",
                            1,
                            labels={"operation": "get_all_users"}
                        )
                    return cached_result
                
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_cache_misses_total",
                        1,
                        labels={"operation": "get_all_users"}
                    )
            
            # Construct pagination
            pagination = {}
            if limit is not None:
                pagination["pageSize"] = min(limit, self._batch_size)
            if offset is not None:
                pagination["page"] = (offset // pagination.get("pageSize", self._batch_size)) + 1
            
            # Get users from Strapi
            users = await self._user_service.find_many(
                filters={},
                sort=None,
                pagination=pagination
            )
            
            # Convert to dictionary format for caching
            user_dicts = [user.dict() for user in users]
            
            # Cache results if cache is available
            if self._cache:
                await self._cache.set(cache_key, user_dicts, ttl=self._cache_ttl)
            
            # Record success metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_all_users", "status": "success"}
                )
            
            return users
            
        except Exception as e:
            # Record error metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_all_users", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "get_all_users"}
                )
            
            if self.logger:
                self.logger.error(
                    "Failed to get all users",
                    context="user_repository",
                    error=str(e)
                )
            
            raise UserError(f"Failed to get all users: {str(e)}") from e 