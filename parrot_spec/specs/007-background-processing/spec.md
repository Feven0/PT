# Feature Specification: Background Audio File Processing

**Feature Branch**: `007-background-processing`  
**Created**: 2024-12-01  
**Status**: Draft  
**Input**: User description: "Users can upload pre-recorded audio files for analysis. Parrot supports three distinct upload scenarios: single audio file (interview recording), dual audio files (separate question and answer files), and answer file with template questions (answer audio matched to predefined template questions)."

## User Scenarios & Testing

### User Story 1 - Single Audio File Upload (Priority: P1)

**As a** trainee user,  
**I want to** upload a single pre-recorded audio file containing a complete interview recording,  
**So that** Parrot can extract questions and answers from the transcript and create an interview session for evaluation.

**Why this priority**: This is the most common use case - users record their entire interview practice session in one audio file.

**Independent Test**: A user uploads a single audio file via POST /audio_upload_external, receives immediate acknowledgment, and gets evaluation results via notification when processing completes.

**Acceptance Scenarios**:

1. **Given** a user uploads a single audio file via POST /api/ipersona/audio_upload_external,  
   **When** the file is received,  
   **Then** the system SHALL validate file format (mp3, wav, webm, mp4, or text/pdf/doc),  
   **And** SHALL upload file to AWS S3,  
   **And** SHALL queue transcription task to Celery (task_type: "audio_processing"),  
   **And** SHALL return acknowledgment immediately within 1 second,  
   **And** SHALL process transcription in background using AssemblyAI (for audio files),  
   **And** SHALL extract text content for document files (text/pdf/doc),  
   **And** SHALL validate interview content using AI-powered content validation,  
   **And** SHALL extract questions and answers from the single transcript,  
   **And** SHALL create interview session,  
   **And** SHALL save extracted Q&A pairs as messages to database,  
   **And** SHALL trigger overall evaluation automatically,  
   **And** SHALL emit "processing_update_success" or "processing_update_failed" events via Socket.IO or notifications.

2. **Given** uploaded audio file contains invalid interview content (no Q/A detected, gibberish, or non-interview content),  
   **When** content validation runs,  
   **Then** the system SHALL fail validation,  
   **And** SHALL emit "processing_update_failed" event with error reason,  
   **And** SHALL update task status to "failed" in Redis,  
   **And** SHALL save notification for user.

3. **Given** background processing completes successfully,  
   **When** transcription, content extraction, and evaluation finish,  
   **Then** the system SHALL save results to database,  
   **And** SHALL emit "processing_update_success" event or notification,  
   **And** SHALL update task status to "completed" in Redis.

### User Story 2 - Dual Audio Files Upload (Priority: P1)

**As a** trainee user,  
**I want to** upload two separate audio files (one containing questions, one containing answers),  
**So that** Parrot can match questions to answers and create an interview session for evaluation.

**Why this priority**: Some users record questions and answers separately, requiring structured matching.

**Independent Test**: A user uploads question_file and answer_file via POST /files_upload_external, receives immediate acknowledgment, and gets evaluation results when processing completes.

**Acceptance Scenarios**:

1. **Given** a user uploads question_file and answer_file via POST /api/ipersona/files_upload_external,  
   **When** both files are received,  
   **Then** the system SHALL validate both file formats (mp3, wav, webm, mp4),  
   **And** SHALL upload both files to AWS S3,  
   **And** SHALL queue dual audio processing task to Celery (task_type: "dual_audio_processing"),  
   **And** SHALL return acknowledgment immediately within 1 second,  
   **And** SHALL transcribe question_file separately using AssemblyAI,  
   **And** SHALL transcribe answer_file separately using AssemblyAI,  
   **And** SHALL use OpenAI embeddings (text-embedding-3-small) to compute semantic embeddings for questions and answers,  
   **And** SHALL compute cosine similarity between question embeddings and answer embeddings,  
   **And** SHALL use structured question-answer matching algorithm with embedding-based similarity scoring,  
   **And** SHALL apply three-band routing: strong accept (>= 30%), borderline (18-30% with LLM verification), low (< 18% rejected),  
   **And** SHALL filter matches with relevance_score >= 90 (from embedding similarity),  
   **And** SHALL create interview session with upload_metadata indicating "qa_split_mode",  
   **And** SHALL save matched Q&A pairs as messages to database,  
   **And** SHALL trigger overall evaluation automatically,  
   **And** SHALL emit success/failure events via Socket.IO or notifications.

