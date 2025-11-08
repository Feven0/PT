# Tasks: Overall Interview Evaluation

**Input**: Design documents from `specs/012-overall-evaluation/`  
**Prerequisites**: plan.md ✓, spec.md ✓

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup
- [x] T001 Project structure exists

## Phase 2: Foundational
- [x] T002 OpenAI GPT client infrastructure exists
- [x] T003 Strapi CMS schema exists for ipersona-session-overall-observer
- [x] T004 AsyncIO infrastructure exists

## Phase 3: User Story 1 - Overall Interview Evaluation (Priority: P1) 🎯 MVP

**Goal**: System automatically generates comprehensive overall evaluation when sessions complete, including metrics and competency assessment

**Independent Test**: A user completes a session with multiple answered questions, system automatically generates and saves overall evaluation with metrics, performance score, and competency assessment within 10 seconds.

### Implementation

- [ ] T005 [P] [US1] Implement overall_interview_evaluations async function in `api/modules/ipersona_parrot_gpt.py`
- [ ] T006 [US1] Implement interview history retrieval from ipersona-chat table
- [ ] T007 [US1] Implement read_prompt_overall_evaluation prompt generation
- [ ] T008 [US1] Implement read_prompt_interview_evaluation_metrics prompt generation
- [ ] T009 [US1] Implement OpenAI GPT calls for overall evaluation and metrics
- [ ] T010 [US1] Implement time management calculation from interview history timestamps
- [ ] T011 [US1] Implement relevancy score calculation from per-question evaluations
- [ ] T012 [US1] Implement overall_performance_score calculation as average of relevance scores
- [ ] T013 [US1] Implement performance rating determination (poor/good/excellent) based on score ranges
- [ ] T014 [US1] Implement saving overall evaluation to ipersona-session-overall-observer table
- [ ] T015 [US1] Implement session status update to "Completed" after evaluation saved
- [ ] T016 [US1] Implement overall_interview_evaluations_external for external audio processing
- [ ] T017 [US1] Add error handling and retry logic for OpenAI GPT failures
- [ ] T018 [US1] Add logging for overall evaluation operations
- [ ] T019 [US1] Implement automatic triggering of overall evaluation on session completion

**Checkpoint**: Overall evaluation generation works automatically when sessions complete

---

## Phase 4: User Story 2 - Fetch Overall Evaluation (Priority: P1)

**Goal**: Users can retrieve overall evaluation data for completed sessions via REST API

**Independent Test**: A user queries POST /fetch_session_overall_evaluation with sessionId, receives overall evaluation data including metrics and competency assessment within 1 second.

### Implementation

- [ ] T020 [P] [US2] Implement POST /fetch_session_overall_evaluation endpoint in `api/pages/ipersona/routers/ipersona_routes.py`
- [ ] T021 [US2] Implement sessionId validation
- [ ] T022 [US2] Implement retrieval of overall evaluation from ipersona-session-overall-observer table
- [ ] T023 [US2] Implement response formatting with interview_evaluation and interview_evaluation_metrics
- [ ] T024 [US2] Add error handling for session not found (404)
- [ ] T025 [US2] Add error handling for evaluation not found (404)
- [ ] T026 [US2] Add logging for fetch operations

**Checkpoint**: Fetch endpoint works and returns overall evaluation data

---

## Phase 5: Integration & Error Handling

**Purpose**: Ensure robust error handling and integration with other features

- [ ] T027 [P] Add Celery task queue support for failed overall evaluations
- [ ] T028 [P] Add json_repair support for malformed OpenAI GPT responses
- [ ] T029 [P] Add validation for insufficient data (no completed questions)
- [ ] T030 [P] Add timeout handling for long-running evaluations (>10 seconds)
- [ ] T031 [P] Add progress tracking integration with calculate_overall_progress function

**Checkpoint**: Overall evaluation handles errors gracefully and integrates with other features

---

**Tasks Version**: 1.0.0 | **Created**: 2024-12-01






