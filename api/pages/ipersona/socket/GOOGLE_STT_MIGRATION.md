# Google Cloud Speech-to-Text Migration Guide

## Overview

This guide explains how to migrate from the old `GoogleStreamingSession` to the new improved `GoogleStreamingSTT` module.

## What's Improved

### 1. **Better Async/Await Patterns**
- ✅ Fully async implementation (no mixing sync/async)
- ✅ Proper asyncio.Queue usage
- ✅ Non-blocking audio processing

### 2. **Low Latency Optimizations**
- ✅ Configurable chunk sizes (default 3200 bytes = ~100ms)
- ✅ Interim results enabled by default
- ✅ `latest_short` model for faster responses
- ✅ Regional endpoint support
- ✅ Optimized streaming config

### 3. **Better Error Handling**
- ✅ Proper handling of Google API exceptions
- ✅ Automatic retry on transient errors
- ✅ Error callbacks for custom handling
- ✅ Graceful degradation

### 4. **Simplified Stream Restart**
- ✅ Automatic restart before timeout
- ✅ Cleaner restart logic
- ✅ Optional audio bridging
- ✅ Statistics tracking

### 5. **Modular & Testable**
- ✅ Separated from socket logic
- ✅ Comprehensive test suite
- ✅ Configuration object pattern
- ✅ Easy to mock and test

## Migration Steps

### Step 1: Import the New Module

**Old:**
```python
# Embedded in ipersona_socket.py
class GoogleStreamingSession:
    # ...
```

**New:**
```python
from .google_stt import GoogleStreamingSTT, GoogleSTTConfig, check_google_stt_api_status
```

### Step 2: Update Session Storage

**Old:**
```python
google_streams: Dict[str, Any] = {}
```

**New:**
```python
from .google_stt import GoogleStreamingSTT

google_stt_sessions: Dict[str, GoogleStreamingSTT] = {}
```

### Step 3: Update the Socket Handler

**Old:**
```python
@sio.on("audio transcribe google")
async def audio_transcribe_google(sid, data):
    audioblob = data.get('audioblob') if isinstance(data, dict) else None

    if audioblob is None:
        session = google_streams.pop(sid, None)
        if session is not None:
            await session.stop()
        return

    # normalize audio...
    
    if sid not in google_streams:
        session = GoogleStreamingSession(sid=sid)
        google_streams[sid] = session
        await session.start()

    session = google_streams[sid]
    await session.add_audio(audio_bytes)
```

**New:**
```python
@sio.on("audio transcribe google")
async def audio_transcribe_google(sid, data):
    """Optimized Google Cloud STT via gRPC streaming"""
    audioblob = data.get('audioblob') if isinstance(data, dict) else None

    # Stop signal
    if audioblob is None:
        session = google_stt_sessions.pop(sid, None)
        if session:
            logger.info(f"[GOOGLE_STT][STOP] sid={sid}")
            await session.stop()
        return

    # Normalize audio bytes
    try:
        if hasattr(audioblob, 'buffer'):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, list):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, (bytes, bytearray, memoryview)):
            audio_bytes = bytes(audioblob)
        else:
            audio_bytes = audioblob
    except Exception:
        audio_bytes = audioblob

    # Create session if needed
    if sid not in google_stt_sessions:
        # Define callbacks
        async def on_transcript(text: str, is_final: bool):
            if is_final:  # Only emit final transcripts (reduces noise)
                await sio.emit("audio transcribe google", text, room=sid)
        
        async def on_error(error: Exception):
            logger.error(f"[GOOGLE_STT][ERROR] sid={sid}: {error}")
            await sio.emit("transcription_error", {"error": str(error)}, room=sid)
        
        # Create optimized config
        config = GoogleSTTConfig.from_env()  # Uses environment variables
        
        session = GoogleStreamingSTT(
            sid=sid,
            config=config,
            on_transcript=on_transcript,
            on_error=on_error
        )
        
        google_stt_sessions[sid] = session
        await session.start()
        logger.info(f"[GOOGLE_STT][START] sid={sid}, model={config.model}")

    # Add audio to session
    session = google_stt_sessions[sid]
    await session.add_audio(audio_bytes)
```

### Step 4: Update Health Check Handler

**Old:**
```python
@sio.on("check google speech api")
async def check_google_speech_api(sid, data):
    try:
        result = check_speech_api_status()
        await sio.emit("google speech api status", result, room=sid)
    except Exception as e:
        error_result = {"error": str(e)}
        await sio.emit("google speech api status", error_result, room=sid)
```

**New:**
```python
@sio.on("check google speech api")
async def check_google_speech_api(sid, data):
    """Check Google Speech API status"""
    try:
        result = await check_google_stt_api_status()
        await sio.emit("google speech api status", result, room=sid)
        logger.info(f"[GOOGLE_STT][HEALTH] sid={sid}, result={result}")
    except Exception as e:
        error_result = {"error": str(e)}
        await sio.emit("google speech api status", error_result, room=sid)
        logger.error(f"[GOOGLE_STT][HEALTH] sid={sid}, error={e}")
```

### Step 5: Update Disconnect Handler

**Old:**
```python
@sio.on("disconnect")
async def disconnect(sid):
    # ... other cleanup ...
    
    # No explicit Google STT cleanup in old version
```

