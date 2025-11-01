# Parrot (iPersona) - System Requirements Specification

> **Document Type**: Technical Requirements Specification  
> **Version**: 1.0  
> **Status**: Normative  
> **Purpose**: Define requirements for building the Parrot AI Interview Platform from scratch

---

## Document Conventions

This document uses **RFC 2119** keywords to indicate requirement levels:

- **MUST** / **REQUIRED** / **SHALL** = Absolute requirement
- **MUST NOT** / **SHALL NOT** = Absolute prohibition
- **SHOULD** / **RECOMMENDED** = Strong recommendation, may be ignored with valid reason
- **SHOULD NOT** / **NOT RECOMMENDED** = Strong discouragement
- **MAY** / **OPTIONAL** = Truly optional

---

## 1. System Overview

### 1.1 Purpose

The system SHALL provide an AI-powered interview practice platform that enables:
- Job seekers to practice interviews with real-time AI evaluation
- HR professionals to assess candidates efficiently
- Trainees to track progress and improve interview skills

### 1.2 Scope

The system MUST implement:
1. Real-time audio transcription and evaluation
2. Interview session management
3. Progress tracking and analytics
4. Template-based interview generation
5. Background processing for uploaded media
6. Administrative oversight and reporting

### 1.3 System Context

```
[User Browser] <--> [Frontend SPA] <--> [FastAPI Backend] <--> [Strapi CMS]
                                    |
                                    |--> [Google Cloud STT]
                                    |--> [OpenAI GPT]
                                    |--> [Celery Workers]
                                    |--> [AWS S3]
```

---

## 2. Functional Requirements

### 2.1 Real-Time Interview (FR-001)

**FR-001.1: Audio Capture**

The system SHALL:
- Accept audio input via WebSocket (Socket.IO)
- Support audio formats: MP3, WAV, WebM, M4A
- Process audio chunks in real-time (< 500ms latency)

**Acceptance Criteria:**
```gherkin
GIVEN a user is in an active interview session
WHEN the user sends an audio chunk via Socket.IO
THEN the system SHALL acknowledge receipt within 100ms
AND SHALL begin processing within 500ms
```

**FR-001.2: Speech-to-Text Transcription (PRIMARY)**

The system SHALL:
- Use Google Cloud Speech-to-Text API as the PRIMARY transcription service
- Support streaming transcription with interim results
- Provide fallback to Faster Whisper if Google Cloud is unavailable
- Return transcription confidence scores

**Acceptance Criteria:**
```gherkin
GIVEN audio is received via "audio transcribe google" event
WHEN the audio is valid and clear
THEN the system SHALL return a transcript within 2 seconds
AND SHALL include a confidence score (0-1)
AND SHALL handle languages: English, Spanish, French, German

GIVEN Google Cloud STT is unavailable
WHEN audio is received for transcription
THEN the system SHALL automatically fallback to Faster Whisper
AND SHALL log the fallback event
AND SHALL complete transcription within 5 seconds
```

**FR-001.3: Real-Time AI Evaluation**

The system SHALL:
- Evaluate each answer using OpenAI GPT models
- Provide evaluation within 3 seconds of transcript completion
- Include: relevance score, communication clarity, engagement level
- Emit results via Socket.IO to connected client

**Acceptance Criteria:**
```gherkin
GIVEN a transcribed answer
WHEN the system evaluates the response
THEN it SHALL return evaluation within 3 seconds
AND SHALL include:
  - relevance_score (0-100)
  - clarity (poor/good/excellent)
  - engagement (poor/good/excellent)
  - specific_feedback (string)
AND SHALL emit via "audio_realtime" Socket.IO event
```

### 2.2 Session Management (FR-002)

**FR-002.1: Session Creation**

The system SHALL:
- Create interview sessions with unique identifiers
- Associate sessions with user profiles, job profiles, or templates
- Initialize session state (pending/active/completed)
- Store session metadata (start time, mode, type)

**Acceptance Criteria:**
```gherkin
GIVEN a user initiates an interview
WHEN they select a job profile OR template OR challenge
THEN the system SHALL create a session record
AND SHALL assign a unique session ID (UUID)
AND SHALL set initial status to "pending"
AND SHALL record the start timestamp
AND SHALL link to: user_profile_id, job_profile_id OR template_id OR challenge_id
```

**FR-002.2: Session State Management**

The system SHALL:
- Track session states: pending, active, paused, completed, failed
- Allow session resume after disconnection
- Prevent duplicate sessions for same user+job combination
- Auto-close sessions after 2 hours of inactivity

**Acceptance Criteria:**
```gherkin
GIVEN an active interview session
WHEN the user disconnects
THEN the system SHALL mark session as "paused"
AND SHALL queue any pending messages
AND SHALL allow reconnection within 30 minutes

GIVEN a paused session
WHEN the user reconnects with same session_id
THEN the system SHALL restore session to "active"
AND SHALL deliver all queued messages
AND SHALL resume from last question
```

### 2.3 Speech-to-Text Services (FR-003)

**FR-003.1: Google Cloud STT (PRIMARY)**

The system MUST:
- Integrate Google Cloud Speech-to-Text API
- Use streaming recognition for real-time audio
- Support single-utterance recognition for short audio
- Handle audio encoding: LINEAR16, FLAC, MP3, WEBM_OPUS

**Acceptance Criteria:**
```gherkin
GIVEN a valid Google Cloud API key is configured
WHEN audio is sent via "audio transcribe google" Socket.IO event
THEN the system SHALL:
  - Stream audio to Google Cloud STT API
  - Return interim results every 1-2 seconds
  - Provide final transcript when speech ends
  - Include confidence score and language code
AND SHALL handle errors gracefully
AND SHALL fallback if API returns 4xx/5xx errors
```

**FR-003.2: Alternative STT Services**

The system SHOULD provide alternative STT services:
1. **Faster Whisper** (local, fallback)
   - MUST run on local CPU/GPU
   - MUST support languages: en, es, fr, de, zh
   - SHOULD complete transcription within 5 seconds

2. **OpenAI Whisper API** (cloud fallback)
   - MUST use OpenAI Whisper API endpoint
   - SHOULD be used if Google Cloud fails
   - MUST handle file uploads up to 25MB

3. **AssemblyAI** (batch processing)
   - MUST be used for uploaded audio files
   - SHOULD provide speaker diarization
   - MUST support asynchronous processing

**Acceptance Criteria:**
```gherkin
GIVEN the primary STT service (Google Cloud) fails
WHEN audio needs transcription
THEN the system SHALL try services in this order:
  1. Faster Whisper (local)
  2. OpenAI Whisper API
  3. AssemblyAI
AND SHALL log which service was used
AND SHALL complete transcription within 10 seconds (any service)
```

### 2.4 AI Evaluation Engine (FR-004)

**FR-004.1: Real-Time Question-Answer Evaluation**

The system SHALL evaluate each answer in real-time using the `realtime_evaluation.txt` prompt.

**Implementation Details:**
- **Prompt Location**: `/api/modules/prompts/ipersona/realtime_evaluation.txt`
- **LLM Function**: `gpt.openai_gpt_assistant_without_streaming()`
- **Evaluation Focus**: ONLY answer relevance to the specific question asked
- **JSON Extraction**: Uses `util.extract_json()` with `json_repair` fallback for malformed responses

**Evaluation Criteria (from actual prompt):**
1. **Answer Relevance** (Focus ONLY on whether response addresses the specific content of the question)
   - 90-100%: Highly relevant, answers question directly
   - 70-89%: Mostly relevant with some unrelated elements
   - 50-69%: Partially addresses with many irrelevant aspects
   - Below 50%: Mostly irrelevant, does not directly answer

**Required Output Structure:**
```json
{
    "realtime_evaluation": {
        "overall": {
            "relevance": "strong|medium|weak",
            "feedback": "evaluation focusing ONLY on relevance to asked question"
        },
        "answer_relevancy": [
            {
                "level": "0-100",
                "reason": "justification for relevance level"
            }
        ]
    }
}
```

**Acceptance Criteria:**
```gherkin
GIVEN a question "{question}" and candidate response "{candidate_response}"
WHEN the system evaluates via `/api/pages/ipersona/socket/ipersona_socket.py::_evaluate_answer_live()`
THEN it SHALL:
  1. Load the realtime_evaluation.txt prompt
  2. Replace {question} and {candidate_response} placeholders
  3. Call OpenAI GPT with the formatted prompt
  4. Extract JSON from the response using util.extract_json()
  5. Return structured evaluation within 3 seconds
  6. Emit via "audio_realtime" Socket.IO event with evaluation data
AND evaluation SHALL use non-gender-specific pronouns ('you', 'your')
AND SHALL NOT assess overall response quality, ONLY relevance

GIVEN malformed JSON in LLM response
WHEN util.extract_json() processes the response
THEN it SHALL:
  - Use json_repair library to fix common JSON errors
  - Strip markdown code blocks (```json ... ```)
  - Handle escaped quotes and newlines
  - Return None if JSON is irreparable
```

