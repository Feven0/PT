# Implementation Plan: Parrot (iPersona) Backend

**Branch**: `backend-implementation` | **Date**: 2024-12-01 | **Spec**: `.specify/memory/specification.md`

## Summary

Parrot (iPersona) backend SHALL be a FastAPI-based REST API service with real-time WebSocket capabilities, providing:
- Interview session management
- Real-time audio transcription via Google Cloud STT
- AI-powered answer evaluation via OpenAI GPT
- Background task processing via Celery
- Data persistence via Strapi CMS GraphQL API

**Primary Technical Approach**: Python 3.12+ with FastAPI framework, Socket.IO for real-time communication, Celery for async tasks, and GraphQL client for Strapi integration.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Framework**: FastAPI 0.112+  
**Real-Time Communication**: python-socketio 5.11+  
**Background Processing**: Celery 5.3+ with Redis broker  
**Database**: Strapi CMS (GraphQL API)  
**Storage**: AWS S3 for audio files  
**Secrets Management**: AWS Secrets Manager  
**Testing**: pytest 7.4+ with pytest-asyncio  
**Target Platform**: Linux server (AWS EC2/ECS compatible)  
**Project Type**: REST API backend service  
**Performance Goals**: 
- 1000 requests/min API throughput
- 100 concurrent Socket.IO sessions
- < 2s STT transcription
- < 3s AI evaluation
- < 1s API endpoint response

**Constraints**:
- All protected endpoints require Bearer token authentication
- Google Cloud STT MUST be primary STT service
- OpenAI GPT MUST be primary LLM
- 99.5% uptime requirement
- Horizontal scaling capability required

**Scale/Scope**:
- 100 concurrent interview sessions
- 50 file uploads/min
- 8 database tables in Strapi CMS
- 50+ REST API endpoints
- 9 Socket.IO event types

## Constitution Check

✅ **Real-Time Performance**: Plan includes Socket.IO, performance targets defined, async/await patterns  
✅ **Primary Service Reliability**: Google Cloud STT as primary with fallback services  
✅ **AI-Powered Evaluation**: OpenAI GPT integration planned  
✅ **Real-Time Communication**: Socket.IO architecture designed  
✅ **Background Processing**: Celery + Redis architecture planned  
✅ **Data Persistence**: Strapi CMS GraphQL integration specified  
✅ **Security-First**: Token authentication middleware planned  
✅ **Error Handling**: Fallback services, retry logic, error codes defined  
✅ **Testability**: pytest with coverage targets specified  
✅ **Specification-Driven**: This plan derived from specification

## Project Structure

### Backend Source Code Structure

```text
api/
├── __init__.py
├── config.py                 # Configuration management
├── pages/
│   ├── __init__.py
│   ├── base.py              # Base router
│   └── ipersona/
│       ├── routers/
│       │   ├── ipersona_routes.py    # REST API endpoints
│       │   └── celery_task.py       # Celery task endpoints
│       ├── socket/
│       │   ├── ipersona_socket.py    # Socket.IO event handlers
│       │   ├── google_stt_v2.py     # Google Cloud STT V2 implementation
│       │   └── stt_utils.py          # STT utility functions
│       └── models/
│           ├── persona.py           # Pydantic request/response models
│           └── endpoint_responses.py # Response schemas
├── services/
│   ├── strapi_graphql.py           # Strapi GraphQL client
│   ├── strapi_ipersona.py          # Strapi-specific operations
│   ├── celery/
│   │   ├── celery_worker.py        # Celery app configuration
│   │   ├── celery_config.py        # Celery configuration
│   │   ├── audio_tasks.py          # Audio processing tasks
│   │   └── tasks.py                # General background tasks
│   ├── redis/
│   │   ├── redis_config.py         # Redis configuration
│   │   └── notification_subscriber.py  # Redis pub/sub
│   ├── aws_config.py               # AWS service configuration
│   └── secret.py                   # Secrets management
├── llm/
│   ├── ipersona/
│   │   ├── ipersona_gpt.py         # OpenAI GPT integration
│   │   ├── ipersona_strapi.py      # Strapi integration helpers
│   │   ├── ipersona_strapi_schemas.py  # Strapi schema definitions
│   │   └── ipersona_agent.py       # AI agent orchestration
│   ├── openai_wrapper.py           # OpenAI client wrapper
│   └── llm_models.py               # LLM model configurations
├── modules/
│   ├── ipersona_parrot_gpt.py      # Core interview logic
│   ├── competency.py               # Competency matching
│   └── cv_analysis.py              # CV analysis (if needed)
├── socket/
│   ├── core.py                     # Socket.IO core setup
│   ├── sid_manager.py              # Session ID management
│   └── celery_emit.py              # Celery-to-Socket.IO bridge
├── utils/
│   ├── audio_utils.py              # Audio processing utilities
│   ├── parrot_utils.py             # Interview-specific utilities
│   ├── logger.py                   # Logging configuration
│   └── s3_client.py                # AWS S3 client
└── tests/
    ├── unit/                       # Unit tests
    ├── integration/               # Integration tests
    └── e2e/                        # End-to-end tests
```

