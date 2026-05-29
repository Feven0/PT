"""Test core functionality."""
import pytest
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock

from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.errors.exceptions import ServiceError, AuthorizationError, ValidationError
from core.types.components import HealthStatus, ComponentState
from core.types.metrics import MetricType
from .base import BaseTest
from .helpers import get_test_config

class TestCore(BaseTest):
    """Test core functionality."""
    
    @pytest.mark.asyncio
    async def test_config_validation(self, mock_config):
        """Test configuration validation."""
        # Test valid config
        assert mock_config.validate() is None
        
        # Test invalid config
        invalid_config = get_test_config({
            "name": "",  # Invalid empty name
            "stage": "invalid",  # Invalid environment
            "log_level": "INVALID"  # Invalid log level
        })
        with pytest.raises(ValueError):
            invalid_config.validate()
    
    @pytest.mark.asyncio
    async def test_logging(self):
        """Test logging functionality."""
        logger = BackendLogger(name="test")
        test_logger = logger.get_logger()
        
        # Test log levels
        with self.assertLogs(level=logging.DEBUG) as logs:
            test_logger.debug("Debug message")
            test_logger.info("Info message")
            test_logger.warning("Warning message")
            test_logger.error("Error message")
            
            assert len(logs.records) == 4
            assert any("Debug message" in record.getMessage() for record in logs.records)
            assert any("Error message" in record.getMessage() for record in logs.records)
        
        # Test structured logging
        with self.assertLogs(level=logging.INFO) as logs:
            test_logger.info(
                "Structured message",
                extra={
                    "context": "test",
                    "data": {"key": "value"}
                }
            )
            assert len(logs.records) == 1
            record = logs.records[0]
            assert "context" in record.__dict__
            assert record.__dict__["context"] == "test"
    
    @pytest.mark.asyncio
    async def test_metrics(self, mock_services):
        """Test metrics collection and management."""
        metrics = mock_services.metrics_manager
        
        # Test counter metrics
        counter = metrics.register_metric(
            name="test_counter",
            type=MetricType.COUNTER,
            description="Test counter",
            labels={"component": "test"}
        )
        
        metrics.record("test_counter", 1, labels={"component": "test"})
        assert metrics.get_metric("test_counter") is not None
        
        # Test gauge metrics
        gauge = metrics.register_metric(
            name="test_gauge",
            type=MetricType.GAUGE,
            description="Test gauge",
            labels={"component": "test"}
        )
        
        metrics.record("test_gauge", 42, labels={"component": "test"})
        assert metrics.get_metric("test_gauge") is not None
        
        # Test histogram metrics
        histogram = metrics.register_metric(
            name="test_histogram",
            type=MetricType.HISTOGRAM,
            description="Test histogram",
            labels={"component": "test"}
        )
        
        metrics.record("test_histogram", 5.0, labels={"component": "test"})
        assert metrics.get_metric("test_histogram") is not None
        
        # Test metric export
        metrics_data = await metrics.export()
        assert "test_counter" in metrics_data
        assert "test_gauge" in metrics_data
        assert "test_histogram" in metrics_data
    
    @pytest.mark.asyncio
    async def test_auth(self, mock_services):
        """Test authentication and authorization."""
        auth = mock_services.auth_manager
        
        # Test token generation
        test_user = {
            "id": "test_user",
            "email": "test@example.com",
            "roles": ["user"]
        }
        
        token = await auth.generate_token(test_user)
        assert token is not None
        
        # Test token validation
        validated_user = await auth.validate_token(token)
        assert validated_user["id"] == test_user["id"]
        assert validated_user["roles"] == test_user["roles"]
        
        # Test invalid token
        with pytest.raises(Exception):
            await auth.validate_token("invalid_token")
        
        # Test role-based access
        assert await auth.check_permission(test_user, "read", "profile")
        assert not await auth.check_permission(test_user, "admin", "system")
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling mechanisms."""
        # Test service error
        with pytest.raises(ServiceError) as exc:
            raise ServiceError("Test service error")
        assert str(exc.value) == "Test service error"
        
        # Test auth error
        with pytest.raises(AuthorizationError) as exc:
            raise AuthorizationError("Test auth error")
        assert str(exc.value) == "Test auth error"
        
        # Test validation error
        with pytest.raises(ValidationError) as exc:
            raise ValidationError("Test validation error")
        assert str(exc.value) == "Test validation error"
    
    @pytest.mark.asyncio
    async def test_dependency_injection(self, mock_services):
        """Test dependency injection system."""
        # Test service injection
        assert mock_services.webrtc_service is not None
        assert mock_services.websocket_service is not None
        
        # Test repository injection
        assert mock_services.interview_repository is not None
        assert mock_services.storage_repository is not None
        
        # Test infrastructure injection
        assert mock_services.s3_client is not None
        assert mock_services.weaviate_client is not None
        
        # Test core component injection
        assert mock_services.metrics_manager is not None
        assert mock_services.auth_manager is not None
    
    @pytest.mark.asyncio
    async def test_lifecycle_management(self, mock_services):
        """Test component lifecycle management."""
        container = mock_services
        
        # Test health checks
        health = await container.check_health()
        assert health.status == "healthy"
        
        # Test shutdown
        await container.stop()
        assert not container.is_running
        
        # Test cleanup
        await container.cleanup()
        assert not container.is_initialized 