# Feature Specification: Create and Start Interview Session

**Feature Branch**: `001-create-session`  
**Created**: 2024-12-01  
**Status**: Draft  
**Input**: User description: "Users can create interview sessions from various content sources. The system is designed to handle multiple scenarios including (but not limited to) job profiles, templates (question drafts created by tutors/admins), challenge documents, and any other file/document types that can provide interview context."

## User Scenarios & Testing

### User Story 1 - Create and Start Interview Session (Priority: P1)

**As a** trainee user,  
**I want to** create a new interview session from various content sources (files, documents, job profiles, templates, challenges, etc.),  
**So that** I can practice answering interview questions relevant to any context.

**Why this priority**: This is the core entry point for all interview practice. Without this, no other features can function. The system is designed to be extensible and handle multiple scenarios. Currently implemented contexts include:
- **Job profiles**: Real job postings with AI-generated questions
- **Templates**: Question drafts created by tutors/admins for structured practice
- **Challenge documents**: Pre-defined challenge-based question sets

**Future extensibility**: The architecture supports adding new content types and file formats as needed, making Parrot adaptable to various interview preparation scenarios.

**Independent Test**: A user can create a session by selecting any supported content source (currently job profile, template, or challenge), and receive an initial question within 30 seconds.

**Acceptance Scenarios**:

1. **Given** a user is authenticated and has selected a content source (job profile, template, challenge document, or other supported file/document),  
   **When** they request to create a new interview session,  
   **Then** the system SHALL create a session record in Strapi CMS,  
   **And** SHALL assign a unique session ID,  
   **And** SHALL initialize session status as "active",  
   **And** SHALL associate session with the appropriate context identifier (job_profile_id, template_id, challenge_id, or other type-specific identifier),  
   **And** SHALL return session metadata within 1 second.

2. **Given** a user creates a session with template_id specified (tutor/admin question draft),  
   **When** the system generates questions,  
   **Then** it SHALL use questions from the selected template,  
   **And** SHALL save template_id to session attributes,  
   **And** SHALL associate session with the template entity.

3. **Given** a user creates a session with challenge_id specified,  
   **When** the system generates questions,  
   **Then** it SHALL use questions from the selected challenge document,  
   **And** SHALL save challenge_id to session attributes,  
   **And** SHALL associate session with the challenge entity.

4. **Given** a user creates a session with job_profile_id specified,  
   **When** the system generates questions,  
   **Then** it SHALL use questions based on the job profile (AI-generated or template-based),  
   **And** SHALL save job_profile_id to session attributes,  
   **And** SHALL associate session with the job profile entity.

5. **Given** a user provides a new file/document type for session creation (future extensibility),  
   **When** the system processes the content source,  
   **Then** it SHALL extract interview context from the file/document,  
   **And** SHALL support the new content type through the extensible architecture,  
   **And** SHALL create session with appropriate type-specific identifier.

6. **Given** a user attempts to create a session without authentication,  
   **When** they send the request,  
   **Then** the system SHALL return a 403 Unauthorized error,  
   **And** SHALL not create any session records.

7. **Given** a user creates a session with generate=true and job_profile_id,  
   **When** the system initializes questions,  
   **Then** it SHALL generate questions using AI based on job profile,  
   **And** SHALL save generated questions to session attributes.

8. **Given** a user creates a session with external=true,  
   **When** the system initializes the session,  
   **Then** it SHALL prepare session for external file upload processing,  
   **And** SHALL not require real-time audio streaming.

### Edge Cases

- **What happens when** a user attempts to create a session with an invalid job_profile_id?  
  **Answer**: System SHALL return error code "JOB_PROFILE_NOT_FOUND" and SHALL not create session.

- **What happens when** a user attempts to create a session with an invalid template_id?  
  **Answer**: System SHALL return error code "TEMPLATE_NOT_FOUND" and SHALL not create session.

- **What happens when** a user attempts to create a session with an invalid challenge_id?  
  **Answer**: System SHALL return error code "CHALLENGE_NOT_FOUND" and SHALL not create session.

- **What happens when** a user attempts to create a session without specifying any content source identifier (job_profile_id, template_id, challenge_id, or other)?  
  **Answer**: System SHALL return error code "INVALID_SESSION_CONTEXT" and SHALL require at least one context identifier from any supported content type.

- **What happens when** a user attempts to create a session with an unsupported content type (future extensibility)?  
  **Answer**: System SHALL return error code "UNSUPPORTED_CONTENT_TYPE" with information about supported types, or SHALL handle through extensible architecture if new type is properly configured.