**FR-004.2: Overall Interview Evaluation with SFIA Competency Framework**

The system SHALL generate comprehensive evaluation after interview completion using the `overall_evaluation.txt` prompt.

**Implementation Details:**
- **Prompt Location**: `/api/modules/prompts/ipersona/overall_evaluation.txt`
- **LLM Function**: `gpt.openai_gpt_assistant_without_streaming()`
- **Framework**: SFIA 7-level competency framework (Skills Framework for the Information Age)
- **History Context**: Entire interview conversation history (`{history}` placeholder)
- **Triggered By**: `POST /api/ipersona/close_session` endpoint

**SFIA Competency Levels (from actual prompt):**
- **Level 1 - Fellow**: Works under close direction, minimal influence, routine activities
- **Level 2 - Assist**: Works under routine direction, limited discretion
- **Level 3 - Apply**: Works under general direction, sometimes complex work
- **Level 4 - Enable**: Substantial personal responsibility, complex technical activities
- **Level 5 - Ensure, advise**: Broad direction, fully responsible for objectives
- **Level 6 - Initiate, influence**: Defined authority, influences policy and strategy
- **Level 7 - Set strategy, inspire, mobilise**: Authority over all aspects, highest leadership

**Required Output Structure:**
```json
{
    "overall_evaluation": {
        "evaluation": "comprehensive summary of candidate performance",
        "recommendation": [
            {
                "title": "Resources",
                "resource": "specific course/book/community site description",
                "type": "Online Course|Book|Community|Certification",
                "link": "www.example.com"
            }
        ],
        "competency": [
            {
                "name": "competency name from job description",
                "sfia_level": "1-7 based on demonstrated performance"
            }
        ]
    }
}
```

**Evaluation Requirements (from actual prompt):**
1. Provide comprehensive evaluation of candidate's performance throughout the interview
2. Assess how well the candidate would fit the role
3. Be honest and constructive to help candidate become interview-ready
4. Offer specific feedback for future interview improvement
5. Provide recommendations to improve skills for the job role
6. Evaluate candidate's competencies using SFIA 7-level framework

**Acceptance Criteria:**
```gherkin
GIVEN a completed interview session
WHEN overall evaluation is triggered
THEN the system SHALL:
  - Calculate average relevance score
  - Identify competency areas (technical, communication, problem-solving)
  - Generate score distribution (poor/good/excellent percentages)
  - Provide overall rating (1-5 stars)
  - Store evaluation in database
AND SHALL complete within 10 seconds
```

### 2.5 Background Processing (FR-005)

**FR-005.1: File Upload Processing**

The system SHALL:
- Accept audio/video file uploads (max 100MB)
- Process uploads asynchronously via Celery
- Provide status updates via Socket.IO or polling
- Store processed files in AWS S3

**Acceptance Criteria:**
```gherkin
GIVEN a user uploads an audio file
WHEN the file is received by the API
THEN the system SHALL:
  - Validate file type and size
  - Create a Celery task for processing
  - Return task_id immediately (< 1 second)
  - Store file temporarily for processing
  - Update Redis with task status

GIVEN a Celery task is processing an upload
WHEN processing progresses
THEN the system SHALL:
  - Update Redis status every 5 seconds
  - Emit Socket.IO events if user connected
  - Upload final file to S3
  - Delete temporary files after processing
```

**FR-005.2: Question-Answer Matching**

The system SHALL:
- Match uploaded question files with answer files
- Use embedding-based similarity matching (primary)
- Use LLM-based matching as fallback
- Generate matched pairs with confidence scores

**Acceptance Criteria:**
```gherkin
GIVEN separate question and answer files
WHEN the matching process runs
THEN the system SHALL:
  - Extract questions from question file
  - Extract answers from answer file
  - Generate embeddings for both using Sentence Transformers
  - Calculate cosine similarity matrix
  - Match questions to answers with highest similarity (>0.6)
  - Return matched pairs with relevance_score
AND SHALL complete within 30 seconds for 50 questions
AND SHALL fallback to LLM matching if embedding service fails
```

### 2.6 Template Management (FR-006)

**FR-006.1: Interview Template Creation**

The system SHALL:
- Allow creation of interview templates
- Support manual question entry
- Support AI-generated questions from job descriptions
- Store templates with metadata (title, description, sections)

**Acceptance Criteria:**
```gherkin
GIVEN a user wants to create a template
WHEN they provide job description and parameters
THEN the system SHALL:
  - Use OpenAI GPT to generate relevant questions
  - Organize questions into sections (technical, behavioral, etc.)
  - Include ideal answers for each question
  - Store template in database
  - Return template_id
AND SHALL generate 10-20 questions within 15 seconds
```

### 2.7 Progress Tracking (FR-007)

**FR-007.1: User Progress Analytics**

The system SHALL:
- Track performance metrics over time
- Calculate progress trends (improving/declining/stable)
- Visualize competency radar charts
- Track per-job/challenge/template progress

**Acceptance Criteria:**
```gherkin
GIVEN a user has completed multiple interview sessions
WHEN progress analytics are requested
THEN the system SHALL return:
  - Overall performance score (0-100) per session
  - Competency breakdown over time
  - Communication skills trends (clarity, engagement)
  - Session count and completion rate
  - Time spent per session
AND SHALL calculate rolling averages (last 5 sessions)
```

---

## 3. Non-Functional Requirements

### 3.1 Performance (NFR-001)

**NFR-001.1: Response Times**

The system SHALL meet these performance targets:

| Operation | Target | Maximum |
|-----------|--------|---------|
| Socket.IO connection | < 500ms | 1s |
| STT transcription (Google) | < 2s | 5s |
| AI evaluation | < 3s | 10s |
| API endpoint response | < 1s | 3s |
| File upload acknowledgment | < 1s | 2s |
| Database query (simple) | < 100ms | 500ms |

**NFR-001.2: Throughput**

The system SHALL support:
- 100 concurrent interview sessions
- 1000 API requests per minute
- 50 file uploads per minute
- 20 Celery tasks processed concurrently

### 3.2 Reliability (NFR-002)

**NFR-002.1: Availability**

The system SHALL:
- Maintain 99.5% uptime (excluding planned maintenance)
- Implement health checks on all services
- Provide graceful degradation when services fail
- Auto-recover from transient failures

**NFR-002.2: Data Integrity**

The system SHALL:
- Store all interview data persistently
- Implement transaction boundaries for critical operations
- Validate all inputs before storage
- Prevent data loss during failures

### 3.3 Security (NFR-003)

**NFR-003.1: Authentication & Authorization**

The system SHALL:
- Require authentication for all protected endpoints
- Use token-based authentication (JWT or similar)
- Implement role-based access control (trainee, admin, staff)
- Expire sessions after inactivity (30 minutes)

**NFR-003.2: Data Protection**

The system SHALL:
- Encrypt sensitive data at rest (S3, database)
- Use TLS 1.2+ for all network communication
- Sanitize all user inputs to prevent injection attacks
- Store API keys in secure secret management (AWS Secrets Manager)

**NFR-003.3: Privacy**

The system SHALL:
- Allow users to delete their data
- Not store audio permanently without consent
- Anonymize analytics data
- Comply with data retention policies

### 3.4 Scalability (NFR-004)

The system SHALL:
- Scale horizontally (add more workers/instances)
- Use Redis for distributed caching
- Implement connection pooling for database
- Support CDN for static assets

### 3.5 Maintainability (NFR-005)

The system SHALL:
- Log all errors with stack traces
- Implement structured logging (JSON format)
- Provide comprehensive API documentation (OpenAPI)
- Include health check endpoints
- Follow PEP 8 style guidelines (Python)

---

## 4. API Contracts

### 4.1 Socket.IO Events

**Implementation File**: `/api/pages/ipersona/socket/ipersona_socket.py`
**Socket.IO Server**: `python-socketio` with `async_mode='asgi'`
**Namespace**: Default namespace `/`

#### 4.1.1 Client → Server Events

**Event: `initial connect`** (CONNECTION ESTABLISHMENT)

**Purpose**: Establish WebSocket connection and initialize session context.

**Payload:**
```json
{
  "user_id": "string (all_user_id)",
  "session_id": "string (optional, for reconnection)",
  "run_stage": "dev|stage|prod"
}
```

