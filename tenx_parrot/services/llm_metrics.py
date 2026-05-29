"""LLM metrics service implementation."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from core.types.components import ComponentState
from core.base import BaseService
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from repositories.llm_metrics import LLMMetricsRepository

class LLMMetricsService(BaseService):
    """Service for managing LLM metrics."""

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        llm_metrics_repository: Optional[LLMMetricsRepository] = None,
        dependencies: Optional[Dict[str, Any]] = None
    ):
        """Initialize LLM metrics service.
        
        Args:
            name: Service name
            config: Application configuration
            metrics: Optional metrics manager
            llm_metrics_repository: Optional LLM metrics repository
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        
        self.llm_metrics_repository = llm_metrics_repository

        self._state = ComponentState.RUNNING

    async def record_metric(self, metric: Dict[str, Any]) -> None:
        """Record an LLM metric.
        
        Args:
            metric: LLM metric to record
        """
        if not self.llm_metrics_repository:
            self.logger.warning("LLM metrics repository not initialized")
            return
            
        await self.llm_metrics_repository.store_llm_metric(metric)

    async def get_provider_stats(
        self,
        provider: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics for a specific provider.
        
        Args:
            provider: Provider name
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Provider statistics
        """
        if not self.llm_metrics_repository:
            self.logger.warning("LLM metrics repository not initialized")
            return {}
            
        metrics = await self.llm_metrics_repository.get_provider_metrics(
            provider,
            start_date,
            end_date
        )
        
        if not metrics:
            return {}
            
        # Calculate provider statistics
        stats = {
            "total_requests": sum(m["total_requests"] for m in metrics),
            "success_rate": sum(m["successful_requests"] for m in metrics) / sum(m["total_requests"] for m in metrics) if metrics else 0,
            "total_tokens": sum(m["total_tokens"] for m in metrics),
            "average_latency": sum(m["average_latency"] for m in metrics) / len(metrics),
            "error_rate": sum(m["error_rate"] for m in metrics) / len(metrics),
            "models_used": list(set(m["model"] for m in metrics))
        }
        
        return stats

    async def get_model_stats(
        self,
        model: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics for a specific model.
        
        Args:
            model: Model name
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Model statistics
        """
        if not self.llm_metrics_repository:
            self.logger.warning("LLM metrics repository not initialized")
            return {}
            
        metrics = await self.llm_metrics_repository.get_model_metrics(
            model,
            start_date,
            end_date
        )
        
        if not metrics:
            return {}
            
        # Calculate model statistics
        stats = {
            "total_requests": sum(m["total_requests"] for m in metrics),
            "success_rate": sum(m["successful_requests"] for m in metrics) / sum(m["total_requests"] for m in metrics) if metrics else 0,
            "total_tokens": sum(m["total_tokens"] for m in metrics),
            "average_latency": sum(m["average_latency"] for m in metrics) / len(metrics),
            "error_rate": sum(m["error_rate"] for m in metrics) / len(metrics),
            "providers": list(set(m["provider"] for m in metrics))
        }
        
        return stats

    async def get_usage_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get usage summary for the specified time period.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Usage summary
        """
        if not self.llm_metrics_repository:
            self.logger.warning("LLM metrics repository not initialized")
            return {}
            
        return await self.llm_metrics_repository.get_summary_metrics(days)

    async def get_metrics_report(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get detailed metrics report with filtering and pagination.
        
        Args:
            provider: Filter by provider
            model: Filter by model
            start_date: Start date for filtering
            end_date: End date for filtering
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Metrics report
        """
        if not self.llm_metrics_repository:
            self.logger.warning("LLM metrics repository not initialized")
            return {
                "metrics": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
            
        metrics = await self.llm_metrics_repository.get_llm_metrics(
            provider=provider,
            model=model,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        
        return {
            "metrics": metrics,
            "total": len(metrics),
            "page": page,
            "page_size": page_size
        } 