- **What happens when** a user attempts to create a duplicate session for the same content source combination?  
  **Answer**: System SHALL check for existing incomplete sessions with same user-context combination (regardless of content type), SHALL return existing session if found, otherwise SHALL create new session with unique ID.

- **What happens when** Strapi CMS is unavailable during session creation?  
  **Answer**: System SHALL return 503 Service Unavailable, SHALL log error, SHALL retry with exponential backoff.

## Requirements

### Functional Requirements

- **FR-001**: System MUST create interview session records in Strapi CMS with unique session IDs
- **FR-002**: System MUST support extensible architecture for multiple content source types (not limited to job profiles, templates, or challenges)
- **FR-003**: System MUST associate sessions with user profiles AND at least one content source identifier (job_profile_id, template_id, challenge_id, or other type-specific identifier)
- **FR-004**: System MUST support session creation for job profiles (job_profile_id) - currently implemented
- **FR-005**: System MUST support session creation for templates (template_id) - question drafts created by tutors/admins, currently implemented
- **FR-006**: System MUST support session creation for challenge documents (challenge_id) - currently implemented
- **FR-007**: System MUST be designed to accommodate future content types and file formats through extensible architecture
- **FR-008**: System MUST initialize session status as "active" upon creation
- **FR-009**: System MUST validate authentication before allowing session creation
- **FR-010**: System MUST return session metadata within 1 second of creation request
- **FR-011**: System MUST check for existing incomplete sessions before creating new ones (checking user_id + content source identifier combination, regardless of content type)
- **FR-012**: System MUST support template-based session creation (load questions from tutor/admin template) - currently implemented
- **FR-013**: System MUST support challenge-based session creation (load questions from challenge document) - currently implemented
- **FR-014**: System MUST support job profile-based session creation (AI-generated or template-based questions) - currently implemented
- **FR-015**: System MUST generate session slugs for URL-friendly identifiers
- **FR-016**: System MUST update session mode (pending/active/completed) via POST /update_session_mode
- **FR-017**: System MUST delete interview sessions via POST /delete_session
- **FR-018**: System MUST fetch chat history for a session via POST /fetch_chat_history
- **FR-019**: System MUST fetch single session details via POST /fetch_single_session
- **FR-020**: System MUST fetch all observer evaluations for a session via POST /fetch_user_all_observer
- **FR-021**: System MUST provide question clarification via POST /clarify endpoint using LLM
- **FR-022**: System MUST fetch all available challenges via POST /get_all_challenges
- **FR-023**: System MUST fetch a specific challenge by ID via POST /get_a_challenge
- **FR-024**: System MUST support session mode parameter (e.g., "Chat") for different interview interaction types
- **FR-025**: System MUST support external mode flag for external file-based interviews
- **FR-026**: System MUST support generate flag for AI-generated questions based on job profile

### Key Entities

- **Session (ipersona-session)**: Represents a single interview practice session. Attributes: id, status, slug, attributes (JSON), createdAt, user_id, job_profile_id (optional), template_id (optional), challenge_id (optional), and extensible fields for future content types. Relationships: messages, observer evaluations, overall observer. Designed to support multiple content source types through flexible attribute structure.

- **Trainee (ipersona-trainee)**: Represents user profile. Attributes: id, user_id, profile data. Relationships: has many sessions across various content types.

- **Job Profile (tinder-job-profile)**: Represents job posting/description. Attributes: id, title, description, skills, competencies. Relationships: has many sessions. One of the currently implemented content source types.

- **Template (tinder-template)**: Represents reusable question set created by tutors/admins. Attributes: id, name, questions (JSON array), job_profile associations, challenge associations. Relationships: can be used by many sessions. Created by tutors/admins for structured interview practice. One of the currently implemented content source types.

- **Challenge Document (challenge-document)**: Represents challenge-based question set. Attributes: id, name, questions (JSON array). Relationships: can be used by many sessions. One of the currently implemented content source types.

**Note on Extensibility**: The system architecture is designed to support additional content types beyond the three currently implemented (job profiles, templates, challenges). Future content types can be integrated through the extensible session attribute structure and content processing pipeline.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create and start an interview session within 1 second of request
- **SC-002**: Session creation succeeds for 99% of valid requests
- **SC-003**: System handles 100 concurrent session creation requests without degradation
- **SC-004**: 95% of users successfully create their first session on first attempt