**Implementation Requirements:**
```python
@sio.on('initial connect')
async def handle_initial_connect(sid, data):
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    run_stage = data.get('run_stage', 'dev')
    
    # Store SID → user_id mapping in Redis
    # Key: f"sid_to_user:{sid}" → user_id
    # Expiry: 30 minutes
    
    # Store user_id → SID mapping in memory (sid_user_map)
    sid_user_map[user_id] = sid
    
    # If reconnecting, deliver queued messages
    # Check: user_message_queue[user_id] and sid_message_queue[sid]
```

**Requirements:**
- The system SHALL store bidirectional SID ↔ user_id mapping
- The system SHALL persist mapping in Redis with 30-minute TTL
- The system SHALL deliver queued messages on reconnection
- The system SHALL emit `connection_confirmed` event to client

---

**Event: `audio transcribe google`** (PRIMARY REAL-TIME TRANSCRIPTION)

**Purpose**: Stream audio chunks for Google Cloud Speech-to-Text transcription.

**Payload:**
```json
{
  "audio": "base64_encoded_pcm16_audio_data",
  "session_id": "uuid",
  "language": "en-US",
  "user_id": "string",
  "format": "pcm16|webm|mp3"
}
```

**Implementation Requirements:**
```python
@sio.on('audio transcribe google')
async def handle_google_transcribe(sid, data):
    audio_b64 = data.get('audio')
    session_id = data.get('session_id')
    language = data.get('language', 'en-US')
    
    # Decode base64 audio
    audio_bytes = base64.b64decode(audio_b64)
    
    # Route to Google Cloud STT V2 streaming
    # File: google_stt_v2.py
    # Class: GoogleStreamingSTTV2
    
    # Send audio chunk to streaming recognizer
    # Receive interim and final results
    
    # Emit transcript via 'transcription_result' event
```

**Requirements:**
- The system SHALL validate `session_id` exists and is active
- The system SHALL decode base64 audio data (handle padding errors)
- The system SHALL use Google Cloud STT V2 API for streaming recognition
- The system SHALL emit interim results via `transcription_interim` event
- The system SHALL emit final transcript via `transcription_result` event within 2 seconds
- The system SHALL fallback to Faster Whisper if Google Cloud fails
- The system SHALL log transcription errors with SID and session_id
- The system SHALL handle errors and emit `transcription_error`

**Event: `audio chat sentence`** (REAL-TIME INTERVIEW - PRIMARY FLOW)

**Purpose**: Process complete audio sentence during live interview, transcribe, evaluate, and provide real-time feedback.

**Payload:**
```json
{
  "audio": "base64_encoded_audio_data",
  "session_id": "uuid",
  "user_id": "string",
  "question_id": "string",
  "run_stage": "dev|stage|prod"
}
```

**Complete Implementation Flow:**
```python
@sio.on('audio chat sentence')
async def handle_audio_chat_sentence(sid, data):
    # Step 1: Validate session
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    session = IpersonaSessionSchema().exists_session_id(session_id)
    
    # Step 2: Decode and save audio temporarily
    audio_bytes = base64.b64decode(data['audio'])
    temp_path = f"/tmp/audio_{session_id}_{timestamp}.mp3"
    
    # Step 3: Transcribe using Google Cloud STT (PRIMARY)
    transcript = await transcribe_with_google_cloud(audio_bytes)
    # FALLBACK: If Google fails, use Faster Whisper
    if transcript.get('error'):
        transcript = transcribe_with_faster_whisper(temp_path)
    
    # Step 4: Retrieve current question from session
    session_data = IpersonaSessionSchema().filter_by_session_id(session_id)
    current_question = session_data['attributes']['message'][-1]['question']
    
    # Step 5: Perform real-time AI evaluation
    # Prompt: /api/modules/prompts/ipersona/realtime_evaluation.txt
    evaluation_prompt = load_prompt('realtime_evaluation.txt')
    evaluation_prompt = evaluation_prompt.replace('{question}', current_question)
    evaluation_prompt = evaluation_prompt.replace('{candidate_response}', transcript['text'])
    
    evaluation_response = await gpt.openai_gpt_assistant_without_streaming(evaluation_prompt)
    evaluation_json = util.extract_json(evaluation_response)
    
    # Step 6: Save message to database
    message_data = {
        "question": current_question,
        "answer": transcript['text'],
        "realtime_evaluation": evaluation_json,
        "timestamp": datetime.now().isoformat()
    }
    IpersonaSessionMessageSchema().save_message(session_id, message_data)
    
    # Step 7: Emit real-time feedback to client
    await sio.emit('audio_realtime', {
        "transcript": transcript['text'],
        "evaluation": evaluation_json,
        "question_id": data.get('question_id')
    }, room=sid)
    
    # Step 8: Update session status
    await sio.emit('realtime_status', {
        "status": "evaluated",
        "session_id": session_id
    }, room=sid)
```

**Requirements:**
- The system SHALL complete the entire flow within 5 seconds
- The system SHALL transcribe using Google Cloud STT as PRIMARY service
- The system SHALL fallback to Faster Whisper if Google Cloud fails
- The system SHALL evaluate answer using `realtime_evaluation.txt` prompt
- The system SHALL save transcript + evaluation to `ipersona-session` message array
- The system SHALL emit `audio_realtime` event with evaluation results
- The system SHALL emit `realtime_status` event with status updates
- The system SHALL handle base64 decoding errors gracefully
- The system SHALL log all steps with session_id and SID for debugging
- The system SHALL use non-blocking async operations throughout

---

### 4.2 Background Tasks (Celery)

**Implementation File**: `/api/services/celery/audio_tasks.py`
**Broker**: Redis (`redis://localhost:6379/0`)
**Result Backend**: Redis
**Worker Command**: `celery -A api.services.celery.celery_app worker --loglevel=info`

#### 4.2.1 Task: `process_upload_external_audio_task`

**Purpose**: Process uploaded audio/document files asynchronously for interview evaluation.

**Function Signature:**
```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=600  # 10 minutes
)
def process_upload_external_audio_task(
    self,
    filename: str,
    content_type: str,
    audio_path: str,
    job_profile_id: int,
    challenge_id: int,
    template_id: int,
    all_user_id: str,
    external: bool,
    run_stage: str,
    user_sid: str = None
):
```

**Implementation Flow:**
```python
# Step 1: Determine active task identifier
task_type, task_id = _get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
# Returns: ("job", job_id) OR ("challenge", challenge_id) OR ("template", template_id)

# Step 2: Set Redis status
redis_key = f"parrot_celery_tasks:audio_status:{task_type}:{task_id}"
redis.set(redis_key, {"status": "processing", "message": ""})

# Step 3: Process based on content type
if "audio" in content_type or "video" in content_type:
    # 3a. Convert to MP3 if needed
    if original_format not in ["mpeg", "mp3"]:
        audio_bytes = util.convert_to_mp3(audio_bytes, original_format)
    
    # 3b. Upload to S3
    s3_url = s3_client.upload_bytes_and_get_url(
        bucket='tenx-parrot-assets',
        contents=audio_bytes,
        key=f"audio/{filename}"
    )
    
    # 3c. Transcribe using external content-extractor service
    result = audio_transcription_logics(filename, audio_path, content_type)
    # Endpoint: https://content-extractor.10academy.org/content-extractor/audio_transcript
    # Uses: Google Gemini 2.5-flash model
    
    transcript = result.get("content")
    
    # 3d. AI-Powered Content Validation
    validation = ai_validate_interview_content(transcript)
    # Uses: OpenAI GPT to detect if content is valid interview Q&A
    # Checks: Has questions AND answers, not just questions
    # Thresholds: >= 3 question indicators + 0 answer indicators = INVALID
    
    if not validation.get('valid'):
        redis.set(redis_key, {
            "status": "failed",
            "message": f"Invalid interview content: {validation['reason']}"
        })
        # Save notification to database
        save_notification(all_user_id, run_stage, f"Invalid interview content: {validation['reason']}")
        return "Invalid interview content"
    
elif "text" in content_type or "pdf" in content_type:
    # 3e. Upload document to S3
    s3_url = s3_client.upload_bytes_and_get_url(
        bucket='tenx-parrot-assets',
        contents=file_bytes,
        key=f"documents/{filename}"
    )
    
    # 3f. Extract text using content-extractor
    result = content_extraction_logics(filename, file_bytes, content_type)
    # Endpoint: https://content-extractor.10academy.org/content-extractor/extract
    
    transcript = result.get("content")
    
    # 3g. Validate extracted content
    validation = ai_validate_interview_content(transcript)

# Step 4: Generate AI evaluation
external_audio_prompt = file_reader('prompts/external_audio_analysis.txt')
external_audio_prompt = external_audio_prompt.replace('{transcription}', transcript)
evaluation_response = gpt.openai_gpt_assistant_without_streaming(external_audio_prompt)
evaluation_json = util.extract_json(evaluation_response)

# Step 5: Create session in database
session = util.create_session(
    run_stage, mode, template, external, challenge,
    all_user_id, tinder_user_profile_id, job_profile_id,
    template_id, challenge_id, message, upload_metadata
)

# Step 6: Save messages to session
strapi.save_messages_to_db(evaluation_json, session['id'])

# Step 7: Run overall evaluation in separate thread
def run_overall():
    loop = asyncio.new_event_loop()
    overall = loop.run_until_complete(
        overall_interview_evaluations_external(
            run_stage, evaluation_json, 'External', session['id'],
            all_user_id, tinder_user_profile_id, job_profile_id,
            challenge_id, template_id, 'job_interview_config'
        )
    )
    
    # Step 8: Update Redis with success
    redis.set(redis_key, {
        "status": "done",
        "message": "Chat Saved Successfully",
        "chat": saved,
        "overall": overall
    })
    
    # Step 9: Save success notification
    save_notification(all_user_id, run_stage, "Uploaded file analysis completed successfully!")

threading.Thread(target=run_overall).start()
```

