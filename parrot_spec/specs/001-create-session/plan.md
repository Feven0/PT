# Implementation Plan: Create and Start Interview Session

**Branch**: `001-create-session` | **Date**: 2024-12-01 | **Spec**: `spec.md`

## Summary

Feature SHALL enable users to create interview sessions for job profiles via REST API endpoint. System SHALL create session records in Strapi CMS with unique identifiers, associate sessions with user/job profiles/templates/challenges, and return session metadata within 1 second.

**Primary Technical Approach**: FastAPI REST endpoint with authentication middleware, Strapi GraphQL mutation for session creation, Pydantic models for request/response validation.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Framework**: FastAPI 0.112+  
**Database**: Strapi CMS (GraphQL API)  
**Storage**: N/A (session data in Strapi)  
**Testing**: pytest 7.4+ with pytest-asyncio  
**Target Platform**: Linux server (AWS EC2/ECS compatible)  
**Project Type**: REST API backend service  
**Performance Goals**: 
- Session creation endpoint responds within 1 second
- Handle 100 concurrent session creation requests
- 99% success rate for valid requests

**Constraints**:
- Endpoint requires Bearer token authentication
- Must validate user, job_profile, template, challenge existence
- Must generate unique session IDs (UUID)
- Must generate URL-friendly slugs

**Scale/Scope**:
- 1 REST API endpoint: POST /api/ipersona/create_user_session
- 5 entities involved: Session, Trainee, Job Profile, Template, Challenge Document
- Session creation rate: 100 requests/minute

## Constitution Check

✅ **Real-Time Performance**: Endpoint responds within 1 second (meets API endpoint target)  
✅ **Data Persistence**: Uses Strapi CMS via GraphQL (constitution requirement)  
✅ **Security-First**: Bearer token authentication required (constitution requirement)  
✅ **Error Handling**: Strapi failure handling with retry logic (constitution requirement)  
✅ **Testability**: pytest with coverage targets (constitution requirement)  
✅ **Specification-Driven**: Feature derived from spec.md (constitution requirement)

**No violations identified.**

## Project Structure

### Source Code (repository root)

```text
api/
├── pages/
│   └── ipersona/
│       ├── routers/
│       │   └── ipersona_routes.py    # POST /api/ipersona/create_user_session endpoint
│       └── models/
│           ├── persona.py           # CreateUserSessionRequest model
│           └── endpoint_responses.py # CreateUserSessionResponse model
├── services/
│   ├── strapi_graphql.py           # Strapi GraphQL client
│   └── strapi_ipersona.py          # Session creation mutation
├── llm/
│   └── ipersona/
│       └── ipersona_strapi_schemas.py  # IpersonaSessionSchema
└── tests/
    ├── integration/
    │   └── test_session_creation.py    # Integration tests
    └── unit/
        └── test_session_models.py      # Unit tests for models
```

**Structure Decision**: Single backend project structure. Feature implemented in existing `api/pages/ipersona/` module. Session creation logic in `api/services/strapi_ipersona.py`. Tests organized by type (integration/unit).

## Component Design

### 1. REST API Endpoint (`api/pages/ipersona/routers/ipersona_routes.py`)

**Responsibilities**:
- Handle POST /api/ipersona/create_user_session requests
- Validate Bearer token authentication
- Parse and validate request body using Pydantic models
- Call session creation service
- Return standardized response

**Input**: `CreateUserSessionRequest` (user_id, job_profile_id, template_id?, challenge_id?)  
**Output**: `CreateUserSessionResponse` (session_id, slug, status, createdAt)

### 2. Request/Response Models (`api/pages/ipersona/models/persona.py`)

**Responsibilities**:
- Define `CreateUserSessionRequest` Pydantic model with validation
- Define `CreateUserSessionResponse` Pydantic model
- Type safety and request validation

### 3. Session Creation Service (`api/services/strapi_ipersona.py`)

**Responsibilities**:
- Generate unique session ID (UUID)
- Generate URL-friendly slug
- Build Strapi GraphQL mutation for session creation
- Execute mutation via Strapi GraphQL client
- Handle errors and retries
- Validate job_profile/template/challenge existence

### 4. Strapi Schema (`api/llm/ipersona/ipersona_strapi_schemas.py`)

**Responsibilities**:
- Define `IpersonaSessionSchema` Pydantic model matching Strapi structure
- Map between API models and Strapi entities

## Data Flow

```
1. Client sends POST /api/ipersona/create_user_session with Bearer token
   ↓
2. FastAPI middleware validates token → Extract user_id
   ↓
3. Parse request body → Validate with CreateUserSessionRequest model
   ↓
4. Session creation service:
   - Generate UUID session_id
   - Generate slug from job title + timestamp
   - Validate job_profile_id exists (if provided)
   - Validate template_id exists (if provided)
   - Validate challenge_id exists (if provided)
   ↓
5. Build Strapi GraphQL mutation:
   mutation {
     createIpersonaSession(data: {
       user_id: $user_id
       job_profile_id: $job_profile_id
       template_id: $template_id
       challenge_id: $challenge_id
       status: "active"
       slug: $slug
       attributes: {...}
     }) { id, slug, status, createdAt }
   }
   ↓
6. Execute mutation via Strapi GraphQL client
   ↓
7. Map Strapi response to CreateUserSessionResponse
   ↓
8. Return response to client (< 1 second target)
```

## Error Handling

### Error Scenarios

**Invalid Authentication**:
- Status: 403 Unauthorized
- Error Code: `UNAUTHORIZED`
- Message: "Authentication required"

**Invalid Job Profile**:
- Status: 404 Not Found
- Error Code: `JOB_PROFILE_NOT_FOUND`
- Message: "Job profile not found"

**Strapi CMS Failure**:
- Status: 503 Service Unavailable
- Error Code: `DATABASE_UNAVAILABLE`
- Retry: Exponential backoff (3 attempts)
- Fallback: Queue operation in Redis for later processing

## Testing Strategy

### Unit Tests
- `CreateUserSessionRequest` model validation
- `CreateUserSessionResponse` model serialization
- Slug generation logic
- UUID generation

### Integration Tests
- Complete session creation flow with authentication
- Strapi GraphQL mutation execution
- Error handling scenarios
- Performance validation (< 1 second response)

## Complexity Tracking

No violations identified. Feature follows constitution principles:
- Single REST endpoint (simplest approach)
- Direct Strapi GraphQL access (no unnecessary abstraction)
- Standard FastAPI patterns (no custom frameworks)

---

**Plan Version**: 1.0.0 | **Created**: 2024-12-01 | **Status**: Ready for Task Breakdown

