# Parrot (iPersona) - Complete Specification

**Created**: 2024-12-01  
**Status**: Draft  
**Version**: 1.0.0

## RFC 2119 Compliance

This specification follows **RFC 2119** standards for requirement keywords. The following terms have specific meanings:

| Keyword | Meaning | Compliance Level |
|---------|---------|------------------|
| **MUST** / **SHALL** / **REQUIRED** | Absolute requirement - mandatory implementation | ❌ Never skip |
| **MUST NOT** / **SHALL NOT** | Absolute prohibition - must not be implemented | ❌ Never violate |
| **SHOULD** / **RECOMMENDED** | Strong recommendation - implement unless documented reason | ⚠️ Can skip with justification |
| **SHOULD NOT** / **NOT RECOMMENDED** | Strong discouragement - avoid unless documented reason | ⚠️ Can implement with justification |
| **MAY** / **OPTIONAL** | Truly optional - implementer's choice | ✅ Optional |

**Note**: In this specification, **SHALL** and **MUST** are used interchangeably to indicate mandatory requirements. Both terms have equivalent meaning per RFC 2119.

## System Overview

**Scope**: This specification covers ONLY the backend API and services for Parrot (iPersona). Frontend implementation is out of scope.

Parrot (iPersona) backend SHALL provide an AI-powered interview practice and evaluation platform backend that enables:
- REST API endpoints for session management, audio processing, and analytics
- Real-time WebSocket communication via Socket.IO for audio streaming and feedback
- Background task processing for heavy operations
- Integration with external AI/ML services (OpenAI GPT, Google Cloud STT)
- Data persistence via Strapi CMS GraphQL API

The backend SHALL serve three primary user types:
1. **Trainees** - Job seekers practicing interviews (via API clients)
2. **HR Professionals** - Assessing candidates (via API clients)
3. **Administrators** - Managing templates, analytics, and system configuration (via API clients)

---

## User Scenarios & Testing

### User Story 1 - Create and Start Interview Session (Priority: P1)

**As a** trainee user,  
**I want to** create a new interview session for a specific job profile,  
**So that** I can practice answering interview questions relevant to that position.

**Why this priority**: This is the core entry point for all interview practice. Without this, no other features can function.

**Independent Test**: A user can create a session, select a job profile, and receive an initial question within 30 seconds.

**Acceptance Scenarios**:

1. **Given** a user is authenticated and has selected a job profile,  
   **When** they request to create a new interview session,  
   **Then** the system SHALL create a session record in Strapi CMS,  
   **And** SHALL assign a unique session ID,  
   **And** SHALL initialize session status as "active",  
   **And** SHALL return session metadata within 1 second.

2. **Given** a user creates a session with template mode enabled,  
   **When** the system generates questions,  
   **Then** it SHALL use questions from the selected template,  
   **And** SHALL save template_id to session attributes.

3. **Given** a user creates a session with challenge mode enabled,  
   **When** the system generates questions,  
   **Then** it SHALL use questions from the selected challenge document,  
   **And** SHALL save challenge_id to session attributes.

4. **Given** a user attempts to create a session without authentication,  
   **When** they send the request,  
   **Then** the system SHALL return a 403 Unauthorized error,  
   **And** SHALL not create any session records.

---

### User Story 2 - Real-Time Audio Transcription (Priority: P1)

**As a** trainee user,  
**I want to** speak my answer and have it transcribed in real-time,  
**So that** I can see what the AI understood from my speech.

**Why this priority**: Real-time transcription is the foundation for AI evaluation. Users need immediate feedback on what was captured.

**Independent Test**: A user can speak for 10 seconds, receive transcription within 2 seconds, and see the text displayed in the UI.

**Acceptance Scenarios**:

1. **Given** a user has an active session and is connected via Socket.IO,  
   **When** they send audio data via "audio transcribe google" event,  
   **Then** the system SHALL route audio to Google Cloud STT service,  
   **And** SHALL receive transcription within 2 seconds,  
   **And** SHALL emit transcript via "audio_realtime" event,  
   **And** SHALL include confidence score in the response.

2. **Given** Google Cloud STT service fails or times out,  
   **When** audio transcription is requested,  
   **Then** the system SHALL automatically fallback to Faster Whisper,  
   **And** SHALL complete transcription within 5 seconds maximum,  
   **And** SHALL log the fallback event for monitoring.