**Requirements:**
- The task SHALL timeout after 10 minutes (600 seconds)
- The task SHALL retry up to 3 times on failure with 60-second delays
- The task SHALL update Redis status at each major step
- The task SHALL validate interview content using AI before processing
- The task SHALL convert all audio/video to MP3 format
- The task SHALL upload all files to S3 bucket `tenx-parrot-assets`
- The task SHALL use external content-extractor service for transcription
- The task SHALL save notifications to `notifications` table via `IpersonaNotificationSchema`
- The task SHALL handle Docker vs localhost path normalization
- The task SHALL compress files exceeding 10MB before transcription

**Error Handling:**
- Base64 decoding errors → Return error immediately
- S3 upload failures → Retry 3 times, then fail task
- Transcription timeouts → Retry with exponential backoff (5min, 10min, 20min)
- Content validation failures → Save error notification, mark Redis as failed
- Session creation failures → Log error, update Redis, re-raise exception

---

**Payload:**
```json
{
  "audio": "base64_encoded_audio_data",
  "session_id": "uuid",
  "question_id": "integer",
  "is_final": boolean
}
```

**Requirements:**
- The system SHALL transcribe using Google Cloud STT
- The system SHALL evaluate answer using OpenAI GPT
- The system SHALL emit `audio_realtime` with evaluation
- The system SHALL save message to database
- The system SHALL complete within 5 seconds total

#### 4.1.2 Server → Client Events

**Event: `audio_realtime`** (EVALUATION RESULTS)

**Payload:**
```json
{
  "session_id": "uuid",
  "question_id": integer,
  "transcript": "string",
  "evaluation": {
    "relevance_score": integer,
    "communication_skills": [...],
    "performance": [...],
    "feedback": "string"
  }
}
```

### 4.3 Additional Celery Tasks

**Task: `process_upload_external_files_task`** (Question + Answer Files)

```python
@celery_app.task(bind=True)
def process_upload_external_files_task(
    self,
    question_filename, question_content_type, question_audio_path, question_contents,
    answer_filename, answer_content_type, answer_audio_path, answer_contents,
    job_profile_id, challenge_id, template_id, session_id, all_user_id, 
    external, run_stage, user_sid=None
)
```

**Purpose**: Process separate question and answer files for interview evaluation.

**Implementation Flow:**
1. Process question file → Extract questions
2. Process answer file → Extract answers  
3. Use **Structured Question-Answer Matching** (embedding-based)
   - File: `/api/utils/question_answer_matcher.py`
   - Uses: `SentenceTransformer('all-MiniLM-L6-v2')`
   - Calculates cosine similarity between question/answer embeddings
   - Filters matches with relevance_score >= 90
4. Generate evaluation using matched Q&A pairs
5. Create session and save to database
6. Run overall evaluation

---

**Task: `process_upload_external_answer_with_template_task`** (Answer File + Template Questions)

```python
@celery_app.task(bind=True)
def process_upload_external_answer_with_template_task(
    self,
    template_questions,  # From database template
    answer_filename, answer_content_type, answer_audio_path, answer_contents,
    job_profile_id, challenge_id, template_id, session_id, all_user_id,
    external, run_stage, user_sid=None
)
```

**Purpose**: Process answer file using pre-defined template questions.

**Key Features:**
- **AI Answer Content Validation** before processing
  - Checks if answer file contains actual answers (not just questions)
  - Uses heuristics: count question vs answer indicators
  - Lenient validation (≥ 6 question indicators + 0 answers = INVALID)
- Uses **Structured Matching** to pair template questions with transcript answers
- More accurate than LLM-based matching

---

### 4.4 REST API Endpoints

**Implementation File**: `/api/pages/ipersona/routers/ipersona_routes.py`
**Base Path**: `/api/ipersona`
**Framework**: FastAPI with automatic OpenAPI documentation

#### 4.4.1 Health & System Endpoints

**GET /api/ipersona/health**

**Purpose**: System health check and external autograde service integration test.

**Acceptance Criteria:**
```gherkin
GIVEN the service is running
WHEN /health is called
THEN it SHALL:
  - Return 200 OK if healthy
  - Call external autograde endpoint with test session data
  - Return autograde service status
  - Log any autograde service failures
```

**Response Example:**
```json
{
  "status": "healthy",
  "autograde_status": "available",
  "autograde_response": {
    "success": true,
    "session_id": "test_session"
  }
}
```

---

#### 4.4.2 Speech-to-Text Endpoints

**POST /api/ipersona/stt/google-upload**

**Purpose**: Transcribe uploaded audio using Google Cloud STT.

**Request:**
```typescript
{
  file: File,  // Audio file (multipart/form-data)
  language?: string  // Optional language code (e.g., "en-US")
}
```

**Response:**
```json
{
  "text": "transcribed text",
  "language": "en-US",
  "status_code": 200,
  "message": "Transcript extracted successfully"
}
```

---

**POST /api/ipersona/stt/whisper-upload**

**Purpose**: Transcribe audio using Faster Whisper (local).

**Requirements:**
- SHALL use Faster Whisper model (default: "base")
- SHALL support languages via ISO 639-1 codes (e.g., "en", "es")
- SHALL return 400 if language code is invalid
- SHALL provide hint for valid language codes in error

---

**POST /api/ipersona/stt/openai-upload**

**Purpose**: Transcribe audio using OpenAI Whisper API.

---

**POST /api/ipersona/stt/gemini-upload**

**Purpose**: Transcribe audio using Google Gemini.

---

#### 4.4.3 Session Management Endpoints

**POST /api/ipersona/create_user_session**

**Purpose**: Create new interview session and generate questions.

**Request Payload:**
```typescript
{
  run_stage: "dev" | "stage" | "prod",
  mode: string,
  template: boolean,
  external: boolean,
  challenge: boolean,
  generate: boolean,
  job_profile_id: number | null,
  all_user_id: string,
  template_id: number | null,
  challenge_id: number | null
}
```

**Implementation Steps:**
1. Validate user exists (`IpersonaTraineeSchema.filter_by_alluser_id()`)
2. Retrieve job/template/challenge data from Strapi
3. Generate interview questions using LLM if `generate=true`
4. Create session in database (`util.create_session()`)
5. Save generated questions to session
6. Return session ID and questions

**Response:**
```json
{
  "session_id": "uuid",
  "questions": [...],
  "status": 200,
  "message": "Session created successfully"
}
```

**Acceptance Criteria:**
```gherkin
GIVEN valid user and job/template/challenge IDs
WHEN create_user_session is called
THEN it SHALL:
  - Create unique session with UUID
  - Generate appropriate questions based on mode
  - Link session to user profile and job/template/challenge
  - Return session data within 5 seconds
  - Set initial status to "pending"
```

---

**POST /api/ipersona/close_session**

**Purpose**: Mark session as complete and trigger final evaluation.

**Request:**
```typescript
{
  session_id: string,
  all_user_id: string,
  run_stage: string
}
```

**Implementation:**
1. Validate session exists
2. Update session status to "Closed"
3. Trigger `overall_interview_evaluations()` asynchronously
4. Calculate progress metrics
5. Update overall observer records

**Acceptance Criteria:**
```gherkin
GIVEN an active session with answered questions
WHEN close_session is called
THEN it SHALL:
  - Mark session as "Closed"
  - Trigger overall evaluation within 10 seconds
  - Calculate SFIA competency levels
  - Generate recommendations
  - Update progress-over-time metrics
  - Return overall evaluation results
```

