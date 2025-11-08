# Implementation Plan: Overall Interview Evaluation

**Branch**: `012-overall-evaluation` | **Date**: 2024-12-01 | **Spec**: `spec.md`

## Summary

Feature SHALL enable comprehensive overall evaluation of complete interview sessions. System SHALL automatically trigger overall evaluation when sessions complete, analyze entire interview history using OpenAI GPT, generate evaluation metrics (time_management, relevancy, overall_performance_score, rating), and save to ipersona-session-overall-observer table. System SHALL support fetching overall evaluation via POST /fetch_session_overall_evaluation endpoint.

**Primary Technical Approach**: Async function `overall_interview_evaluations` triggered automatically on session completion, OpenAI GPT analysis of complete interview history, calculation of metrics from per-question evaluations, persistence to Strapi CMS, and REST endpoint for retrieval.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Framework**: FastAPI + AsyncIO  
**LLM Service**: OpenAI GPT (gpt-4o-mini or gpt-4o)  
**Database**: Strapi CMS (GraphQL API)  
**Testing**: pytest 7.4+ with pytest-asyncio  
**Target Platform**: Linux server  
**Project Type**: Backend API service  
**Performance Goals**: 
- Overall evaluation generation completes within 10 seconds for 95% of sessions
- Fetch endpoint responds within 1 second for 99% of requests

**Constraints**:
- Must trigger automatically when session completes
- Must retrieve complete interview history for analysis
- Must calculate metrics from existing per-question evaluations
- Must handle async processing for long-running evaluations
- Must support both regular and external audio file processing

## Constitution Check

✅ **AI-Powered Evaluation**: OpenAI GPT as primary LLM ✓  
✅ **Real-Time Performance**: Evaluation completes within 10 seconds ✓  
✅ **Data Persistence**: Strapi CMS for storing overall evaluation ✓  
✅ **Error Handling**: Celery queue for retry on failures ✓  
✅ **Background Processing**: Async processing for heavy operations ✓

## Project Structure

```text
api/
├── modules/
│   └── ipersona_parrot_gpt.py          # overall_interview_evaluations function
├── pages/
│   └── ipersona/
│       └── routers/
│           └── ipersona_routes.py      # POST /fetch_session_overall_evaluation endpoint
└── tests/
    ├── integration/
    │   └── test_overall_evaluation.py
    └── unit/
        └── test_overall_evaluation_logic.py
```

## Component Design

### 1. Overall Evaluation Function (`api/modules/ipersona_parrot_gpt.py`)

**Responsibilities**:
- Trigger automatically when session completes
- Retrieve complete interview history from ipersona-chat table
- Generate OpenAI GPT prompts for overall evaluation and metrics
- Send interview history to OpenAI GPT for analysis
- Calculate time management metrics from history timestamps
- Calculate relevancy scores from per-question evaluations
- Compute overall_performance_score as average of relevance scores
- Determine performance rating based on score ranges
- Save overall evaluation to ipersona-session-overall-observer table
- Update session status to "Completed"

### 2. Evaluation Retrieval Endpoint (`api/pages/ipersona/routers/ipersona_routes.py`)

**Responsibilities**:
- Handle POST /fetch_session_overall_evaluation requests
- Validate sessionId parameter
- Retrieve overall evaluation from ipersona-session-overall-observer table
- Return interview_evaluation and interview_evaluation_metrics
- Handle errors (session not found, evaluation not found)

### 3. External Audio Processing Support (`api/modules/ipersona_parrot_gpt.py`)

**Responsibilities**:
- Support overall_interview_evaluations_external function
- Handle overall evaluation for external audio file processing
- Use same evaluation logic as regular sessions

## Data Flow

```
1. Session completes (all questions answered or session closed)
   ↓
2. Trigger overall_interview_evaluations function
   ↓
3. Retrieve complete interview history from ipersona-chat table
   ↓
4. Generate OpenAI GPT prompts:
   - read_prompt_overall_evaluation (for competency assessment)
   - read_prompt_interview_evaluation_metrics (for metrics)
   ↓
5. Send interview history to OpenAI GPT (two separate calls)
   ↓
6. Receive overall evaluation response and metrics response
   ↓
7. Calculate time management metrics from history timestamps
   ↓
8. Calculate relevancy scores from per-question evaluations
   ↓
9. Compute overall_performance_score as average of relevance scores
   ↓
10. Determine performance rating (poor/good/excellent) from score ranges
   ↓
11. Save to ipersona-session-overall-observer table:
    - interview_evaluation (competency, message)
    - interview_evaluation_metrics (time_management, relevancy, overall_performance_score, rating)
   ↓
12. Update session status to "Completed"
   ↓
13. Calculate overall progress (if status == 'Completed')
```

## Complexity Tracking

No violations identified.

---

**Plan Version**: 1.0.0 | **Created**: 2024-12-01 | **Status**: Ready for Task Breakdown






