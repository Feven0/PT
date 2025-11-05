# Tasks: Create and Start Interview Session

**Input**: Design documents from `specs/001-create-session/`  
**Prerequisites**: plan.md ✓, spec.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure exists

- [x] T001 Project structure already exists in `api/` directory
- [x] T002 Python dependencies already defined in `requirements.txt`
- [x] T003 FastAPI application already initialized in `app.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before feature implementation

**⚠️ CRITICAL**: No feature work can begin until this phase is complete

### Authentication Infrastructure

- [x] T004 Authentication middleware exists in `app.py`
- [x] T005 Strapi GraphQL client exists in `api/services/strapi_graphql.py`
- [ ] T006 Verify user authentication validation for session creation endpoint

### Database Integration

- [x] T007 Strapi GraphQL client wrapper exists
- [ ] T008 Verify GraphQL mutation helpers for session creation

### Error Handling

- [ ] T009 Verify error response format utilities in `api/utils/error_utils.py`
- [ ] T010 Verify standard error codes implementation

**Checkpoint**: Foundation ready - feature implementation can now begin

---

## Phase 3: User Story 1 - Create and Start Interview Session (Priority: P1) 🎯 MVP

**Goal**: Users can create interview sessions for job profiles via REST API

**Independent Test**: A user can create a session, select a job profile, and receive session metadata within 1 second.

### Tests for User Story 1

- [ ] T011 [P] [US1] Unit test for CreateUserSessionRequest model validation in `tests/unit/test_session_models.py`
- [ ] T012 [P] [US1] Unit test for CreateUserSessionResponse model serialization in `tests/unit/test_session_models.py`
- [ ] T013 [P] [US1] Integration test for POST /api/ipersona/create_user_session endpoint in `tests/integration/test_session_creation.py`
- [ ] T014 [P] [US1] Integration test for authentication validation in `tests/integration/test_session_creation.py`
- [ ] T015 [P] [US1] Integration test for invalid job_profile_id error handling in `tests/integration/test_session_creation.py`

### Implementation for User Story 1

- [ ] T016 [P] [US1] Create CreateUserSessionRequest model in `api/pages/ipersona/models/persona.py`
- [ ] T017 [P] [US1] Create CreateUserSessionResponse model in `api/pages/ipersona/models/endpoint_responses.py`
- [x] T018 [P] [US1] IpersonaSessionSchema exists in `api/llm/ipersona/ipersona_strapi_schemas.py`
- [ ] T019 [US1] Implement session creation service function in `api/services/strapi_ipersona.py`
- [ ] T020 [US1] Implement UUID generation for session_id in session creation service
- [ ] T021 [US1] Implement slug generation logic in session creation service
- [ ] T022 [US1] Implement job_profile_id validation in session creation service
- [ ] T023 [US1] Implement template_id validation in session creation service (if provided)
- [ ] T024 [US1] Implement challenge_id validation in session creation service (if provided)
- [ ] T025 [US1] Build Strapi GraphQL mutation for session creation in session creation service
- [ ] T026 [US1] Implement POST /api/ipersona/create_user_session endpoint in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T027 [US1] Add authentication middleware to session creation endpoint
- [ ] T028 [US1] Add request validation using CreateUserSessionRequest model
- [ ] T029 [US1] Add error handling for invalid job_profile_id (404, JOB_PROFILE_NOT_FOUND)
- [ ] T030 [US1] Add error handling for Strapi CMS failures (503, DATABASE_UNAVAILABLE)
- [ ] T031 [US1] Add logging for session creation operations
- [ ] T032 [US1] Verify response time < 1 second for session creation

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - already complete
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS feature implementation**
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion

### Task Dependencies

- **T016-T017**: Models can be created in parallel (different files)
- **T019-T025**: Service implementation tasks (sequential within service)
- **T026-T032**: Endpoint implementation tasks (sequential within endpoint)
- **T011-T015**: Tests can be written in parallel (different test files)

### Parallel Opportunities

**Phase 2**:
- T006, T008, T009, T010 can run in parallel (different components)

**Phase 3**:
- T011-T015 can run in parallel (different test files)
- T016-T017 can run in parallel (different model files)
- T026-T032 can run after T019-T025 completes

---

## Implementation Strategy

### MVP First

1. Complete Phase 1: Setup ✅ (already done)
2. Complete Phase 2: Foundational (verify/complete infrastructure)
3. Complete Phase 3: User Story 1 (session creation)
4. **STOP and VALIDATE**: Test independently
5. Deploy/demo if ready

### Task Execution Order

1. **Foundation** (T006-T010): Verify authentication, database, error handling
2. **Models** (T016-T017): Create Pydantic models (parallel)
3. **Tests** (T011-T015): Write tests first (TDD approach, parallel)
4. **Service** (T019-T025): Implement session creation logic
5. **Endpoint** (T026-T032): Implement REST endpoint with error handling
6. **Validation**: Verify performance targets (< 1 second response)

---

## Notes

- **[P]** tasks = different files, no dependencies
- **[US1]** label maps task to User Story 1
- Feature should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at checkpoint to validate feature independently
- **Total Tasks**: 32 tasks (T001-T032)
- **Estimated MVP**: Phases 1-3 (T001-T032) = 32 tasks

---

**Tasks Version**: 1.0.0 | **Created**: 2024-12-01 | **Status**: Ready for Implementation