---

**POST /api/ipersona/delete_session**

**Purpose**: Soft-delete a session (mark as deleted).

---

**POST /api/ipersona/clarify**

**Purpose**: Request AI clarification for an interview question.

---

#### 4.4.4 Data Retrieval Endpoints

**POST /api/ipersona/fetch_user_session**

**Purpose**: Retrieve all interview sessions for a specific user.

**Request:**
```typescript
{
  all_user_id: string,
  run_stage: string
}
```

**Response:**
```json
{
  "sessions": [
    {
      "id": "uuid",
      "status": "Closed",
      "job_profile": {...},
      "created_at": "ISO 8601",
      "message_count": 10
    }
  ],
  "status": 200
}
```

---

**POST /api/ipersona/fetch_chat_history**

**Purpose**: Retrieve conversation history for a session.

**Request:**
```typescript
{
  session_id: string
}
```

**Response:**
```json
{
  "messages": [
    {
      "question": "Tell me about yourself",
      "answer": "I am a software engineer...",
      "realtime_evaluation": {...},
      "timestamp": "ISO 8601"
    }
  ],
  "status": 200
}
```

---

**POST /api/ipersona/fetch_user_all_observer**

**Purpose**: Retrieve all evaluation observations for a user.

---

**POST /api/ipersona/fetch_session_overall_evaluation**

**Purpose**: Retrieve final overall evaluation for a completed session.

**Response:**
```json
{
  "overall_evaluation": {
    "evaluation": "comprehensive summary",
    "recommendation": [...],
    "competency": [
      {"name": "Python", "sfia_level": "4"}
    ]
  },
  "evaluation_metrics": {
    "overall_performance_score": 85,
    "communication_skills": [...],
    "relevancy": [...]
  },
  "status": 200
}
```

---

#### 4.4.5 Progress & Analytics Endpoints

**POST /api/ipersona/calculate_session_overall_progress**

**Purpose**: Calculate aggregated progress metrics for a user across all sessions.

**Implementation:**
- Aggregates clarity, confidence, engagement over time
- Calculates competency progression
- Formats data for charting (LineChart, RadarChart)

---

**POST /api/ipersona/calculate_allstat_progress**

**Purpose**: Calculate all-time statistics for a user across all job types, challenges, and templates.

---

**POST /api/ipersona/engagement_jobs_status**

**Purpose**: Calculate interview engagement metrics for job-related interviews.

**Response:**
```json
{
  "all_user_id": "string",
  "jobs": [
    {
      "job_profile_id": 123,
      "total_sessions": 5,
      "completed_sessions": 3,
      "average_score": 82,
      "last_session": "ISO 8601"
    }
  ],
  "cursor": {...},
  "status": 200
}
```

---

**POST /api/ipersona/engagement_challenge_status**

**Purpose**: Calculate engagement metrics for challenge-based interviews.

---

**POST /api/ipersona/engagement_template_status**

**Purpose**: Calculate engagement metrics for template-based interviews.

---

**POST /api/ipersona/engagement_status**

**Purpose**: Overall engagement dashboard data combining all types.

---

#### 4.4.6 Admin Endpoints

**POST /api/ipersona/admin_overview_status**

**Purpose**: Admin dashboard overview with system-wide statistics.

**Acceptance Criteria:**
```gherkin
GIVEN an admin user
WHEN admin_overview_status is called
THEN it SHALL return:
  - Total number of users
  - Total number of sessions
  - Average performance scores
  - Recent activity summary
  - System health metrics
```

---

**POST /api/ipersona/admin_allusers_data**

**Purpose**: Retrieve data for all users with filtering and pagination.

---

**POST /api/ipersona/admin_alljobs_data**

**Purpose**: Retrieve data for all job profiles with session counts.

---

**POST /api/ipersona/admin_allchallenges_data**

**Purpose**: Retrieve data for all challenges with completion rates.

---

**POST /api/ipersona/admin_each_job_overview_data**

**Purpose**: Detailed analytics for a specific job profile.

---

**POST /api/ipersona/admin_each_challenge_overview_data**

**Purpose**: Detailed analytics for a specific challenge.

---

**POST /api/ipersona/admin_allusers_performance_data**

**Purpose**: Performance metrics across all users for comparison.

---

**POST /api/ipersona/admin_job_by_template_id**

**Purpose**: Retrieve job data filtered by template ID.

---

**POST /api/ipersona/admin_challenge_by_template_id**

**Purpose**: Retrieve challenge data filtered by template ID.

---

**POST /api/ipersona/admin_interview_by_template**

**Purpose**: Retrieve interview sessions filtered by template.

---

#### 4.4.7 Template Management Endpoints

**POST /api/ipersona/get_all_tinder_templates**

**Purpose**: Retrieve all available interview templates.

**Response:**
```json
{
  "templates": [
    {
      "id": 1,
      "name": "Software Engineer Interview",
      "description": "Standard SWE questions",
      "questions": [
        {
          "question": "...",
          "ideal_answer": "...",
          "sectionType": "Technical"
        }
      ]
    }
  ],
  "status": 200
}
```

---

**POST /api/ipersona/save_tinder_template**

**Purpose**: Create a new interview template.

**Request:**
```typescript
{
  name: string,
  description: string,
  questions: Array<{
    question: string,
    ideal_answer: string,
    sectionType: string
  }>,
  job_profile_id?: number,
  run_stage: string
}
```

---

**POST /api/ipersona/get_a_template**

**Purpose**: Retrieve a single template by ID.

---

**POST /api/ipersona/update_tinder_template**

**Purpose**: Update an existing template.

---

**POST /api/ipersona/attach_job_id_to_template**

**Purpose**: Link a job profile to a template.

---

**POST /api/ipersona/create_template_by_llm**

**Purpose**: Generate interview template using LLM from job description.

**Request:**
```typescript
{
  context: string,  // Job description
  run_stage: string
}
```

**Implementation:**
1. Send job description to OpenAI GPT
2. Generate relevant interview questions
3. Extract ideal answers
4. Format as template structure
5. Save to database

**Acceptance Criteria:**
```gherkin
GIVEN a valid job description
WHEN create_template_by_llm is called
THEN it SHALL:
  - Generate minimum 5 relevant questions
  - Include ideal answers for each question
  - Categorize questions by type (Technical, Behavioral, etc.)
  - Return template within 30 seconds
  - Save template to database
```

---

#### 4.4.8 Challenge Endpoints

**POST /api/ipersona/get_all_challenges**

**Purpose**: Retrieve all available challenge documents.

---

**POST /api/ipersona/get_a_challenge**

**Purpose**: Retrieve a single challenge by ID.

---

#### 4.4.9 File Upload Endpoints (Celery-backed)

**POST /api/ipersona/audio_upload_external**

**Purpose**: Upload single audio/document file for background processing.

**Request:** `multipart/form-data` with file upload

**Response:**
```json
{
  "task_id": "celery_task_uuid",
  "status": "processing",
  "message": "File queued for processing"
}
```

**Implementation:**
1. Save uploaded file to `/tmp` or `/audio` directory
2. Queue `process_upload_external_audio_task` Celery task
3. Return task_id immediately
4. Client polls Redis or receives Socket.IO updates

---

**POST /api/ipersona/files_upload_external**

**Purpose**: Upload separate question and answer files for background processing.

**Requirements:**
- SHALL accept two file uploads (question_file, answer_file)
- SHALL queue `process_upload_external_files_task`
- SHALL use structured matching to pair questions with answers

---

**POST /api/ipersona/answer_file_upload_external**

**Purpose**: Upload answer file with template questions for background processing.

**Requirements:**
- SHALL accept answer file + template_id
- SHALL retrieve template questions from database
- SHALL queue `process_upload_external_answer_with_template_task`
- SHALL validate answer content contains actual answers (not questions)

---

**POST /api/ipersona/test_celery_event**

**Purpose**: Test Celery and Socket.IO integration.

---

### 4.5 Server-to-Client Socket.IO Events

**Event: `audio_realtime`** (REAL-TIME EVALUATION RESULTS)

**Payload:**
```json
{
  "transcript": "transcribed text",
  "evaluation": {
    "overall": {
      "relevance": "strong",
      "feedback": "Answer directly addresses the question"
    },
    "answer_relevancy": [
      {"level": "85", "reason": "..."}
    ]
  },
  "question_id": "string"
}
```

---

**Event: `realtime_status`** (STATUS UPDATES)

**Payload:**
```json
{
  "status": "evaluated|processing|error",
  "session_id": "uuid",
  "message": "optional status message"
}
```

---