2. **Given** structured matching fails to find valid matches (all relevance_score < 90 or matching algorithm fails),  
   **When** processing completes,  
   **Then** the system SHALL emit "processing_update_failed" event with error message,  
   **And** SHALL update task status to "failed" in Redis,  
   **And** SHALL save notification for user.

3. **Given** question_file and answer_file contain valid interview content,  
   **When** processing completes successfully,  
   **Then** the system SHALL create session with both file URLs in upload_metadata,  
   **And** SHALL save all matched Q&A pairs,  
   **And** SHALL trigger overall evaluation.

### User Story 3 - Answer File with Template Questions (Priority: P2)

**As a** trainee user,  
**I want to** upload an answer audio file that will be matched to predefined template questions,  
**So that** Parrot can evaluate my answers against template questions created by tutors/admins.

**Why this priority**: Templates allow structured practice sessions with predefined questions from tutors or admins.

**Independent Test**: A user uploads answer_file via POST /answer_file_upload_external with template_id, receives immediate acknowledgment, and gets evaluation results when processing completes.

**Acceptance Scenarios**:

1. **Given** a user uploads answer_file via POST /api/ipersona/answer_file_upload_external with template_id in target parameter,  
   **When** the file is received,  
   **Then** the system SHALL validate file format (mp3, wav, webm, mp4),  
   **And** SHALL upload file to AWS S3,  
   **And** SHALL queue template answer processing task to Celery (task_type: "template_answer_processing"),  
   **And** SHALL return acknowledgment immediately within 1 second,  
   **And** SHALL fetch template questions from database using template_id,  
   **And** SHALL transcribe answer_file using AssemblyAI,  
   **And** SHALL use OpenAI embeddings (text-embedding-3-small) to compute semantic embeddings for template questions and transcribed answers,  
   **And** SHALL compute cosine similarity between question embeddings and answer embeddings,  
   **And** SHALL use structured question-answer matching algorithm with embedding-based similarity scoring,  
   **And** SHALL apply three-band routing: strong accept (>= 30%), borderline (18-30% with LLM verification), low (< 18% rejected),  
   **And** SHALL filter matches with relevance_score >= 90 (from embedding similarity),  
   **And** SHALL create interview session,  
   **And** SHALL save matched Q&A pairs (template questions + matched answers) as messages to database,  
   **And** SHALL trigger overall evaluation automatically,  
   **And** SHALL emit success/failure events via Socket.IO or notifications.

2. **Given** template_id is provided but template has no template_questions,  
   **When** processing starts,  
   **Then** the system SHALL fail immediately,  
   **And** SHALL emit error "No template questions found for template_id",  
   **And** SHALL update task status to "failed" in Redis.

3. **Given** answer file matches some but not all template questions,  
   **When** structured matching completes,  
   **Then** the system SHALL proceed with matched questions only (relevance_score >= 90),  
   **And** SHALL skip unmatched questions,  
   **And** SHALL create session with available matches,  
   **And** SHALL trigger overall evaluation.

### Edge Cases

- **What happens when** uploaded file format is unsupported?  
  **Answer**: System SHALL return error "INVALID_FILE_FORMAT", SHALL specify supported formats, SHALL not process the file.

- **What happens when** Celery task fails during processing?  
  **Answer**: System SHALL update task status to "failed" in Redis, SHALL log error, SHALL emit "processing_update_failed" event or notification, SHALL not create session.

- **What happens when** content validation fails for single audio upload?  
  **Answer**: System SHALL emit "processing_update_failed" event with validation reason, SHALL update Redis status to "failed", SHALL save notification, SHALL not create session.

- **What happens when** dual audio upload results in no valid matches (all relevance_score < 90)?  
  **Answer**: System SHALL emit "processing_update_failed" event with message "No valuable matches found", SHALL update Redis status to "failed", SHALL save notification, SHALL not create session.

- **What happens when** user subscribes to task status updates via Socket.IO "subscribe_to_processing" event?  
  **Answer**: System SHALL emit "processing_confirmed" event when subscription succeeds, SHALL emit "processing_error" event when subscription fails, SHALL deliver task status updates in real-time.

## Requirements

### Functional Requirements

