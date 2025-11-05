# Implementation Plan: Real-Time Audio Transcription

**Branch**: `002-audio-transcription` | **Date**: 2024-12-01 | **Spec**: `spec.md`

## Summary

Feature SHALL enable real-time audio transcription via Socket.IO. System SHALL route audio to Google Cloud STT as primary service, provide fallback services in priority order (OpenAI Whisper API → AssemblyAI → Faster Whisper/Gemini) on failure, and emit transcription results via Socket.IO events within 2 seconds.

**Primary Technical Approach**: Socket.IO event handler for "audio transcribe google" event, Google Cloud STT V2 streaming client, fallback service chain (OpenAI Whisper API as first backup, AssemblyAI as second backup, Faster Whisper/Gemini as tertiary), real-time result emission.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Framework**: FastAPI + Socket.IO (python-socketio 5.11+)  
**STT Service**: Google Cloud Speech-to-Text V2 API (PRIMARY)  
**Fallback STT Hierarchy**:
  1. **First Backup**: OpenAI Whisper API
  2. **Second Backup**: AssemblyAI
  3. **Tertiary Fallbacks**: Faster Whisper (local), Google Gemini  
**Testing**: pytest 7.4+ with pytest-asyncio  
**Target Platform**: Linux server  
**Project Type**: Real-time WebSocket service  
**Performance Goals**: 
- Transcription completes within 2 seconds for 95% of requests (Google Cloud STT)
- Socket.IO event emission < 100ms latency

**Constraints**:
- Google Cloud STT MUST be primary service (constitution requirement)
- Fallback services MUST activate in priority order: OpenAI Whisper API → AssemblyAI → Faster Whisper/Gemini
- Must support audio formats: MP3, WAV, WebM, M4A
- Must handle concurrent transcription requests

## Constitution Check

✅ **Primary Service Reliability**: Google Cloud STT as primary ✓  
✅ **Real-Time Communication**: Socket.IO architecture ✓  
✅ **Error Handling**: Fallback service implementation ✓  
✅ **Real-Time Performance**: < 2s transcription target ✓

## Project Structure

```text
api/
├── pages/
│   └── ipersona/
│       └── socket/
│           ├── ipersona_socket.py    # "audio transcribe google" event handler
│           ├── google_stt_v2.py      # Google Cloud STT V2 client
│           └── stt_utils.py          # Audio utilities and fallback
├── utils/
│   └── audio_utils.py               # Audio format conversion
└── tests/
    ├── integration/
    │   └── test_audio_transcription.py
    └── unit/
        └── test_google_stt.py
```

## Component Design

### 1. Socket.IO Event Handler (`api/pages/ipersona/socket/ipersona_socket.py`)

**Responsibilities**:
- Handle "audio transcribe google" Socket.IO event
- Validate audio data format
- Route to Google Cloud STT service (PRIMARY)
- Handle fallback chain: OpenAI Whisper API (first backup) → AssemblyAI (second backup) → Faster Whisper/Gemini (tertiary)
- Emit results via "audio_realtime" event

### 2. Google Cloud STT Client (`api/pages/ipersona/socket/google_stt_v2.py`)

**Responsibilities**:
- Initialize Google Cloud STT V2 client
- Manage streaming transcription sessions
- Handle audio format conversion
- Extract confidence scores
- Error handling and timeout management

### 3. STT Fallback Services (`api/pages/ipersona/socket/stt_utils.py`)

**Responsibilities**:
- Implement fallback chain: OpenAI Whisper API (first backup) → AssemblyAI (second backup) → Faster Whisper/Gemini (tertiary)
- Initialize OpenAI Whisper API client
- Initialize AssemblyAI client
- Initialize Faster Whisper model (tertiary fallback)
- Process audio when Google Cloud fails, following fallback priority order
- Return transcription with confidence scores
- Complete within 5 seconds maximum for fallback services

## Data Flow

```
1. Client emits "audio transcribe google" event with audio data
   ↓
2. Socket.IO handler validates audio format
   ↓
3. Route to Google Cloud STT V2 client (PRIMARY)
   ↓
4. Stream audio to Google Cloud STT API
   ↓
5. Receive transcription + confidence score (< 2s)
   ↓
6. Emit "audio_realtime" event with transcript
   ↓
[If Google Cloud fails]
7. Fallback to OpenAI Whisper API (FIRST BACKUP)
8. Process via OpenAI Whisper API (< 5s)
9. Emit "audio_realtime" event with transcript
   ↓
[If OpenAI Whisper API also fails]
10. Fallback to AssemblyAI (SECOND BACKUP)
11. Process via AssemblyAI (< 5s)
12. Emit "audio_realtime" event with transcript
   ↓
[If AssemblyAI also fails]
13. Fallback to Faster Whisper/Gemini (TERTIARY)
14. Process locally or via Gemini API (< 5s)
15. Emit "audio_realtime" event with transcript
```

## Complexity Tracking

No violations identified.

---

**Plan Version**: 1.0.0 | **Created**: 2024-12-01 | **Status**: Ready for Task Breakdown
