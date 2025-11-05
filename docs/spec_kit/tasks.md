# Tasks: Parrot (iPersona) Backend

**Input**: Design documents from `.specify/memory/`  
**Prerequisites**: plan.md ✓, spec.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan in `api/` directory
- [ ] T002 Initialize Python 3.12+ project with FastAPI dependencies in `requirements.txt`
- [ ] T003 [P] Configure Black formatter in `pyproject.toml`
- [ ] T004 [P] Configure Ruff linter in `ruff.toml`
- [ ] T005 [P] Configure MyPy type checking in `mypy.ini`
- [ ] T006 [P] Configure Bandit security scanner in `bandit.yml`
- [ ] T007 [P] Setup pytest configuration in `pytest.ini`
- [ ] T008 Create `.env.example` template with required environment variables
- [ ] T009 Create `README.md` with setup instructions and project overview

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration & Environment

- [ ] T010 Create `api/config.py` with configuration management (settings, folders, environment)
- [ ] T011 [P] Implement AWS Secrets Manager integration in `api/services/secret.py`
- [ ] T012 [P] Setup environment variable loading with python-dotenv
- [ ] T013 Create `api/utils/logger.py` with structured logging configuration

### Authentication Infrastructure

- [ ] T014 Implement authentication middleware in `app.py` (Bearer token validation)
- [ ] T015 Create Strapi GraphQL client wrapper in `api/services/strapi_graphql.py`
- [ ] T016 Implement user authentication validation against Strapi in middleware
- [ ] T017 Create user context management for authenticated requests

### Error Handling & Logging

- [ ] T018 Create error response format utilities in `api/utils/error_utils.py`
- [ ] T019 Implement standard error codes (SESSION_NOT_FOUND, INVALID_AUDIO_FORMAT, etc.)
- [ ] T020 Setup exception handling middleware in FastAPI app
- [ ] T021 Configure structured logging with request IDs and context

### Database Integration

- [ ] T022 Create Strapi GraphQL query builders in `api/services/strapi_graphql.py`
- [ ] T023 Implement GraphQL mutation helpers for create/update/delete operations
- [ ] T024 Create connection pooling and retry logic for Strapi API
- [ ] T025 Setup Strapi schema definitions in `api/llm/ipersona/ipersona_strapi_schemas.py`

### Real-Time Infrastructure

- [ ] T026 Setup Socket.IO server initialization in `api/socket/core.py`
- [ ] T027 Create Socket.IO ASGI app wrapper in `api/socket/core.py`
- [ ] T028 Implement Socket.IO authentication handler for connection events
- [ ] T029 Create SID-to-user mapping system in `api/socket/sid_manager.py`
- [ ] T030 Setup Redis connection for SID persistence in `api/services/redis/redis_config.py`

### Background Processing Infrastructure

- [ ] T031 Create Celery application configuration in `api/services/celery/celery_worker.py`
- [ ] T032 Setup Celery broker connection (Redis) in `api/services/celery/celery_config.py`
- [ ] T033 Create Celery task base classes and decorators
- [ ] T034 Implement task result tracking and status updates
- [ ] T035 Setup Redis pub/sub subscriber in `api/services/redis/notification_subscriber.py`

### External Service Clients

- [ ] T036 Create AWS S3 client wrapper in `api/utils/s3_client.py`
- [ ] T037 Setup Google Cloud STT client initialization (placeholders)
- [ ] T038 Setup OpenAI GPT client wrapper in `api/llm/openai_wrapper.py`
- [ ] T039 Create service failure detection and fallback infrastructure

### Base Models & Schemas

- [ ] T040 Create Pydantic request models in `api/pages/ipersona/models/persona.py`
- [ ] T041 Create Pydantic response models in `api/pages/ipersona/models/endpoint_responses.py`
- [ ] T042 Create base error response models
- [ ] T043 Create base session models and schemas

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Start Interview Session (Priority: P1) 🎯 MVP

**Goal**: Users can create interview sessions for job profiles and receive initial questions

**Independent Test**: Create a session via REST API, verify session record in Strapi, receive session ID and metadata within 1 second

### Tests for User Story 1

- [ ] T044 [P] [US1] Contract test for POST /api/ipersona/create_user_session in `tests/integration/test_session_creation.py`
- [ ] T045 [P] [US1] Integration test for session creation with authentication in `tests/integration/test_session_creation.py`
- [ ] T046 [P] [US1] Unit test for session model validation in `tests/unit/test_session_models.py`

