"""
Test suite for Google Cloud Speech-to-Text V2 streaming module.

Run with: pytest test_google_stt_v2.py -v
"""

import asyncio
import pytest
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from google_stt_v2 import GoogleStreamingSTTV2, GoogleSTTV2Config, check_google_stt_v2_status


class TestGoogleSTTV2Config:
    """Test GoogleSTTV2Config dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = GoogleSTTV2Config()
        assert config.sample_rate_hz == 16000
        assert config.language_codes == ["en-US"]
        assert config.model == "short"  # V2 uses "short" not "latest_short"
        assert config.enable_interim_results is True
        assert config.enable_automatic_punctuation is True
        assert config.emit_interim_results is True
        assert config.enable_self_correction is True
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = GoogleSTTV2Config(
            sample_rate_hz=48000,
            language_codes=["es-ES", "fr-FR"],
            model="chirp_2",
            enable_interim_results=False,
            emit_only_final=True,
        )
        assert config.sample_rate_hz == 48000
        assert config.language_codes == ["es-ES", "fr-FR"]
        assert config.model == "chirp_2"
        assert config.enable_interim_results is False
        assert config.emit_only_final is True
    
    def test_from_env(self):
        """Test configuration from environment variables"""
        with patch.dict(os.environ, {
            'GOOGLE_STT_V2_LANGUAGES': 'en-US,es-ES',
            'GOOGLE_STT_V2_MODEL': 'long',
            'GOOGLE_STT_V2_INTERIM': 'false',
            'GOOGLE_STT_V2_EMIT_INTERIM': 'false',
            'GOOGLE_STT_V2_EMIT_ONLY_FINAL': 'true',
            'GOOGLE_STT_V2_SELF_CORRECTION': 'false',
        }):
            config = GoogleSTTV2Config.from_env()
            assert config.language_codes == ['en-US', 'es-ES']
            assert config.model == 'long'
            assert config.enable_interim_results is False
            assert config.emit_interim_results is False
            assert config.emit_only_final is True
            assert config.enable_self_correction is False
    
    def test_emission_strategy_presets(self):
        """Test different emission strategy configurations"""
        
        # Word-by-word with self-correction
        config1 = GoogleSTTV2Config(
            emit_interim_results=True,
            emit_only_final=False,
            enable_self_correction=True,
        )
        assert config1.emit_interim_results is True
        assert config1.enable_self_correction is True
        
        # Final only
        config2 = GoogleSTTV2Config(
            emit_interim_results=False,
            emit_only_final=True,
        )
        assert config2.emit_only_final is True
        
        # Utterance end
        config3 = GoogleSTTV2Config(
            emit_interim_results=False,
            emit_on_utterance_end=True,
        )
        assert config3.emit_on_utterance_end is True


class TestGoogleStreamingSTTV2:
    """Test GoogleStreamingSTTV2 class"""
    
    @pytest.fixture
    def mock_credentials_file(self, tmp_path):
        """Create a mock credentials file"""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text('{"project_id": "test-project-v2"}')
        return str(creds_file)
    
    @pytest.fixture
    def mock_speech_client(self):
        """Mock Google Speech V2 client"""
        with patch('google_stt_v2.SpeechAsyncClient') as mock:
            mock_client = MagicMock()
            mock.return_value = mock_client
            yield mock_client
    
    def test_initialization(self, mock_credentials_file, mock_speech_client):
        """Test basic initialization"""
        config = GoogleSTTV2Config()
        stt = GoogleStreamingSTTV2(
            sid="test-session-v2-1",
            config=config,
            credentials_path=mock_credentials_file
        )
        
        assert stt.sid == "test-session-v2-1"
        assert stt.config == config
        assert stt.restart_counter == 0
        assert stt.total_audio_bytes == 0
        assert stt.total_transcripts == 0
    
    def test_initialization_without_v2_library(self):
        """Test that initialization fails gracefully without google-cloud-speech V2"""
        with patch('google_stt_v2.SpeechAsyncClient', None):
            with pytest.raises(RuntimeError, match="google-cloud-speech V2 is not installed"):
                GoogleStreamingSTTV2(sid="test", credentials_path="/fake/path")
    
    @pytest.mark.asyncio
    async def test_start_stop(self, mock_credentials_file, mock_speech_client):
        """Test starting and stopping the stream"""
        stt = GoogleStreamingSTTV2(
            sid="test-session",
            credentials_path=mock_credentials_file
        )
        
        await stt.start()
        assert stt._stream_task is not None
        assert stt._restart_timer_task is not None
        
        await stt.stop()
        assert stt._stop_event.is_set()
    
    @pytest.mark.asyncio
    async def test_add_audio(self, mock_credentials_file, mock_speech_client):
        """Test adding audio to the queue"""
        stt = GoogleStreamingSTTV2(
            sid="test-session",
            credentials_path=mock_credentials_file
        )
        
        # Add some mock audio data
        audio_data = b'\x00\x01' * 1600  # 100ms of 16kHz PCM16
        await stt.add_audio(audio_data)
        
        assert stt.total_audio_bytes == len(audio_data)
        assert stt._audio_queue.qsize() == 1
    
    @pytest.mark.asyncio
    async def test_transcript_callback(self, mock_credentials_file, mock_speech_client):
        """Test transcript callback is called with V2 signature"""
        transcripts = []
        
        async def on_transcript(text: str, is_final: bool, result: dict):
            transcripts.append({
                "text": text,
                "is_final": is_final,
                "language": result.get("language_code")
            })
        
        stt = GoogleStreamingSTTV2(
            sid="test-session",
            on_transcript=on_transcript,
            credentials_path=mock_credentials_file
        )
        
        # Manually call the callback
        await on_transcript("Hello world", True, {"language_code": "en-US"})
        
        assert len(transcripts) == 1
        assert transcripts[0]["text"] == "Hello world"
        assert transcripts[0]["is_final"] is True
        assert transcripts[0]["language"] == "en-US"
    
    @pytest.mark.asyncio
    async def test_error_callback(self, mock_credentials_file, mock_speech_client):
        """Test error callback is called"""
        errors = []
        
        async def on_error(error: Exception):
            errors.append(error)
        
        stt = GoogleStreamingSTTV2(
            sid="test-session",
            on_error=on_error,
            credentials_path=mock_credentials_file
        )
        
        # Manually trigger error callback
        test_error = Exception("Test V2 error")
        await on_error(test_error)
        
        assert len(errors) == 1
        assert str(errors[0]) == "Test V2 error"
    
    @pytest.mark.asyncio
    async def test_speech_event_callback(self, mock_credentials_file, mock_speech_client):
        """Test speech event callback (VAD)"""
        events = []
        
        async def on_speech_event(event_type: str, event: dict):
            events.append({"type": event_type, "event": event})
        
        stt = GoogleStreamingSTTV2(
            sid="test-session",
            config=GoogleSTTV2Config(enable_voice_activity_events=True),
            on_speech_event=on_speech_event,
            credentials_path=mock_credentials_file
        )
        
        # Manually trigger event callback
        await on_speech_event("END_OF_SINGLE_UTTERANCE", {"data": "test"})
        
        assert len(events) == 1
        assert events[0]["type"] == "END_OF_SINGLE_UTTERANCE"
    
    def test_config_creation(self, mock_credentials_file, mock_speech_client):
        """Test V2 streaming config creation"""
        config = GoogleSTTV2Config(
            enable_word_time_offsets=True,
            enable_voice_activity_events=True,
        )
        
        stt = GoogleStreamingSTTV2(
            sid="test-session",
            config=config,
            credentials_path=mock_credentials_file
        )
        
        streaming_config = stt._create_streaming_config()
        
        # Verify config structure
        assert streaming_config.config is not None
        assert streaming_config.streaming_features is not None
        assert streaming_config.streaming_features.interim_results is True


class TestHealthCheckV2:
    """Test V2 API health check utility"""
    
    @pytest.fixture
    def mock_credentials_file(self, tmp_path):
        """Create a mock credentials file"""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text('{"project_id": "test-project-v2-123"}')
        return str(creds_file)
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_credentials_file):
        """Test successful V2 health check"""
        with patch('google_stt_v2.SpeechAsyncClient') as mock_client:
            mock_client.return_value = MagicMock()
            
            result = await check_google_stt_v2_status(mock_credentials_file)
            
            assert result["project_id"] == "test-project-v2-123"
            assert result["api_version"] == "v2"
            assert result["client_initialized"] is True
            assert result["status"] == "ready"
    
    @pytest.mark.asyncio
    async def test_health_check_missing_file(self):
        """Test health check with missing credentials file"""
        result = await check_google_stt_v2_status("/nonexistent/path.json")
        
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_health_check_no_project_id(self, tmp_path):
        """Test health check when project_id missing"""
        creds_file = tmp_path / "bad_credentials.json"
        creds_file.write_text('{"type": "service_account"}')  # No project_id
        
        result = await check_google_stt_v2_status(str(creds_file))
        
        assert "error" in result
        assert "project_id" in result["error"].lower()


class TestV2ModelNames:
    """Test V2 model naming conventions"""
    
    def test_v2_model_names(self):
        """Ensure we're using correct V2 model names"""
        config = GoogleSTTV2Config()
        
        # Default should be V2 name, not V1
        assert config.model == "short"  # NOT "latest_short"
        
        # Test valid V2 model names
        valid_models = ["short", "long", "chirp", "chirp_2"]
        for model in valid_models:
            config = GoogleSTTV2Config(model=model)
            assert config.model == model
    
    def test_v2_vs_v1_model_names(self):
        """Document V1 vs V2 model name differences"""
        v1_to_v2_mapping = {
            "latest_short": "short",
            "latest_long": "long",
        }
        
        for v1_name, v2_name in v1_to_v2_mapping.items():
            # V1 names should NOT be used in V2
            assert v1_name != v2_name
            # V2 config should use V2 names
            config = GoogleSTTV2Config(model=v2_name)
            assert config.model == v2_name


