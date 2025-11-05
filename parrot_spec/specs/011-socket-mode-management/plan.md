# Implementation Plan: Socket.IO Mode Management and Connection Lifecycle

**Branch**: `011-socket-mode-management` | **Date**: 2024-12-01 | **Spec**: `spec.md`

## Summary

Feature SHALL manage Socket.IO connection lifecycle and support multiple interview interaction modes (Audio, Chat, Video). System SHALL handle connection/disconnection events, maintain user_id-to-SID mappings for reconnection support, queue messages for disconnected users, route Socket.IO events based on session mode, and support mode switching.

**Primary Technical Approach**: Socket.IO event handlers for connection lifecycle, Redis-backed SID mapping with in-memory fallback, mode-based event routing, message queuing system, and safe message emission utilities.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Framework**: FastAPI + Socket.IO (python-socketio 5.11+)  
**Message Queue**: Redis (with in-memory fallback)  
**Storage**: In-memory dictionaries + Redis for persistence  
**Testing**: pytest 7.4+ with pytest-asyncio  
**Target Platform**: Linux server (AWS EC2/ECS compatible)  
**Project Type**: Real-time WebSocket service  
**Performance Goals**: 
- Socket.IO connections establish within 500ms for 95% of attempts
- Connection reconnection and message delivery within 1 second
- Mode switching completes within 500ms
- Support 100 concurrent Socket.IO connections

**Constraints**:
- Must support user_id-based and SID-only connection modes (backward compatibility)
- Must maintain Redis-backed SID mapping (with in-memory fallback)
- Must support three modes: Audio, Chat, Video
- Must handle concurrent connections per user_id (multi-device support)

**Scale/Scope**:
- Socket.IO event handlers: connect, disconnect, initial connect
- Mode routing: Chat, Audio, Video handlers
- SID mapping: Redis + in-memory dictionaries
- Message queuing: Redis-backed (with in-memory fallback)
- Room management: SID-based and user_id-based rooms

## Constitution Check

✅ **Real-Time Communication Architecture**: Socket.IO for bidirectional communication ✓  
✅ **Error Handling**: Graceful degradation with in-memory fallback when Redis unavailable ✓  
✅ **Real-Time Performance**: Connection establishment < 500ms ✓  
✅ **Security-First**: Connection validation and session management ✓  
✅ **Testability**: pytest with Socket.IO testing support ✓  
✅ **Specification-Driven**: Feature derived from spec.md ✓

**No violations identified.**

## Project Structure

### Source Code (repository root)

```text
api/
├── socket/
│   └── core.py                    # Socket.IO server initialization
├── pages/
│   └── ipersona/
│       └── socket/
│           ├── ipersona_socket.py     # Connection lifecycle and mode handlers
│           └── sid_manager.py         # SID-to-user_id mapping utilities
├── services/
│   └── redis/
│       └── redis_client.py      # Redis client for message queuing
└── tests/
    ├── integration/
    │   └── test_socket_connection.py  # Integration tests
    └── unit/
        └── test_sid_manager.py        # Unit tests for SID mapping
```

**Structure Decision**: Single backend project structure. Socket.IO handlers implemented in existing `api/pages/ipersona/socket/` module. SID mapping utilities in separate module for reusability. Redis client service for message queuing. Tests organized by type (integration/unit).

## Component Design

### 1. Connection Lifecycle Handler (`api/pages/ipersona/socket/ipersona_socket.py`)

**Responsibilities**:
- Handle @sio.event connect - Extract user_id, run_stage from query params
- Handle @sio.on("disconnect") - Cleanup resources, queue messages
- Handle @sio.on("initial connect") - Emit connection confirmation
- Map user_id to SID for reconnection support
- Join users to SID-based and user_id-based rooms
- Deliver queued messages on reconnection

**Input**: Socket.IO connection event with query parameters (user_id?, run_stage?)  
**Output**: "initial connect" event emission, session data storage

### 2. SID Manager (`api/pages/ipersona/socket/sid_manager.py`)

**Responsibilities**:
- Maintain user_id-to-SID mapping (Redis + in-memory)
- Update SID mapping on reconnection
- Track active SIDs per user_id (multi-device support)
- Provide mapping lookup utilities
- Handle Redis fallback to in-memory

### 3. Message Queue System (`api/pages/ipersona/socket/ipersona_socket.py`)

