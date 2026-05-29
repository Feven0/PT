"""Integration tests."""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
import json
from unittest.mock import patch, MagicMock

from core.types.components import HealthStatus
from .base import BaseTest
from .helpers import get_test_config

class TestIntegration(BaseTest):
    """Integration tests for end-to-end functionality."""
    
    @pytest.mark.asyncio
    async def test_interview_flow(self, mock_services):
        """Test complete interview flow."""
        # 1. Setup services
        ws_service = mock_services.websocket_service
        webrtc = mock_services.webrtc_service
        analysis = mock_services.analysis_service
        storage = mock_services.storage_client
        
        # 2. Create interview session
        session_id = "test_interview_1"
        participant_id = "test_participant_1"
        
        with self.assert_metrics(mock_services, {
            "interview_sessions_total": 1,
            "active_participants": 1
        }):
            # Create WebRTC session
            await webrtc.create_session(session_id)
            await webrtc.add_participant(session_id, participant_id)
            
            # Register WebSocket client
            test_client = MagicMock()
            await ws_service.register_client(test_client)
        
        # 3. Simulate interview recording
        test_audio = b"test audio data"
        timestamp = datetime.now(timezone.utc)
        
        with self.assert_metrics(mock_services, {
            "storage_operations_total": 1,
            "audio_recordings_total": 1
        }):
            # Store audio recording
            audio_key = f"interviews/{session_id}/audio_{timestamp}.wav"
            await storage.write(audio_key, test_audio)
        
        # 4. Process interview
        with self.assert_metrics(mock_services, {
            "analysis_jobs_total": 1,
            "analysis_jobs_completed": 1
        }):
            # Create analysis job
            analysis_job = await analysis.create_job({
                "session_id": session_id,
                "audio_key": audio_key,
                "type": "interview_analysis"
            })
            
            # Wait for analysis completion
            await self.wait_for_condition(
                lambda: analysis.get_job_status(analysis_job) == "completed",
                timeout=30
            )
            
            # Get analysis results
            results = await analysis.get_job_results(analysis_job)
            assert results is not None
        
        # 5. Cleanup
        with self.assert_metrics(mock_services, {
            "interview_sessions_total": -1,
            "active_participants": -1
        }):
            await webrtc.end_session(session_id)
            await ws_service.remove_client(test_client)
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, mock_services):
        """Test handling of concurrent interview sessions."""
        num_sessions = 3
        sessions = []
        
        # 1. Create multiple concurrent sessions
        for i in range(num_sessions):
            session_id = f"concurrent_test_{i}"
            participant_id = f"participant_{i}"
            
            await mock_services.webrtc_service.create_session(session_id)
            await mock_services.webrtc_service.add_participant(session_id, participant_id)
            sessions.append((session_id, participant_id))
        
        # 2. Verify resource allocation
        metrics = self.get_component_metrics(mock_services, "webrtc_service")
        assert metrics["active_sessions"] == num_sessions
        
        # 3. Simulate concurrent activity
        async def session_activity(session_id: str, participant_id: str):
            # Simulate WebRTC activity
            ice_candidate = {"candidate": "test", "sdpMid": "0", "sdpMLineIndex": 0}
            await mock_services.webrtc_service.handle_ice_candidate(
                session_id, participant_id, ice_candidate
            )
            
            # Simulate data storage
            test_data = f"test data for {session_id}".encode()
            await mock_services.storage_client.write(
                f"sessions/{session_id}/data.txt",
                test_data
            )
            
            # Simulate analysis
            await mock_services.analysis_service.create_job({
                "session_id": session_id,
                "type": "concurrent_test"
            })
        
        # Run concurrent activities
        await asyncio.gather(
            *(session_activity(sid, pid) for sid, pid in sessions)
        )
        
        # 4. Verify system stability
        for component in [
            "webrtc_service",
            "storage_client",
            "analysis_service"
        ]:
            health = await getattr(mock_services, component).check_health()
            assert health.status == HealthStatus.HEALTHY
        
        # 5. Cleanup
        for session_id, _ in sessions:
            await mock_services.webrtc_service.end_session(session_id)
    
    @pytest.mark.asyncio
    async def test_system_recovery(self, mock_services):
        """Test system recovery from failures."""
        # 1. Simulate component failures
        async def simulate_failures():
            # Simulate storage failure
            with patch.object(mock_services.storage_client, 'write', side_effect=ConnectionError):
                with pytest.raises(ConnectionError):
                    await mock_services.storage_client.write("test", b"data")
            
            # Simulate WebRTC failure
            with patch.object(mock_services.webrtc_service, '_create_peer_connection', 
                            side_effect=RuntimeError):
                with pytest.raises(RuntimeError):
                    await mock_services.webrtc_service.create_session("test")
            
            # Simulate analysis failure
            with patch.object(mock_services.analysis_service, 'process_job',
                            side_effect=TimeoutError):
                with pytest.raises(TimeoutError):
                    await mock_services.analysis_service.create_job({"type": "test"})
        
        await simulate_failures()
        
        # 2. Verify system recovery
        # Wait for circuit breakers to reset
        await asyncio.sleep(
            mock_services.storage_client.circuit_breaker.reset_timeout
        )
        
        # Verify components are operational
        test_session = "recovery_test"
        
        # Storage should work
        await mock_services.storage_client.write(
            f"recovery/{test_session}/data.txt",
            b"recovery test"
        )
        
        # WebRTC should work
        await mock_services.webrtc_service.create_session(test_session)
        
        # Analysis should work
        job = await mock_services.analysis_service.create_job({
            "session_id": test_session,
            "type": "recovery_test"
        })
        assert job is not None
    
    @pytest.mark.asyncio
    async def test_data_consistency(self, mock_services):
        """Test data consistency across components."""
        # 1. Create test data
        session_id = "consistency_test"
        test_data = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"type": "consistency_test"}
        }
        
        # 2. Store data in different components
        # Storage
        await mock_services.storage_client.write(
            f"sessions/{session_id}/metadata.json",
            json.dumps(test_data).encode()
        )
        
        # Analysis
        analysis_job = await mock_services.analysis_service.create_job(test_data)
        
        # WebRTC session
        await mock_services.webrtc_service.create_session(
            session_id,
            metadata=test_data["metadata"]
        )
        
        # 3. Verify data consistency
        # Check storage
        stored_data = await mock_services.storage_client.read(
            f"sessions/{session_id}/metadata.json"
        )
        stored_json = json.loads(stored_data.decode())
        assert stored_json["session_id"] == session_id
        
        # Check analysis
        analysis_results = await mock_services.analysis_service.get_job_results(
            analysis_job
        )
        assert analysis_results["session_id"] == session_id
        
        # Check WebRTC
        session_info = await mock_services.webrtc_service.get_session_info(session_id)
        assert session_info["metadata"] == test_data["metadata"] 