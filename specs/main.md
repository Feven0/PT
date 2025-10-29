# Parrot (iPersona) - AI Interview Platform Specification

> **📝 Document Type**: Reverse-Engineered Specification
> 
> **Status**: Documents existing production application (6+ months development)
> 
> **Purpose**: This specification reverse-engineers an existing, fully-functional application that was built starting 6 months ago. It serves as:
> - **Living documentation** of the current system
> - **Source of truth** for understanding architecture
> - **Blueprint** for AI-assisted modifications and enhancements
> - **Onboarding guide** for new developers
>
> **Last Updated**: December 2024

## Overview

**Parrot** is an AI-driven job interview platform that helps job seekers assess job fit, engage in mock interviews, and receive personalized feedback. The system uses AI to generate interview questions, evaluate candidate responses in real-time, and provide comprehensive performance analysis.

**Current Status**: Production-ready application with 50+ API endpoints, real-time Socket.IO communication, Celery background processing, and comprehensive admin analytics.

### Purpose

Parrot enables:
- **Job seekers**: Practice interviews, get AI-powered feedback, and improve interview skills
- **HR professionals**: Assess candidates for job openings
- **Trainees**: Track progress and performance over time

### Technology Stack

**Backend:**
- **Framework**: FastAPI (Python 3.12)
- **Database**: Strapi CMS (GraphQL API)
- **Task Queue**: Celery with Redis broker
- **Real-time**: Socket.IO (python-socketio)
- **Web Server**: Uvicorn (dev), Gunicorn (prod)

**AI & ML Services:**
- **LLM Providers**: OpenAI GPT models (primary)
- **LLM Gateway**: LiteLLM (multi-provider support)
- **Structured Outputs**: Instructor library
- **Speech-to-Text**: 
  - AssemblyAI
  - Faster Whisper (local)
  - OpenAI Whisper API
  - Google Cloud Speech-to-Text
  - Google Gemini
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **AI Agents**: AutoGen framework (for complex workflows)

**Frontend:**
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Ant Design (Charts, Forms, Tables)
- **State Management**: React Context API
- **Real-time**: Socket.IO Client
- **Charts**: Recharts, AntD Charts (Radar, Line, Bar, Sankey, Liquid)

**Infrastructure:**
- **Package Manager**: uv (Python), npm/pnpm (Node.js)
- **Code Quality**: Black, isort, Ruff, MyPy
- **Security**: Bandit, Safety
- **Testing**: Pytest, coverage
- **Containerization**: Docker, Docker Compose
- **Cloud Services**: AWS S3, AWS Secrets Manager
- **Storage**: S3 for audio/documents

