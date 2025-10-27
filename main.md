# Parrot (iPersona) - AI Interview Platform Specification

## Overview

**Parrot** is an AI-driven job interview platform that helps job seekers assess job fit, engage in mock interviews, and receive personalized feedback. The system uses AI to generate interview questions, evaluate candidate responses in real-time, and provide comprehensive performance analysis.

### Purpose

Parrot enables:
- **Job seekers**: Practice interviews, get AI-powered feedback, and improve interview skills
- **HR professionals**: Assess candidates for job openings
- **Trainees**: Track progress and performance over time

### Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: Strapi CMS (via GraphQL)
- **AI**: OpenAI GPT models, AssemblyAI for transcription
- **Real-time**: Socket.IO for live interview sessions
- **Background Processing**: Celery with Redis
- **Audio**: AssemblyAI, Faster Whisper, Google Speech-to-Text
- **Frontend**: React/Vue (separate frontend application)

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
```python
def realtime_response_evaluation(run_stage, data, sessionId, interview_type, is_last_response):
    """Evaluate single response in real-time"""
    # Build evaluation prompt with:
    # - Question text
    # - Answer transcript
    # - Job requirements
    # - Competencies
    # Call OpenAI GPT for evaluation
    # Return evaluation JSON
```

**Evaluation Criteria:**
- Relevance to question
- Technical accuracy
- Communication clarity
- Competency demonstration
- SFIA level assessment

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
Uses structured matching system (see `STRUCTURED_MATCHING_SYSTEM.md`):
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

#### Events

**Client → Server:**
- `connect`: Establish connection with auth token
- `audio chat sentence`: Send audio chunk for processing
- `chat message`: Send text message
- `disconnect`: Close connection

**Server → Client:**
- `audio_realtime`: Real-time evaluation results
- `realtime_status`: Evaluation status (start/end)
- `task_status`: Background task status updates
- `error`: Error notifications

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

See `STRUCTURED_MATCHING_SYSTEM.md` for detailed specification.

**Key Components:**
- `QuestionAnswerMatcher`: Main matching engine
- Uses sentence transformers for embeddings
- Cosine similarity for matching
- Configurable thresholds
- Fallback to LLM-based matching

**Use Case:**
When processing dual audio files (questions + answers), intelligently match questions to answer segments.

## API Endpoints Summary

### Interview Session
- `POST /api/ipersona/create-user-session` - Create session
- `POST /api/ipersona/update-session-mode` - Update mode
- `GET /api/ipersona/get-session/{session_id}` - Get session
- `POST /api/ipersona/generate-interview-question` - Generate questions
- `POST /api/ipersona/overall-interview-evaluations` - Final evaluation

### Audio Processing
- `POST /api/ipersona/audio_upload_external_celery` - Upload audio
- `GET /api/ipersona/audio_upload_external_celery_status/{task_id}` - Check status
- `POST /api/ipersona/files_upload_external_celery` - Upload dual files
- `GET /api/ipersona/files_upload_external_celery_status/{task_id}` - Check status

### Speech-to-Text
- `POST /api/stt/whisper-upload` - Faster Whisper transcription
- `POST /api/stt/gemini-upload` - Google Gemini transcription
- `POST /api/speech-to-text` - Main STT endpoint

### Task Management
- `GET /api/tasks/{task_id}/status` - Task status
- `POST /api/tasks/test-celery` - Test Celery connection

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

This specification can be compiled into working code using AI coding agents. Update this specification to reflect desired changes, then use prompts like:

**compile.prompt.md:**
```
- Update the application to follow [this specification](./main.md)
- Build the code with the FastAPI tasks. Avoid asking to run commands manually.
- Maintain backward compatibility with existing endpoints.
```

**lint.prompt.md:**
```
- Optimize [the specification](./main.md) for clarity and conciseness
- Remove duplicate content
- Preserve all important details
- Do not modify the actual code with this prompt.
```

