"""Metrics and health check routes."""
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from core.di import get_container
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager, AlertLevel
from core.recovery.manager import RecoveryManager
from core.types.recovery import RecoveryStrategy
from services.storage import StorageService
from services.interview import InterviewService
from services.chat import ChatService
from services.webrtc import WebRTCService
from domain.models.health import (
    HealthStatus,
    SystemHealth,
    ServiceHealth,
    CacheHealth,
    QueueHealth
)



router = APIRouter(prefix="/metrics", tags=["metrics"])


def get_storage_service() -> StorageService:
    """Get storage service instance."""
    container = get_container()
    return container.storage_service


def get_interview_service() -> InterviewService:
    """Get interview service instance."""
    container = get_container()
    return container.interview_service


def get_chat_service() -> ChatService:
    """Get chat service instance."""
    container = get_container()
    return container.chat_service


def get_webrtc_service() -> WebRTCService:
    """Get webrtc service instance."""
    container = get_container()
    return container.webrtc_service


def get_alert_manager() -> AlertManager:
    """Get alert manager instance."""
    container = get_container()
    return container.alert_manager


def get_metrics() -> Optional[MetricsManager]:
    """Get metrics manager instance."""
    container = get_container()
    return container.metrics


def get_recovery_manager() -> RecoveryManager:
    """Get recovery manager instance."""
    container = get_container()
    return container.recovery_manager


@router.get("/health")
async def check_health(
    storage: StorageService = Depends(get_storage_service),
    interview: InterviewService = Depends(get_interview_service),
    chat: ChatService = Depends(get_chat_service),
    webrtc: WebRTCService = Depends(get_webrtc_service),
    alert_manager: AlertManager = Depends(get_alert_manager),
    metrics: Optional[MetricsManager] = Depends(get_metrics)
) -> SystemHealth:
    """Check system health."""
    try:
        # Get storage health
        storage_health = await storage.check_health()
        
        # Get service health
        services = {
            "interview": await interview.check_health(),
            "chat": await chat.check_health(),
            "webrtc": await webrtc.check_health()
        }
        
        # Get cache health if available
        cache_health = None
        if hasattr(Container, 'cache'):
            cache = Container.cache()
            if cache:
                cache_health = await cache.check_health()
        
        # Get queue health if available
        queue_health = None
        if hasattr(Container, 'queue'):
            queue = Container.queue()
            if queue:
                queue_health = await queue.check_health()
        
        # Create system health report
        health = SystemHealth(
            status=HealthStatus.UNKNOWN,
            strapi=storage_health.get('strapi'),
            weaviate=storage_health.get('weaviate'),
            cache=cache_health,
            queue=queue_health,
            services=services,
            last_check=datetime.now()
        )
        
        # Update overall status
        health.status = health.get_overall_status()
        
        # Check for alerts
        health_data = {
            "strapi": storage_health.get('strapi'),
            "weaviate": storage_health.get('weaviate'),
            "cache": cache_health,
            "queue": queue_health,
            **services
        }
        await alert_manager.check_alerts(health_data)
        
        # Record metrics
        if metrics:
            metrics.gauge("system_health_status", health.status.value)
            if health.strapi:
                metrics.gauge("strapi_latency_ms", health.strapi.latency_ms)
                metrics.gauge("strapi_error_rate", health.strapi.error_rate)
            if health.weaviate:
                metrics.gauge("weaviate_latency_ms", health.weaviate.latency_ms)
                metrics.gauge("weaviate_error_rate", health.weaviate.error_rate)
            if storage_health.get('storage_infrastructure'):
                metrics.gauge(
                    "storage_infrastructure_latency_ms", 
                    storage_health['storage_infrastructure'].latency_ms
                )
                metrics.gauge(
                    "storage_infrastructure_error_rate", 
                    storage_health['storage_infrastructure'].error_rate
                )
                metrics.gauge(
                    "storage_infrastructure_status",
                    storage_health['storage_infrastructure'].status.value
                )
        
        return health
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check system health: {str(e)}"
        )


@router.get("/alerts")
async def get_alerts(
    severity: Optional[AlertLevel] = None,
    alert_manager: AlertManager = Depends(get_alert_manager)
) -> List[Dict]:
    """Get active alerts."""
    return alert_manager.get_active_alerts(severity)


@router.get("/alerts/history")
async def get_alert_history(
    severity: Optional[AlertLevel] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    alert_manager: AlertManager = Depends(get_alert_manager)
) -> List[Dict]:
    """Get alert history."""
    return alert_manager.get_alert_history(severity, start_time, end_time)


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    user: str,
    alert_manager: AlertManager = Depends(get_alert_manager)
) -> Dict:
    """Acknowledge an alert."""
    await alert_manager.acknowledge_alert(alert_id, user)
    return {"status": "acknowledged"}


@router.post("/recovery/{component}")
async def trigger_recovery(
    component: str,
    recovery_strategy: Optional[RecoveryStrategy] = None,
    recovery_manager: RecoveryManager = Depends(get_recovery_manager)
) -> Dict:
    """Trigger recovery action for a component."""
    success = await recovery_manager.attempt_recovery(component, recovery_strategy)
    return {
        "status": "success" if success else "failed",
        "component": component
    }


@router.get("/recovery/history")
async def get_recovery_history(
    component: Optional[str] = None,
    recovery_strategy: Optional[RecoveryStrategy] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    success_only: bool = False,
    recovery_manager: RecoveryManager = Depends(get_recovery_manager)
) -> List[Dict]:
    """Get recovery action history."""
    return recovery_manager.get_recovery_history(
        component,
        recovery_strategy,
        start_time,
        end_time,
        success_only
    )


@router.get("/health/infrastructure")
async def check_infrastructure(
    storage: StorageService = Depends(get_storage_service),
    metrics: Optional[MetricsManager] = Depends(get_metrics)
) -> Dict:
    """Check infrastructure health."""
    try:
        # Get storage health
        storage_health = await storage.check_health()
        
        # Get cache health if available
        cache_health = None
        container = get_container()
        if hasattr(container, 'cache'):
            cache = container.cache
            if cache:
                cache_health = await cache.check_health()
        
        # Get queue health if available
        queue_health = None
        if hasattr(container, 'queue'):
            queue = container.queue
            if queue:
                queue_health = await queue.check_health()
        
        return {
            "storage": storage_health,
            "cache": cache_health.dict() if cache_health else None,
            "queue": queue_health.dict() if queue_health else None,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check infrastructure health: {str(e)}"
        )


@router.get("/health/liveness")
async def check_liveness() -> Dict[str, str]:
    """Simple liveness check endpoint."""
    return {"status": "alive"} 