"""Base test class and utilities."""
import pytest
import asyncio
from typing import Dict, Any, Optional, Generator
from contextlib import contextmanager
import logging

from core.config import AppConfig
from core.di.container import Container
from .mock_config import create_mock_config

class BaseTest:
    """Base test class with common utilities."""
    
    @pytest.fixture(autouse=True)
    def setup_logging(self):
        """Setup test logging."""
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @pytest.fixture
    def config(self) -> AppConfig:
        """Provide test configuration."""
        return create_mock_config()
    
    @pytest.fixture
    async def container(self, config: AppConfig) -> Generator[Container, None, None]:
        """Provide initialized container."""
        container = Container(config)
        try:
            await container.initialize()
            await container.start()
            yield container
        finally:
            await container.stop()
            await container.cleanup()
    
    @contextmanager
    def assert_logs(self, expected_messages: list, level=logging.INFO):
        """Assert that specific log messages are emitted.
        
        Args:
            expected_messages: List of expected log messages
            level: Log level to capture
        """
        with self.assertLogs(level=level) as logs:
            yield
            messages = [record.getMessage() for record in logs.records]
            for expected in expected_messages:
                assert any(expected in msg for msg in messages), \
                    f"Expected log message '{expected}' not found in {messages}"
    
    @contextmanager
    def assert_metrics(self, container: Container, expected_metrics: Dict[str, Any]):
        """Assert that specific metrics are recorded.
        
        Args:
            container: Test container
            expected_metrics: Dictionary of metric name to expected value
        """
        metrics_before = {
            name: metric._value.get()
            for name, metric in container.metrics_manager._metrics.items()
            if name in expected_metrics
        }
        
        yield
        
        metrics_after = {
            name: metric._value.get()
            for name, metric in container.metrics_manager._metrics.items()
            if name in expected_metrics
        }
        
        for name, expected in expected_metrics.items():
            if callable(expected):
                assert expected(metrics_before.get(name, 0), metrics_after.get(name, 0)), \
                    f"Metric {name} did not match expected condition"
            else:
                assert metrics_after.get(name, 0) - metrics_before.get(name, 0) == expected, \
                    f"Metric {name} did not increase by {expected}"
    
    async def assert_health_check(self, container: Container, component_name: str):
        """Assert that a component's health check passes.
        
        Args:
            container: Test container
            component_name: Name of component to check
        """
        component = getattr(container, f"{component_name}")
        health = await component.check_health()
        assert health.status == "healthy", \
            f"Component {component_name} health check failed: {health.details}"
    
    def get_component_metrics(self, container: Container, component_name: str) -> Dict[str, Any]:
        """Get all metrics for a component.
        
        Args:
            container: Test container
            component_name: Component name
            
        Returns:
            Dictionary of metric name to current value
        """
        return {
            name: metric._value.get()
            for name, metric in container.metrics_manager._metrics.items()
            if name.startswith(f"{component_name}_")
        }
    
    async def wait_for_condition(self, condition: callable, timeout: float = 5.0, interval: float = 0.1):
        """Wait for a condition to become true.
        
        Args:
            condition: Callable that returns bool
            timeout: Maximum time to wait in seconds
            interval: Check interval in seconds
        """
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            if condition():
                return
            await asyncio.sleep(interval)
        raise TimeoutError(f"Condition not met within {timeout} seconds") 