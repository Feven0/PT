"""Test API endpoints."""
import pytest
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.di import get_container
from .base import BaseTest
from .helpers import get_test_config

class TestAPIEndpoints(BaseTest):
    """Test API endpoint functionality."""
    
    @pytest.fixture
    def app(self, mock_config) -> FastAPI:
        """Create test FastAPI application."""
        from api.v1 import router as api_router
        
        app = FastAPI()
        app.include_router(api_router)
        # Set test configuration
        app.state.config = mock_config
        return app
    
    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create test client."""
        return TestClient(app)
    
    async def test_storage_endpoints(self, client: TestClient, mock_services):
        """Test storage API endpoints."""
        # Test file upload
        test_file_content = b"test file content"
        test_filename = "test.txt"
        
        with self.assert_metrics(mock_services, {
            "storage_operations_total": 1,
            "s3_uploads_total": 1
        }):
            response = client.post(
                "/v1/storage/s3/upload",
                files={"file": (test_filename, test_file_content)},
                params={"folder": "test"}
            )
            assert response.status_code == 200
            result = response.json()
            assert result["object_name"] == f"test/{test_filename}"
        
        # Test file listing
        response = client.get("/v1/storage/s3/files", params={"prefix": "test/"})
        assert response.status_code == 200
        files = response.json()
        assert len(files) > 0
        assert any(f["key"] == f"test/{test_filename}" for f in files)
    
    async def test_interview_endpoints(self, client: TestClient, mock_services):
        """Test interview API endpoints."""
        # Test interview creation
        test_interview = {
            "session_id": "test_session",
            "participant_id": "test_participant",
            "type": "technical",
            "metadata": {"skill_level": "senior"}
        }
        
        with self.assert_metrics(mock_services, {
            "interview_sessions_total": 1
        }):
            response = client.post(
                "/v1/interviews/",
                json=test_interview
            )
            assert response.status_code == 200
            created = response.json()
            assert created["session_id"] == test_interview["session_id"]
        
        # Test interview retrieval
        response = client.get(f"/v1/interviews/{test_interview['session_id']}")
        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved == created
        
        # Test non-existent interview
        response = client.get("/v1/interviews/nonexistent")
        assert response.status_code == 404
    
    async def test_admin_endpoints(self, client: TestClient, mock_services):
        """Test admin API endpoints."""
        # Test user metrics
        with self.assert_metrics(mock_services, {
            "admin_operations_total": 1
        }):
            response = client.get("/v1/admin/metrics/users")
            assert response.status_code == 200
            metrics = response.json()
            assert "total_users" in metrics
            assert "active_users" in metrics
        
        # Test system health
        response = client.get("/v1/admin/health")
        assert response.status_code == 200
        health = response.json()
        assert health["status"] == "healthy"
        
        # Test component metrics
        components = ["webrtc", "storage", "analysis"]
        for component in components:
            response = client.get(f"/v1/admin/metrics/{component}")
            assert response.status_code == 200
            assert response.json()["component"] == component
    
    async def test_error_handling(self, client: TestClient, mock_services):
        """Test API error handling."""
        # Test invalid interview data
        invalid_interview = {
            "session_id": "",  # Invalid empty session ID
            "type": "unknown"  # Invalid interview type
        }
        response = client.post("/v1/interviews/", json=invalid_interview)
        assert response.status_code == 422  # Validation error
        
        # Test storage errors
        with patch.object(mock_services.s3_client, 'upload_file', side_effect=Exception("Storage error")):
            response = client.post(
                "/v1/storage/s3/upload",
                files={"file": ("test.txt", b"test")}
            )
            assert response.status_code == 500
            assert "Storage error" in response.json()["detail"]
        
        # Test authentication errors
        response = client.get(
            "/v1/admin/metrics/users",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    async def test_metrics_endpoints(self, client: TestClient, mock_services):
        """Test metrics API endpoints."""
        # Test metrics collection
        test_metric = {
            "name": "test_metric",
            "value": 1.0,
            "labels": {"component": "test"}
        }
        
        with self.assert_metrics(mock_services, {
            "metrics_operations_total": 1
        }):
            response = client.post("/v1/metrics/collect", json=test_metric)
            assert response.status_code == 200
        
        # Test metrics retrieval
        response = client.get("/v1/metrics/component/test")
        assert response.status_code == 200
        metrics = response.json()
        assert any(m["name"] == "test_metric" for m in metrics)
        
        # Test metrics aggregation
        response = client.get(
            "/v1/metrics/aggregate",
            params={
                "metric": "test_metric",
                "operation": "sum",
                "start_time": datetime.now(timezone.utc).isoformat()
            }
        )
        assert response.status_code == 200
        assert response.json()["value"] == 1.0
    
    async def test_websocket_endpoints(self, client: TestClient, mock_services):
        """Test WebSocket API endpoints."""
        # Test WebSocket connection
        with client.websocket_connect("/v1/ws") as websocket:
            # Test message sending
            test_message = {"type": "test", "data": "test_data"}
            websocket.send_json(test_message)
            
            # Test message receiving
            response = websocket.receive_json()
            assert response["type"] == "test"
            assert response["data"] == "test_data"
        
        # Test WebSocket authentication
        with pytest.raises(Exception):
            with client.websocket_connect(
                "/v1/ws",
                headers={"Authorization": "Bearer invalid_token"}
            ):
                pass
    
    async def test_webrtc_endpoints(self, client: TestClient, mock_services):
        """Test WebRTC API endpoints."""
        # Test session creation
        test_session = {
            "session_id": "test_webrtc",
            "participant_id": "test_participant"
        }
        
        with self.assert_metrics(mock_services, {
            "webrtc_sessions_total": 1
        }):
            response = client.post("/v1/webrtc/sessions", json=test_session)
            assert response.status_code == 200
            session = response.json()
            assert session["session_id"] == test_session["session_id"]
        
        # Test ICE candidate handling
        ice_candidate = {
            "candidate": "test",
            "sdpMid": "0",
            "sdpMLineIndex": 0
        }
        response = client.post(
            f"/v1/webrtc/sessions/{test_session['session_id']}/ice",
            json=ice_candidate
        )
        assert response.status_code == 200
        
        # Test session cleanup
        response = client.delete(f"/v1/webrtc/sessions/{test_session['session_id']}")
        assert response.status_code == 204 