**Structure Decision**: Single backend project with modular organization. Separation of concerns:
- `pages/` - API routes and Socket.IO handlers
- `services/` - External service integrations (Strapi, Celery, Redis, AWS)
- `llm/` - AI/ML service integrations
- `modules/` - Business logic and domain models
- `socket/` - Real-time communication infrastructure
- `utils/` - Shared utilities

## Architecture Design

### System Architecture

```
┌─────────────────┐
│   API Clients   │
│  (Frontend/API) │
└────────┬─────────┘
         │
         │ HTTP/REST + WebSocket
         │
┌────────▼──────────────────────────────────┐
│         FastAPI Application                │
│  ┌────────────────────────────────────┐  │
│  │  REST API Endpoints                │  │
│  │  - Session Management               │  │
│  │  - Audio Upload                    │  │
│  │  - Templates                       │  │
│  │  - Admin Analytics                 │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Socket.IO Server                  │  │
│  │  - Real-time audio streaming       │  │
│  │  - Evaluation results              │  │
│  │  - Session synchronization         │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Authentication Middleware         │  │
│  │  - Bearer token validation         │  │
│  │  - Strapi user verification        │  │
│  └────────────────────────────────────┘  │
└────────┬──────────────────────────────────┘
         │
         ├─────────────────┬──────────────────┐
         │                 │                  │
┌────────▼────────┐ ┌──────▼──────┐ ┌─────────▼──────────┐
│  Strapi CMS     │ │   Redis     │ │  Celery Workers   │
│  (GraphQL API)  │ │  (Broker)    │ │  - Audio tasks    │
│                 │ │              │ │  - Batch STT     │
│  - Sessions     │ │  - Pub/Sub   │ │  - Analytics     │
│  - Users        │ │  - Caching   │ │                   │
│  - Templates    │ │  - SID store │ │                   │
└─────────────────┘ └──────────────┘ └───────────────────┘
         │
         │
┌────────▼──────────────────────────────────┐
│         External Services                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Google   │ │ OpenAI   │ │ AWS S3   │  │
│  │ Cloud STT│ │ GPT      │ │ Storage  │  │
│  └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐               │
│  │AssemblyAI│ │Faster    │               │
│  │ (fallback)│ │Whisper  │               │
│  └──────────┘ └──────────┘               │
└───────────────────────────────────────────┘
```

### Core Components

#### 1. FastAPI Application (`app.py`)

**Responsibilities**:
- Initialize FastAPI application with CORS middleware
- Mount REST API routes
- Integrate Socket.IO ASGI app
- Configure authentication middleware
- Startup/shutdown lifecycle management

**Key Implementation**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.pages.ipersona.routers.ipersona_routes import routes
from api.pages.ipersona.socket.ipersona_socket import get_socketio_app

