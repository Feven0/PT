# Feature Specification: Real-Time Audio Transcription

**Feature Branch**: `002-audio-transcription`  
**Created**: 2024-12-01  
**Status**: Draft  
**Input**: User description: "Users can send audio via Socket.IO and receive real-time transcription using Google Cloud Speech-to-Text as the primary service. Other STT services (Faster Whisper, AssemblyAI) are available only as fallback backups when Google Cloud is unavailable."

## User Scenarios & Testing

### User Story 1 - Real-Time Audio Transcription (Priority: P1)

**As a** trainee user,  
**I want to** speak my answer and have it transcribed in real-time,  
**So that** I can see what the AI understood from my speech.

**Why this priority**: Real-time transcription is the foundation for AI evaluation. Users need immediate feedback on what was captured.

**Service Selection**: Google Cloud Speech-to-Text MUST be used as the primary and required STT service for all real-time interview transcription in Parrot. Fallback services are available ONLY when Google Cloud fails or is unavailable, in the following priority order:
1. **Primary**: Google Cloud Speech-to-Text (MUST be used for all real-time interviews)
2. **First Backup**: OpenAI Whisper API (fallback when Google Cloud fails)
3. **Second Backup**: AssemblyAI (fallback when OpenAI Whisper API also fails)
4. **Tertiary Fallbacks**: Faster Whisper, Google Gemini (available "in case" but lower priority)

These fallback services were tested during development to find the best model, but Google Cloud Speech-to-Text is the chosen primary service for production use.

**Independent Test**: A user can speak for 10 seconds, receive transcription via Google Cloud STT within 2 seconds, and transcript is available via Socket.IO event.

**Acceptance Scenarios**:

1. **Given** a user has an active session and is connected via Socket.IO,  
   **When** they send audio data via "audio transcribe google" event,  
   **Then** the system SHALL route audio to Google Cloud STT service (PRIMARY SERVICE),  
   **And** SHALL use Google Cloud STT for all real-time interview transcription,  
   **And** SHALL receive transcription within 2 seconds,  
   **And** SHALL emit transcript via "audio_realtime" event,  
   **And** SHALL include confidence score in the response.

2. **Given** Google Cloud STT service fails, times out, or is unavailable,  
   **When** audio transcription is requested,  
   **Then** the system SHALL automatically fallback to OpenAI Whisper API (FIRST BACKUP),  
   **And** SHALL complete transcription within 5 seconds maximum,  
   **And** SHALL log the fallback event for monitoring,  
   **And** SHALL attempt to restore Google Cloud STT service for subsequent requests.

3. **Given** Google Cloud STT and OpenAI Whisper API both fail or are unavailable,  
   **When** audio transcription is requested,  
   **Then** the system SHALL automatically fallback to AssemblyAI (SECOND BACKUP),  
   **And** SHALL complete transcription within 5 seconds maximum,  
   **And** SHALL log the fallback event for monitoring,  
   **And** SHALL attempt to restore Google Cloud STT service for subsequent requests.

4. **Given** audio data is malformed or empty,  
   **When** transcription is requested,  
   **Then** the system SHALL return an error with code "INVALID_AUDIO_FORMAT",  
   **And** SHALL not process the request,  
   **And** SHALL emit error via Socket.IO.

5. **Given** Google Cloud STT is unavailable and fallback is needed,  
   **When** a user sends audio via "audio transcribe whisper" Socket.IO event (tertiary fallback mode),  
   **Then** the system SHALL use Faster Whisper for transcription (TERTIARY BACKUP),  
   **And** SHALL emit transcript via "audio transcribe whisper" event,  
   **And** SHALL complete within 5 seconds,  
   **And** SHALL log that tertiary fallback service was used.

6. **Given** Google Cloud STT is unavailable and fallback is needed,  
   **When** a user sends audio via "audio transcribe" Socket.IO event (second backup mode),  
   **Then** the system SHALL use AssemblyAI Universal Streaming for transcription (SECOND BACKUP),  
   **And** SHALL emit transcript via "audio transcribe" event,  
   **And** SHALL support streaming interim results.

### Edge Cases