3. **Given** audio data is malformed or empty,  
   **When** transcription is requested,  
   **Then** the system SHALL return an error with code "INVALID_AUDIO_FORMAT",  
   **And** SHALL not process the request,  
   **And** SHALL emit error via Socket.IO.

---

### User Story 3 - Real-Time Interview Evaluation (Priority: P1)

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

---

### User Story 4 - Session Management and Completion (Priority: P1)

**As a** trainee user,  
**I want to** complete my interview session and receive overall feedback,  
**So that** I can understand my overall performance and areas for improvement.

**Why this priority**: Users need closure on their practice session and comprehensive feedback to guide improvement.

**Independent Test**: A user can complete a session, receive overall evaluation, and see progress saved for future reference.

**Acceptance Scenarios**:

1. **Given** a user has an active session with at least one completed question,  
   **When** they request to close the session,  
   **Then** the system SHALL calculate overall evaluation metrics,  
   **And** SHALL compute average relevance score across all questions,  
   **And** SHALL determine performance level (poor/good/excellent based on score ranges),  
   **And** SHALL save overall evaluation to ipersona-session-overall-observer table,  
   **And** SHALL update session status to "completed",  
   **And** SHALL return overall feedback within 1 second.

2. **Given** a user attempts to close a session that is already completed,  
   **When** they send the close request,  
   **Then** the system SHALL return error code "SESSION_ALREADY_CLOSED",  
   **And** SHALL return existing overall evaluation instead of recalculating.

3. **Given** a session has been inactive for 2 hours,  
   **When** the system detects inactivity,  
   **Then** it SHALL automatically mark session as "inactive",  
   **And** SHALL allow user to resume within 24 hours,  
   **And** SHALL auto-close after 48 hours of inactivity.

---

### User Story 5 - Question Generation from Job Profile (Priority: P2)

**As a** trainee user,  
**I want to** have interview questions generated based on the job profile I'm applying for,  
**So that** I practice with relevant questions for that specific role.

**Why this priority**: Relevant questions increase the value of practice. Users need job-specific interview preparation.

**Independent Test**: A user selects a job profile, and the system generates 5-10 relevant interview questions within 10 seconds.

**Acceptance Scenarios**:

1. **Given** a user creates a session with a job_profile_id and generate=true,  
   **When** the system generates questions,  
   **Then** it SHALL analyze job profile (skills, competencies, requirements),  
   **And** SHALL send job profile to OpenAI GPT with question generation prompt,  
   **And** SHALL receive 5-10 relevant questions tailored to the job,  
   **And** SHALL save questions to session attributes as "generated_questions",  
   **And** SHALL complete generation within 10 seconds.

2. **Given** job profile lacks sufficient detail for question generation,  
   **When** the system attempts to generate questions,  
   **Then** it SHALL use default questions from a general template,  
   **And** SHALL log a warning about insufficient job profile data.

---

### User Story 6 - Template-Based Interview Questions (Priority: P2)

**As an** administrator,  
**I want to** create reusable interview templates,  
**So that** trainees can practice with standardized question sets.

**Why this priority**: Templates enable consistent evaluation and allow admins to curate quality questions.

**Independent Test**: An admin can create a template with questions, and trainees can use it to start sessions with those questions.

**Acceptance Scenarios**:

1. **Given** an administrator has template creation permissions,  
   **When** they create a new template via POST /api/ipersona/create_template_by_llm,  
   **Then** the system SHALL validate template data structure,  
   **And** SHALL save template to tinder-template table in Strapi,  
   **And** SHALL return template_id,  
   **And** SHALL allow template to be associated with job profiles.

2. **Given** a user creates a session with template_id,  
   **When** the system initializes questions,  
   **Then** it SHALL load questions from the template,  
   **And** SHALL save them to session attributes as "template_questions",  
   **And** SHALL use template questions instead of generating new ones.

---

### User Story 7 - Background Audio File Processing (Priority: P2)

**As a** trainee user,  
**I want to** upload pre-recorded audio files for analysis,  
**So that** I can get feedback on answers I prepared in advance.

**Why this priority**: Some users prefer to prepare answers offline. Background processing enables non-blocking uploads.