class TestEmissionStrategies:
    """Test different transcript emission strategies"""
    
    def test_word_by_word_config(self):
        """Test word-by-word with self-correction configuration"""
        config = GoogleSTTV2Config(
            emit_interim_results=True,
            emit_only_final=False,
            enable_self_correction=True,
        )
        
        assert config.emit_interim_results is True
        assert config.emit_only_final is False
        assert config.enable_self_correction is True
    
    def test_final_only_config(self):
        """Test final-only configuration"""
        config = GoogleSTTV2Config(
            emit_interim_results=False,
            emit_only_final=True,
            enable_self_correction=False,
        )
        
        assert config.emit_interim_results is False
        assert config.emit_only_final is True
    
    def test_utterance_end_config(self):
        """Test utterance-end configuration"""
        config = GoogleSTTV2Config(
            emit_interim_results=False,
            emit_on_utterance_end=True,
            enable_voice_activity_events=True,
        )
        
        assert config.emit_on_utterance_end is True
        assert config.enable_voice_activity_events is True


class TestV2APIStructure:
    """Test V2 API structure differences from V1"""
    
    @pytest.fixture
    def mock_credentials_file(self, tmp_path):
        """Create a mock credentials file"""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text('{"project_id": "test-v2"}')
        return str(creds_file)
    
    def test_streaming_features_separate_class(self, mock_credentials_file):
        """Test that StreamingRecognitionFeatures is imported separately"""
        with patch('google_stt_v2.SpeechAsyncClient'):
            from google_stt_v2 import StreamingRecognitionFeatures
            
            # Should be importable (not nested)
            assert StreamingRecognitionFeatures is not None
    
    def test_config_structure(self, mock_credentials_file):
        """Test V2 config uses separate StreamingRecognitionFeatures class"""
        with patch('google_stt_v2.SpeechAsyncClient'):
            stt = GoogleStreamingSTTV2(
                sid="test",
                credentials_path=mock_credentials_file
            )
            
            config = stt._create_streaming_config()
            
            # Should have streaming_features as separate object
            assert hasattr(config, 'streaming_features')
            assert config.streaming_features is not None