**Event: `transcription_result`** (FINAL TRANSCRIPT)

**Payload:**
```json
{
  "text": "final transcript",
  "confidence": 0.95,
  "language": "en-US"
}
```

---

**Event: `transcription_interim`** (INTERIM TRANSCRIPT)

**Payload:**
```json
{
  "text": "partial transcript...",
  "is_final": false
}
```

---

**Event: `transcription_error`** (TRANSCRIPTION FAILURE)

**Payload:**
```json
{
  "error": "error message",
  "service": "google_cloud_stt",
  "fallback_attempted": true
}
```

---

**Event: `processing_update`** (CELERY TASK STATUS)

**Payload:**
```json
{
  "status": "processing|done|failed",
  "message": "status message",
  "progress": 50,  // 0-100
  "task_type": "audio_processing"
}
```

---

**Event: `processing_update_success`** (TASK COMPLETION)

**Payload:**
```json
{
  "status": "Task completed successfully",
  "result": {...}
}
```

---

**Event: `processing_update_failed`** (TASK FAILURE)

**Payload:**
```json
{
  "status": "Task failed",
  "error": "error message"
}
```

---

**Event: `error`** (GENERAL ERROR)

**Payload:**
```json
{
  "error": "error message",
  "details": "additional context"
}
```

---

**Event: `notification`** (SYSTEM NOTIFICATION)

**Payload:**
```json
{
  "type": "info|warning|error|success",
  "message": "notification message",
  "timestamp": "ISO 8601"
}
```

---

## 5. Data Models (Strapi CMS)

**Implementation File**: `/api/llm/ipersona/ipersona_strapi_schemas.py`
**Database**: Strapi CMS (GraphQL API)
**Base Class**: `LeapBaseClass` (provides GraphQL query/mutation helpers)

### 5.1 Core Data Models

#### 5.1.1 `ipersona-session` (IpersonaSessionSchema)

**Table Name**: `iPersonaSessions` (plural), `iPersonaSession` (singular)
**Schema Class**: `IpersonaSessionSchema`
**Purpose**: Stores interview session metadata and conversation history

**Strapi GraphQL Structure:**
```graphql
type IPersonaSession {
  id: ID!
  attributes: IPersonaSessionAttributes!
}

type IPersonaSessionAttributes {
  slug: String
  status: String
  attributes: JSON  # Contains session data
  metadata: JSON    # Contains upload_metadata
  createdAt: DateTime!
  updatedAt: DateTime
  
  # Relations
  i_persona_observer: IPersonaObserverRelation
  i_persona_messages: [IPersonaMessageRelation]
  tinder_job_profile: TinderJobProfileRelation
  tinder_user_profile: TinderUserProfileRelation
  tinder_template: TinderTemplateRelation
  challenge_document: ChallengeDocumentRelation
}
```

**`attributes` JSON Structure:**
```json
{
  "session_id": "uuid-string",
  "mode": "realtime|external_audio|qa_split|answer_only",
  "template": boolean,
  "external": boolean,
  "challenge": boolean,
  "all_user_id": "string",
  "tinder_user_profile_id": "integer",
  "tinder_job_profile_id": "integer|null",
  "challenge_document_id": "integer|null",
  "tinder_template_id": "integer|null",
  "message": [
    {
      "question": "string",
      "answer": "string",
      "realtime_evaluation": {
        "overall": {
          "relevance": "strong|medium|weak",
          "feedback": "string"
        },
        "answer_relevancy": [
          {
            "level": "0-100",
            "reason": "string"
          }
        ]
      },
      "timestamp": "ISO 8601 datetime"
    }
  ],
  "generated_questions": [],
  "template_questions": [],
  "challenge_questions": []
}
```

**`metadata` JSON Structure (upload_metadata):**
```json
{
  "mode": "combined_mode|qa_split_mode|answer_only_mode",
  "source": "uploaded_file",
  "content": {
    "url": "s3://bucket/path",
    "content_type": "audio/mpeg|video/mp4|application/pdf",
    "original_filename": "string",
    "duration_secs": "123.45 seconds",
    "size_bytes": 1234567
  },
  "question": {
    "url": "s3://...",
    "content_type": "...",
    "original_filename": "...",
    "duration_secs": "...",
    "size_bytes": 123456
  },
  "answer": {
    "url": "s3://...",
    "content_type": "...",
    "original_filename": "...",
    "duration_secs": "...",
    "size_bytes": 123456
  }
}
```

**GraphQL Mutations:**
```graphql
# Create Session
mutation CreateSession($data: IPersonaSessionInput!) {
  createIPersonaSession(data: $data) {
    data {
      id
      attributes {
        slug
        status
        attributes
        createdAt
      }
    }
  }
}

# Update Session
mutation UpdateSession($id: ID!, $data: IPersonaSessionInput!) {
  updateIPersonaSession(id: $id, data: $data) {
    data {
      id
      attributes {
        status
        attributes
        updatedAt
      }
    }
  }
}
```

**Schema Methods:**
```python
class IpersonaSessionSchema(LeapBaseClass):
    def exists_session_id(self, sessionId: str) -> bool:
        """Check if session exists"""
        
    def filter_by_observer_id(self, vid: str) -> dict:
        """Get session by observer ID"""
        
    def filter_by_tinder_user_profile_id(self, user_profile_id: int) -> list:
        """Get all sessions for a user profile"""
        
    def filter_by_with_user_job_id(self, user_profile_id: int, job_profile_id: int) -> list:
        """Get sessions for specific user+job combination"""
        
    def filter_by_with_user_template_id(self, user_profile_id: int, template_id: int) -> list:
        """Get sessions for specific user+template"""
        
    def filter_by_with_user_challenge_id(self, user_profile_id: int, challenge_id: int) -> list:
        """Get sessions for specific user+challenge"""
        
    def update_session(self, params: dict) -> dict:
        """Update session status and attributes"""
```

**Constraints:**
- MUST have exactly ONE of: `tinder_job_profile_id`, `tinder_template_id`, `challenge_document_id` (not null)
- `status` values: "pending", "active", "paused", "External", "Closed", "deleted", "failed"
- `status` MUST NOT transition from "Closed" to "active"
- `createdAt` is auto-managed by Strapi (immutable)
- Session with status "Closed" triggers overall evaluation

**Indexes** (Strapi auto-managed):
- Primary key on `id`
- Automatically indexed on relations (foreign keys)

---

#### 5.1.2 `ipersona-session-observer` (IpersonaSessionObserverSchema)

**Table Name**: `iPersonaSessionObservers`
**Purpose**: Stores detailed AI evaluation results for completed sessions

**GraphQL Structure:**
```graphql
type IPersonaSessionObserver {
  id: ID!
  attributes: IPersonaSessionObserverAttributes!
}

type IPersonaSessionObserverAttributes {
  status: String!
  attributes: JSON  # Contains evaluation data
  metadata: JSON
  createdAt: DateTime!
  
  # Relations
  i_persona_session: IPersonaSessionRelation!
}
```

**`attributes` JSON Structure (interview_evaluation):**
```json
{
  "interview_evaluation": {
    "evaluation": "comprehensive summary of candidate performance",
    "recommendation": [
      {
        "title": "Resources",
        "resource": "AWS Certified Solutions Architect course",
        "type": "Online Course",
        "link": "www.coursera.org"
      }
    ],
    "competency": [
      {
        "name": "Cloud Architecture",
        "sfia_level": "4"
      },
      {
        "name": "Python Programming",
        "sfia_level": "3"
      }
    ],
    "message": "Poor match"
  },
  "interview_evaluation_metrics": {
    "communication_skills": [
      {
        "skill": "clarity",
        "level": "good",
        "description": "Answers were clear and well-structured"
      },
      {
        "skill": "engagement",
        "level": "excellent",
        "description": "Showed enthusiasm and engagement"
      }
    ],
    "performance": [
      {
        "aspect": "Technical Knowledge",
        "level": "good",
        "feedback": "Demonstrated solid understanding"
      }
    ],
    "relevancy": [
      {"question_id": 1, "score": 85},
      {"question_id": 2, "score": 92}
    ],
    "overall_performance_score": 88.5,
    "rating": "4.5",
    "competency": [...],
    "message": "Good match"
  }
}
```

**Schema Methods:**
```python
class IpersonaSessionObserverSchema(LeapBaseClass):
    def save_observer(self, params: dict) -> dict:
        """Save evaluation observer for a session"""
        
    def filter_by_observer_session_id(self, sessionId: str) -> dict:
        """Get observer data by session ID"""
```

---

#### 5.1.3 `ipersona-session-overall-observer` (IpersonaSessionOverallObserverSchema)