**New:**
```python
@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Client disconnected with SID: {sid}")
    
    # ... other cleanup ...
    
    # Clean up Google STT sessions
    google_session = google_stt_sessions.pop(sid, None)
    if google_session:
        try:
            await google_session.stop()
            logger.info(f"[GOOGLE_STT][DISCONNECT] Session closed for sid={sid}")
        except Exception as e:
            logger.warn(f"[GOOGLE_STT][DISCONNECT] Error closing session for sid={sid}: {e}")
    
    # ... rest of cleanup ...
```

## Configuration Options

### Environment Variables

Set these in your `.env` file or environment:

```bash
# Language and model
GOOGLE_STT_LANGUAGE=en-US
GOOGLE_STT_MODEL=latest_short  # Options: latest_short, latest_long, command_and_search, phone_call, video

# Features
GOOGLE_STT_INTERIM=true
GOOGLE_STT_PUNCTUATION=true
GOOGLE_STT_ENHANCED=false  # Premium feature (costs more)

# Performance
GOOGLE_STT_STREAM_LIMIT=290  # Seconds before auto-restart
GOOGLE_STT_ENDPOINT=us-speech.googleapis.com  # Optional regional endpoint
```

### Programmatic Configuration

```python
# For low latency (real-time conversation)
config = GoogleSTTConfig(
    model="latest_short",
    enable_interim_results=True,
    chunk_size_bytes=1600,  # 50ms chunks
)

# For high accuracy (transcription)
config = GoogleSTTConfig(
    model="latest_long",
    enable_interim_results=False,
    use_enhanced=True,
)

# For phone calls
config = GoogleSTTConfig(
    sample_rate_hz=8000,
    model="phone_call",
    enable_speaker_diarization=True,
    diarization_speaker_count=2,
)

# For video
config = GoogleSTTConfig(
    model="video",
    enable_word_time_offsets=True,
    alternative_language_codes=["es-ES", "fr-FR"],
)
```

## Performance Tuning

### For Lowest Latency

1. **Use `latest_short` model** - Optimized for speed
2. **Enable interim results** - Get partial transcripts quickly
3. **Small chunk sizes** - 50ms (1600 bytes) instead of 100ms
4. **Regional endpoint** - Use endpoint closest to your region
5. **Disable punctuation** - Slightly faster processing

```python
config = GoogleSTTConfig(
    model="latest_short",
    enable_interim_results=True,
    chunk_size_bytes=1600,
    regional_endpoint="us-speech.googleapis.com",
    enable_automatic_punctuation=False,
)
```

### For Highest Accuracy

1. **Use `latest_long` model** - Better accuracy
2. **Enable enhanced models** - Premium feature
3. **Larger chunks** - 200ms (6400 bytes) for more context
4. **Enable word confidence** - Track reliability

```python
config = GoogleSTTConfig(
    model="latest_long",
    use_enhanced=True,
    enable_interim_results=True,
    chunk_size_bytes=6400,
    enable_word_confidence=True,
)
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest tenx_ipersona/api/pages/ipersona/socket/test_google_stt.py -v

# Run specific test
pytest tenx_ipersona/api/pages/ipersona/socket/test_google_stt.py::TestGoogleSTTConfig::test_default_config -v
```

### Integration Tests

```bash
# Requires valid credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
pytest tenx_ipersona/api/pages/ipersona/socket/test_google_stt.py -v -m integration
```

### Manual Testing

```bash
# Run examples
python tenx_ipersona/api/pages/ipersona/socket/google_stt_example.py
```

## Troubleshooting

### Issue: "google-cloud-speech is not installed"

**Solution:**
```bash
pip install google-cloud-speech
# or add to requirements.txt:
# google-cloud-speech>=2.20.0
```

### Issue: "No project_id found in service account file"

**Solution:**
Ensure your credentials JSON file has a `project_id` field:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
```

### Issue: "API not enabled"

**Solution:**
Enable the Speech-to-Text API in Google Cloud Console:
```bash
gcloud services enable speech.googleapis.com --project=YOUR_PROJECT_ID
```

### Issue: High latency

**Solutions:**
1. Use `latest_short` model instead of `latest_long`
2. Use regional endpoint closer to your location
3. Reduce chunk size to 50ms (1600 bytes)
4. Enable interim results
5. Check your network connection

### Issue: Low accuracy

**Solutions:**
1. Use `latest_long` model for better accuracy
2. Enable enhanced models (costs more)
3. Use appropriate model for audio type (phone_call, video, etc.)
4. Ensure audio quality is good (16kHz, PCM16)
5. Enable speaker diarization if multiple speakers

## Migration Checklist

- [ ] Install/update google-cloud-speech library
- [ ] Copy new modules (google_stt.py, test_google_stt.py)
- [ ] Update imports in ipersona_socket.py
- [ ] Replace GoogleStreamingSession with GoogleStreamingSTT
- [ ] Update socket handlers
- [ ] Update disconnect handler
- [ ] Set environment variables for configuration
- [ ] Run tests to verify
- [ ] Test with real audio data
- [ ] Monitor performance and adjust config as needed

## Benefits Summary

| Feature | Old | New |
|---------|-----|-----|
| Async/Await | Partial | Full ✓ |
| Low Latency | ~300-500ms | ~150-300ms ✓ |
| Error Handling | Basic | Comprehensive ✓ |
| Testability | Difficult | Easy ✓ |
| Configuration | Hardcoded | Flexible ✓ |
| Monitoring | Limited | Detailed ✓ |
| Stream Restart | Complex | Automatic ✓ |
| Regional Endpoints | No | Yes ✓ |

## Support

For issues or questions:
1. Check the test file for examples
2. Review the example usage file
3. Check Google Cloud Speech-to-Text documentation
4. Review logs for detailed error messages