**Independent Test**: A user can upload an audio file, receive immediate acknowledgment, and get evaluation results via notification when processing completes.

**Acceptance Scenarios**:

1. **Given** a user uploads an audio file via POST /api/ipersona/audio_upload_external,  
   **When** the file is received,  
   **Then** the system SHALL validate file format (mp3, wav, webm, mp4),  
   **And** SHALL upload file to AWS S3,  
   **And** SHALL queue transcription task to Celery,  
   **And** SHALL return task_id immediately within 1 second,  
   **And** SHALL process transcription in background using AssemblyAI,  
   **And** SHALL emit "task_status" events via Socket.IO as processing progresses.

2. **Given** background processing completes successfully,  
   **When** transcription and evaluation finish,  
   **Then** the system SHALL save results to database,  
   **And** SHALL emit "notification" event with results,  
   **And** SHALL update task status to "completed".

---

### User Story 8 - Progress Tracking and Analytics (Priority: P2)

**As a** trainee user,  
**I want to** view my interview performance history and progress over time,  
**So that** I can identify improvement trends and areas needing work.

**Why this priority**: Progress tracking motivates users and provides visibility into skill development.

**Independent Test**: A user can view their past sessions, see score trends, and access detailed analytics for any session.

**Acceptance Scenarios**:

1. **Given** a user requests their session history via POST /api/ipersona/fetch_user_session,  
   **When** the system queries sessions,  
   **Then** it SHALL return all sessions for that user,  
   **And** SHALL include session status, overall score, date, and job profile association,  
   **And** SHALL support pagination with cursor-based pagination,  
   **And** SHALL filter by date range if "since" parameter provided.

2. **Given** a user requests overall progress metrics,  
   **When** the system calculates progress,  
   **Then** it SHALL compute average relevance score across all completed sessions,  
   **And** SHALL show score trends over time,  
   **And** SHALL highlight areas of strength and weakness,  
   **And** SHALL return data in format suitable for chart visualization.

---

### User Story 9 - Admin Dashboard and Analytics (Priority: P3)

**As an** administrator,  
**I want to** view system-wide analytics and user performance metrics,  
**So that** I can understand platform usage and identify areas for improvement.

**Why this priority**: Admin visibility enables data-driven decisions and platform optimization.

**Independent Test**: An admin can access dashboard, view user statistics, job performance metrics, and template usage analytics.

**Acceptance Scenarios**:

1. **Given** an administrator has admin role permissions,  
   **When** they request admin overview via POST /api/ipersona/admin_overview_status,  
   **Then** the system SHALL return aggregate statistics:
     - Total active sessions
     - Total completed sessions
     - Average session scores
     - Most popular job profiles
     - Template usage statistics
   **And** SHALL complete query within 1 second.

2. **Given** an admin requests performance data for a specific job profile,  
   **When** they query via POST /api/ipersona/admin_each_job_overview_data,  
   **Then** the system SHALL return performance metrics for all users who practiced that job,  
   **And** SHALL include average scores, completion rates, and common weaknesses.

---

### Edge Cases

- **What happens when** a user disconnects during an active interview session?  
  **Answer**: System SHALL maintain session state in database, SHALL queue messages in Redis, SHALL restore session when user reconnects with same session_id.

- **What happens when** Google Cloud STT quota is exceeded?  
  **Answer**: System SHALL automatically fallback to Faster Whisper, SHALL log quota exceeded event, SHALL notify administrators via monitoring alerts.

- **What happens when** OpenAI API rate limits are hit?  
  **Answer**: System SHALL queue evaluations in Celery with exponential backoff, SHALL process when rate limit resets, SHALL notify users of delay via Socket.IO.

- **What happens when** Strapi CMS is unavailable?  
  **Answer**: System SHALL return 503 Service Unavailable, SHALL log error, SHALL retry with exponential backoff, SHALL not lose data (queue operations).

