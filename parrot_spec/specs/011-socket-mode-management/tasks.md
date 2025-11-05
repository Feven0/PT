# Tasks: Socket.IO Mode Management and Connection Lifecycle

**Input**: Design documents from `specs/011-socket-mode-management/`  
**Prerequisites**: plan.md ✓, spec.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure exists

- [x] T001 Project structure already exists in `api/` directory
- [x] T002 Socket.IO infrastructure already exists in `api/socket/core.py`
- [x] T003 Redis client already exists in `api/services/redis/redis_client.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before feature implementation

**⚠️ CRITICAL**: No feature work can begin until this phase is complete

### Socket.IO Infrastructure

- [x] T004 Socket.IO server initialized in `api/socket/core.py`
- [x] T005 Socket.IO event handlers structure exists in `api/pages/ipersona/socket/ipersona_socket.py`
- [ ] T006 Verify Socket.IO connection/disconnection handlers are properly structured

### SID Management Infrastructure

- [x] T007 Redis client wrapper exists in `api/services/redis/redis_client.py`
- [ ] T008 [P] [US1] Implement SID manager utilities in `api/pages/ipersona/socket/sid_manager.py`:
  - user_id_to_sid mapping (Redis + in-memory)
  - sid_to_user_id lookup
  - active_sids tracking per user_id
  - Redis fallback to in-memory

### Message Queue Infrastructure

- [x] T009 Redis available for message queuing
- [ ] T010 [P] [US1] Implement message queue utilities:
  - Queue messages for user_id (Redis-backed)
  - Queue messages for SID (in-memory)
  - Deliver queued messages on reconnection
  - Handle orphaned SID queues

**Checkpoint**: Foundation ready - feature implementation can now begin

---

## Phase 3: User Story 1 - Socket.IO Connection Lifecycle Management (Priority: P1) 🎯 MVP

**Goal**: Users can establish and maintain Socket.IO connections with reconnection support

**Independent Test**: A user can connect via Socket.IO, receive connection confirmation, exchange messages, disconnect, reconnect, and receive queued messages.

### Connection Establishment

- [ ] T011 [US1] Implement @sio.event connect handler in `api/pages/ipersona/socket/ipersona_socket.py`:
  - Extract user_id and run_stage from query parameters
  - Store user_id and run_stage in session
  - Join SID-based room
  - Join user_id-based room (if user_id provided)
  - Update SID mapping via sid_manager
  - Emit "initial connect" event
  - Deliver queued messages for user_id

- [ ] T012 [US1] Implement @sio.on("initial connect") handler for connection confirmation

- [ ] T013 [US1] Support legacy SID-only mode (when user_id not provided):
  - Store only run_stage in session
  - Emit "initial connect" event
  - Support SID-based message delivery only

### Reconnection Support

- [ ] T014 [US1] Detect reconnection in connect handler:
  - Check if user_id already has active SID mapping
  - Update SID mapping with new SID
  - Maintain old SID reference for orphaned queue delivery

- [ ] T015 [US1] Deliver queued messages on reconnection:
  - Check Redis queue for user_id
  - Check in-memory queue for user_id
  - Check orphaned SID queues
  - Deliver all queued messages to new SID

### Disconnection Handling

- [ ] T016 [US1] Implement @sio.on("disconnect") handler:
  - Clean up session resources
  - Remove SID from active connections tracking
  - Queue any pending messages for delivery on reconnection
  - Clean up mode-specific resources (audio streams, video streams)

### Multi-Device Support

- [ ] T017 [US1] Track multiple active SIDs per user_id:
  - Maintain USER_ID_ACTIVE_SIDS dictionary
  - Support delivering messages to all active connections
  - Handle multiple device scenarios

### Tests for User Story 1

- [ ] T018 [P] [US1] Unit test for SID mapping utilities in `tests/unit/test_sid_manager.py`
- [ ] T019 [P] [US1] Unit test for message queue utilities in `tests/unit/test_message_queue.py`
- [ ] T020 [US1] Integration test for connection lifecycle in `tests/integration/test_socket_connection.py`:
  - Connection establishment
  - Reconnection with message delivery
  - Disconnection and cleanup
  - Multi-device connection support

**Checkpoint**: Connection lifecycle works independently

---

## Phase 4: User Story 2 - Interview Mode Management (Priority: P1) 🎯 MVP

**Goal**: System routes Socket.IO events based on session mode (Chat, Audio, Video)

**Independent Test**: A user can create a session, set mode (Chat, Audio, or Video), and interact through appropriate Socket.IO events for that mode.

### Mode-Based Event Routing

- [ ] T021 [US2] Implement mode validation utility:
  - Validate session mode exists ("Chat", "Audio", "Video")
  - Validate mode compatibility with Socket.IO events
  - Return error "INSUPPORTED_MODE" or "INVALID_MODE_FOR_EVENT"

- [ ] T022 [US2] Implement mode router in Socket.IO handlers:
  - Check session mode before processing events
  - Route to appropriate handler based on mode:
    - Chat mode → "interview chat" handler
    - Audio mode → "audio chat sentence" handler
    - Video mode → "video chat" handler
  - Validate event compatibility with mode

### Chat Mode Support

- [x] T023 [US2] "interview chat" event handler already exists in `api/pages/ipersona/socket/ipersona_socket.py`
- [ ] T024 [US2] Verify Chat mode routing:
  - Route "interview chat" events when mode="Chat"
  - Validate mode compatibility

### Audio Mode Support

- [x] T025 [US2] "audio chat sentence" event handler already exists in `api/pages/ipersona/socket/ipersona_socket.py`
- [ ] T026 [US2] Verify Audio mode routing:
  - Route "audio chat sentence" events when mode="Audio"
  - Validate mode compatibility

### Video Mode Support

- [ ] T027 [US2] Implement "video chat" event handler in `api/pages/ipersona/socket/ipersona_socket.py`:
  - Handle video frame streaming
  - Process video alongside audio
  - Support facial expression analysis
  - Route when mode="Video"

- [ ] T028 [US2] Implement video processing utilities:
  - Video frame extraction
  - Facial expression analysis integration
  - Video-audio synchronization

### Mode Switching

- [x] T029 [US2] POST /update_session_mode endpoint already exists in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T030 [US2] Verify mode switching:
  - Update session metadata with new mode
  - Route subsequent events to new mode handler
  - Preserve existing session data (messages, evaluations)
  - Support seamless mode transitions

### Tests for User Story 2

- [ ] T031 [P] [US2] Unit test for mode validation in `tests/unit/test_mode_validation.py`
- [ ] T032 [P] [US2] Unit test for mode routing logic in `tests/unit/test_mode_routing.py`
- [ ] T033 [US2] Integration test for mode-based routing in `tests/integration/test_mode_management.py`:
  - Chat mode event routing
  - Audio mode event routing
  - Video mode event routing
  - Mode switching scenarios
  - Invalid mode handling

**Checkpoint**: Mode management works independently

---

## Phase 5: Integration and Refinement

**Purpose**: Integrate features and ensure system-wide consistency

- [ ] T034 Integration test combining connection lifecycle and mode management
- [ ] T035 Performance test: 100 concurrent Socket.IO connections
- [ ] T036 Performance test: Connection establishment latency (< 500ms)
- [ ] T037 Performance test: Reconnection and message delivery latency (< 1 second)
- [ ] T038 Performance test: Mode switching latency (< 500ms)
- [ ] T039 Error handling test: Redis unavailable scenarios
- [ ] T040 Error handling test: Invalid mode scenarios
- [ ] T041 Error handling test: Mode-event incompatibility scenarios

---

**Tasks Version**: 1.0.0 | **Created**: 2024-12-01 | **Status**: Ready for Implementation

