# Google Cloud STT Quick Start Guide

## 🚀 5-Minute Quick Start

### 1. Install Dependencies
```bash
pip install google-cloud-speech google-api-core
```

### 2. Set Up Credentials
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### 3. Basic Usage
```python
from google_stt import GoogleStreamingSTT, GoogleSTTConfig

# Callback for transcripts
async def on_transcript(text: str, is_final: bool):
    print(f"{'FINAL' if is_final else 'interim'}: {text}")

# Create STT instance
stt = GoogleStreamingSTT(
    sid="my-session",
    config=GoogleSTTConfig.from_env(),
    on_transcript=on_transcript
)

# Start streaming
await stt.start()

# Send audio (16kHz PCM16 mono)
audio_chunk = b'\x00\x01' * 1600  # 100ms
await stt.add_audio(audio_chunk)

# Stop when done
await stt.stop()
```

## 📋 Common Configurations

### Lowest Latency (Real-time Chat)
```python
config = GoogleSTTConfig(
    model="latest_short",
    enable_interim_results=True,
    chunk_size_bytes=1600,  # 50ms
)
```

### Best Accuracy (Transcription)
```python
config = GoogleSTTConfig(
    model="latest_long",
    use_enhanced=True,
    enable_word_confidence=True,
)
```

### Phone Calls
```python
config = GoogleSTTConfig(
    sample_rate_hz=8000,
    model="phone_call",
    enable_speaker_diarization=True,
    diarization_speaker_count=2,
)
```

### Video Content
```python
config = GoogleSTTConfig(
    model="video",
    enable_word_time_offsets=True,
    alternative_language_codes=["es-ES"],
)
```

## 🔧 Environment Variables

```bash
# Language
GOOGLE_STT_LANGUAGE=en-US

# Model (latest_short, latest_long, phone_call, video, command_and_search)
GOOGLE_STT_MODEL=latest_short

# Features
GOOGLE_STT_INTERIM=true
GOOGLE_STT_PUNCTUATION=true
GOOGLE_STT_ENHANCED=false

# Performance
GOOGLE_STT_STREAM_LIMIT=290
GOOGLE_STT_ENDPOINT=us-speech.googleapis.com
```

## 🧪 Testing

```bash
# Run all tests
pytest test_google_stt.py -v

# Run specific test
pytest test_google_stt.py::TestGoogleSTTConfig::test_default_config

# Integration tests (requires credentials)
pytest test_google_stt.py -m integration
```

## 🔍 Health Check

```python
from google_stt import check_google_stt_api_status

status = await check_google_stt_api_status()
print(status)
# {"project_id": "...", "api_enabled": true, "state": "ENABLED"}
```

## 📊 Socket.IO Integration

```python
from google_stt import GoogleStreamingSTT, GoogleSTTConfig

google_sessions = {}

@sio.on("audio transcribe google")
async def handle_audio(sid, data):
    audioblob = data.get('audioblob')
    
    # Stop
    if audioblob is None:
        session = google_sessions.pop(sid, None)
        if session:
            await session.stop()
        return
    
    # Create/get session
    if sid not in google_sessions:
        async def on_transcript(text: str, is_final: bool):
            if is_final:
                await sio.emit("audio transcribe google", text, room=sid)
        
        session = GoogleStreamingSTT(
            sid=sid,
            config=GoogleSTTConfig(model="latest_short"),
            on_transcript=on_transcript
        )
        google_sessions[sid] = session
        await session.start()
    
    # Add audio
    await google_sessions[sid].add_audio(bytes(audioblob))

@sio.on("disconnect")
async def on_disconnect(sid):
    session = google_sessions.pop(sid, None)
    if session:
        await session.stop()
```

## 🎯 Model Selection Guide

| Use Case | Model | Latency | Accuracy |
|----------|-------|---------|----------|
| Real-time chat | `latest_short` | ⚡⚡⚡ | ⭐⭐⭐ |
| Transcription | `latest_long` | ⚡⚡ | ⭐⭐⭐⭐ |
| Voice commands | `command_and_search` | ⚡⚡⚡ | ⭐⭐⭐ |
| Phone calls | `phone_call` | ⚡⚡ | ⭐⭐⭐⭐ |
| Video | `video` | ⚡⚡ | ⭐⭐⭐⭐ |

## ⚠️ Troubleshooting

### Error: "google-cloud-speech is not installed"
```bash
pip install google-cloud-speech
```

### Error: "No credentials found"
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Error: "API not enabled"
```bash
gcloud services enable speech.googleapis.com
```

### High latency?
- Use `latest_short` model
- Reduce chunk size to 1600 bytes (50ms)
- Use regional endpoint: `us-speech.googleapis.com`

### Low accuracy?
- Use `latest_long` or enhanced models
- Ensure 16kHz PCM16 audio quality
- Enable automatic punctuation

## 📚 More Resources

- [Full Migration Guide](./GOOGLE_STT_MIGRATION.md) - Detailed migration instructions
- [Improvements Summary](./GOOGLE_STT_IMPROVEMENTS.md) - Benchmarks and comparison
- [Example Code](./google_stt_example.py) - Complete usage examples
- [Test Suite](./test_google_stt.py) - Test examples

## 💡 Quick Tips

1. **Filter silence** to save costs:
   ```python
   from stt_utils import is_silent_pcm16
   if not is_silent_pcm16(audio_chunk):
       await stt.add_audio(audio_chunk)
   ```

2. **Monitor usage**:
   ```python
   print(f"Bytes: {stt.total_audio_bytes}")
   print(f"Transcripts: {stt.total_transcripts}")
   print(f"Restarts: {stt.restart_counter}")
   ```

3. **Handle errors**:
   ```python
   async def on_error(error: Exception):
       logger.error(f"STT Error: {error}")
       await sio.emit("error", {"msg": str(error)}, room=sid)
   
   stt = GoogleStreamingSTT(..., on_error=on_error)
   ```

4. **Use interim results** for better UX:
   ```python
   async def on_transcript(text: str, is_final: bool):
       if is_final:
           # Show permanent text
           print(f"FINAL: {text}")
       else:
           # Show temporary text (updates as user speaks)
           print(f"interim: {text}", end='\r')
   ```

---

**Need help?** Check the full documentation or run the examples:
```bash
python google_stt_example.py
```