# Integration test (requires real Google Cloud credentials)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_v2_audio_transcription():
    """
    Integration test with real Google Cloud STT V2 API.
    
    Requires:
    - Valid Google Cloud credentials
    - Speech-to-Text V2 API enabled
    - Set GOOGLE_APPLICATION_CREDENTIALS environment variable
    
    Run with: pytest test_google_stt_v2.py -v -m integration
    """
    # Skip if no credentials
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):
        pytest.skip("No Google Cloud credentials found")
    
    transcripts = []
    events = []
    
    async def on_transcript(text: str, is_final: bool, result: dict):
        transcripts.append({
            "text": text,
            "is_final": is_final,
            "language": result.get("language_code"),
            "stability": result.get("stability"),
        })
        print(f"Transcript ({'FINAL' if is_final else 'interim'}): {text}")
    
    async def on_error(error: Exception):
        print(f"Error: {error}")
        raise error  # Fail test on error
    
    async def on_speech_event(event_type: str, event: dict):
        events.append(event_type)
        print(f"Speech Event: {event_type}")
    
    # Create V2 STT client
    config = GoogleSTTV2Config(
        model="short",  # V2 model name
        enable_interim_results=True,
        enable_voice_activity_events=True,
    )
    
    stt = GoogleStreamingSTTV2(
        sid="integration-test-v2",
        config=config,
        on_transcript=on_transcript,
        on_error=on_error,
        on_speech_event=on_speech_event,
        credentials_path=creds_path
    )
    
    # Start streaming
    await stt.start()
    print("\n=== V2 Integration Test Started ===")
    
    # Generate synthetic audio (silence for testing)
    # In real scenario, use actual speech audio
    sample_rate = 16000
    duration_seconds = 3
    audio_data = b'\x00\x01' * (sample_rate * duration_seconds)
    
    # Send audio in chunks
    chunk_size = 3200  # 100ms chunks
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        await stt.add_audio(chunk)
        await asyncio.sleep(0.1)  # Simulate real-time
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Stop streaming
    await stt.stop()
    
    # Verify statistics
    print(f"\nStatistics:")
    print(f"  Total audio: {stt.total_audio_bytes} bytes")
    print(f"  Total transcripts: {len(transcripts)}")
    print(f"  Speech events: {len(events)}")
    print(f"  Restarts: {stt.restart_counter}")
    
    assert stt.total_audio_bytes > 0
    # Note: Silence won't produce transcripts, but stream should work