### Implementation for User Story 1

- [ ] T047 [P] [US1] Create IpersonaSessionSchema class in `api/llm/ipersona/ipersona_strapi_schemas.py`
- [ ] T048 [P] [US1] Create CreateUserSessionRequest model in `api/pages/ipersona/models/persona.py`
- [ ] T049 [P] [US1] Create CreateUserSessionResponse model in `api/pages/ipersona/models/endpoint_responses.py`
- [ ] T050 [US1] Implement session creation logic in `api/services/strapi_ipersona.py` (create_session method)
- [ ] T051 [US1] Implement POST /api/ipersona/create_user_session endpoint in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T052 [US1] Add session status initialization ("active")
- [ ] T053 [US1] Add session ID generation and slug creation
- [ ] T054 [US1] Add authentication validation for session creation
- [ ] T055 [US1] Add error handling for invalid job_profile_id
- [ ] T056 [US1] Add logging for session creation operations

**Checkpoint**: User Story 1 complete - users can create sessions via REST API

---

## Phase 4: User Story 2 - Real-Time Audio Transcription (Priority: P1) 🎯 MVP

**Goal**: Users can send audio via Socket.IO and receive real-time transcription via Google Cloud STT

**Independent Test**: Connect via Socket.IO, send audio chunk, receive transcript within 2 seconds

### Tests for User Story 2

- [ ] T057 [P] [US2] Integration test for Socket.IO audio transcription in `tests/integration/test_audio_transcription.py`
- [ ] T058 [P] [US2] Unit test for Google Cloud STT client wrapper in `tests/unit/test_google_stt.py`
- [ ] T059 [P] [US2] Unit test for audio format validation in `tests/unit/test_audio_utils.py`

### Implementation for User Story 2

- [ ] T060 [P] [US2] Create Google Cloud STT V2 client in `api/pages/ipersona/socket/google_stt_v2.py`
- [ ] T061 [P] [US2] Create GoogleSTTV2Config class for configuration
- [ ] T062 [P] [US2] Create GoogleStreamingSTTV2 class for streaming transcription
- [ ] T063 [P] [US2] Create audio utility functions in `api/utils/audio_utils.py`
- [ ] T064 [US2] Implement "audio transcribe google" Socket.IO event handler in `api/pages/ipersona/socket/ipersona_socket.py`
- [ ] T065 [US2] Implement audio format conversion (PCM16, WAV, etc.)
- [ ] T066 [US2] Implement Google Cloud STT streaming session management
- [ ] T067 [US2] Implement transcript response emission via "audio_realtime" event
- [ ] T068 [US2] Add confidence score extraction from STT response
- [ ] T069 [US2] Add error handling for malformed audio data
- [ ] T070 [US2] Add error handling for Google Cloud STT failures
- [ ] T071 [US2] Implement Faster Whisper fallback in `api/pages/ipersona/socket/stt_utils.py`
- [ ] T072 [US2] Add logging for transcription operations

**Checkpoint**: User Story 2 complete - real-time audio transcription works via Socket.IO

---

## Phase 5: User Story 3 - Real-Time Interview Evaluation (Priority: P1) 🎯 MVP

**Goal**: Users receive immediate AI evaluation feedback after answering each question

**Independent Test**: Send transcript via Socket.IO, receive evaluation with relevance score, communication skills, and feedback within 3 seconds

### Tests for User Story 3

- [ ] T073 [P] [US3] Integration test for AI evaluation flow in `tests/integration/test_evaluation.py`
- [ ] T074 [P] [US3] Unit test for OpenAI GPT integration in `tests/unit/test_openai_gpt.py`
- [ ] T075 [P] [US3] Unit test for evaluation response parsing in `tests/unit/test_evaluation_parsing.py`

### Implementation for User Story 3

- [ ] T076 [P] [US3] Create OpenAI GPT client wrapper in `api/llm/ipersona/ipersona_gpt.py`
- [ ] T077 [P] [US3] Create evaluation prompt templates in `api/modules/prompts/`
- [ ] T078 [P] [US3] Create evaluation response models (Pydantic) in `api/pages/ipersona/models/persona.py`
- [ ] T079 [US3] Implement "audio chat sentence" Socket.IO event handler in `api/pages/ipersona/socket/ipersona_socket.py`
- [ ] T080 [US3] Implement evaluation request to OpenAI GPT with structured output
- [ ] T081 [US3] Implement relevance_score extraction (0-100 integer)
- [ ] T082 [US3] Implement communication_skills array parsing
- [ ] T083 [US3] Implement feedback text extraction
- [ ] T084 [US3] Implement evaluation persistence to ipersona-session-observer table
- [ ] T085 [US3] Implement evaluation emission via "audio_realtime" event
- [ ] T086 [US3] Add question_id and session_id linkage to evaluations
- [ ] T087 [US3] Add error handling for OpenAI GPT failures
- [ ] T088 [US3] Implement Celery queuing for failed evaluations
- [ ] T089 [US3] Add logging for evaluation operations

