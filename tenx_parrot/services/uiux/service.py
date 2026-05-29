"""UIUX service implementation."""
from typing import Dict, Any, Optional, Set
import time

from core.base.service import BaseService
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert import AlertManager
from core.cache.manager import CacheManager
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation


class UIUXService(BaseService):
    """Service for managing UI/UX components."""
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: MetricsManager,
        alert_manager: AlertManager,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None,
        cache: Optional[CacheManager] = None
    ):
        """Initialize UI/UX service.
        
        Args:
            name: Service name
            config: Application configuration
            metrics: Metrics collector
            alert_manager: Alert manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
            cache: Optional cache manager
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        
        self.alert_manager = alert_manager
        self.cache = cache
        self.themes: Dict[str, Any] = {}
        self.preferences: Dict[str, Any] = {}

        # Initialize UIUX service settings from config
        self._cache_ttl = self._config.get("cache_ttl", 3600)  # 1 hour default
        self._max_themes = self._config.get("max_themes", 100)
        self._max_preferences = self._config.get("max_preferences", 1000)
        
        # Update health status with UIUX service specific details
        self._health_status.details.update({
            "cache_ttl": self._cache_ttl,
            "max_themes": self._max_themes,
            "max_preferences": self._max_preferences,
            "active_themes": len(self.themes),
            "active_preferences": len(self.preferences)
        })

        # Register metrics if available
        if self.metrics:
            self._register_metrics()

    def _register_metrics(self) -> None:
        """Register service metrics."""
        # Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Theme Metrics
        self.metrics.register_metric(
            f"{self.name}_active_themes",
            MetricType.GAUGE,
            f"Current number of active themes in {self.name}",
            labels={"type": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_theme_operations_total",
            MetricType.COUNTER,
            f"Total number of theme operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Preference Metrics
        self.metrics.register_metric(
            f"{self.name}_active_preferences",
            MetricType.GAUGE,
            f"Current number of active preferences in {self.name}",
            labels={"type": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_preference_operations_total",
            MetricType.COUNTER,
            f"Total number of preference operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Performance Metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Cache Metrics
        self.metrics.register_metric(
            f"{self.name}_cache_operations_total",
            MetricType.COUNTER,
            f"Total number of cache operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )

    @track_component_operation("initialize")
    async def _do_initialize(self) -> None:
        """Initialize UI/UX service."""
        try:
            # Load themes and preferences
            self.themes = self._load_themes()
            self.preferences = self._load_preferences()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_themes",
                    len(self.themes),
                    labels={"type": "total"}
                )
                self.metrics.record(
                    f"{self.name}_active_preferences",
                    len(self.preferences),
                    labels={"type": "total"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "initialize"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "error"}
                )
            raise

    @track_component_operation("start")
    async def _do_start(self) -> None:
        """Start UI/UX service."""
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
        """Stop UI/UX service."""
        try:
            # Clear themes and preferences
            self.themes.clear()
            self.preferences.clear()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_themes",
                    0,
                    labels={"type": "total"}
                )
                self.metrics.record(
                    f"{self.name}_active_preferences",
                    0,
                    labels={"type": "total"}
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

    def _load_themes(self) -> Dict[str, Any]:
        """Load UI themes from configuration."""
        try:
            if self.cache:
                themes = self.cache.get("uiux_themes")
                if themes:
                    return themes
                    
            # Load from config if not in cache
            themes = self.config.uiux.themes
            
            # Cache themes
            if self.cache:
                self.cache.set("uiux_themes", themes)
                
            return themes
            
        except Exception as e:
            self.logger.error(f"Failed to load themes: {e}")
            return {}
            
    def _load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from cache."""
        try:
            if self.cache:
                preferences = self.cache.get("uiux_preferences")
                if preferences:
                    return preferences
                    
            return {}
            
        except Exception as e:
            self.logger.error(f"Failed to load preferences: {e}")
            return {}
            
    async def _save_preferences(self) -> None:
        """Save user preferences to cache."""
        try:
            if self.cache:
                self.cache.set("uiux_preferences", self.preferences)
                
        except Exception as e:
            self.logger.error(f"Failed to save preferences: {e}")
            
    async def _check_health(self) -> Dict[str, Any]:
        """Check UI/UX service health."""
        health_info = {
            "status": "healthy",
            "metrics": {
                "themes": len(self.themes),
                "preferences": len(self.preferences)
            }
        }
        
        # Check cache if available
        if self.cache:
            try:
                await self.cache.ping()
                health_info["cache_status"] = "connected"
            except Exception as e:
                health_info["status"] = "degraded"
                health_info["cache_status"] = str(e)
                
        return health_info 