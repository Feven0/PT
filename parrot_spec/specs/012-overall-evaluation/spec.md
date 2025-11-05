# Feature Specification: Overall Interview Evaluation

**Feature Branch**: `012-overall-evaluation`  
**Created**: 2024-12-01  
**Status**: Draft  
**Input**: User description: "Parrot analyzes the complete interview session and generates comprehensive overall evaluation metrics and feedback after all questions are answered"

## User Scenarios & Testing

### User Story 1 - Overall Interview Evaluation (Priority: P1)

**As a** trainee user,  
**I want to** receive comprehensive overall evaluation of my entire interview session,  
**So that** I can understand my overall performance, strengths, weaknesses, and areas for improvement across the entire interview.

**Why this priority**: Overall evaluation provides closure and comprehensive feedback that helps users understand their performance holistically, beyond individual question assessments.

**Independent Test**: A user completes a session with multiple answered questions, and the system automatically generates and saves overall evaluation with metrics, performance score, and competency assessment.

**Acceptance Scenarios**:

1. **Given** a user has completed an interview session with at least one answered question,  
   **When** the session reaches completion (all questions answered or session closed),  
   **Then** the system SHALL automatically trigger overall evaluation calculation,  
   **And** SHALL retrieve complete interview history (all questions and answers),  
   **And** SHALL send interview history to OpenAI GPT for overall analysis,  
   **And** SHALL generate overall evaluation response with competency assessment,  
   **And** SHALL generate evaluation metrics (time_management, relevancy, overall_performance_score, rating),  
   **And** SHALL calculate time management metrics from interview history,  
   **And** SHALL calculate relevancy scores from per-question evaluations,  
   **And** SHALL compute overall_performance_score as average of relevance scores,  
   **And** SHALL determine performance rating (poor/good/excellent) based on score ranges,  
   **And** SHALL save overall evaluation to ipersona-session-overall-observer table,  
   **And** SHALL complete within 10 seconds.

2. **Given** a user requests overall evaluation for a completed session,  
   **When** they query via POST /fetch_session_overall_evaluation with sessionId,  
   **Then** the system SHALL retrieve overall evaluation from ipersona-session-overall-observer table,  
   **And** SHALL return interview_evaluation (overall feedback with competency, message),  
   **And** SHALL return interview_evaluation_metrics (time_management, relevancy, overall_performance_score, rating),  
   **And** SHALL return response within 1 second.

3. **Given** overall evaluation is triggered for a session,  
   **When** OpenAI GPT service fails or times out,  
   **Then** the system SHALL queue overall evaluation task for retry via Celery,  
   **And** SHALL log the error for monitoring,  
   **And** SHALL complete evaluation when service recovers.

4. **Given** an external audio file is processed and session completes,  
   **When** overall evaluation is triggered via overall_interview_evaluations_external,  
   **Then** the system SHALL generate overall evaluation using external audio transcriptions,  
   **And** SHALL save to ipersona-session-overall-observer table,  
   **And** SHALL complete within 10 seconds.

5. **Given** overall evaluation is triggered for a session that already has overall evaluation,  
   **When** the evaluation completes,  
   **Then** the system SHALL update existing overall evaluation record,  
   **And** SHALL not create duplicate records.

### Edge Cases

- **What happens when** session has no completed questions when overall evaluation is triggered?  
  **Answer**: System SHALL return error "INSUFFICIENT_DATA", SHALL log warning, SHALL not generate overall evaluation until at least one question is answered.

- **What happens when** OpenAI GPT returns malformed JSON for overall evaluation?  
  **Answer**: System SHALL use json_repair library to fix common errors, SHALL fallback to retry if irreparable, SHALL log error for monitoring.

- **What happens when** overall evaluation calculation exceeds 10 seconds?  
  **Answer**: System SHALL continue processing in background, SHALL save result when complete, SHALL notify user via Socket.IO when ready.

- **What happens when** user requests overall evaluation for a session that doesn't exist?  
  **Answer**: System SHALL return 404 error with message "Session not found", SHALL not attempt to generate evaluation.

## Requirements

### Functional Requirements

- **FR-001**: System MUST automatically trigger overall evaluation when session completes
- **FR-002**: System MUST use OpenAI GPT as primary LLM for overall interview analysis
- **FR-003**: System MUST retrieve complete interview history (all questions and answers) for analysis
- **FR-004**: System MUST generate overall evaluation response with competency assessment and message
- **FR-005**: System MUST generate evaluation metrics including time_management, relevancy, overall_performance_score, and rating
- **FR-006**: System MUST calculate time management metrics from interview history timestamps
- **FR-007**: System MUST calculate relevancy scores from per-question evaluation data
- **FR-008**: System MUST compute overall_performance_score as average of relevance scores across all questions
- **FR-009**: System MUST determine performance rating (poor/good/excellent) based on score percentage ranges
- **FR-010**: System MUST save overall evaluation to ipersona-session-overall-observer table
- **FR-011**: System MUST support fetching overall evaluation via POST /fetch_session_overall_evaluation endpoint
- **FR-012**: System MUST return overall evaluation within 1 second when fetching from database
- **FR-013**: System MUST complete overall evaluation generation within 10 seconds
- **FR-014**: System MUST support overall evaluation for external audio file processing via overall_interview_evaluations_external
- **FR-015**: System MUST queue failed overall evaluations for retry via Celery
- **FR-016**: System MUST use read_prompt_overall_evaluation to generate evaluation prompt
- **FR-017**: System MUST use read_prompt_interview_evaluation_metrics to generate metrics prompt
- **FR-018**: System MUST update session status to "Completed" after overall evaluation is saved
- **FR-019**: System MUST update existing overall evaluation record if evaluation already exists for session

### Key Entities

- **Overall Observer (ipersona-session-overall-observer)**: Represents complete session evaluation. Attributes: id, attributes (JSON containing interview_evaluation and interview_evaluation_metrics), i_persona_session linkage, status. Relationships: belongs to session.

- **Session (ipersona-session)**: Required for overall evaluation context. Status transitions to "Completed" after overall evaluation is saved. Attributes: id, status, slug, attributes (JSON), createdAt, user_id.

- **Observer Evaluation (ipersona-session-observer)**: Per-question evaluations used to calculate overall metrics. Attributes: relevance_score, communication_skills. Relationships: belongs to session.

- **Message (ipersona-chat)**: Interview history used for overall analysis. Contains all questions and answers. Relationships: belongs to session.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Overall evaluation completes within 10 seconds for 95% of sessions
- **SC-002**: Overall evaluation accurately reflects session performance with meaningful metrics
- **SC-003**: Overall evaluation fetch endpoint responds within 1 second for 99% of requests
- **SC-004**: Failed overall evaluations are retried successfully within 60 seconds