- **FR-001**: System MUST support background processing via Celery for long-running operations
- **FR-002**: System MUST validate audio file formats before processing (mp3, wav, webm, mp4)
- **FR-003**: System MUST validate document file formats (text, pdf, doc, docx)
- **FR-004**: System MUST upload files to AWS S3 before processing
- **FR-005**: System MUST return acknowledgment immediately within 1 second for all upload endpoints
- **FR-006**: System MUST support single audio file upload via POST /audio_upload_external
- **FR-007**: System MUST support dual audio files upload via POST /files_upload_external (question_file + answer_file)
- **FR-008**: System MUST support answer file upload with template via POST /answer_file_upload_external
- **FR-009**: System MUST queue transcription tasks to Celery with appropriate task_type:
  - "audio_processing" for single audio upload
  - "dual_audio_processing" for dual audio upload
  - "template_answer_processing" for template answer upload
- **FR-010**: System MUST process transcription in background using AssemblyAI for audio files
- **FR-011**: System MUST extract text content from document files (text/pdf/doc)
- **FR-012**: System MUST validate interview content using AI-powered content validation for single audio uploads
- **FR-013**: System MUST extract questions and answers from single transcript (single audio upload)
- **FR-014**: System MUST transcribe question_file and answer_file separately (dual audio upload)
- **FR-015**: System MUST use OpenAI embeddings (text-embedding-3-small) to compute semantic embeddings for questions and answers
- **FR-016**: System MUST compute cosine similarity between question embeddings and answer embeddings using sklearn cosine_similarity
- **FR-017**: System MUST use structured question-answer matching algorithm with embedding-based similarity scoring (QuestionAnswerMatcher)
- **FR-018**: System MUST apply three-band routing for matching decisions:
  - Strong accept: relevance_score >= 30% (accepted directly by embedding similarity)
  - Borderline: relevance_score 18-30% (requires LLM verification via OpenAI GPT)
  - Low: relevance_score < 18% (rejected)
- **FR-019**: System MUST filter matches with relevance_score >= 90 (from embedding similarity) for dual audio and template answer uploads
- **FR-020**: System MUST convert embedding similarity score (0-1) to relevance_score (0-100 integer) for matching
- **FR-021**: System MUST fetch template questions from database using template_id (template answer upload)
- **FR-022**: System MUST match transcribed answers to template questions using structured matching with OpenAI embeddings (template answer upload)
- **FR-023**: System MUST require OpenAI API key (OPENAI_PARROT_API_KEY) for embedding-based matching - system MUST fail gracefully if API key is missing
- **FR-024**: System MUST create interview session for all three upload types
- **FR-025**: System MUST save matched Q&A pairs as messages to database
- **FR-026**: System MUST trigger overall evaluation automatically after session creation
- **FR-027**: System MUST emit "processing_update_success" or "processing_update_failed" events via Socket.IO or notifications
- **FR-028**: System MUST update task status in Redis (processing, completed, failed)
- **FR-029**: System MUST support subscribe_to_processing Socket.IO event for task status updates
- **FR-030**: System MUST emit "processing_confirmed" event when subscription succeeds
- **FR-031**: System MUST emit "processing_error" event when subscription fails
- **FR-032**: System MUST support target parameter (JSON) with job_profile_id, challenge_id, template_id, session_id, all_user_id
- **FR-033**: System MUST support sid parameter for Socket.IO event emission
- **FR-034**: System MUST include upload_metadata in session creation with file URLs, content types, and sizes

### Key Entities

- **Session (ipersona-session)**: Created for all three upload types. Links background processing to interview session context. Includes upload_metadata indicating upload mode and file information.

- **Message (ipersona-chat)**: Represents matched Q&A pairs saved to database. Attributes: question, answer, session_id linkage. Relationships: belongs to session.

- **Template (ipersona-tinder-template)**: Required for template answer upload. Contains template_questions array. Relationships: used by template answer processing.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Background file processing completes within 5 minutes for files up to 50MB
- **SC-002**: File upload acknowledgment returns within 1 second for 99% of requests
- **SC-003**: Task status updates are delivered via Socket.IO or notifications in real-time
- **SC-004**: Content validation accurately identifies invalid interview content (90% accuracy)
- **SC-005**: Embedding-based matching correctly matches questions to answers (85% accuracy for relevance_score >= 90)
- **SC-006**: OpenAI embeddings API calls complete within 10 seconds for typical question/answer sets