app = FastAPI(title="Parrot Backend")
app.add_middleware(CORSMiddleware, ...)
app.mount("/api", routes)
app = get_socketio_app(app)
```

#### 2. REST API Routes (`api/pages/ipersona/routers/ipersona_routes.py`)

**Responsibilities**:
- Session management endpoints
- STT service endpoints (Google, Whisper, Gemini, OpenAI)
- Template management endpoints
- Admin analytics endpoints
- Background task endpoints

**Key Endpoints**:
- `POST /api/ipersona/create_user_session` - Create session
- `POST /api/ipersona/close_session` - Complete session
- `POST /api/ipersona/stt/google-upload` - Google Cloud STT
- `POST /api/ipersona/audio_upload_external` - Background processing
- `POST /api/ipersona/admin_overview_status` - Admin dashboard

#### 3. Socket.IO Handlers (`api/pages/ipersona/socket/ipersona_socket.py`)

**Responsibilities**:
- Handle real-time audio streaming
- Process Google Cloud STT transcription
- Trigger AI evaluation
- Emit results to clients
- Manage session state

**Key Events**:
- `audio transcribe google` → Google Cloud STT → emit `audio_realtime`
- `audio chat sentence` → STT + GPT evaluation → emit `audio_realtime`
- `initial connect` → Session setup and authentication

#### 4. Google Cloud STT Integration (`api/pages/ipersona/socket/google_stt_v2.py`)

**Responsibilities**:
- Initialize Google Cloud STT V2 client
- Manage streaming transcription sessions
- Handle audio format conversion
- Implement fallback to Faster Whisper on failure
- Error handling and retry logic

**Key Implementation**:
- Use `google.genai` SDK for V2 API
- Stream audio chunks for real-time transcription
- Maintain session state per Socket.IO connection
- Automatic fallback on service failure

#### 5. OpenAI GPT Integration (`api/llm/ipersona/ipersona_gpt.py`)

**Responsibilities**:
- Send transcripts to OpenAI GPT for evaluation
- Structure evaluation prompts
- Parse structured responses (relevance score, feedback)
- Handle rate limiting and retries
- Cache responses when appropriate

**Key Implementation**:
- Use OpenAI Python SDK
- Structured output via Pydantic models
- Streaming support for long evaluations
- Error handling with fallback strategies

#### 6. Strapi CMS Integration (`api/services/strapi_graphql.py`)

**Responsibilities**:
- GraphQL query execution
- Mutation operations (create, update, delete)
- Authentication token management
- Error handling and retries
- Response parsing and normalization

**Key Implementation**:
- GraphQL client with httpx
- Schema-specific query builders
- Connection pooling
- Caching for read operations

#### 7. Celery Background Tasks (`api/services/celery/audio_tasks.py`)

**Responsibilities**:
- Process large audio files asynchronously
- Batch transcription via AssemblyAI
- Generate analytics reports
- Send notifications via Socket.IO

**Key Tasks**:
- `process_upload_external_audio_task` - Background audio processing
- `process_upload_external_files_task` - Batch file processing
- `emit_simple_event_task` - Socket.IO notifications

#### 8. Redis Integration (`api/services/redis/`)

**Responsibilities**:
- Session ID mapping persistence
- Message queue for disconnected clients
- Pub/Sub for notifications
- Caching frequently accessed data

**Key Implementation**:
- Redis client with connection pooling
- Pub/Sub subscriber for background notifications
- SID-to-user mapping with TTL
- Idempotency keys for event deduplication

## Data Flow

### Real-Time Interview Flow

```
1. Client connects → Socket.IO "initial connect"
   ↓
2. Authenticate user via Strapi
   ↓
3. Create session in Strapi CMS
   ↓
4. Client sends audio → "audio chat sentence"
   ↓
5. Route to Google Cloud STT → Get transcript (< 2s)
   ↓
6. Send transcript + question context to OpenAI GPT
   ↓
7. Receive evaluation (< 3s)
   ↓
8. Save evaluation to Strapi (ipersona-session-observer)
   ↓
9. Emit results → "audio_realtime" event
   ↓
10. Client receives feedback
```

### Background Processing Flow

```
1. Client uploads audio → POST /api/ipersona/audio_upload_external
   ↓
2. Validate file format → Upload to S3
   ↓
3. Queue Celery task → Return task_id immediately
   ↓
4. Celery worker processes:
   - Download from S3
   - Transcribe via AssemblyAI
   - Evaluate via OpenAI GPT
   - Save to Strapi
   ↓
5. Emit completion → "task_status" event
   ↓