**Checkpoint**: User Story 3 complete - real-time AI evaluation works end-to-end

---

## Phase 6: User Story 4 - Session Management and Completion (Priority: P1) 🎯 MVP

**Goal**: Users can complete sessions and receive overall feedback

**Independent Test**: Close session via REST API, receive overall evaluation with average score and performance level

### Tests for User Story 4

- [ ] T090 [P] [US4] Integration test for session closure in `tests/integration/test_session_closure.py`
- [ ] T091 [P] [US4] Unit test for overall evaluation calculation in `tests/unit/test_overall_evaluation.py`

### Implementation for User Story 4

- [ ] T092 [P] [US4] Create IpersonaSessionOverallObserverSchema in `api/llm/ipersona/ipersona_strapi_schemas.py`
- [ ] T093 [P] [US4] Create CloseSessionRequest model in `api/pages/ipersona/models/persona.py`
- [ ] T094 [US4] Implement POST /api/ipersona/close_session endpoint in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T095 [US4] Implement overall evaluation calculation logic in `api/modules/ipersona_parrot_gpt.py`
- [ ] T096 [US4] Implement average relevance score calculation across all questions
- [ ] T097 [US4] Implement performance level determination (poor/good/excellent)
- [ ] T098 [US4] Implement overall evaluation persistence to ipersona-session-overall-observer table
- [ ] T099 [US4] Implement session status update to "completed"
- [ ] T100 [US4] Add validation for already-closed sessions
- [ ] T101 [US4] Implement session timeout detection (2 hours inactivity)
- [ ] T102 [US4] Add logging for session closure operations

**Checkpoint**: User Story 4 complete - session management and completion works

---

## Phase 7: User Story 5 - Question Generation from Job Profile (Priority: P2)

**Goal**: System generates interview questions based on job profile using AI

**Independent Test**: Create session with job_profile_id and generate=true, receive 5-10 relevant questions within 10 seconds

### Tests for User Story 5

- [ ] T103 [P] [US5] Integration test for question generation in `tests/integration/test_question_generation.py`
- [ ] T104 [P] [US5] Unit test for question generation prompt in `tests/unit/test_question_generation.py`

### Implementation for User Story 5

- [ ] T105 [P] [US5] Create question generation prompt templates in `api/modules/prompts/`
- [ ] T106 [US5] Implement question generation logic in `api/modules/ipersona_parrot_gpt.py` (generate_interview_question function)
- [ ] T107 [US5] Implement job profile analysis and extraction
- [ ] T108 [US5] Implement OpenAI GPT question generation request
- [ ] T109 [US5] Implement question parsing and validation (5-10 questions)
- [ ] T110 [US5] Implement question storage in session attributes as "generated_questions"
- [ ] T111 [US5] Add fallback to default questions if job profile insufficient
- [ ] T112 [US5] Add logging for question generation operations

**Checkpoint**: User Story 5 complete - AI question generation works

---

## Phase 8: User Story 6 - Template-Based Interview Questions (Priority: P2)

**Goal**: Administrators can create reusable interview templates

**Independent Test**: Create template via REST API, use template_id in session creation, verify template questions loaded

### Tests for User Story 6

- [ ] T113 [P] [US6] Integration test for template creation in `tests/integration/test_templates.py`
- [ ] T114 [P] [US6] Integration test for template usage in sessions in `tests/integration/test_templates.py`

### Implementation for User Story 6

- [ ] T115 [P] [US6] Create IpersonaTinderTemplateSchema in `api/llm/ipersona/ipersona_strapi_schemas.py`
- [ ] T116 [P] [US6] Create TemplateRequest models in `api/pages/ipersona/models/persona.py`
- [ ] T117 [US6] Implement POST /api/ipersona/create_template_by_llm endpoint in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T118 [US6] Implement POST /api/ipersona/get_all_tinder_templates endpoint
- [ ] T119 [US6] Implement POST /api/ipersona/update_tinder_template endpoint
- [ ] T120 [US6] Implement template loading logic in session creation
- [ ] T121 [US6] Implement template question storage in session attributes as "template_questions"
- [ ] T122 [US6] Add template validation and error handling
- [ ] T123 [US6] Add logging for template operations

