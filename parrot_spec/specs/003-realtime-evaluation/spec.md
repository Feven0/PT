# Feature Specification: Real-Time Interview Evaluation

**Feature Branch**: `003-realtime-evaluation`  
**Created**: 2024-12-01  
**Status**: Draft  
**Input**: User description: "Users receive immediate AI evaluation feedback after answering each question"

## User Scenarios & Testing

### User Story 1 - Real-Time Interview Evaluation (Priority: P1)

**As a** trainee user,  
**I want to** receive immediate evaluation feedback after answering each question,  
**So that** I can adjust my approach for subsequent questions.

**Why this priority**: Real-time feedback is the core value proposition. Users expect instant assessment to improve their performance.

**Independent Test**: A user submits an answer, receives evaluation with relevance score, communication skills breakdown, and feedback within 3 seconds.

**Acceptance Scenarios**:

1. **Given** a user has answered a question and transcript is available,  
   **When** they trigger evaluation via "audio chat sentence" event,  
   **Then** the system SHALL send transcript and question context to OpenAI GPT,  
   **And** SHALL receive structured evaluation within 3 seconds,  
   **And** SHALL include relevance_score (0-100 integer),  
   **And** SHALL include communication_skills array with specific assessments,  
   **And** SHALL include feedback text with actionable recommendations,  
   **And** SHALL emit complete evaluation via "audio_realtime" event,  
   **And** SHALL save evaluation to ipersona-session-observer table.

2. **Given** OpenAI GPT service fails or times out,  
   **When** evaluation is requested,  
   **Then** the system SHALL return error code "LLM_SERVICE_UNAVAILABLE",  
   **And** SHALL queue the evaluation for retry via Celery,  
   **And** SHALL notify user via "notification" event,  
   **And** SHALL complete evaluation when service recovers.

3. **Given** evaluation completes successfully,  
   **When** the response is received,  
   **Then** the system SHALL update session progress tracking,  
   **And** SHALL calculate running average relevance score,  
   **And** SHALL store evaluation with question_id and session_id linkage.

4. **Given** a user submits a text response via "interview chat" event,  
   **When** the system evaluates the response,  
   **Then** it SHALL process text-based evaluation (no transcription needed),  
   **And** SHALL emit evaluation via "interview chat" event,  
   **And** SHALL emit final evaluation via "last_realtime_evaluation" event,  
   **And** SHALL complete within 3 seconds.

5. **Given** an audio-based interview session completes,  
   **When** the final question is answered,  
   **Then** the system SHALL emit "last_audio_realtime_evaluation" event with final evaluation summary.

### Edge Cases

- **What happens when** OpenAI API rate limits are hit?  
  **Answer**: System SHALL queue evaluations in Celery with exponential backoff, SHALL process when rate limit resets, SHALL notify users of delay via Socket.IO.

- **What happens when** transcript is empty or too short?  
  **Answer**: System SHALL return error "INVALID_TRANSCRIPT", SHALL prompt user to provide more detailed answer, SHALL not process evaluation.

- **What happens when** evaluation response is malformed JSON?  
  **Answer**: System SHALL use json_repair library to fix common errors, SHALL fallback to retry if irreparable, SHALL log error for monitoring.

## Requirements

### Functional Requirements

- **FR-001**: System MUST use OpenAI GPT as primary LLM for answer evaluation
- **FR-002**: System MUST provide evaluation within 3 seconds of transcript completion
- **FR-003**: System MUST include relevance_score (0-100 integer) in evaluation response
- **FR-004**: System MUST include communication_skills array with specific assessments
- **FR-005**: System MUST include feedback text with actionable recommendations
- **FR-006**: System MUST emit evaluation results via Socket.IO "audio_realtime" event
- **FR-007**: System MUST persist evaluations to ipersona-session-observer table
- **FR-008**: System MUST queue failed evaluations for retry via Celery
- **FR-009**: System MUST support text-based interview evaluation via Socket.IO "interview chat" event
- **FR-010**: System MUST emit final evaluation via "last_audio_realtime_evaluation" event after completion
- **FR-011**: System MUST emit final evaluation via "last_realtime_evaluation" event for text-based interviews
- **FR-012**: System MUST generate next interview question after evaluation completes via "audio chat sentence" event
- **FR-013**: System MUST emit "time_limit" event with recommended answer duration for each question
- **FR-014**: System MUST emit "audio_base64_chunks" and "audio-single-chunk" events for question audio synthesis
- **FR-015**: System MUST emit "audio-single-text-chunk-done" event when question audio synthesis completes
- **FR-016**: System MUST support resume flag to skip question generation when resuming session

### Key Entities

- **Observer Evaluation (ipersona-session-observer)**: Represents per-question evaluation. Attributes: id, attributes (JSON containing relevance_score, communication_skills, feedback), question_id, session_id linkage. Relationships: belongs to session.

- **Message (ipersona-chat)**: Represents question-answer exchange. Attributes: id, attributes (JSON containing question, answer, transcript), session_id linkage. Relationships: belongs to session.

## Success Criteria

### Measurable Outcomes

- **SC-001**: AI evaluation responses delivered within 3 seconds for 95% of requests
- **SC-002**: Evaluation accuracy provides meaningful feedback for 90% of answers
- **SC-003**: System handles 100 concurrent evaluation requests without degradation
- **SC-004**: Failed evaluations are retried successfully within 30 seconds

