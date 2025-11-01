---
mode: agent
language: python
framework: fastapi
compliance: RFC 2119
---

# Compile Specification to Implementation

## Instructions for AI Coding Agent

You are tasked with implementing the **Parrot AI Interview Platform** according to the [main.md specification](./main.md).

### Critical Requirements

1. **Compliance Level**:
   - Implement ALL requirements marked with MUST, REQUIRED, SHALL
   - Implement SHOULD/RECOMMENDED unless there's documented reason not to
   - Implement MAY/OPTIONAL based on priority and time

2. **RFC 2119 Compliance**:
   - Treat MUST/SHALL as absolute requirements
   - Treat MUST NOT/SHALL NOT as absolute prohibitions
   - Document any deviations from SHOULD requirements

3. **Acceptance Criteria**:
   - Every feature MUST pass its acceptance criteria
   - Implement tests based on GIVEN/WHEN/THEN scenarios
   - Verify all edge cases and error scenarios

### Implementation Order

**Phase 1: Core Infrastructure (Week 1-2)**
1. Project setup (FastAPI, Socket.IO, Celery)
2. Database models (implement Section 5)
3. Authentication & authorization
4. Health check endpoints

**Phase 2: STT Integration (Week 3)**
1. Google Cloud STT integration (PRIMARY - FR-003.1)
2. Faster Whisper fallback (FR-003.2)
3. Socket.IO event handlers for transcription
4. Error handling and fallback logic

**Phase 3: Real-Time Interview (Week 4-5)**
1. Socket.IO connection management (FR-001.1)
2. Real-time transcription flow (FR-001.2)
3. AI evaluation engine (FR-004)
4. Session management (FR-002)

**Phase 4: Background Processing (Week 6)**
1. Celery tasks for file uploads (FR-005.1)
2. Question-answer matching (FR-005.2)
3. Status updates via Redis and Socket.IO
4. S3 integration

**Phase 5: Templates & Analytics (Week 7-8)**
1. Template management (FR-006)
2. Progress tracking (FR-007)
3. Admin analytics endpoints
4. Frontend components

**Phase 6: Testing & Optimization (Week 9-10)**
1. Unit tests (80% coverage minimum)
2. Integration tests (all API endpoints)
3. Performance testing (meet NFR-001 targets)
4. Security audit

### Code Generation Guidelines

**1. API Endpoints**:
```python
# Example structure for STT endpoint (FR-003.1)

@app.post("/api/ipersona/stt/google-upload")
async def google_stt_upload(
    file: UploadFile = File(...),
    language: str = Form("en-US")
):
    """
    Transcribe audio using Google Cloud Speech-to-Text (PRIMARY STT).
    
    Requirements: FR-003.1
    Acceptance Criteria: See main.md section 2.3
    """
    # MUST validate file format and size
    if file.content_type not in ["audio/wav", "audio/mp3", "audio/webm"]:
        raise HTTPException(400, "INVALID_AUDIO_FORMAT")
    
    # MUST use Google Cloud STT
    try:
        transcript = await google_stt_service.transcribe(file, language)
        # MUST return within 10 seconds (NFR-001.1)
        return {
            "transcript": transcript.text,
            "confidence": transcript.confidence,
            "language": transcript.language
        }
    except GoogleSTTException as e:
        # SHALL fallback to Faster Whisper (FR-003.2)
        logger.warning(f"Google STT failed, falling back: {e}")
        transcript = await whisper_service.transcribe(file)
        return {"transcript": transcript.text, "confidence": transcript.confidence}
```

**2. Socket.IO Event Handlers**:
```python
# Example structure for real-time transcription (FR-001.2)

@sio.on("audio transcribe google")
async def audio_transcribe_google(sid, data):
    """
    PRIMARY real-time transcription using Google Cloud STT.
    
    Requirements: FR-001.2, FR-003.1
    Acceptance Criteria: See main.md section 2.1
    """
    # MUST validate session
    session_id = data.get("session_id")
    if not session_id or not await is_session_active(session_id):
        await sio.emit("transcription_error", 
                      {"error": "SESSION_NOT_FOUND"}, to=sid)
        return
    
    # MUST decode and transcribe within 2 seconds
    audio_data = base64.b64decode(data["audio"])
    try:
        result = await google_stt_stream(audio_data, data.get("language", "en-US"))
        # MUST emit result
        await sio.emit("transcription_result", {
            "session_id": session_id,
            "transcript": result.text,
            "confidence": result.confidence,
            "is_final": result.is_final
        }, to=sid)
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        await sio.emit("transcription_error", {"error": str(e)}, to=sid)
```