**Checkpoint**: User Story 6 complete - template management works

---

## Phase 9: User Story 7 - Background Audio File Processing (Priority: P2)

**Goal**: Users can upload audio files for asynchronous processing

**Independent Test**: Upload audio file, receive task_id immediately, receive notification when processing completes

### Tests for User Story 7

- [ ] T124 [P] [US7] Integration test for audio upload in `tests/integration/test_background_processing.py`
- [ ] T125 [P] [US7] Unit test for Celery task execution in `tests/unit/test_celery_tasks.py`

### Implementation for User Story 7

- [ ] T126 [P] [US7] Create Celery audio processing task in `api/services/celery/audio_tasks.py` (process_upload_external_audio_task)
- [ ] T127 [P] [US7] Implement file upload validation (format, size) in `api/utils/audio_utils.py`
- [ ] T128 [US7] Implement POST /api/ipersona/audio_upload_external endpoint in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T129 [US7] Implement S3 upload logic in `api/utils/s3_client.py`
- [ ] T130 [US7] Implement Celery task queuing with task_id generation
- [ ] T131 [US7] Implement AssemblyAI transcription in Celery task
- [ ] T132 [US7] Implement evaluation processing in Celery task
- [ ] T133 [US7] Implement task status tracking and updates
- [ ] T134 [US7] Implement "task_status" Socket.IO event emission
- [ ] T135 [US7] Implement "notification" event for completion
- [ ] T136 [US7] Add error handling for file upload failures
- [ ] T137 [US7] Add logging for background processing operations

**Checkpoint**: User Story 7 complete - background audio processing works

---

## Phase 10: User Story 8 - Progress Tracking and Analytics (Priority: P2)

**Goal**: Users can view their interview performance history and progress

**Independent Test**: Fetch user sessions, verify session history returned with scores, dates, and job associations

### Tests for User Story 8

- [ ] T138 [P] [US8] Integration test for session history retrieval in `tests/integration/test_progress_tracking.py`
- [ ] T139 [P] [US8] Unit test for progress calculation in `tests/unit/test_progress_calculation.py`

### Implementation for User Story 8

- [ ] T140 [P] [US8] Implement POST /api/ipersona/fetch_user_session endpoint in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T141 [US8] Implement session filtering by user_id in Strapi queries
- [ ] T142 [US8] Implement cursor-based pagination for session queries
- [ ] T143 [US8] Implement date range filtering (since parameter)
- [ ] T144 [US8] Implement session data aggregation and formatting
- [ ] T145 [US8] Implement POST /api/ipersona/calculate_session_overall_progress endpoint
- [ ] T146 [US8] Implement average score calculation across sessions
- [ ] T147 [US8] Implement score trend calculation over time
- [ ] T148 [US8] Implement strength/weakness identification
- [ ] T149 [US8] Add logging for progress tracking operations

**Checkpoint**: User Story 8 complete - progress tracking works

---

## Phase 11: User Story 9 - Admin Dashboard and Analytics (Priority: P3)

**Goal**: Administrators can view system-wide analytics

**Independent Test**: Access admin endpoints, verify aggregate statistics returned

### Tests for User Story 9

- [ ] T150 [P] [US9] Integration test for admin endpoints in `tests/integration/test_admin_analytics.py`
- [ ] T151 [P] [US9] Unit test for admin role validation in `tests/unit/test_admin_auth.py`

### Implementation for User Story 9

- [ ] T152 [P] [US9] Implement admin role validation middleware
- [ ] T153 [US9] Implement POST /api/ipersona/admin_overview_status endpoint in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T154 [US9] Implement aggregate statistics calculation:
  - Total active sessions
  - Total completed sessions
  - Average session scores
  - Most popular job profiles
  - Template usage statistics
- [ ] T155 [US9] Implement POST /api/ipersona/admin_each_job_overview_data endpoint
- [ ] T156 [US9] Implement job-specific performance metrics
- [ ] T157 [US9] Implement POST /api/ipersona/admin_allusers_data endpoint
- [ ] T158 [US9] Implement user performance aggregation
- [ ] T159 [US9] Add caching for admin queries (performance optimization)
- [ ] T160 [US9] Add logging for admin operations