6. Notify client → "notification" event
```

## Error Handling Strategy

### Service Failure Handling

**Google Cloud STT Failure**:
1. Catch exception/timeout
2. Log error with context
3. Fallback to Faster Whisper
4. Continue processing
5. Alert monitoring if repeated failures

**OpenAI GPT Failure**:
1. Catch exception/timeout
2. Queue evaluation in Celery with retry
3. Notify user of delay
4. Process when service recovers
5. Alert monitoring if rate limited

**Strapi CMS Failure**:
1. Return 503 Service Unavailable
2. Queue operations in Redis
3. Retry with exponential backoff
4. Log errors for investigation
5. Alert monitoring immediately

### Error Response Format

All errors SHALL follow standard format:
```json
{
  "error": "Human-readable message",
  "error_code": "ERROR_CODE",
  "details": "Additional context",
  "timestamp": "ISO 8601",
  "request_id": "UUID"
}
```

## Security Architecture

### Authentication Flow

```
1. Client requests endpoint with Bearer token
   ↓
2. Extract token from Authorization header
   ↓
3. Validate token with Strapi GraphQL API
   ↓
4. Cache user info in request context
   ↓
5. Process request with user context
   ↓
6. Return response
```

### Socket.IO Authentication

```
1. Client connects with auth data in connection event
   ↓
2. Validate credentials with Strapi
   ↓
3. Map user_id to Socket.IO session ID
   ↓
4. Store mapping in Redis
   ↓
5. Allow Socket.IO events for authenticated user
```

### Secrets Management

- API keys stored in AWS Secrets Manager
- Retrieval via `api/services/secret.py`
- No hardcoded credentials
- Environment-specific secrets (dev/prod)

## Performance Optimization

### Caching Strategy

- **Strapi Queries**: Cache read operations for 5 minutes
- **User Info**: Cache in request context for session duration
- **SID Mappings**: Store in Redis with TTL
- **Template Data**: Cache frequently accessed templates

### Database Query Optimization

- Use GraphQL field selection (only fetch needed fields)
- Implement pagination for large result sets
- Use cursor-based pagination for better performance
- Index frequently queried fields in Strapi

### Connection Pooling

- HTTP client connection pooling (httpx)
- Redis connection pooling
- Database connection reuse
- STT client session reuse

## Testing Strategy

### Unit Tests

- Business logic in `modules/`
- Utility functions
- Model validation (Pydantic)
- Service integrations (mocked)

### Integration Tests

- API endpoint testing
- Socket.IO event testing
- Strapi integration testing
- External service mocking

### End-to-End Tests

- Complete interview session flow
- Background processing flow
- Error recovery scenarios
- Performance validation

### Performance Tests

- Load testing (100 concurrent sessions)
- API throughput testing (1000 req/min)
- Latency validation (NFR-001 targets)
- Stress testing (service failure scenarios)

## Deployment Architecture

### Container Structure

```
Backend API Container:
  - FastAPI application
  - Socket.IO server
  - Uvicorn ASGI server

Celery Worker Container:
  - Celery worker process
  - Task handlers
  - Redis connection

Redis Container:
  - Redis server
  - Pub/Sub channels
  - Cache storage
```

### Environment Configuration

- Development: Local Docker Compose
- Staging: AWS ECS with Fargate
- Production: AWS ECS with auto-scaling
- Secrets: AWS Secrets Manager per environment

### Monitoring & Observability

- Application logs → CloudWatch
- Metrics → CloudWatch Metrics
- Alerts → CloudWatch Alarms
- Health checks → `/api/ipersona/health` endpoint

## Complexity Tracking

No violations identified. Architecture follows constitution principles:
- Single backend project (simplest structure)
- Direct Strapi GraphQL access (no unnecessary abstraction)
- Standard FastAPI patterns (no custom frameworks)
- Clear separation of concerns (modular organization)

## Next Steps

1. **Phase 0 Complete**: Architecture designed, constitution validated
2. **Phase 1**: Detailed data model design (see `data-model.md`)
3. **Phase 2**: Task breakdown (see `tasks.md`)
4. **Phase 3**: Implementation
5. **Phase 4**: Testing and validation

---

**Plan Version**: 1.0.0 | **Created**: 2024-12-01 | **Status**: Ready for Task Breakdown

