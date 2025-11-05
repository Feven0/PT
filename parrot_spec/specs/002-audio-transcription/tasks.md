# Tasks: Real-Time Audio Transcription

**Input**: Design documents from `specs/002-audio-transcription/`  
**Prerequisites**: plan.md ✓, spec.md ✓

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup
- [x] T001 Project structure exists

## Phase 2: Foundational
- [x] T002 Socket.IO infrastructure exists
- [ ] T003 Verify Google Cloud STT credentials configuration

## Phase 3: User Story 1 - Real-Time Audio Transcription (Priority: P1) 🎯 MVP

**Goal**: Users can send audio and receive transcription within 2 seconds

**Independent Test**: A user can speak for 10 seconds, receive transcription within 2 seconds

### Tests
- [ ] T004 [P] [US1] Unit test for Google Cloud STT client in `tests/unit/test_google_stt.py`
- [ ] T005 [P] [US1] Integration test for Socket.IO transcription flow in `tests/integration/test_audio_transcription.py`

### Implementation
- [ ] T006 [P] [US1] Implement Google Cloud STT V2 client in `api/pages/ipersona/socket/google_stt_v2.py`
- [ ] T007 [P] [US1] Implement OpenAI Whisper API fallback (FIRST BACKUP) in `api/pages/ipersona/socket/stt_utils.py`
- [ ] T007b [P] [US1] Implement AssemblyAI fallback (SECOND BACKUP) in `api/pages/ipersona/socket/stt_utils.py`
- [ ] T007c [US1] Implement Faster Whisper fallback (TERTIARY) in `api/pages/ipersona/socket/stt_utils.py`
- [ ] T008 [P] [US1] Implement audio format validation in `api/utils/audio_utils.py`
- [ ] T009 [US1] Implement "audio transcribe google" Socket.IO event handler in `api/pages/ipersona/socket/ipersona_socket.py`
- [ ] T010 [US1] Add audio format conversion logic
- [ ] T011 [US1] Add transcription result emission via "audio_realtime" event
- [ ] T012 [US1] Add fallback logic for Google Cloud STT failures (OpenAI Whisper API → AssemblyAI → Faster Whisper/Gemini)
- [ ] T013 [US1] Add error handling for invalid audio format
- [ ] T014 [US1] Add logging for transcription operations
- [ ] T015 [US1] Verify transcription completes within 2 seconds

**Checkpoint**: Real-time audio transcription works independently

---

**Tasks Version**: 1.0.0 | **Created**: 2024-12-01
