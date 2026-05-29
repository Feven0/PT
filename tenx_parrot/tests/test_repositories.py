"""Test repository implementations."""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

from core.types.components import HealthStatus
from core.types.analysis import AnalysisResult, AnalysisMetric, AnalysisType, AnalysisStatus
from .base import BaseTest
from .helpers import get_test_config

class TestRepositories(BaseTest):
    """Test repository functionality."""
    
    @pytest.mark.asyncio
    async def test_analysis_repository(self, mock_services):
        """Test analysis repository operations."""
        repo = mock_services.analysis_repository
        
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
        
        # Test analysis storage
        with self.assert_metrics(mock_services, {
            "analysis_repository_operations_total": 1
        }):
            stored_analysis = await repo.store_analysis(test_analysis, str(test_analysis.session_id))
            assert stored_analysis is not None
            assert stored_analysis.id == test_analysis.id
        
        # Test analysis retrieval
        retrieved_analysis = await repo.get_analysis(str(test_analysis.session_id))
        assert retrieved_analysis is not None
        assert retrieved_analysis.id == test_analysis.id
        
        # Test analysis update
        metric = AnalysisMetric(
            name="Technical Knowledge",
            score=85.0,
            weight=0.4,
            feedback="Strong understanding of core concepts",
            details={"strengths": ["System Design", "Algorithms"]}
        )
        retrieved_analysis.add_metric(metric)
        updated_analysis = await repo.update_analysis(
            str(test_analysis.session_id),
            {"metrics": retrieved_analysis.metrics}
        )
        assert updated_analysis is not None
        assert len(updated_analysis.metrics) == 1
        assert updated_analysis.overall_score == 85.0
        
        # Test analysis deletion
        await repo.delete_analysis(str(test_analysis.session_id))
        deleted_analysis = await repo.get_analysis(str(test_analysis.session_id))
        assert deleted_analysis is None
    
    @pytest.mark.asyncio
    async def test_interview_repository(self, mock_services):
        """Test interview repository operations."""
        repo = mock_services.interview_repository
        
        # Test interview creation
        test_interview = {
            "session_id": "test_interview",
            "participant_id": "test_participant",
            "type": "technical",
            "created_at": datetime.now(timezone.utc)
        }
        
        with self.assert_metrics(mock_services, {
            "interview_repository_operations_total": 1
        }):
            await repo.create_interview(test_interview)
        
        # Test interview retrieval
        interview = await repo.get_interview(test_interview["session_id"])
        assert interview["participant_id"] == test_interview["participant_id"]
        
        # Test interview update
        updated_data = {"status": "completed"}
        await repo.update_interview(test_interview["session_id"], updated_data)
        interview = await repo.get_interview(test_interview["session_id"])
        assert interview["status"] == "completed"
        
        # Test interview deletion
        await repo.delete_interview(test_interview["session_id"])
        interview = await repo.get_interview(test_interview["session_id"])
        assert interview is None
    
    @pytest.mark.asyncio
    async def test_storage_repository(self, mock_services):
        """Test storage repository operations."""
        repo = mock_services.storage_repository
        
        # Test file storage
        test_data = b"test storage data"
        test_key = "test/storage.txt"
        
        with self.assert_metrics(mock_services, {
            "storage_repository_operations_total": 1,
            "storage_repository_bytes_written": len(test_data)
        }):
            await repo.store_file(test_key, test_data)
        
        # Test file retrieval
        data = await repo.get_file(test_key)
        assert data == test_data
        
        # Test file listing
        files = await repo.list_files("test/")
        assert test_key in files
        
        # Test file deletion
        await repo.delete_file(test_key)
        with pytest.raises(KeyError):
            await repo.get_file(test_key)
    
    @pytest.mark.asyncio
    async def test_session_repository(self, mock_services):
        """Test session repository operations."""
        repo = mock_services.session_repository
        
        # Test session creation
        test_session = {
            "id": "test_session",
            "type": "interview",
            "created_at": datetime.now(timezone.utc),
            "metadata": {"skill_level": "senior"}
        }
        
        with self.assert_metrics(mock_services, {
            "session_repository_operations_total": 1
        }):
            await repo.create_session(test_session)
        
        # Test session retrieval
        session = await repo.get_session(test_session["id"])
        assert session["type"] == test_session["type"]
        assert session["metadata"] == test_session["metadata"]
        
        # Test session listing
        sessions = await repo.list_sessions(
            start_time=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        assert any(s["id"] == test_session["id"] for s in sessions)
        
        # Test session update
        updated_data = {"status": "active"}
        await repo.update_session(test_session["id"], updated_data)
        session = await repo.get_session(test_session["id"])
        assert session["status"] == "active"
        
        # Test session deletion
        await repo.delete_session(test_session["id"])
        session = await repo.get_session(test_session["id"])
        assert session is None
    
    @pytest.mark.asyncio
    async def test_user_repository(self, mock_services):
        """Test user repository operations."""
        repo = mock_services.user_repository
        
        # Test user creation
        test_user = {
            "id": "test_user",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": datetime.now(timezone.utc)
        }
        
        with self.assert_metrics(mock_services, {
            "user_repository_operations_total": 1
        }):
            await repo.create_user(test_user)
        
        # Test user retrieval
        user = await repo.get_user(test_user["id"])
        assert user["email"] == test_user["email"]
        
        # Test user search
        users = await repo.search_users({"email": test_user["email"]})
        assert len(users) == 1
        assert users[0]["id"] == test_user["id"]
        
        # Test user update
        updated_data = {"status": "active"}
        await repo.update_user(test_user["id"], updated_data)
        user = await repo.get_user(test_user["id"])
        assert user["status"] == "active"
        
        # Test user deletion
        await repo.delete_user(test_user["id"])
        user = await repo.get_user(test_user["id"])
        assert user is None
    
    @pytest.mark.asyncio
    async def test_repository_error_handling(self, mock_services):
        """Test repository error handling."""
        # Test storage errors
        repo = mock_services.storage_repository
        with patch.object(repo._client, 'write', side_effect=Exception("Storage error")):
            with pytest.raises(Exception):
                await repo.store_file("test.txt", b"test")
        
        # Test database errors
        repo = mock_services.interview_repository
        with patch.object(repo._db, 'insert', side_effect=Exception("DB error")):
            with pytest.raises(Exception):
                await repo.create_interview({"session_id": "test"})
    
    @pytest.mark.asyncio
    async def test_repository_metrics(self, mock_services):
        """Test repository metrics collection."""
        repos = [
            mock_services.analysis_repository,
            mock_services.interview_repository,
            mock_services.storage_repository,
            mock_services.session_repository,
            mock_services.user_repository
        ]
        
        # Test metrics for each repository
        for repo in repos:
            metrics = self.get_component_metrics(mock_services, repo.__class__.__name__.lower())
            assert "operations_total" in metrics
            assert metrics["operations_total"] >= 0
    
    @pytest.mark.asyncio
    async def test_repository_health_checks(self, mock_services):
        """Test repository health checks."""
        repos = [
            mock_services.analysis_repository,
            mock_services.interview_repository,
            mock_services.storage_repository,
            mock_services.session_repository,
            mock_services.user_repository
        ]
        
        # Test health check for each repository
        for repo in repos:
            health = await repo.check_health()
            assert health.status == HealthStatus.HEALTHY 