**3. Business Logic**:
```python
# Example evaluation logic (FR-004)

async def evaluate_answer(question: str, answer: str, context: dict) -> dict:
    """
    Evaluate interview answer using OpenAI GPT.
    
    Requirements: FR-004.1
    Must return structured evaluation within 3 seconds.
    """
    prompt = f"""
    Evaluate this interview answer:
    Question: {question}
    Answer: {answer}
    
    Return JSON with: relevance_score (0-100), communication_skills, 
    performance, overall_feedback, suggestions
    """
    
    # MUST complete within 3 seconds (FR-004.1)
    start_time = time.time()
    response = await openai_client.complete(prompt, timeout=3)
    elapsed = time.time() - start_time
    
    if elapsed > 3:
        logger.warning(f"Evaluation exceeded 3s target: {elapsed}s")
    
    # MUST return structured format
    evaluation = json.loads(response)
    assert "relevance_score" in evaluation
    assert 0 <= evaluation["relevance_score"] <= 100
    
    return evaluation
```

### Testing Requirements

**Every feature MUST include tests:**

```python
# Unit test example (FR-003.1)
@pytest.mark.asyncio
async def test_google_stt_transcription():
    """Test Google Cloud STT transcription (FR-003.1)"""
    # GIVEN valid audio file
    audio_file = load_test_audio("test_interview.mp3")
    
    # WHEN transcribed via Google Cloud STT
    result = await google_stt_service.transcribe(audio_file, "en-US")
    
    # THEN transcript should be returned
    assert result.text is not None
    assert len(result.text) > 0
    # AND confidence score should be provided
    assert 0 <= result.confidence <= 1
    # AND language should match
    assert result.language == "en-US"
    
@pytest.mark.asyncio
async def test_google_stt_fallback():
    """Test fallback when Google STT fails (FR-003.2)"""
    # GIVEN Google Cloud STT is unavailable
    with mock.patch("google_stt_service.transcribe", side_effect=Exception("Service down")):
        # WHEN transcription is requested
        result = await transcribe_with_fallback(audio_file)
        
        # THEN Faster Whisper should be used
        assert result.service_used == "faster_whisper"
        # AND transcript should still be provided
        assert result.text is not None
```

### Validation Checklist

Before marking any requirement as complete:

- [ ] All MUST/SHALL requirements implemented
- [ ] All acceptance criteria pass
- [ ] Error handling implemented
- [ ] Performance targets met (NFR-001)
- [ ] Tests written and passing (minimum 70% coverage)
- [ ] Security requirements met (NFR-003)
- [ ] Code follows style guidelines (PEP 8)
- [ ] Type hints included
- [ ] Docstrings added
- [ ] Logging implemented
- [ ] API documentation updated

### Compliance Verification

To verify compliance with the specification:

```bash
# Run all tests
pytest tests/ -v --cov=api --cov-report=html

# Verify performance targets
pytest tests/performance/ -v

# Check code quality
black . --check
isort . --check
ruff check .
mypy api/

# Verify API contracts
python scripts/validate_api_contracts.py
```

### Non-Compliance Reporting

If you cannot implement a MUST/SHALL requirement, you MUST document:

1. **Requirement ID**: (e.g., FR-003.1)
2. **Reason**: Why it cannot be implemented
3. **Impact**: What functionality is affected
4. **Alternative**: Proposed workaround or alternative
5. **Timeline**: When it can be implemented

Example:
```markdown
## Non-Compliance Report

**Requirement**: FR-003.1 - Google Cloud STT Integration
**Status**: NOT IMPLEMENTED
**Reason**: Google Cloud API keys not yet available
**Impact**: Real-time transcription not functional
**Alternative**: Using Faster Whisper for all transcription
**Timeline**: Can implement within 1 week of receiving API keys
```

### Success Criteria

Implementation is complete when:

1. ✅ All MUST/SHALL requirements implemented
2. ✅ All acceptance criteria pass
3. ✅ Test coverage ≥ 70%
4. ✅ All performance targets met
5. ✅ Security audit passed
6. ✅ API documentation complete
7. ✅ Deployment successful

---

**Remember**: This specification is NORMATIVE. Treat MUST/SHALL as non-negotiable. Implement according to RFC 2119 compliance levels.

**Good luck building Parrot!** 🦜🚀