- **What happens when** audio file exceeds size limits?  
  **Answer**: System SHALL reject upload with error "FILE_TOO_LARGE", SHALL specify maximum size (e.g., 100MB), SHALL not process the file.

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide REST API endpoints for session management, audio processing, and analytics
- **FR-002**: System MUST provide Socket.IO real-time events for audio transcription and evaluation
- **FR-003**: System MUST use Google Cloud Speech-to-Text as primary STT service for real-time interviews
- **FR-004**: System MUST use OpenAI GPT as primary LLM for question generation and answer evaluation
- **FR-005**: System MUST persist all session data, evaluations, and user progress in Strapi CMS
- **FR-006**: System MUST authenticate all API requests using Bearer token authentication
- **FR-007**: System MUST support background processing via Celery for long-running operations
- **FR-008**: System MUST store audio files in AWS S3 with presigned URLs for secure access
- **FR-009**: System MUST support multiple STT fallback services (Faster Whisper, AssemblyAI, OpenAI Whisper, Gemini)
- **FR-010**: System MUST generate interview questions based on job profiles using AI
- **FR-011**: System MUST support reusable interview templates created by administrators
- **FR-012**: System MUST calculate and store overall session evaluations
- **FR-013**: System MUST track user progress across multiple sessions
- **FR-014**: System MUST provide admin dashboard with analytics and metrics
- **FR-015**: System MUST handle session timeouts and reconnection scenarios
- **FR-016**: System MUST validate audio file formats before processing
- **FR-017**: System MUST emit real-time notifications for background task completion
- **FR-018**: System MUST support filtering and pagination for session queries
- **FR-019**: System MUST calculate performance levels (poor/good/excellent) based on relevance scores
- **FR-020**: System MUST support challenge-based interviews with predefined question sets

### Key Entities

- **Session (ipersona-session)**: Represents a single interview practice session. Attributes: id, status, slug, attributes (JSON), createdAt, user_id, job_profile_id, template_id, challenge_id. Relationships: messages, observer evaluations, overall observer.

- **Message (ipersona-chat)**: Represents a question-answer exchange. Attributes: id, attributes (JSON containing question, answer, transcript), session_id linkage. Relationships: belongs to session.

- **Observer Evaluation (ipersona-session-observer)**: Represents per-question evaluation. Attributes: id, attributes (JSON containing relevance_score, communication_skills, feedback), question_id, session_id linkage. Relationships: belongs to session.

- **Overall Observer (ipersona-session-overall-observer)**: Represents complete session evaluation. Attributes: id, attributes (JSON containing overall_score, performance_level, summary), session_id linkage. Relationships: belongs to session.

- **Trainee (ipersona-trainee)**: Represents user profile. Attributes: id, user_id, profile data. Relationships: has many sessions.

- **Job Profile (tinder-job-profile)**: Represents job posting/description. Attributes: id, title, description, skills, competencies. Relationships: has many sessions.

- **Template (tinder-template)**: Represents reusable question set. Attributes: id, name, questions (JSON array), job_profile associations. Relationships: can be used by many sessions.

- **Challenge Document (challenge-document)**: Represents challenge-based question set. Attributes: id, name, questions (JSON array). Relationships: can be used by many sessions.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create and start an interview session within 1 second of request
- **SC-002**: Real-time audio transcription completes within 2 seconds for 95% of requests
- **SC-003**: AI evaluation responses delivered within 3 seconds for 95% of requests
- **SC-004**: System handles 100 concurrent interview sessions without performance degradation
- **SC-005**: API endpoints respond within 1 second for 99% of requests
- **SC-006**: Background file processing completes within 5 minutes for files up to 50MB
- **SC-007**: 90% of users successfully complete at least one full interview session
- **SC-008**: System maintains 99.5% uptime excluding scheduled maintenance
- **SC-009**: Session data is persisted with 100% reliability (no data loss)
- **SC-010**: Admin dashboard queries complete within 1 second for standard reports

---

## Non-Functional Requirements

### Performance (NFR-001)

- Socket.IO connection establishment: < 500ms target, < 1s maximum
- Google Cloud STT transcription: < 2s target, < 5s maximum
- AI evaluation response: < 3s target, < 10s maximum
- REST API endpoint response: < 1s target, < 3s maximum
- File upload acknowledgment: < 1s target, < 2s maximum

### Throughput (NFR-002)

- Concurrent sessions: 100 simultaneous sessions
- API requests: 1000 requests per minute
- File uploads: 50 uploads per minute
- Database queries: < 100ms average response time

### Reliability (NFR-003)

- System uptime: 99.5% availability target
- Data persistence: 100% reliability (no data loss)
- Service fallback: Automatic failover within 5 seconds
- Error recovery: Graceful degradation with user notification