**Checkpoint**: User Story 9 complete - admin analytics work

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation & Configuration

- [ ] T161 [P] Create comprehensive API documentation in `docs/openapi.yaml`
- [ ] T162 [P] Update README.md with deployment instructions
- [ ] T163 [P] Create environment setup guide in `docs/setup.md`
- [ ] T164 [P] Document Socket.IO events in `docs/socket_events.md`

### Error Handling & Resilience

- [ ] T165 Implement comprehensive error handling across all endpoints
- [ ] T166 Add retry logic for external service calls (exponential backoff)
- [ ] T167 Implement circuit breaker patterns for degraded services
- [ ] T168 Add graceful degradation for service failures

### Performance Optimization

- [ ] T169 [P] Implement caching for Strapi read operations
- [ ] T170 [P] Optimize GraphQL queries (field selection)
- [ ] T171 [P] Implement connection pooling for all external services
- [ ] T172 [P] Add database query optimization (indexing strategy)

### Security Hardening

- [ ] T173 Implement input sanitization for all endpoints
- [ ] T174 Add rate limiting for API endpoints
- [ ] T175 Implement request size limits
- [ ] T176 Add security headers (CORS, CSP, etc.)
- [ ] T177 Audit secrets management implementation

### Monitoring & Observability

- [ ] T178 [P] Implement health check endpoint GET /api/ipersona/health
- [ ] T179 [P] Add metrics collection (prometheus/cloudwatch)
- [ ] T180 [P] Setup logging aggregation
- [ ] T181 [P] Implement request tracing with request IDs

### Testing & Quality

- [ ] T182 [P] Add unit tests for utility functions (target: 80% coverage)
- [ ] T183 [P] Add integration tests for all API endpoints
- [ ] T184 [P] Add performance tests validating NFR-001 targets
- [ ] T185 [P] Add end-to-end tests for core user journeys

### Code Quality

- [ ] T186 Run code formatter (Black) across all files
- [ ] T187 Run linter (Ruff) and fix issues
- [ ] T188 Run type checker (MyPy) and fix issues
- [ ] T189 Run security scanner (Bandit) and fix issues
- [ ] T190 Code review and refactoring pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-11)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - Requires US1 for session context
- **User Story 3 (P1)**: Can start after Foundational - Requires US2 for transcription
- **User Story 4 (P1)**: Can start after Foundational - Requires US1 and US3 for session and evaluations
- **User Story 5 (P2)**: Can start after Foundational - Requires US1 for session creation
- **User Story 6 (P2)**: Can start after Foundational - Requires US1 for session creation
- **User Story 7 (P2)**: Can start after Foundational - Independent, uses Celery infrastructure
- **User Story 8 (P2)**: Can start after Foundational - Requires US1 and US4 for sessions and completion
- **User Story 9 (P3)**: Can start after Foundational - Requires US1-US8 for data aggregation

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase**:
- T003-T009 can run in parallel (different configuration files)

**Foundational Phase**:
- T011-T017 can run in parallel (different service modules)
- T026-T029 can run in parallel (Socket.IO components)
- T031-T035 can run in parallel (Celery components)
- T036-T039 can run in parallel (external service clients)

**User Stories**:
- Once Foundational completes, User Stories 1-9 can start in parallel (if team capacity allows)
- Within each story, [P] marked tasks can run in parallel
- Different user stories can be worked on by different team members

---

## Implementation Strategy

### MVP First (Core User Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (**CRITICAL - blocks all stories**)
3. Complete Phase 3: User Story 1 (Session Creation)
4. Complete Phase 4: User Story 2 (Real-Time Transcription)
5. Complete Phase 5: User Story 3 (Real-Time Evaluation)
6. Complete Phase 6: User Story 4 (Session Completion)
7. **STOP and VALIDATE**: Test MVP independently
8. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Session Creation)
   - Developer B: User Story 2 (Transcription) - after US1
   - Developer C: User Story 7 (Background Processing) - independent
   - Developer D: User Story 5 (Question Generation) - after US1
3. Stories complete and integrate independently

---

## Notes

- **[P]** tasks = different files, no dependencies
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **Total Tasks**: 190 tasks across 12 phases
- **Estimated MVP**: Phases 1-6 (T001-T102) = ~102 tasks
- **Estimated Full System**: All phases (T001-T190) = 190 tasks

---

**Tasks Version**: 1.0.0 | **Created**: 2024-12-01 | **Status**: Ready for Implementation

