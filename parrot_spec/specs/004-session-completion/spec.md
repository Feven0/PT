# Feature Specification: Session Management and Completion

**Feature Branch**: `004-session-completion`  
**Created**: 2024-12-01  
**Status**: Draft  
**Input**: User description: "Users can manage interview session lifecycle including closing sessions, handling inactivity, resetting closed sessions, and fetching overall evaluation results. Note: Overall evaluation generation process is detailed in Feature 012-overall-evaluation."

## User Scenarios & Testing

### User Story 1 - Session Management and Completion (Priority: P1)

**As a** trainee user,  
**I want to** manage my interview session lifecycle (close, reset, resume),  
**So that** I can control when sessions are completed and retrieve overall evaluation results.

**Why this priority**: Users need control over session lifecycle and ability to retrieve completed session evaluations.

**Independent Test**: A user can close a session, reset it if needed, and fetch overall evaluation results.

**Acceptance Scenarios**:

1. **Given** a user has an active session with at least one completed question,  
   **When** they request to close the session via POST /close_session,  
   **Then** the system SHALL trigger overall evaluation generation (see Feature 012-overall-evaluation),  
   **And** SHALL update session status to "Closed" or "Completed",  
   **And** SHALL return session closure acknowledgment within 1 second.

2. **Given** a user attempts to close a session that is already closed/completed,  
   **When** they send the close request,  
   **Then** the system SHALL return error code "SESSION_ALREADY_CLOSED",  
   **And** SHALL return existing overall evaluation instead of regenerating (see Feature 012-overall-evaluation).

3. **Given** a session has been inactive for 2 hours,  
   **When** the system detects inactivity,  
   **Then** it SHALL automatically mark session as "inactive",  
   **And** SHALL allow user to resume within 24 hours,  
   **And** SHALL auto-close after 48 hours of inactivity.

4. **Given** a user has a closed session,  
   **When** they request to reset it via POST /reset_closed_session,  
   **Then** the system SHALL update session status from "Closed" to "Incomplete",  
   **And** SHALL delete all observer evaluations linked to the session,  
   **And** SHALL allow the user to continue the session.

5. **Given** a user requests overall evaluation for a completed session,  
   **When** they query via POST /fetch_session_overall_evaluation,  
   **Then** the system SHALL return overall evaluation data (see Feature 012-overall-evaluation for evaluation structure).

### Edge Cases

- **What happens when** a user disconnects during an active interview session?  
  **Answer**: System SHALL maintain session state in database, SHALL queue messages in Redis, SHALL restore session when user reconnects with same session_id.

- **What happens when** session has no completed questions at closure?  
  **Answer**: System SHALL return error "SESSION_INCOMPLETE", SHALL allow session to remain active, SHALL prompt user to complete at least one question.

- **What happens when** user attempts to reset a session that is not in "Closed" status?  
  **Answer**: System SHALL return error indicating current status, SHALL allow reset only for "Closed" sessions.

## Requirements

### Functional Requirements

- **FR-001**: System MUST support closing sessions via POST /close_session endpoint
- **FR-002**: System MUST trigger overall evaluation generation when session closes (see Feature 012-overall-evaluation)
- **FR-003**: System MUST update session status to "Closed" or "Completed" upon closure
- **FR-004**: System MUST prevent closing already-closed sessions (return error "SESSION_ALREADY_CLOSED")
- **FR-005**: System MUST detect and handle session inactivity (2 hour timeout)
- **FR-006**: System MUST support session resume within 24 hours of inactivity
- **FR-007**: System MUST auto-close sessions after 48 hours of inactivity
- **FR-008**: System MUST reset closed sessions to incomplete status via POST /reset_closed_session
- **FR-009**: System MUST delete observer evaluations when resetting a closed session
- **FR-010**: System MUST only allow reset for sessions with status "Closed"
- **FR-011**: System MUST support fetching overall evaluation via POST /fetch_session_overall_evaluation endpoint (see Feature 012-overall-evaluation for response structure)
- **FR-012**: System MUST maintain session state persistence through disconnections
- **FR-013**: System MUST restore session state when user reconnects with same session_id

### Key Entities

- **Session (ipersona-session)**: Status transitions: pending → active → completed/inactive → closed. Attributes: id, status, slug, attributes (JSON), createdAt, user_id, job_profile_id. Relationships: messages, observer evaluations, overall observer.

- **Overall Observer (ipersona-session-overall-observer)**: Represents complete session evaluation. See Feature 012-overall-evaluation for detailed structure and generation process.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Session closure completes within 1 second for 99% of requests
- **SC-002**: Session state persists correctly through disconnections
- **SC-003**: Inactive sessions are properly detected and managed
- **SC-004**: Session reset completes within 1 second for 99% of requests
- **SC-005**: Overall evaluation fetch endpoint responds within 1 second (see Feature 012-overall-evaluation)

## Related Features

- **Feature 012-overall-evaluation**: Details the comprehensive overall evaluation generation process, including OpenAI GPT analysis, metrics calculation, and evaluation structure.

