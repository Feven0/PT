# Feature Specification: Socket.IO Mode Management and Connection Lifecycle

**Feature Branch**: `011-socket-mode-management`  
**Created**: 2024-12-01  
**Status**: Draft  
**Input**: User description: "Parrot manages Socket.IO connections and supports multiple interview interaction modes (Audio, Chat, and Video). The system handles connection lifecycle, mode-based routing, and session management for real-time interactions."

## User Scenarios & Testing

### User Story 1 - Socket.IO Connection Lifecycle Management (Priority: P1)

**As a** trainee user,  
**I want to** establish and maintain Socket.IO connections for real-time interview interactions,  
**So that** I can receive instant feedback and updates during my interview session.

**Why this priority**: Socket.IO connections are the foundation for all real-time interactions. Without reliable connection management, no real-time features can function properly.

**Independent Test**: A user can connect via Socket.IO, receive connection confirmation, exchange messages, and gracefully disconnect. The system handles reconnections and delivers queued messages.

**Acceptance Scenarios**:

1. **Given** a user initiates a Socket.IO connection with user_id query parameter,  
   **When** the connection is established,  
   **Then** the system SHALL emit "initial connect" event,  
   **And** SHALL store user_id and run_stage in session,  
   **And** SHALL join user to SID-based room and user_id-based room,  
   **And** SHALL map user_id to SID for reconnection support,  
   **And** SHALL deliver any queued messages for that user.

2. **Given** a user's Socket.IO connection drops unexpectedly,  
   **When** they reconnect with the same user_id,  
   **Then** the system SHALL recognize the reconnection,  
   **And** SHALL update SID mapping,  
   **And** SHALL deliver any messages queued during disconnection,  
   **And** SHALL maintain session continuity.

3. **Given** a user explicitly disconnects via Socket.IO disconnect event,  
   **When** the disconnect is processed,  
   **Then** the system SHALL clean up session resources,  
   **And** SHALL remove SID from active connections,  
   **And** SHALL queue any pending messages for delivery on reconnection.

4. **Given** a user connects without user_id query parameter,  
   **When** the connection is established,  
   **Then** the system SHALL use legacy SID-only mode,  
   **And** SHALL store only run_stage in session,  
   **And** SHALL emit "initial connect" event,  
   **And** SHALL support SID-based message delivery only.

### User Story 2 - Interview Mode Management (Priority: P1)

**As a** trainee user,  
**I want to** interact with interviews in different modes (Audio, Chat, and Video),  
**So that** I can choose the interaction style that best suits my needs.

**Why this priority**: Mode management enables flexible interview experiences. Users expect to switch between text-based, audio-based, and video-based interactions based on their needs.

**Supported modes**:
- **Audio Mode**: Real-time voice interaction with transcription and audio synthesis
- **Chat Mode**: Text-based question-answer interaction
- **Video Mode**: Video-based interviews with facial expression analysis and audio processing

**Independent Test**: A user can create a session, set the mode (Audio, Chat, or Video), and interact through the appropriate Socket.IO events for that mode.

**Acceptance Scenarios**:

1. **Given** a user creates a session with mode="Chat",  
   **When** they interact via Socket.IO,  
   **Then** the system SHALL route interactions to "interview chat" event handler,  
   **And** SHALL process text-based question-answer exchanges,  
   **And** SHALL not require audio transcription services.

2. **Given** a user creates a session with mode="Audio" (or default audio mode),  
   **When** they interact via Socket.IO,  
   **Then** the system SHALL route interactions to "audio chat sentence" event handler,  
   **And** SHALL process audio transcription and synthesis,  
   **And** SHALL require audio streaming capabilities.

3. **Given** a user updates session mode via POST /update_session_mode,  
   **When** the mode is changed,  
   **Then** the system SHALL update session metadata,  
   **And** SHALL route subsequent Socket.IO interactions to the appropriate mode handler,  
   **And** SHALL return updated session status.

4. **Given** a user creates a session with mode="Video",  
   **When** they interact via Socket.IO,  
   **Then** the system SHALL route interactions to "video chat" event handler,  
   **And** SHALL process video frames alongside audio,  
   **And** SHALL support facial expression analysis,  
   **And** SHALL require video streaming capabilities.

5. **Given** a user attempts to use an unsupported mode,  
   **When** they request an invalid mode,  
   **Then** the system SHALL return error code "UNSUPPORTED_MODE" with supported modes listed ("Chat", "Audio", "Video").