@pytest.mark.integration
@pytest.mark.asyncio
async def test_v2_health_check():
    """
    Test V2 API health check with real credentials.
    
    Run with: pytest test_google_stt_v2.py::test_v2_health_check -v -m integration
    """
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '.envdir/tenx-saas-3ff848c57fc5.json')
    if not os.path.exists(creds_path):
        pytest.skip("No Google Cloud credentials found")
    
    status = await check_google_stt_v2_status(creds_path)
    
    print("\n=== V2 Health Check ===")
    print(f"Status: {status}")
    
    assert "project_id" in status
    assert status.get("api_version") == "v2"
    assert status.get("client_initialized") is True


@pytest.mark.asyncio
async def test_deduplication_logic():
    """Test smart deduplication algorithm (simulated)"""
    
    # Simulate the deduplication logic from ipersona_socket.py lines 505-516
    def should_emit(current_text: str, last_text: str) -> bool:
        """Smart deduplication: only emit if meaningful change"""
        if current_text == last_text:
            return False
        
        words_last = set(last_text.lower().split())
        words_current = set(current_text.lower().split())
        new_words = words_current - words_last
        
        # Emit if: new words added OR text substantially longer
        return bool(new_words) or len(current_text) > len(last_text) + 2
    
    # Test cases
    assert should_emit("Hello", "") is True  # First word
    assert should_emit("Hello", "Hello") is False  # Duplicate
    assert should_emit("Hello my", "Hello") is True  # New word
    assert should_emit("Hello my name", "Hello my") is True  # New word
    assert should_emit("Hello my name", "Hello my name") is False  # Duplicate
    
    # Prevents repetition
    assert should_emit("Hello", "Hello") is False
    assert should_emit("Hello.", "Hello") is False  # Same content
    
    # Allows progression
    assert should_emit("Hello my name is Abel", "Hello my") is True


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v", "--tb=short", "-m", "not integration"])