**Table Name**: `iPersonaSessionOverallObservers`
**Purpose**: Aggregates evaluation metrics over multiple sessions for progress tracking

**GraphQL Structure:**
```graphql
type IPersonaSessionOverallObserver {
  id: ID!
  attributes: IPersonaSessionOverallObserverAttributes!
}

type IPersonaSessionOverallObserverAttributes {
  attributes: JSON  # Contains aggregated metrics
  createdAt: DateTime!
  updatedAt: DateTime
  
  # Relations
  tinder_user_profile: TinderUserProfileRelation!
  tinder_job_profile: TinderJobProfileRelation
  challenge_document: ChallengeDocumentRelation
  tinder_template: TinderTemplateRelation
  i_persona_observers: [IPersonaObserverRelation]
}
```

**`attributes` JSON Structure:**
```json
{
  "overall_confidence": [
    {"time": "2024-01-15 10:30", "level": "good", "value": 2},
    {"time": "2024-01-16 14:20", "level": "excellent", "value": 3}
  ],
  "overall_clarity": [
    {"time": "2024-01-15 10:30", "level": "good", "value": 2}
  ],
  "overall_engagement": [
    {"time": "2024-01-15 10:30", "level": "excellent", "value": 3}
  ],
  "overall_time_management": [],
  "overall_competency": [
    {
      "time": "2024-01-15 10:30",
      "competency": [
        {"name": "Python", "sfia_level": "3"},
        {"name": "AWS", "sfia_level": "4"}
      ]
    }
  ],
  "overall_performance": [
    {"time": "2024-01-15 10:30", "score": 85},
    {"time": "2024-01-16 14:20", "score": 90}
  ]
}
```

**Schema Methods:**
```python
class IpersonaSessionOverallObserverSchema(LeapBaseClass):
    def filter_by_with_user_and_job_id(self, user_profile_id: int, job_profile_id: int) -> dict:
        """Get overall progress for user+job"""
        
    def filter_by_with_user_and_challenge_id(self, user_profile_id: int, challenge_id: int) -> dict:
        """Get overall progress for user+challenge"""
        
    def filter_by_with_user_and_template_id(self, user_profile_id: int, template_id: int) -> dict:
        """Get overall progress for user+template"""
        
    def save_Session_Overall_Observer(self, params: dict) -> dict:
        """Create new overall observer record"""
        
    def update_session(self, params: dict) -> dict:
        """Update existing overall observer with new metrics"""
```

**Update Logic:**
- Appends new session metrics to existing arrays
- Maintains chronological order by timestamp
- Used for charting progress over time in frontend

---

#### 5.1.4 `tinder-user-profile` (IpersonaTraineeSchema)

**Table Name**: `tinderUserProfiles`
**Purpose**: Stores detailed user profile information for interview candidates

**GraphQL Structure:**
```graphql
type TinderUserProfile {
  id: ID!
  attributes: TinderUserProfileAttributes!
}

type TinderUserProfileAttributes {
  attributes: JSON  # Contains profile data
  all_users: AllUserRelation  # Link to ipersona-all-user
}
```

**`attributes` JSON Structure:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "experience": "5 years as Software Engineer",
  "skills": ["Python", "AWS", "Docker", "React"],
  "cv_url": "s3://bucket/cv/john_doe.pdf",
  "education": "BS Computer Science",
  "location": "San Francisco, CA"
}
```

**Schema Methods:**
```python
class IpersonaTraineeSchema(LeapBaseClass):
    def get_trainee_by_id(self, user_profile_id: int) -> dict:
        """Get trainee profile by ID"""
        
    def filter_by_alluser_id(self, all_user_id: str) -> dict:
        """Get trainee profile by all_user_id"""
        
    def save_trainee_user_profile(self, params: dict) -> dict:
        """Create new trainee profile"""
```

---

#### 5.1.5 `ipersona-all-user` (IpersonaAllUserSchema)

**Table Name**: `allUsers`
**Purpose**: Stores basic user account information

**GraphQL Structure:**
```graphql
type AllUser {
  id: ID!
  attributes: AllUserAttributes!
}

type AllUserAttributes {
  email: String!
  username: String!
  Batch: String  # Batch/cohort identifier
  createdAt: DateTime!
  updatedAt: DateTime
}
```

**Schema Methods:**
```python
class IpersonaAllUserSchema(LeapBaseClass):
    def get_alluser_by_id(self, all_user_id: str) -> dict:
        """Get user by all_user_id"""
```

**Usage in Notifications:**
- Used to retrieve `Batch` ID for notification targeting
- Links to `tinder-user-profile` for detailed profile data

---

#### 5.1.6 `tinder-template` (IpersonaTinderTemplateSchema)

**Table Name**: `tinderTemplates`
**Purpose**: Stores reusable interview question templates

**GraphQL Structure:**
```graphql
type TinderTemplate {
  id: ID!
  attributes: TinderTemplateAttributes!
}

type TinderTemplateAttributes {
  name: String!
  type: String
  tag: String
  description: String
  attributes: JSON  # Contains questions array
  metadata: JSON
  config: JSON
  tinder_job_profiles: [TinderJobProfileRelation]
  challenge_documents: [ChallengeDocumentRelation]
  i_persona_sessions: [IPersonaSessionRelation]
}
```

**`attributes` JSON Structure:**
```json
{
  "questions": [
    {
      "question": "Tell me about your experience with Python",
      "ideal_answer": "Candidate should mention specific projects, frameworks, years of experience",
      "sectionType": "Technical"
    },
    {
      "question": "Describe a challenging team situation",
      "ideal_answer": "Should demonstrate conflict resolution and communication skills",
      "sectionType": "Behavioral"
    }
  ]
}
```

**Schema Methods:**
```python
class IpersonaTinderTemplateSchema(LeapBaseClass):
    def save_session(self, params: dict) -> dict:
        """Create new template"""
        
    def get_template_by_id(self, template_id: int) -> dict:
        """Get single template"""
        
    def get_all_templates(self) -> list:
        """Get all available templates"""
        
    def filter_by_with_job_id(self, job_profile_id: int) -> list:
        """Get templates linked to a job"""
        
    def filter_by_with_challenge_id(self, challenge_id: int) -> list:
        """Get templates linked to a challenge"""
        
    def add_job_profiles_to_template(self, template_id: int, job_profile_ids: list) -> dict:
        """Link job profiles to template"""
```

**Template Types:**
- `type`: "interview" | "assessment" | "practice"
- `tag`: Category tags for filtering (e.g., "Software Engineering", "Data Science")

---

#### 5.1.7 `tinder-job-profile` (IpersonaJobSchema)

**Table Name**: `tinderJobProfiles`
**Purpose**: Stores job posting information for interview targeting

**GraphQL Structure:**
```graphql
type TinderJobProfile {
  id: ID!
  attributes: TinderJobProfileAttributes!
}

type TinderJobProfileAttributes {
  title: String!
  description: String
  attributes: JSON  # Job requirements, skills, etc.
  metadata: JSON
}
```

**`attributes` JSON Structure:**
```json
{
  "company": "TechCorp Inc.",
  "location": "Remote",
  "salary_range": "$120k - $180k",
  "required_skills": ["Python", "AWS", "Docker"],
  "preferred_skills": ["Kubernetes", "React"],
  "experience_level": "Senior (5+ years)",
  "job_type": "Full-time",
  "responsibilities": [
    "Design and implement scalable systems",
    "Mentor junior developers",
    "Collaborate with product team"
  ]
}
```

**Schema Methods:**
```python
class IpersonaJobSchema(LeapBaseClass):
    def filter_by_job_id(self, job_profile_id: int) -> dict:
        """Get job profile by ID"""
```

---

#### 5.1.8 `challenge-document` (IpersonaChallengeDocumentSchema)

**Table Name**: `challengeDocuments`
**Purpose**: Stores technical assessment challenges

**GraphQL Structure:**
```graphql
type ChallengeDocument {
  id: ID!
  attributes: ChallengeDocumentAttributes!
}

type ChallengeDocumentAttributes {
  Title: String!
  subtitle: String
  challenge_sections: [ChallengeSectionRelation]
  tinder_templates: [TinderTemplateRelation]
  createdAt: DateTime!
  updatedAt: DateTime
}
```

**Challenge Section Structure:**
```json
{
  "id": 1,
  "attributes": {
    "content": "Build a REST API that...",
    "difficulty": "Medium",
    "time_limit": "60 minutes",
    "evaluation_criteria": [
      "Code quality",
      "Test coverage",
      "API design"
    ]
  }
}
```

**Schema Methods:**
```python
class IpersonaChallengeDocumentSchema(LeapBaseClass):
    def get_challenge_by_id(self, challengeId: int) -> dict:
        """Get challenge by ID"""
        
    def get_all_challenges(self) -> list:
        """Get all available challenges"""