### Security (NFR-004)

- Authentication: Token-based for all protected endpoints
- Data encryption: TLS 1.2+ for all network communication
- Input validation: Sanitization to prevent injection attacks
- Secrets management: AWS Secrets Manager for API keys and credentials
- Data encryption at rest: S3 and database encryption enabled

### Scalability (NFR-005)

- Horizontal scaling: System MUST support multiple backend instances
- Database scaling: Strapi CMS MUST support increased load
- File storage: AWS S3 MUST handle unlimited file uploads
- Background workers: Celery workers MUST scale independently

---

## API Contracts

### REST Endpoints

#### Session Management
- `POST /api/ipersona/create_user_session` - Create new interview session
- `POST /api/ipersona/close_session` - Complete and close session
- `POST /api/ipersona/fetch_user_session` - Get user's session history
- `POST /api/ipersona/fetch_single_session` - Get single session details

#### STT Services
- `POST /api/ipersona/stt/google-upload` - Upload audio for Google Cloud STT
- `POST /api/ipersona/stt/whisper-upload` - Upload audio for Faster Whisper
- `POST /api/ipersona/stt/openai-upload` - Upload audio for OpenAI Whisper
- `POST /api/ipersona/stt/gemini-upload` - Upload audio for Google Gemini

#### Background Processing
- `POST /api/ipersona/audio_upload_external` - Upload audio for background processing
- `POST /api/ipersona/files_upload_external` - Upload files for background processing

#### Templates
- `POST /api/ipersona/get_all_tinder_templates` - List all templates
- `POST /api/ipersona/create_template_by_llm` - Create template using AI
- `POST /api/ipersona/update_tinder_template` - Update existing template

#### Admin
- `POST /api/ipersona/admin_overview_status` - Get admin dashboard overview
- `POST /api/ipersona/admin_allusers_data` - Get all users data
- `POST /api/ipersona/admin_each_job_overview_data` - Get job-specific analytics

#### Health
- `GET /api/ipersona/health` - Health check endpoint

### Socket.IO Events

#### Client → Server
- `initial connect` - Establish session connection with auth data
- `audio transcribe google` - Send audio for Google Cloud STT transcription
- `audio chat sentence` - Send audio for real-time interview evaluation
- `audio transcribe whisper` - Send audio for Faster Whisper transcription
- `audio transcribe` - Send audio for AssemblyAI transcription
- `interview chat` - Send text message for evaluation

#### Server → Client
- `audio_realtime` - Real-time transcription and evaluation results
- `task_status` - Background task progress updates
- `notification` - System notifications and alerts

---

## Error Handling

### Error Response Format

All errors SHALL follow this structure:

```json
{
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE_CONSTANT",
  "details": "Optional additional details",
  "timestamp": "2024-12-01T10:30:00Z",
  "request_id": "uuid-for-tracing"
}
```

### Standard Error Codes

- `SESSION_NOT_FOUND` (404) - Requested session does not exist
- `INVALID_AUDIO_FORMAT` (400) - Audio file format not supported
- `STT_SERVICE_UNAVAILABLE` (503) - STT service failure
- `LLM_SERVICE_UNAVAILABLE` (503) - LLM service failure
- `UNAUTHORIZED` (403) - Authentication required
- `FILE_TOO_LARGE` (400) - Uploaded file exceeds size limit
- `SESSION_ALREADY_CLOSED` (400) - Cannot modify closed session
- `INVALID_SESSION_STATE` (400) - Session in invalid state for operation

---

## Data Models

### Session Status Values

- `active` - Session is currently in progress
- `completed` - Session has been finished
- `inactive` - Session paused or timed out
- `cancelled` - Session was cancelled

### Performance Levels

- `poor` - Relevance score 0-40
- `good` - Relevance score 41-70
- `excellent` - Relevance score 71-100

### Evaluation Structure

```json
{
  "relevance_score": 85,
  "communication_skills": [
    {
      "skill": "clarity",
      "rating": "excellent",
      "feedback": "Clear and concise explanation"
    }
  ],
  "feedback": "Strong answer demonstrating relevant experience...",
  "question_id": 123,
  "timestamp": "2024-12-01T10:30:00Z"
}
```

---

**End of Specification**

