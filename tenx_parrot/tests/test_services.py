"""Test service components."""
import pytest
import asyncio
import logging
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from core.types.components import HealthStatus
from core.types.analysis import AnalysisResult, AnalysisMetric, AnalysisType, AnalysisStatus
from .base import BaseTest
from .helpers import get_test_config

class TestServiceComponents(BaseTest):
    """Test service component functionality."""
    
    @pytest.mark.asyncio
    async def test_websocket_service(self, mock_services):
        """Test WebSocket service functionality."""
        ws_service = mock_services.websocket_service
        
        # Test client connection handling
        test_client = MagicMock()
        
        with self.assert_metrics(mock_services, {
            "websocket_service_connections_total": 1,
            "websocket_service_active_connections": 1
        }):
            await ws_service.register_client(test_client)
        
        # Test message broadcasting
        test_message = {"type": "test", "data": "test_data"}
        with self.assert_metrics(mock_services, {
            "websocket_service_messages_sent": 1
        }):
            await ws_service.broadcast(test_message)
        
        # Test client cleanup
        with self.assert_metrics(mock_services, {
            "websocket_service_active_connections": -1
        }):
            await ws_service.remove_client(test_client)
    
    @pytest.mark.asyncio
    async def test_webrtc_service(self, mock_services):
        """Test WebRTC service functionality."""
        webrtc = mock_services.webrtc_service
        
        # Test session creation
        session_id = "test_session"
        participant_id = "test_participant"
        
        with self.assert_metrics(mock_services, {
            "webrtc_service_sessions_total": 1,
            "webrtc_service_participants_total": 1
        }):
            await webrtc.create_session(session_id)
            await webrtc.add_participant(session_id, participant_id)
        
        # Test ICE candidate handling
        ice_candidate = {"candidate": "test", "sdpMid": "0", "sdpMLineIndex": 0}
        with self.assert_metrics(mock_services, {
            "webrtc_service_ice_candidates_processed": 1
        }):
            await webrtc.handle_ice_candidate(session_id, participant_id, ice_candidate)
        
        # Test session cleanup
        with self.assert_metrics(mock_services, {
            "webrtc_service_sessions_total": -1,
            "webrtc_service_participants_total": -1
        }):
            await webrtc.end_session(session_id)
    
    @pytest.mark.asyncio
    async def test_analysis_service(self, mock_services):
        """Test analysis service functionality."""
        analysis = mock_services.analysis_service
        
        # Create test analysis result
        test_analysis = AnalysisResult(
            id=uuid4(),
            session_id=uuid4(),
            type=AnalysisType.TECHNICAL,
            status=AnalysisStatus.PENDING,
            start_time=datetime.now(timezone.utc),
            metrics=[],
            recommendations=[],
            metadata={}
        )
        
        # Test analysis creation
        with self.assert_metrics(mock_services, {
            "analysis_service_operations_total": 1
        }):
            created_analysis = await analysis.create_analysis(test_analysis)
            assert created_analysis is not None
            assert created_analysis.id == test_analysis.id
        
        # Test analysis processing
        metric = AnalysisMetric(
            name="Technical Knowledge",
            score=85.0,
            weight=0.4,
            feedback="Strong understanding of core concepts",
            details={"strengths": ["System Design", "Algorithms"]}
        )
        
        with self.assert_metrics(mock_services, {
            "analysis_service_operations_total": 1,
            "analysis_service_analyzed_interviews_total": 1
        }):
            processed_analysis = await analysis.process_analysis(created_analysis.id)
            assert processed_analysis is not None
            assert processed_analysis.status == AnalysisStatus.COMPLETED
            assert processed_analysis.overall_score == 85.0
    
    @pytest.mark.asyncio
    async def test_service_error_handling(self, mock_services):
        """Test service error handling and recovery."""
        # Test WebSocket error handling
        ws_service = mock_services.websocket_service
        
        with patch.object(ws_service, '_send_message', side_effect=ConnectionError):
            with self.assert_logs([
                "websocket_error",
                "client_disconnect"
            ], level=logging.ERROR):
                with pytest.raises(ConnectionError):
                    await ws_service.broadcast({"type": "test"})
        
        # Test WebRTC error handling
        webrtc = mock_services.webrtc_service
        
        with patch.object(webrtc, '_create_peer_connection', side_effect=RuntimeError):
            with self.assert_logs([
                "webrtc_error",
                "peer_connection_failed"
            ], level=logging.ERROR):
                with pytest.raises(RuntimeError):
                    await webrtc.create_session("test")
    
    @pytest.mark.asyncio
    async def test_service_interaction(self, mock_services):
        """Test interaction between services."""
        # Test WebSocket-WebRTC interaction
        ws_service = mock_services.websocket_service
        webrtc = mock_services.webrtc_service
        
        # Simulate WebRTC signaling through WebSocket
        test_client = MagicMock()
        await ws_service.register_client(test_client)
        
        session_id = "test_interaction"
        offer_sdp = {"type": "offer", "sdp": "test_sdp"}
        
        with self.assert_metrics(mock_services, {
            "websocket_service_messages_sent": 1,
            "webrtc_service_sessions_total": 1
        }):
            await webrtc.create_session(session_id)
            await ws_service.send_to_client(test_client, {
                "type": "webrtc_offer",
                "session_id": session_id,
                "sdp": offer_sdp
            })
    
    @pytest.mark.asyncio
    async def test_service_lifecycle(self, mock_services):
        """Test service lifecycle management."""
        services = [
            mock_services.websocket_service,
            mock_services.webrtc_service,
            mock_services.analysis_service
        ]
        
        # Test initialization
        for service in services:
            assert service.is_initialized
            assert service.state == "running"
        
        # Test health checks
        for service in services:
            health = await service.check_health()
            assert health.status == HealthStatus.HEALTHY
        
        # Test graceful shutdown
        await mock_services.stop()
        
        for service in services:
            assert service.state == "stopped"
            assert not service.is_initialized
    
    @pytest.mark.asyncio
    async def test_service_metrics(self, mock_services):
        """Test service metrics collection."""
        # Get initial metrics
        initial_metrics = {
            service: self.get_component_metrics(mock_services, service)
            for service in ["websocket_service", "webrtc_service", "analysis_service"]
        }
        
        # Perform some operations
        await mock_services.websocket_service.broadcast({"type": "test"})
        await mock_services.webrtc_service.create_session("test_metrics")
        await mock_services.analysis_service.create_analysis(AnalysisResult(
            id=uuid4(),
            session_id=uuid4(),
            type=AnalysisType.TECHNICAL,
            status=AnalysisStatus.PENDING,
            start_time=datetime.now(timezone.utc),
            metrics=[],
            recommendations=[],
            metadata={}
        ))
        
        # Verify metrics changed
        for service, metrics in initial_metrics.items():
            current_metrics = self.get_component_metrics(mock_services, service)
            assert current_metrics != metrics, f"Metrics for {service} did not change" 