```

---

#### 5.1.9 `ipersona-session-message` (IpersonaSessionMessageSchema)

**Table Name**: `iPersonaSessionMessages`
**Purpose**: Stores individual messages within interview sessions (alternative to embedded messages in session)

**GraphQL Structure:**
```graphql
type IPersonaSessionMessage {
  id: ID!
  attributes: IPersonaSessionMessageAttributes!
}

type IPersonaSessionMessageAttributes {
  attributes: JSON  # Contains question, answer, evaluation
  i_persona_session: IPersonaSessionRelation!
  createdAt: DateTime!
}
```

**`attributes` JSON Structure:**
```json
{
  "question": "Tell me about yourself",
  "answer": "I am a software engineer with 5 years of experience...",
  "realtime_evaluation": {
    "overall": {
      "relevance": "strong",
      "feedback": "Direct and relevant answer"
    },
    "answer_relevancy": [
      {"level": "90", "reason": "Addressed question comprehensively"}
    ]
  },
  "timestamp": "2024-12-10T14:30:00Z"
}
```

**Schema Methods:**
```python
class IpersonaSessionMessageSchema(LeapBaseClass):
    def filter_by_session_id(self, sessionId: str) -> list:
        """Get all messages for a session"""
        
    def save_message(self, params: dict) -> dict:
        """Save new message to session"""
        
    def update_session_message(self, params: dict) -> dict:
        """Update existing message"""
```

---

#### 5.1.10 `notifications` (IpersonaNotificationSchema)

**Table Name**: `notifications`
**Purpose**: Stores system notifications for users

**GraphQL Structure:**
```graphql
type Notification {
  id: ID!
  attributes: NotificationAttributes!
}

type NotificationAttributes {
  sender: String!  # User ID of sender
  receiver: String!  # User ID of receiver
  Detail: JSON!  # Notification details
  BatchIDs: [String]  # Batch targeting
  origin: String!  # "leap" or other origin
  read: Boolean
  createdAt: DateTime!
}
```

**`Detail` JSON Structure:**
```json
{
  "topic": "external upload data processing status",
  "where": "",
  "notificationMessage": "Uploaded file analysis completed successfully!",
  "traineeLink": "#",
  "staffLink": "#"
}
```

**Schema Methods:**
```python
class IpersonaNotificationSchema(LeapBaseClass):
    def _create_notification(self, params: dict) -> dict:
        """Create new notification"""
```

**Used By:**
- `AudioUtils.save_notification()` for Celery task status notifications
- Success/failure notifications for file processing
- Real-time updates for background tasks

---

### 5.2 Data Model Relationships

**Key Relationships:**
1. `ipersona-session` → `tinder-user-profile` (many-to-one)
2. `ipersona-session` → `tinder-job-profile` OR `tinder-template` OR `challenge-document` (exclusive, many-to-one)
3. `ipersona-session` → `ipersona-session-observer` (one-to-one)
4. `ipersona-session-observer` → `ipersona-session-overall-observer` (many-to-one)
5. `tinder-user-profile` → `ipersona-all-user` (many-to-one)
6. `tinder-template` → `tinder-job-profile` (many-to-many)
7. `tinder-template` → `challenge-document` (many-to-many)

**Constraint:** A session MUST have exactly ONE of:
- `tinder_job_profile_id` (job interview)
- `tinder_template_id` (template-based interview)
- `challenge_document_id` (challenge assessment)

---

## 6. Business Rules

### 6.1 Interview Session Rules

**BR-001**: A user MAY have only one active session per job/challenge/template at a time
**BR-002**: A session SHALL timeout after 2 hours of inactivity
**BR-003**: A completed session SHALL NOT be reopened
**BR-004**: Evaluation SHALL only occur for sessions with at least 1 answered question

### 6.2 Transcription Service Selection

**BR-101**: Google Cloud STT SHALL be attempted first for all real-time transcription
**BR-102**: If Google Cloud STT fails, system SHALL fallback to Faster Whisper
**BR-103**: AssemblyAI SHALL be used for uploaded audio files only
**BR-104**: The system SHALL log which STT service was used for each transcription

### 6.3 Scoring Rules

**BR-201**: Relevance scores SHALL be integers from 0 to 100
**BR-202**: Overall performance score SHALL be the average of all question scores
**BR-203**: Competency levels SHALL be: poor (0-40), good (41-70), excellent (71-100)

---

## 7. Error Handling

### 7.1 Error Response Format

The system SHALL return errors in this format:

```json
{
  "error": "string (error message)",
  "error_code": "string (ERROR_CODE)",
  "details": "string (optional details)",
  "timestamp": "ISO 8601 timestamp",
  "request_id": "uuid"
}
```

### 7.2 Error Scenarios

**STT Service Failure:**
```gherkin
GIVEN Google Cloud STT is unavailable
WHEN transcription is requested
THEN the system SHALL fallback to Faster Whisper
AND SHALL log error with level: WARNING
AND SHALL continue processing
```

**Session Not Found:**
```gherkin
GIVEN a session_id that doesn't exist
WHEN an operation references that session
THEN the system SHALL return HTTP 404
AND SHALL return error_code "SESSION_NOT_FOUND"
```

**Invalid Audio Format:**
```gherkin
GIVEN an uploaded file is not valid audio
WHEN file is processed
THEN the system SHALL return HTTP 400
AND SHALL return error_code "INVALID_AUDIO_FORMAT"
AND SHALL specify supported formats in details
```

---

## 8. Acceptance Criteria Summary

### 8.1 Core User Journeys

**UC-001: Complete Real-Time Interview**
```gherkin
GIVEN a user has selected a job profile
WHEN they start an interview
THEN they SHALL:
  - Connect via Socket.IO successfully
  - Receive interview questions in sequence
  - Send audio responses
  - Receive real-time transcription
  - Receive real-time evaluation
  - Complete interview and see overall score
AND the entire flow SHALL complete without errors
AND responses SHALL be evaluated within 5 seconds each
```

**UC-002: Upload and Process Interview Recording**
```gherkin
GIVEN a user has a recorded interview audio file
WHEN they upload the file
THEN the system SHALL:
  - Accept the upload immediately
  - Return a task_id
  - Process file in background
  - Transcribe all audio
  - Evaluate all answers
  - Generate overall evaluation
  - Notify user when complete
AND SHALL complete within 5 minutes for 30-minute audio
```

---

## 9. Implementation Requirements

### 9.1 Technology Stack

The system SHALL be implemented using:

**Backend:**
- Python 3.12+
- FastAPI framework
- Socket.IO (python-socketio)
- Celery with Redis broker
- SQLAlchemy ORM (if using local database)

**Primary Services:**
- **Google Cloud Speech-to-Text** (PRIMARY STT)
- OpenAI GPT API (PRIMARY LLM)
- Strapi CMS (database/backend)
- AWS S3 (file storage)

**Alternative/Fallback Services:**
- Faster Whisper (local STT fallback)
- OpenAI Whisper API (cloud STT fallback)
- AssemblyAI (batch processing STT)

**Frontend:**
- React 18+ with TypeScript
- Vite build tool
- Socket.IO client
- Ant Design components

**Infrastructure:**
- Redis (caching, task queue)
- Docker (containerization)
- AWS infrastructure

### 9.2 Code Quality Requirements

The implementation SHALL:
- Follow PEP 8 style guide (Python)
- Achieve minimum 70% test coverage
- Use type hints throughout Python code
- Use TypeScript (no `any` types) for frontend
- Pass all linters (Ruff, MyPy, ESLint)
- Include docstrings for all public functions/classes

---

## 10. Validation & Testing

### 10.1 Test Requirements

The implementation SHALL include:

**Unit Tests:**
- All business logic functions
- All data transformation functions
- All validation functions
- Minimum 80% code coverage

**Integration Tests:**
- All API endpoints
- Database operations
- External service integrations (mocked)
- Socket.IO event handlers

**End-to-End Tests:**
- Complete interview flow (real-time)
- File upload and processing flow
- Template creation and usage
- Progress tracking calculations

### 10.2 Performance Testing

The system SHALL be tested for:
- Load testing (100 concurrent users)
- Stress testing (identify breaking point)
- Latency testing (verify response times)
- Throughput testing (requests per minute)

---

## Document Control

**Version**: 1.0  
**Created**: December 2024  
**Status**: NORMATIVE  
**Compliance**: RFC 2119

**Revision History:**
- v1.0 (2024-12): Initial specification

---

**END OF SPECIFICATION**

