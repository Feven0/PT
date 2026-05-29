"""Job service implementation."""
from typing import Dict, Any, Optional, Set
import asyncio
import time

from core.base.service import BaseService
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alerts import AlertManager
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation


class JobService(BaseService):
    """Service for managing background jobs."""
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: MetricsManager,
        alert_manager: AlertManager,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize job service.
        
        Args:
            name: Service name
            config: Application configuration
            metrics: Metrics collector
            alert_manager: Alert manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        
        self.alert_manager = alert_manager
        self.jobs: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, Any] = {}
        self.job_metrics: Dict[str, Dict[str, Any]] = {}

        # Initialize job service settings from config
        self._max_concurrent_jobs = self._config.get("max_concurrent_jobs", 10)
        self._job_timeout = self._config.get("job_timeout", 3600)  # 1 hour default
        self._max_retries = self._config.get("max_retries", 3)
        
        # Update health status with job service specific details
        self._health_status.details.update({
            "max_concurrent_jobs": self._max_concurrent_jobs,
            "job_timeout": self._job_timeout,
            "max_retries": self._max_retries,
            "active_jobs": len(self.jobs)
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
        
        # Job Metrics
        self.metrics.register_metric(
            f"{self.name}_active_jobs",
            MetricType.GAUGE,
            f"Current number of active jobs in {self.name}",
            labels={"type": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_job_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of jobs in {self.name}",
            labels={"job_id": "", "type": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_job_queue_size",
            MetricType.GAUGE,
            f"Current size of job queue in {self.name}",
            labels={"type": ""}
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

    @track_component_operation("initialize")
    async def _do_initialize(self) -> None:
        """Initialize job service."""
        try:
            # Initialize job tracking
            self.jobs.clear()
            self.results.clear()
            self.job_metrics.clear()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_jobs",
                    0,
                    labels={"type": "total", "status": "active"}
                )
                self.metrics.record(
                    f"{self.name}_job_queue_size",
                    0,
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
        """Start job service."""
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
        """Stop job service."""
        try:
            # Cancel all running jobs
            for job_id, task in self.jobs.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    
            # Clear job tracking
            self.jobs.clear()
            self.results.clear()
            self.job_metrics.clear()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_active_jobs",
                    0,
                    labels={"type": "total", "status": "active"}
                )
                self.metrics.record(
                    f"{self.name}_job_queue_size",
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

    async def _cleanup_loop(self) -> None:
        """Background task to cleanup completed jobs."""
        while True:
            try:
                # Remove completed jobs older than retention period
                for job_id, task in list(self.jobs.items()):
                    if task.done():
                        # Store result
                        try:
                            self.results[job_id] = task.result()
                        except Exception as e:
                            self.results[job_id] = str(e)
                            
                        # Remove job
                        del self.jobs[job_id]
                        
                        # Update metrics
                        if job_id in self.job_metrics:
                            metrics = self.job_metrics[job_id]
                            metrics["completed_at"] = asyncio.get_event_loop().time()
                            metrics["duration"] = metrics["completed_at"] - metrics["started_at"]
                            
                            if self.metrics:
                                self.metrics.histogram(
                                    "job_duration_seconds",
                                    metrics["duration"],
                                    labels={"job_id": job_id}
                                )
                
                # Sleep before next cleanup
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Job cleanup error: {e}")
                await asyncio.sleep(60)  # Retry after error 