# Feature Specification: Template-Based Interview Questions

**Feature Branch**: `006-templates`  
**Created**: 2024-12-01  
**Status**: Draft  
**Input**: User description: "Administrators can create reusable interview templates"

## User Scenarios & Testing

### User Story 1 - Template-Based Interview Questions (Priority: P2)

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

3. **Given** an administrator requests a template by ID,  
   **When** they query via POST /get_a_template,  
   **Then** the system SHALL return the template with all questions and associations.

4. **Given** an administrator requests filtered templates,  
   **When** they query via POST /get_tinder_templates with filters (job_profile_id, challenge_id, type),  
   **Then** the system SHALL return matching templates with pagination support.

5. **Given** an administrator updates a template,  
   **When** they send POST /update_tinder_template,  
   **Then** the system SHALL update template name, questions, and associations,  
   **And** SHALL return updated template data.

## Requirements

### Functional Requirements

- **FR-001**: System MUST support reusable interview templates created by administrators
- **FR-002**: System MUST validate template data structure before saving
- **FR-003**: System MUST save templates to tinder-template table in Strapi
- **FR-004**: System MUST allow templates to be associated with job profiles
- **FR-005**: System MUST load template questions when template_id is provided
- **FR-006**: System MUST retrieve template by ID via POST /get_a_template
- **FR-007**: System MUST retrieve filtered templates via POST /get_tinder_templates with filtering options
- **FR-008**: System MUST update existing templates via POST /update_tinder_template
- **FR-009**: System MUST attach job profiles, challenges, and prompts to templates via POST /attach_job_id_to_template
- **FR-010**: System MUST save templates via POST /save_tinder_template

### Key Entities

- **Template (tinder-template)**: Represents reusable question set. Attributes: id, name, questions (JSON array), job_profile associations. Relationships: can be used by many sessions.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Administrators can create templates within 5 seconds
- **SC-002**: Templates are successfully loaded for session creation 99% of the time
- **SC-003**: Template questions are properly associated with sessions
