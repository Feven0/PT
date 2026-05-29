"""Alert manager implementation."""
from typing import Dict, Any, Optional, List, Set, Union
from datetime import datetime, timezone

from core.base.manager import BaseManager
from core.types.alert import AlertPriority, AlertMessage, AlertLevel, AlertProviderProtocol
from core.types.components import ComponentState, HealthStatus, HealthStatusInfo
from core.types.metrics import MetricType
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.config import AppConfig
from .providers import EmailAlertProvider, SlackAlertProvider, TelegramAlertProvider


class AlertManager(BaseManager):
    """Alert manager implementation."""
    
    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional['MetricsManager'] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Initialize alert manager."""
        super().__init__(name=name, 
                        config=config, 
                        metrics=metrics,
                        logger=logger,
                        dependencies=dependencies)
        
        # Initialize providers
        self._providers: Dict[str, AlertProviderProtocol] = {}
        self.enabled_providers: Set[str] = set()
        self.last_alert_time: Optional[datetime] = None
        
        # Get settings from config dict
        self._enabled = self._config.get("enabled", True)
        self._strategy = self._config.get("notification_strategy", "priority")
        self._default_provider = self._config.get("default_provider", "email")
        self._rate_limit = self._config.get("rate_limit", 100)
        self._cb_threshold = self._config.get("circuit_breaker_threshold", 5)
        self._cb_timeout = self._config.get("circuit_breaker_timeout", 60)
        
        # Priority routes configuration
        self._priority_routes = self._config.get("priority_routes", {
            AlertPriority.CRITICAL: ["email", "slack", "telegram"],
            AlertPriority.HIGH: ["email", "slack"],
            AlertPriority.MEDIUM: ["slack"],
            AlertPriority.LOW: ["slack"]
        })

    async def _initialize_impl(self) -> None:
        """Initialize alert manager."""
        await super()._initialize_impl()
        
        # Register metrics
        if self.metrics:
            self.metrics.register_metric(
                name="alerts_total",
                mtype=MetricType.COUNTER,
                description="Total number of alerts sent",
                labels={"provider":"", "status":"", "priority":""}
            )
            
            self.metrics.register_metric(
                name="alert_send_duration_seconds",
                mtype=MetricType.HISTOGRAM,
                description="Time taken to send alerts",
                labels={"provider":"", "priority":""}
            )
            
            self.metrics.register_metric(
                name="alert_errors_total",
                mtype=MetricType.COUNTER,
                description="Total number of alert sending errors",
                labels={"provider":"", "error_type":""}
            )

        # Provider class mapping
        provider_classes = {
            "email": EmailAlertProvider,
            "slack": SlackAlertProvider,
            "telegram": TelegramAlertProvider
        }
        
        # Get provider configs from nested structure
        providers_config = self._config.get("providers", {})
        
        # Initialize each provider
        for provider_name, provider_class in provider_classes.items():
            provider_config = providers_config.get(provider_name, {})
            if provider_config.get("enabled", True):
                try:
                    provider = provider_class(
                        name=f"{self.name}.{provider_name}",
                        config=provider_config,
                    )
                    await self.register_provider(provider_name, provider)
                    # Register templates
                    templates = self._config.get("templates", {})
                    for template_name, template_data in templates.items():
                        provider.register_template(
                            name=template_name,
                            subject=template_data.get("subject", ""),
                            message=template_data.get("message", ""),
                            priority=template_data.get("priority", "low")
                        )
                except Exception as e:
                    self.logger.error(
                        f"Failed to initialize {provider_name} provider",
                        error=str(e),
                        provider=provider_name
                    )

    async def register_provider(
        self,
        name: str,
        provider: AlertProviderProtocol,
        enabled: bool = True
    ) -> None:
        """Register alert provider.
        
        Args:
            name: Provider name
            provider: Provider instance
            enabled: Whether provider should be enabled
        """
        self._providers[name] = provider
        if enabled:
            self.enabled_providers.add(name)
            
        self.logger.info(
            "provider_registered",
            provider=name,
            enabled=enabled
        )

    async def _check_provider_health(self, provider: str) -> Dict[str, Any]:
        """Check health of a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Provider health status
        """
        provider_instance = self._providers.get(provider)
        if not provider_instance:
            return {
                "status": HealthStatus.UNKNOWN,
                "error": f"Provider {provider} not found"
            }
            
        try:
            is_healthy = await provider_instance.check_health()
            return {
                "status": HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "enabled": provider in self.enabled_providers
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "last_check": datetime.now(timezone.utc).isoformat(),
                "enabled": provider in self.enabled_providers
            }

    async def check_health(self) -> HealthStatusInfo:
        """Check component health.
        
        Returns:
            Health status information
        """
        provider_health = {
            provider: await self._check_provider_health(provider)
            for provider in self._providers
        }
        
        alerts_total = self.metrics.get_metric("alerts_total") or 0
        errors_total = self.metrics.get_metric("alert_errors_total") or 0
        
        return HealthStatusInfo(
            status=self._get_health_status(),
            details={
                "providers": provider_health,
                "metrics": {
                    "alerts_sent_total": alerts_total,
                    "errors_total": errors_total
                },
                "last_alert_time": self.last_alert_time.isoformat() if self.last_alert_time else None,
                "enabled_providers": list(self.enabled_providers),
                "state": self.state
            },
            timestamp=datetime.now(timezone.utc),
            state_info=self.state_info
        )

    def _get_health_status(self) -> HealthStatus:
        """Get overall health status.
        
        Returns:
            Health status
        """
        if not self.enabled_providers:
            return HealthStatus.DEGRADED
            
        return HealthStatus.HEALTHY if self.state == ComponentState.RUNNING else HealthStatus.UNHEALTHY

    def _get_providers_for_priority(self, priority: AlertPriority) -> List[str]:
        """Get providers for priority level.
        
        Args:
            priority: Alert priority
            
        Returns:
            List of provider names
        """
        return self._priority_routes.get(priority, [self._default_provider])

    async def create_message(
        self,
        subject: str,
        content: str,
        priority: AlertPriority,
        metadata: Optional[Dict[str, Any]] = None,
        recipients: Optional[List[str]] = None
    ) -> AlertMessage:
        """Create alert message.
        
        Args:
            subject: Message subject
            content: Message content
            priority: Message priority
            metadata: Optional metadata
            recipients: Optional recipients
            
        Returns:
            Alert message
        """
        return AlertMessage(
            subject=subject,
            message=content,
            priority=priority,
            metadata=metadata,
            recipients=recipients
        )

    async def send_message(
        self,
        message: AlertMessage,
        providers: Optional[List[str]] = None
    ) -> bool:
        """Send alert message through providers.
        
        Args:
            message: Alert message
            providers: Optional list of providers to use
            
        Returns:
            True if message was sent successfully
        """
        target_providers = providers or self._get_providers_for_priority(message.priority)
        success = False
        
        for provider in target_providers:
            if provider not in self._providers:
                self.logger.warning(f"Provider {provider} not found")
                continue
                
            if provider not in self.enabled_providers:
                self.logger.warning(f"Provider {provider} not enabled")
                continue
                
            try:
                start_time = datetime.now(timezone.utc)
                await self._providers[provider].send(message)
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        name="alerts_total",
                        value=1,
                        labels={
                            "provider": provider,
                            "status": "success",
                            "priority": message.priority
                        }
                    )
                    
                    self.metrics.record(
                        name="alert_send_duration_seconds",
                        value=duration,
                        labels={
                            "provider": provider,
                            "priority": message.priority
                        }
                    )
                
                success = True
                self.last_alert_time = datetime.now(timezone.utc)
                
            except Exception as e:
                self.logger.error(
                    f"Failed to send alert via {provider}",
                    error=str(e)
                )
                
                if self.metrics:
                    self.metrics.record(
                        name="alert_errors_total",
                        value=1,
                        labels={
                            "provider": provider,
                            "error_type": e.__class__.__name__
                        }
                    )
                    
                    self.metrics.record(
                        name="alerts_total",
                        value=1,
                        labels={
                            "provider": provider,
                            "status": "error",
                            "priority": message.priority
                        }
                    )
                
        # Update state info
        self.state_info.update(
            state=self.state,
            metadata={
                "enabled_providers": list(self.enabled_providers),
                "last_alert_time": self.last_alert_time,
                "alert_count": await self.metrics.get_metric("alerts_total")
            }
        )
        
        return success

    async def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "info",
        tags: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send alert with simplified interface.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            tags: Optional tags
            
        Returns:
            True if alert was sent successfully
        """
        # Map severity to priority
        priority_map = {
            "critical": AlertPriority.CRITICAL,
            "error": AlertPriority.HIGH,
            "warning": AlertPriority.MEDIUM,
            "info": AlertPriority.LOW
        }
        priority = priority_map.get(severity.lower(), AlertPriority.LOW)
        
        # Create and send message
        alert_message = await self.create_message(
            subject=title,
            content=message,
            priority=priority,
            metadata=tags
        )
        
        return await self.send_message(alert_message) 