**External Services:**
- **Content Extraction**: Custom API (https://content-extractor.10academy.org)
- **Autograde Service**: Custom API (https://autograde.10academy.org)

## Database Architecture

### Core Tables (Strapi CMS)

#### ipersona-session
Stores interview session information
- `id`: Primary key
- `user_id`: Foreign key to user
- `job_profile_id`: Foreign key to job profile
- `status`: Session status (active, completed, closed)
- `created_at`, `updated_at`: Timestamps
- `mode`: Interview mode (mock, real, practice)

#### ipersona-trainee
User profile/trainee information
- `id`: Primary key
- `all_user_id`: Foreign key to main user table
- `cv`, `resume`, `profile_data`: User documents
- `competencies`: Skills and competencies
- Tracks trainee progress and history

#### ipersona-job
Job profiles and requirements
- `id`: Primary key
- `job_title`, `job_description`: Job details
- `required_competencies`: Required skills
- `job_profile_id`: Unique identifier
- Linked to interview templates

#### ipersona-session-message
Interview conversation messages
- `id`: Primary key
- `session_id`: Foreign key to session
- `sender`: AI or candidate
- `content`: Message text
- `audio_path`: Optional audio recording
- `created_at`: Timestamp
- Tracks entire interview conversation

#### ipersona-session-observer
Real-time evaluation of responses
- `id`: Primary key
- `session_id`: Foreign key to session
- `realtime_evaluation`: JSON evaluation data
- `interview_evaluation`: Final overall evaluation
- `interview_evaluation_metrics`: Performance metrics
- `status`: Observer status

#### ipersona-session-overall-observer
Final interview evaluation
- `id`: Primary key
- `session_id`: Foreign key to session
- `overall_evaluation`: Complete evaluation JSON
- `interview_metrics`: Comprehensive metrics
- Calculated after interview completion

#### ipersona-tinder-template
Interview question templates
- `id`: Primary key
- `job_profile_id`: Linked job profile
- `questions`: Template questions (JSON)
- `question_type`: Question type
- Used to generate interview questions

#### ipersona-challenge-document
Challenge documents and answer templates
- `id`: Primary key
- `challenge_id`: Challenge identifier
- `question_file`, `answer_file`: Uploaded files
- `template_data`: Template structure
- For external audio/file processing

## Core Features

### 1. Interview Session Management

#### Create Interview Session
```python
POST /api/ipersona/create-user-session
```
- Accepts user authentication token
- Validates job profile exists
- Creates session record in Strapi
- Returns session ID for real-time connection

**Logic:**
1. Extract user information from token (via Strapi GraphQL)
2. Verify job_profile_id exists and is valid
3. Create ipersona-session record with status="start"
4. Return session details including sessionId

#### Update Session Mode
```python
POST /api/ipersona/update-session-mode
```
- Updates interview mode (practice, interview, evaluation)
- Updates session record status

#### Get Session Details
```python
GET /api/ipersona/get-session/{session_id}
```
- Retrieves full session information
- Includes messages, evaluations, and status

### 2. AI-Powered Question Generation

#### Generate Interview Questions
```python
POST /api/ipersona/generate-interview-question
```

**Process:**
1. Parse job profile and competencies
2. Load persona templates based on job type
3. Call OpenAI GPT with structured prompt
4. Extract questions from LLM response
5. Format questions as JSON array
6. Save to session messages

**Prompt Structure:**
- Use job description to identify persona (technical, behavioral, soft skills)
- Generate 5-10 questions covering required competencies
- Include SFIA framework levels where appropriate
- Tailor questions to job level (entry, mid, senior)

### 3. Real-Time Interview with Socket.IO

#### Connection Flow
```javascript
// Client connects via Socket.IO
socket.io.connect(SERVER_URL, { auth: { token } })

// Server authenticates via Strapi
@sio.on("connect")
async def connect(sid, environ):
    # Validate token
    # Create socket session
    # Join user to room
```

#### Audio Chat Processing
```javascript
// Client sends audio chunk
socket.emit("audio chat sentence", {
    user_session: { id: sessionId },
    response: audioBlob,
    question_text: "question text"
})
```

**Server Processing:**
1. Receive audio blob
2. Transcribe audio using Faster Whisper or AssemblyAI
3. Save transcript to session messages
4. Perform real-time evaluation
5. Emit evaluation results back to client

```python
@sio.on("audio chat sentence")
async def audio_end_point(sid, data):
    # Extract session_id from data
    # Get accumulated audio
    # Transcribe audio
    # Save message to database
    # Perform real-time evaluation
    # Emit results via Socket.IO
```

#### Real-Time Evaluation

**Algorithm: Evaluate Single Response in Real-Time**

```python
# Function signature
def realtime_response_evaluation(run_stage, data, sessionId, interview_type, is_last_response):
```

**Step-by-step process:**

1. **Determine if final response**
   - If `is_last_response == True`, log "FINAL RESPONSE EVALUATION" and mark interview as ending
   - If `is_last_response == False`, treat as normal mid-interview evaluation

2. **Fetch the previous question from database**
   - Query `ipersona-session-message` table filtered by `session_id = sessionId` 
   - Filter by `sender = 'ai'` to get the assistant's last message
   - Extract question text from `last_assistant_response`

3. **Build evaluation prompt**
   - Read base prompt template from `prompts/ipersona/realtime_evaluation.txt`
   - If `is_last_response == True`, use `prompts/ipersona/closing_question_realtime_evaluation.txt` instead
   - Replace placeholders in prompt with:
     - Previous question text
     - Candidate's response from `data['user_session']`
     - Job requirements from `data['job_profile']`
     - Interview type from `interview_type` parameter
   
4. **Load persona context**
   - Extract `persona` from `data['user_session']['attributes']['attributes']`
   - Prepend persona to the prompt content for role-specific evaluation

5. **Call OpenAI GPT for evaluation**
   - Use `gpt.openai_gpt_assistant_without_streaming(content)`
   - Pass the complete prompt with persona context
   - Wait for LLM response (no streaming)

6. **Parse JSON response**
   - Call `extract_json(llm_response, quite=False)`
   - Validate JSON structure
   - Extract `realtime_evaluation` field from response

7. **Handle errors**
   - If exception occurs, log error with `logger.error()`
   - Return `{'error': str(e)}`
   - Do not crash - allow interview to continue

8. **Return evaluation data**
   - Return dictionary with structure:
     ```json
     {
       "realtime_evaluation": "Overall assessment text...",
       "score": 85,
       "feedback": "Strengths and weaknesses",
       "competencies": {...}
     }
     ```

**Evaluation Criteria (Embedded in Prompt):**
- Relevance to question: Does the answer directly address what was asked?
- Technical accuracy: Are technical details correct?
- Communication clarity: Is the answer clear and well-structured?
- Competency demonstration: Which competencies from job description are shown?
- SFIA level assessment: What SFIA level does this response demonstrate?

**Database Operations:**
- Read: Query `ipersona-session-message` to fetch last question
- Read: Retrieve job profile and competencies from `data` parameter
- No write operations in this function (done separately by caller)

**Integration Points:**
- Input: Receives `data` dictionary with user_session, job_profile, candidate response
- Output: Returns evaluation JSON that will be emitted via Socket.IO
- Triggered: After each candidate audio response is transcribed

#### Session State Management
- Track chat_count (current question number)
- Track total_questions for interview
- Detect when interview is complete
- Trigger overall evaluation when all questions answered

### 4. External Audio/File Processing

#### Process Uploaded Audio File
```python
POST /api/ipersona/audio_upload_external_celery
```

**Celery Task Flow:**
1. Accept audio file upload
2. Save to temporary storage
3. Queue Celery task (background processing)
4. Return task_id immediately
5. Client polls for status

**Background Processing:**
```python
@celery_app.task(name="process_upload_external_audio")
def process_upload_external_audio_task(audio_path, job_profile_id, ...):
    # 1. Transcribe audio using AssemblyAI
    transcript = transcriber.transcribe(audio_path)
    
    # 2. Analyze transcription with LLM
    prompt = build_external_audio_analysis_prompt(transcript, job_profile)
    analysis = gpt.openai_gpt_assistant_without_streaming(prompt)
    
    # 3. Extract JSON response
    evaluation_data = extract_json(analysis)
    
    # 4. Save to database
    save_evaluation(evaluation_data)
    
    # 5. Emit completion event via Socket.IO
    emit_task_completion(session_id, evaluation_data)
```

#### Process Dual Audio Files (Question + Answer)
```python
POST /api/ipersona/files_upload_external_celery
```
- Accept two files: Question file and Answer file
- Transcribe both files
- Match questions with answers using semantic similarity
- Generate comprehensive evaluation
- Save results to database

**Question-Answer Matching:**
Uses structured matching system (see `../STRUCTURED_MATCHING_SYSTEM.md`):
1. Parse questions from template
2. Segment answer transcript intelligently
3. Generate embeddings for questions and answers
4. Compute similarity matrix
5. Match questions to answers with threshold filtering
6. Return matched pairs

### 5. Overall Interview Evaluation

#### Trigger Overall Evaluation
```python
async def overall_interview_evaluations(run_stage, sessionId, ...):
    """Generate final evaluation after interview completes"""
```

**Process:**
1. Retrieve all session messages
2. Build complete interview history
3. Load job profile and competencies
4. Call OpenAI GPT with overall_evaluation prompt
5. Extract evaluation JSON
6. Calculate performance metrics
7. Save to ipersona-session-overall-observer

**Evaluation Output:**
```json
{
  "overall_evaluation": {
    "strengths": [...],
    "weaknesses": [...],
    "recommendations": [...],
    "fit_score": 85,
    "competencies_evaluated": {
      "skill_name": "SFIA_level"
    }
  },
  "interview_metrics": {
    "average_response_time": "...",
    "communication_score": 90,
    "technical_score": 85,
    "overall_score": 88
  }
}
```

### 6. Speech-to-Text (STT) Services

#### Multiple STT Providers

**1. Faster Whisper (Local)**
```python
POST /api/stt/whisper-upload
```
- Uses Faster Whisper model (local CPU/GPU)
- Supports language specification
- Returns transcript and language detection

**2. Google Gemini Speech-to-Text**
```python
POST /api/stt/gemini-upload
```
- Uses Google Gemini API for transcription
- Returns transcript with timestamps

**3. AssemblyAI**
- Primary transcription service
- Used for real-time and batch processing
- Returns transcript with speaker diarization

**Selection Logic:**
- Use Faster Whisper for local, fast transcription
- Use AssemblyAI for production, high-accuracy needs
- Use Google Gemini as fallback

### 7. Authentication & Authorization

#### Authentication Flow
```python
# All requests require Bearer token
Authorization: Bearer {token}

# Middleware validates token
@app.middleware("http")
async def check_authentication(request, call_next):
    # Extract token from Authorization header
    # Validate token via Strapi GraphQL
    # Attach user_info to request
    # Allow/deny request
```

**Token Validation:**
1. Extract "Bearer {token}" from headers
2. Call Strapi GraphQL `get_user_info` query
3. Verify user exists and is authorized
4. Store user_info in config.fastapi.user_info
5. Continue with request or return 403

**Exception:**
- Socket.IO connections require token in auth parameter
- Socket.IO connect event validates separately

#### CORS Configuration
- Allow specific origins from config
- Support wildcard for development
- Include credentials in cookies

### 8. Background Task Processing (Celery)

#### Celery Setup
```python
# Broker: Redis
BROKER_URL = "redis://redis.10academy.org:6379/0"
RESULT_BACKEND = "redis://redis.10academy.org:6379/0"

# Queues
CELERY_TASK_ROUTES = {
    'audio_processing': 'audio_queue',
    'file_processing': 'file_queue'
}
```

#### Task Types
1. **Audio Processing**: `process_upload_external_audio_task`
2. **File Processing**: `process_upload_external_files_task`
3. **Answer Processing**: `process_upload_external_answer_file_task`
4. **Emit Events**: `emit_simple_event_task`

#### Monitoring
- Flower dashboard: http://localhost:5555
- Monitor task status and worker health
- View task history and logs
- Retry failed tasks

### 9. Socket.IO Real-Time Communication

#### Socket.IO Events (Actual Implementation)

**Client → Server Events:**
- `initial connect` - Initialize connection and session setup
- `disconnect` - Client disconnection event
- `subscribe_to_processing` - Subscribe to Celery background task updates
- `assemblyai_status` - Check AssemblyAI transcription status
- `audio transcribe whisper` - Transcribe audio using Faster Whisper
- `audio transcribe` - Generic audio transcription event
- `audio transcribe google` - Transcribe using Google Cloud STT
- `audio chat sentence` - Real-time interview audio response (main event)
- `interview chat` - Text-based interview chat

**Server → Client Events:**
- `audio_realtime` - Real-time evaluation results
- `realtime_status` - Evaluation status (start/end)
- `task_status` - Background task status updates
- `processing_update` - File processing status updates
- `processing_update_success` - Processing completed successfully
- `processing_update_failed` - Processing failed with error
- `error` - Error notifications
- `notification` - General notifications to client

#### Session Management
```python
@sio.on("connect")
async def connect(sid, environ):
    # Validate auth token
    session = await sio.get_session(sid)
    session['user_id'] = user_id
    session['run_stage'] = run_stage
    
    # Join user-specific room
    await sio.enter_room(sid, user_id)
    
    # Deliver queued messages
    await deliver_queued_messages_for_user(user_id, sid)
```

#### Message Queuing
- If client disconnects during processing
- Queue messages for delivery when client reconnects
- Prevent message loss during network interruptions

### 10. Structured Question-Answer Matching

See `../STRUCTURED_MATCHING_SYSTEM.md` for detailed specification.

**Key Components:**
- `QuestionAnswerMatcher`: Main matching engine
- Uses sentence transformers for embeddings
- Cosine similarity for matching
- Configurable thresholds
- Fallback to LLM-based matching

**Use Case:**
When processing dual audio files (questions + answers), intelligently match questions to answer segments.

## API Endpoints Summary

**Total Endpoints**: 50+ active endpoints across multiple categories

### Speech-to-Text (STT) Endpoints
- `POST /api/ipersona/stt/whisper-upload` - Faster Whisper transcription (local)
- `POST /api/ipersona/stt/gemini-upload` - Google Gemini STT
- `POST /api/ipersona/stt/openai-upload` - OpenAI Whisper API
- `POST /api/ipersona/stt/google-upload` - Google Cloud STT
- `POST /api/ipersona/audio_upload` - Main audio transcription endpoint

### Session Management Endpoints
- `POST /api/ipersona/clarify` - Request question clarification
- `POST /api/ipersona/delete_session` - Delete interview session
- `POST /api/ipersona/close_session` - Close/complete session
- `POST /api/ipersona/calculate_session_overall_progress` - Calculate progress metrics
- `POST /api/ipersona/calculate_allstat_progress` - All-time statistics
- `POST /api/ipersona/fetch_user_session` - Get user's sessions
- `POST /api/ipersona/fetch_chat_history` - Get conversation history
- `POST /api/ipersona/fetch_user_all_observer` - Get all evaluations
- `POST /api/ipersona/fetch_session_overall_evaluation` - Get final evaluation
- `POST /api/ipersona/fetch_single_session` - Get specific session details

### Engagement & Analytics Endpoints
- `POST /api/ipersona/engagement_jobs_status` - Job interview engagement metrics
- `POST /api/ipersona/engagement_challenge_status` - Challenge engagement metrics
- `POST /api/ipersona/engagement_template_status` - Template usage metrics
- `POST /api/ipersona/engagement_status` - Overall engagement dashboard

### Admin & Oversight Endpoints
- `POST /api/ipersona/admin_overview_status` - Admin dashboard overview
- `POST /api/ipersona/admin_allusers_data` - All users data table
- `POST /api/ipersona/admin_alljobs_data` - All jobs data table
- `POST /api/ipersona/admin_allchallenges_data` - All challenges data
- `POST /api/ipersona/admin_each_job_overview_data` - Per-job analytics
- `POST /api/ipersona/admin_each_challenge_overview_data` - Per-challenge analytics
- `POST /api/ipersona/admin_allusers_performance_data` - User performance metrics
- `POST /api/ipersona/admin_job_by_template_id` - Job by template lookup
- `POST /api/ipersona/admin_challenge_by_template_id` - Challenge by template
- `POST /api/ipersona/admin_interview_by_template` - Interview sessions by template

### Template Management Endpoints
- `POST /api/ipersona/get_all_tinder_templates` - List all templates
- `POST /api/ipersona/save_tinder_template` - Create new template
- `POST /api/ipersona/get_tinder_templates` - Get filtered templates
- `POST /api/ipersona/get_a_template` - Get single template
- `POST /api/ipersona/update_tinder_template` - Update template
- `POST /api/ipersona/attach_job_id_to_template` - Link template to job
- `POST /api/ipersona/create_template_by_llm` - AI-generate template from job description

### Challenge Endpoints
- `POST /api/ipersona/get_all_challenges` - List all challenges
- `POST /api/ipersona/get_a_challenge` - Get specific challenge

### Audio Processing with Celery (Background Tasks)
- `POST /api/ipersona/audio_upload_external` - Upload single audio file (Celery)
- `POST /api/ipersona/files_upload_external` - Upload question + answer files (Celery)
- `POST /api/ipersona/answer_file_upload_external` - Upload answer file with template (Celery)
- `POST /api/ipersona/test_celery_event` - Test Celery + Socket.IO integration

### Health & Testing
- `GET /api/ipersona/health` - Health check endpoint

## Frontend Application

### Overview

The frontend is a **React 18 + TypeScript** single-page application (SPA) built with **Vite**. It provides:
- Real-time interview interface with Socket.IO
- Admin analytics dashboard
- Audio recording and playback
- Template management
- User progress tracking

### Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Admin/          # Admin dashboard components
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── AllDataFilterAdmin.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   └── StatusDashboardAdmin.tsx
│   │   ├── Charts/         # Data visualization
│   │   │   ├── BarChart.tsx
│   │   │   ├── LineChart.tsx
│   │   │   ├── RadarChart.tsx
│   │   │   ├── SankeyChart.tsx
│   │   │   └── LiquidAntd.tsx
│   │   ├── AudioChatRecord.tsx
│   │   ├── InterviewChat.tsx
│   │   ├── GoogleSTT.tsx
│   │   ├── TemplateForm.tsx
│   │   └── ...
│   ├── context/            # React Context providers
│   │   ├── context.tsx
│   │   └── ProcessingContext.tsx
│   ├── hooks/              # Custom React hooks
│   │   ├── useWebSocket.tsx
│   │   ├── useMiddleSocket.tsx
│   │   └── useProcessingWebSocket.tsx
│   ├── pages/              # Route pages
│   │   ├── Jobs.tsx
│   │   ├── JobDetail.tsx
│   │   ├── Trainee.tsx
│   │   └── AssemblyAITest.tsx
│   ├── routes/
│   │   └── AppRoutes.tsx
│   └── Services/
│       └── Services.tsx
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### Key Components

**Admin Dashboard:**
- `AdminDashboard.tsx` - Main admin interface
- `AllDataFilterAdmin.tsx` - Data filtering and export
- `StatusDashboardAdmin.tsx` - Real-time status monitoring
- Multi-tab interface for users, jobs, challenges, templates

**Charts & Visualizations:**
- `LineChart.tsx` - Progress over time
- `RadarChart.tsx` - Skill assessment visualization
- `BarChart.tsx` - Comparative metrics
- `SankeyChart.tsx` - Flow diagrams
- `LiquidAntd.tsx` - Progress percentage
- `PerformanceChart.tsx` - Overall performance

**Interview Components:**
- `InterviewChat.tsx` - Real-time interview interface
- `AudioChatRecord.tsx` - Audio recording with real-time transcription
- `GoogleSTT.tsx` - Google STT integration
- `Messages.tsx` - Chat message display
- `RealTimeEvaluation.tsx` - Live evaluation feedback

**Template Management:**
- `TemplateForm.tsx` - Create/edit templates
- `UpdateTemplate.tsx` - Modify existing templates

### Socket.IO Integration

**Custom Hooks:**
```typescript
// useWebSocket.tsx - Main interview Socket.IO connection
const { socket, messages, sendMessage } = useWebSocket(sessionId);

// useProcessingWebSocket.tsx - Background task status
const { status, progress } = useProcessingWebSocket(taskId);
```

**Events Handled:**
- `audio_realtime` - Real-time evaluation results
- `realtime_status` - Evaluation status updates
- `task_status` - Background task progress
- `processing_update` - File processing status
- `notification` - System notifications

### State Management

**Context Providers:**
- `ProcessingContext` - Global processing state
- `context.tsx` - Authentication and user state

### Build & Deployment

**Development:**
```bash
cd frontend
npm install
npm run dev        # Runs on http://localhost:5173
```

**Production Build:**
```bash
npm run build      # Outputs to dist/
npm run preview    # Preview production build
```

**Docker:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build
CMD ["npm", "run", "preview"]
```

### API Integration

**Base URL Configuration:**
```typescript
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:9990';
const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:9990';
```

**Service Layer:**
```typescript
// Services/Services.tsx
export const fetchUserSessions = async (userId) => {
  const response = await fetch(`${API_BASE}/api/ipersona/fetch_user_session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ all_user_id: userId })
  });
  return response.json();
};
```

## Development Infrastructure

### Makefile Automation

The project uses a comprehensive **Makefile** for development workflow automation:

**Environment Setup:**
```bash
make uv-install        # Install uv package manager
make install-deps      # Install Python dependencies
make setup-backend     # Setup backend environment
make setup-frontend    # Setup frontend environment
make setup             # Setup both backend and frontend
```

**Development:**
```bash
make start-backend     # Run FastAPI server (port 9990)
make start-frontend    # Run Vite dev server (port 5173)
```

**Code Quality:**
```bash
make format            # Format code (black, isort)
make lint              # Run linters (ruff, mypy)
make security          # Security checks (bandit, safety)
```

**Testing:**
```bash
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-coverage     # Generate coverage report
make test-watch        # Run tests in watch mode
```

**Celery Workers:**
```bash
make workers           # Start Celery worker
make work              # Kill existing workers and start fresh
```

**Cleanup:**
```bash
make clean             # Remove build artifacts, caches, etc.
```

### Testing Infrastructure

**Test Files (`tests/`):**
- `test_aws_connectivity.py` - AWS service connection tests
- `test_s3_connectivity.py` - S3 operations tests
- `test_s3_helper_run.py` - S3 helper function tests
- `test_speech_to_text.py` - STT integration tests
- `test_gemini_stt.py` - Google Gemini STT tests
- `test_google_stt_debug.py` - Google Cloud STT debugging
- `test_gdrive.py` - Google Drive integration tests
- `test_gdrive_stt_*.py` - Google Drive STT tests
- `check_credentials_project.py` - Credential validation

**Test Configuration:**
```python
# pytest.ini (implied configuration)
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
```

**Coverage Reports:**
```bash
make test-coverage
# Outputs:
# - Terminal report (missing lines highlighted)
# - HTML report: coverage/index.html
# - XML report: coverage/coverage.xml
```

### Docker & Deployment

**Main Dockerfile (Backend):**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV STRAPI_STAGE=dev-prod
EXPOSE 4500
CMD uvicorn app:app --host 0.0.0.0 --port 4500
```

**Docker Compose (Celery):**
```yaml
# docker-compose-celery.yml
version: '3.8'
services:
  celery-worker:
    build: .
    command: celery -A api.services.celery.celery_worker worker -l info
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  flower:
    build: .
    command: celery -A api.services.celery.celery_worker flower
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

**Build Scripts:**
- `build.sh` - Main application build script
- `build-celery.sh` - Celery worker build script
- `fbuild.sh` - Frontend build script (in frontend/)

**Startup Scripts:**
- `start_celery.sh` - Start Celery worker
- `start_celery_worker.sh` - Start Celery worker with logging
- `monitor_celery.sh` - Monitor Celery tasks

### Documentation

**OpenAPI Specifications (`docs/`):**
- `openapi.yaml` - Main OpenAPI 3.0 specification
- `openapi_with_sockets.yaml` - Extended with Socket.IO events
- `openapi_theneo_ready.yaml` - Formatted for Theneo documentation platform

**Socket.IO Documentation:**
- `socket_events.md` - Socket.IO event documentation
- `socket_events_theneo_ready.md` - Formatted for Theneo
- `socket_events_raw.txt` - Raw event list

**Additional Documentation:**
- `CELERY_README.md` - Celery setup and usage
- `STRUCTURED_MATCHING_SYSTEM.md` - Embedding-based matching documentation
- `specs/` - This specification directory

### Notebooks

**Jupyter Notebooks (`notebooks/`):**
- `parrot_notebook.ipynb` - Development and testing notebook
- `check.json` - Validation data
- `generate.json` - Generation examples

## Configuration

### Environment Variables
```bash
# Strapi
STRAPI_STAGE=dev-prod
STRAPI_BASE_URL=https://api.example.com

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_PARROT_API_KEY=sk-...

# AssemblyAI
ASSEMBLYAI_API_KEY=...

# FastAPI
PORT=9900
PROJECT_NAME=Parrot Backend
PROJECT_DESCRIPTION=AI-driven interview platform

# Celery
CELERY_BROKER_URL=redis://redis.10academy.org:6379/0
CELERY_RESULT_BACKEND=redis://redis.10academy.org:6379/0

# Whisper
FW_MODEL=base
FW_DEVICE=cpu
FW_COMPUTE_TYPE=int8
```

### Matching Configuration
```python
# api/utils/matching_config.py
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.3
RELEVANCE_THRESHOLD = 60
MIN_ANSWER_LENGTH = 20
```

## Deployment

### Docker Compose
```yaml
services:
  ipersona:
    build: .
    ports:
      - "9900:9900"
    environment:
      - STRAPI_STAGE=dev-prod
  
  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile.celery
    depends_on:
      - redis
  
  flower:
    image: mher/flower
    ports:
      - "5555:5555"
```

### Startup Commands
```bash
# Development
make dev-start

# Production
make prod-start

# Celery only
make celery-start

# Monitor
make celery-monitor
```

## Testing

### Test Audio Processing
```bash
curl -X POST http://localhost:9900/api/ipersona/audio_upload_external_celery \
  -F "file=@test_audio.mp3" \
  -F "target={\"job_profile_id\":123}"
```

### Test STT
```bash
curl -X POST http://localhost:9900/api/stt/whisper-upload \
  -F "file=@audio.wav"
```

### Test Socket.IO
```javascript
const socket = io('http://localhost:9900', {
  auth: { token: 'Bearer YOUR_TOKEN' }
});

socket.on('connect', () => {
  console.log('Connected');
});

socket.emit('audio chat sentence', {
  user_session: { id: 'session_id' },
  response: audioBlob,
  question_text: 'Tell me about yourself'
});
```

## Development Workflow

1. **Add new feature**: Update spec in `main.md`
2. **Generate code**: Use AI coding agent to compile spec
3. **Test**: Run tests and verify functionality
4. **Deploy**: Use Docker compose for deployment

## Monitoring & Logging

### Logging
- Uses `LLPackerLogger` for structured logging
- Logs saved to `logs/` directory with timestamps
- Log levels: INFO, ERROR, WARN, SUCCESS

### Celery Monitoring
- Flower dashboard: http://localhost:5555
- View active tasks, worker status, task history
- Retry failed tasks

### Health Checks
- Celery: `make celery-status`
- API: `curl http://localhost:9900/health`

## Future Enhancements

1. **Multi-language support**: Support interviews in multiple languages
2. **Video analysis**: Analyze video alongside audio
3. **Advanced analytics**: Track trends and improvements over time
4. **Integration with ATS**: Direct integration with applicant tracking systems
5. **Mobile app**: Native mobile application for interviews
6. **Custom models**: Fine-tune models on domain-specific data
7. **A/B testing**: Compare different evaluation approaches

## Error Handling

### Common Errors
- **401 Unauthorized**: Invalid or missing auth token
- **403 Forbidden**: User not authorized for resource
- **404 Not Found**: Session or resource not found
- **500 Internal Error**: Server-side processing error

### Graceful Degradation
- STT fallback: If one STT service fails, try another
- LLM fallback: If structured matching fails, use LLM matching
- Task retry: Failed Celery tasks automatically retry

## Security

- All endpoints require authentication (except docs)
- Tokens validated via Strapi GraphQL
- CORS configured for specific origins
- Secure file uploads with type validation
- Redis for secure task queue

---

## AI Compilation Instructions

**⚠️ IMPORTANT**: This specification documents an **EXISTING** application, not a new one.

This specification serves as **living documentation** for the existing Parrot application. When using AI coding agents:

**To understand the system:**
```
Read and explain [the specification](./main.md)
```

**To make modifications:**
```
Update [feature X] according to the specification in ./main.md
Maintain strict backward compatibility with all existing endpoints
```

**To lint/improve the spec:**
```
/load specs/lint.prompt.md
```

### How This Spec Was Created

This specification was **reverse-engineered** from a production application:

1. **Application Development**: Started 6 months ago, built organically
2. **Spec Discovery**: Team learned about spec-driven development in December 2024
3. **Reverse Engineering**: Comprehensive codebase analysis conducted in December 2024:
   - **Backend**: Scanned 50+ API endpoints in `ipersona_routes.py`
   - **Real-time**: Documented 9 Socket.IO events from `ipersona_socket.py`
   - **Database**: Mapped 8 Strapi CMS tables and relationships
   - **Tasks**: Identified Celery background task architecture
   - **AI/ML**: Catalogued 5 STT services, LLM providers, and ML models
   - **Frontend**: Analyzed React/TypeScript SPA with 30+ components
   - **Infrastructure**: Documented Makefile, Docker, testing framework
   - **Dependencies**: Reviewed 137 Python packages in requirements.txt

4. **Documentation Sources Analyzed**:
   - Source code: 50+ Python files, 30+ TypeScript components
   - Existing docs: OpenAPI specs, Socket.IO event documentation
   - Infrastructure: Makefile, Dockerfiles, build scripts
   - Configuration: Environment variables, service configs

5. **Purpose**: Now serves as authoritative documentation and blueprint for future development

### Comprehensive Application Inventory

**Backend Components:**
- ✅ 50+ REST API endpoints across 8 categories
- ✅ 9 Socket.IO real-time events
- ✅ 8 Strapi CMS database tables
- ✅ 3 Celery background task types
- ✅ 5 Speech-to-Text service integrations
- ✅ 2 external API integrations (content extraction, autograde)
- ✅ Structured question-answer matching system (embeddings)

**Frontend Components:**
- ✅ React 18 + TypeScript SPA (Vite)
- ✅ 30+ React components
- ✅ 3 custom Socket.IO hooks
- ✅ 2 Context providers for state management
- ✅ 8+ chart/visualization components
- ✅ Admin dashboard with multi-tab analytics
- ✅ Real-time audio recording and transcription UI

**AI/ML Services:**
- ✅ OpenAI GPT (primary LLM)
- ✅ LiteLLM (multi-provider gateway)
- ✅ Instructor (structured outputs)
- ✅ Sentence Transformers (embeddings)
- ✅ AutoGen (AI agent framework)
- ✅ AssemblyAI (STT)
- ✅ Faster Whisper (local STT)
- ✅ Google Cloud STT
- ✅ Google Gemini
- ✅ OpenAI Whisper API

**Infrastructure:**
- ✅ FastAPI backend (Python 3.12)
- ✅ Celery + Redis task queue
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ AWS S3 storage integration
- ✅ AWS Secrets Manager
- ✅ Comprehensive Makefile automation

**Development Tools:**
- ✅ uv package manager
- ✅ Pytest testing framework
- ✅ Coverage reporting
- ✅ Black code formatter
- ✅ isort import sorter
- ✅ Ruff linter
- ✅ MyPy type checker
- ✅ Bandit security scanner
- ✅ Safety dependency checker

**Testing:**
- ✅ 11 integration test files
- ✅ AWS/S3 connectivity tests
- ✅ STT service integration tests
- ✅ Google Drive integration tests
- ✅ Credential validation tests

**Documentation:**
- ✅ 3 OpenAPI specification versions
- ✅ Socket.IO event documentation
- ✅ Celery setup guide
- ✅ Structured matching system docs
- ✅ This comprehensive specification

**File Statistics:**
- Total Python files: 100+
- Total TypeScript files: 50+
- Total API endpoints: 50+
- Total Socket.IO events: 9
- Total dependencies: 137 Python packages
- Lines of spec documentation: 1100+

### Using This Spec Going Forward

**For New Features:**
1. Update `main.md` with new feature specification
2. Use AI agent with `compile.prompt.md` to implement
3. Test thoroughly
4. Update spec if implementation differs

**For Bug Fixes:**
1. Document expected behavior in spec
2. Fix code to match spec
3. Update spec if original behavior was incorrect

**For Onboarding:**
- Read `main.md` to understand entire system architecture
- Reference specific sections for detailed feature understanding