**Responsibilities**:
- Queue messages for disconnected users (Redis-backed)
- Deliver queued messages on reconnection
- Handle orphaned SID queues
- Support user_id-based and SID-based queuing
- Provide safe_emit_or_queue utility function

### 4. Mode-Based Routing (`api/pages/ipersona/socket/ipersona_socket.py`)

**Responsibilities**:
- Route Socket.IO events based on session mode:
  - Chat mode: "interview chat" event handler
  - Audio mode: "audio chat sentence" event handler
  - Video mode: "video chat" event handler
- Validate mode compatibility with events
- Support mode switching mid-session

### 5. Redis Client (`api/services/redis/redis_client.py`)

**Responsibilities**:
- Provide Redis connection for SID mapping persistence
- Provide Redis connection for message queuing
- Handle Redis connection failures gracefully
- Support in-memory fallback

## Data Flow

### Connection Establishment Flow

```
1. Client connects via Socket.IO with user_id query parameter
   ↓
2. @sio.event connect handler:
   - Extract user_id, run_stage from query params
   - Store in session (run_stage, user_id)
   - Join SID-based room
   - Join user_id-based room (if user_id provided)
   ↓
3. SID Manager:
   - Map user_id to SID (Redis + in-memory)
   - Track active SIDs per user_id
   ↓
4. Emit "initial connect" event
   ↓
5. Deliver queued messages for user_id (if any)
   ↓
6. Connection ready for interactions
```

### Reconnection Flow

```
1. User reconnects with same user_id
   ↓
2. @sio.event connect handler detects reconnection
   ↓
3. SID Manager:
   - Update user_id-to-SID mapping (new SID)
   - Keep old SID mapping for orphaned queue delivery
   ↓
4. Deliver messages queued during disconnection:
   - Check Redis queue for user_id
   - Check in-memory queue for user_id
   - Check orphaned SID queues
   ↓
5. Join new SID to rooms
   ↓
6. Connection restored with message delivery
```

### Mode-Based Event Routing Flow

```
1. Client sends Socket.IO event (e.g., "interview chat")
   ↓
2. Handler checks session mode:
   - Retrieve session mode from session metadata
   ↓
3. Route to appropriate handler:
   - mode="Chat" → "interview chat" handler
   - mode="Audio" → "audio chat sentence" handler
   - mode="Video" → "video chat" handler
   ↓
4. Validate mode compatibility:
   - If event incompatible with mode → error "INVALID_MODE_FOR_EVENT"
   ↓
5. Process event through mode-specific handler
```

## Error Handling

### Error Scenarios

**Connection Without Session**:
- Event: Socket.IO connection established but no session exists
- Action: Emit "SESSION_NOT_FOUND" error event
- Behavior: Allow connection but require valid session_id for interactions

**Redis Unavailable**:
- Event: Redis connection failure
- Action: Fallback to in-memory message queue
- Behavior: Log warning, attempt Redis reconnection, queue messages in memory

**Invalid Mode for Event**:
- Event: Client sends event incompatible with session mode
- Action: Return error "INVALID_MODE_FOR_EVENT"
- Behavior: Provide guidance on correct event for current mode

**Unsupported Mode**:
- Event: Client requests invalid mode
- Action: Return error "UNSUPPORTED_MODE"
- Behavior: List supported modes: "Chat", "Audio", "Video"

## Testing Strategy

### Unit Tests
- SID mapping utilities (user_id to SID)
- Message queue operations (enqueue, dequeue)
- Mode validation logic
- safe_emit_or_queue utility function

### Integration Tests
- Complete connection lifecycle (connect → interact → disconnect)
- Reconnection with message delivery
- Mode switching scenarios
- Multi-device support (multiple connections per user_id)
- Redis fallback to in-memory

### Performance Tests
- Connection establishment latency (< 500ms)
- Reconnection and message delivery latency (< 1 second)
- Concurrent connection handling (100 connections)

## Complexity Tracking

No violations identified. Feature follows constitution principles:
- Socket.IO standard patterns (no custom frameworks)
- Redis-backed persistence with graceful fallback (simplest reliable approach)
- Mode routing through standard event handlers (no complex abstractions)

---

**Plan Version**: 1.0.0 | **Created**: 2024-12-01 | **Status**: Ready for Task Breakdown