- **What happens when** Google Cloud STT quota is exceeded or service is unavailable?  
  **Answer**: System SHALL automatically fallback to OpenAI Whisper API (FIRST BACKUP), SHALL log quota exceeded/service unavailable event, SHALL notify administrators via monitoring alerts, SHALL attempt to restore Google Cloud STT for subsequent requests. If OpenAI Whisper API also fails, SHALL fallback to AssemblyAI (SECOND BACKUP).

- **What happens when** audio file format is unsupported?  
  **Answer**: System SHALL return error "INVALID_AUDIO_FORMAT", SHALL specify supported formats (MP3, WAV, WebM, M4A), SHALL not process the file.

- **What happens when** Socket.IO connection drops during transcription?  
  **Answer**: System SHALL maintain transcription state, SHALL queue results, SHALL deliver when connection restored.

## Requirements

### Functional Requirements

- **FR-001**: System MUST use Google Cloud Speech-to-Text as the PRIMARY and REQUIRED STT service for all real-time interview transcription in Parrot
- **FR-002**: System MUST route all real-time interview audio through Google Cloud STT first before considering fallback options
- **FR-003**: System MUST support streaming transcription with interim results via Google Cloud STT
- **FR-004**: System MUST provide fallback to OpenAI Whisper API as FIRST BACKUP when Google Cloud STT is unavailable or fails
- **FR-005**: System MUST provide fallback to AssemblyAI as SECOND BACKUP when OpenAI Whisper API also fails or is unavailable
- **FR-006**: System MUST support tertiary fallback services (Faster Whisper, Google Gemini) "in case" primary and first/second backups fail
- **FR-007**: System MUST return transcription confidence scores (0-1) from Google Cloud STT
- **FR-008**: System MUST support audio formats: MP3, WAV, WebM, M4A
- **FR-009**: System MUST complete transcription within 2 seconds for 95% of requests (Google Cloud STT performance target)
- **FR-010**: System MUST emit transcription results via Socket.IO "audio_realtime" event
- **FR-011**: System MUST handle multiple concurrent transcription requests through Google Cloud STT
- **FR-012**: System MUST support Socket.IO "audio transcribe whisper" event ONLY for tertiary fallback scenarios when Google Cloud STT and OpenAI Whisper API are unavailable
- **FR-013**: System MUST support Socket.IO "audio transcribe" event for AssemblyAI (second backup) when Google Cloud STT and OpenAI Whisper API are unavailable
- **FR-014**: System MUST provide REST endpoints for STT uploads: POST /stt/whisper-upload, /stt/gemini-upload, /stt/openai-upload, /stt/google-upload (fallback/testing endpoints)
- **FR-015**: System MUST provide simple audio upload endpoint via POST /audio_upload for direct transcription (uses Google Cloud STT)
- **FR-016**: System MUST emit "google_transcription_complete" event when Google Cloud STT completes
- **FR-017**: System MUST emit "transcription_complete" event when AssemblyAI fallback completes
- **FR-018**: System MUST emit "transcription_error" event when transcription fails
- **FR-019**: System MUST support Socket.IO "assemblyai_status" event for monitoring AssemblyAI fallback sessions
- **FR-020**: System MUST emit "assemblyai_status_response" with session statistics
- **FR-021**: System MUST emit "assemblyai_status_error" when status check fails
- **FR-022**: System MUST handle Socket.IO connection lifecycle via @sio.event connect and @sio.on("disconnect")
- **FR-023**: System MUST emit "initial connect" event when Socket.IO connection is established
- **FR-024**: System MUST queue messages for disconnected users in Redis and deliver on reconnection
- **FR-025**: System MUST maintain SID-to-user_id mapping in Redis for reconnection support
- **FR-026**: System MUST support full_bytes parameter in "audio transcribe" event for complete audio upload (fallback mode)
- **FR-027**: System MUST store audio WAV bytes per session_id for S3 upload after transcription

### Key Entities

- **Session (ipersona-session)**: Required for transcription context. Links transcription to specific interview session.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Real-time audio transcription completes within 2 seconds for 95% of requests
- **SC-002**: Transcription accuracy meets or exceeds 90% for clear audio input
- **SC-003**: System handles 100 concurrent transcription requests without degradation
- **SC-004**: Fallback service activates within 1 second of primary service failure