### Edge Cases

- **What happens when** a user connects via Socket.IO but session doesn't exist?  
  **Answer**: System SHALL emit error event "SESSION_NOT_FOUND", SHALL log the error, SHALL allow connection but SHALL require valid session_id for any interaction events.

- **What happens when** multiple Socket.IO connections exist for the same user_id?  
  **Answer**: System SHALL track all active SIDs per user, SHALL deliver messages to all active connections, SHALL support multi-device scenarios.

- **What happens when** a user switches modes mid-session?  
  **Answer**: System SHALL update session mode, SHALL route new interactions to new mode handler, SHALL preserve existing session data (messages, evaluations), SHALL support mode transitions seamlessly.

- **What happens when** Socket.IO connection times out due to inactivity?  
  **Answer**: System SHALL implement connection timeout handling, SHALL queue messages for disconnected users, SHALL support reconnection with message delivery.

- **What happens when** a user sends events for wrong mode (e.g., sends "interview chat" when mode is Audio)?  
  **Answer**: System SHALL validate mode compatibility, SHALL return error "INVALID_MODE_FOR_EVENT", SHALL provide guidance on correct event for current mode.

- **What happens when** Redis is unavailable for message queuing?  
  **Answer**: System SHALL fallback to in-memory message queue, SHALL log warning, SHALL attempt Redis reconnection, SHALL support graceful degradation.

## Requirements

### Functional Requirements

- **FR-001**: System MUST handle Socket.IO connection lifecycle via @sio.event connect and @sio.on("disconnect") handlers
- **FR-002**: System MUST emit "initial connect" event when Socket.IO connection is established
- **FR-003**: System MUST support user_id-based connection management for reconnection support
- **FR-004**: System MUST support SID-only connection mode for backward compatibility
- **FR-005**: System MUST map user_id to SID for reconnection and message routing
- **FR-006**: System MUST queue messages for disconnected users and deliver on reconnection
- **FR-007**: System MUST maintain SID-to-user_id mapping in Redis (with in-memory fallback)
- **FR-008**: System MUST support session mode parameter: "Chat", "Audio", and "Video"
- **FR-009**: System MUST route Socket.IO events based on session mode:
  - Chat mode: "interview chat" event handler
  - Audio mode: "audio chat sentence" event handler
  - Video mode: "video chat" event handler
- **FR-010**: System MUST update session mode via POST /update_session_mode endpoint
- **FR-011**: System MUST validate mode compatibility with Socket.IO events
- **FR-012**: System MUST support multiple active connections per user_id (multi-device support)
- **FR-013**: System MUST join users to both SID-based and user_id-based rooms for targeted messaging
- **FR-014**: System MUST clean up connection resources on disconnect
- **FR-015**: System MUST support connection timeout handling and graceful disconnection
- **FR-016**: System MUST support Video mode with video frame processing and facial expression analysis
- **FR-017**: System MUST support safe message emission with queuing fallback via safe_emit_or_queue utility
- **FR-018**: System MUST handle reconnection scenarios with SID mapping updates
- **FR-019**: System MUST deliver orphaned SID queues to users upon reconnection with user_id

### Key Entities

- **Socket.IO Connection**: Represents a WebSocket connection. Attributes: sid (session ID), user_id (optional), run_stage, connected_at, last_activity. Relationships: belongs to user (if user_id provided), associated with session for interactions.

- **Session Mode**: Represents interview interaction mode. Supported modes: "Chat", "Audio", "Video". Mode determines which Socket.IO event handlers are used and what capabilities are required.

- **Message Queue**: Represents queued messages for disconnected users. Attributes: user_id or sid, messages (array of event/data pairs), queued_at. Relationships: belongs to user (if user_id available) or SID (legacy). Supports Redis-backed persistence with in-memory fallback.

**Note**: The Socket.IO mode management architecture supports three interaction modes: Audio (voice-based), Chat (text-based), and Video (video-based with facial analysis). All three modes are fully supported features of the system.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Socket.IO connections establish within 500ms for 95% of connection attempts
- **SC-002**: Connection reconnection succeeds and delivers queued messages within 1 second for 99% of cases
- **SC-003**: Mode switching completes within 500ms without interrupting active sessions
- **SC-004**: System handles 100 concurrent Socket.IO connections without degradation
- **SC-005**: Message queuing and delivery succeeds for 99.9% of disconnected user scenarios
- **SC-006**: Multi-device support (multiple connections per user) works correctly for 100% of cases

