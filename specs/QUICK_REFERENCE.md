# Quick Reference - Parrot Specification

> **One-page cheat sheet for the Parrot requirements specification**

---

## 🎯 RFC 2119 Keywords

| Keyword | Level | Can Skip? |
|---------|-------|-----------|
| **MUST** / **SHALL** | Mandatory | ❌ Never |
| **MUST NOT** / **SHALL NOT** | Prohibited | ❌ Never |
| **SHOULD** | Recommended | ⚠️ With reason |
| **SHOULD NOT** | Discouraged | ⚠️ With reason |
| **MAY** / **OPTIONAL** | Optional | ✅ Yes |

---

## 🔑 Core Requirements (MUST Implement)

### Primary Services
1. ✅ **Google Cloud STT** - Primary transcription (FR-003.1)
2. ✅ **OpenAI GPT** - AI evaluation (FR-004)
3. ✅ **FastAPI + Socket.IO** - Backend (FR-001)
4. ✅ **Celery + Redis** - Background processing (FR-005)
5. ✅ **Strapi CMS** - Database backend
6. ✅ **AWS S3** - File storage

### Fallback Services
- **Faster Whisper** - STT fallback if Google Cloud fails
- **OpenAI Whisper API** - Secondary cloud STT
- **AssemblyAI** - Batch processing for uploads

---

## ⚡ Performance Targets (NFR-001)

| Operation | Target | Max |
|-----------|--------|-----|
| Socket.IO connection | 500ms | 1s |
| Google Cloud STT | 2s | 5s |
| AI evaluation | 3s | 10s |
| API endpoint | 1s | 3s |
| File upload ACK | 1s | 2s |

**Throughput:**
- 100 concurrent sessions
- 1000 API requests/min
- 50 file uploads/min

---

## 🧪 Acceptance Criteria Format

```gherkin
GIVEN [initial state]
WHEN [action happens]
THEN [expected result]
AND [additional expectations]
```

**Every feature must have acceptance criteria!**

---

## 📊 Test Requirements

| Test Type | Requirement |
|-----------|-------------|
| Unit tests | ≥ 80% coverage |
| Integration tests | All API endpoints |
| E2E tests | Core user journeys |
| Performance tests | Meet NFR-001 targets |

---

## 🔌 Key API Contracts

### Socket.IO Events (Client → Server)

```javascript
// PRIMARY transcription
"audio transcribe google" {
  audio: "base64...",
  session_id: "uuid",
  language: "en-US"
}

// Real-time interview
"audio chat sentence" {
  audio: "base64...",
  session_id: "uuid",
  question_id: 123
}
```

### Socket.IO Events (Server → Client)

```javascript
// Evaluation results
"audio_realtime" {
  session_id: "uuid",
  transcript: "...",
  evaluation: {
    relevance_score: 85,
    communication_skills: [...],
    feedback: "..."
  }
}
```

### REST Endpoints (Critical)

```
POST /api/ipersona/stt/google-upload  # Google STT
POST /api/ipersona/close_session      # Complete interview
POST /api/ipersona/audio_upload_external  # Celery upload
```

---

## 🗄️ Database Requirements

### Critical Tables (8 total)

1. **ipersona-session** - Interview sessions
2. **ipersona-chat** - Q&A messages
3. **ipersona-session-observer** - Evaluations
4. **ipersona-trainee** - User profiles
5. **tinder-job-profile** - Job listings
6. **tinder-template** - Interview templates
7. **challenge-document** - Challenges
8. **ipersona-session-overall-observer** - Progress

---

## 🎯 Business Rules (BR-xxx)

**Session Rules:**
- BR-001: One active session per user+job at a time
- BR-002: Session timeout after 2 hours inactivity
- BR-003: Completed sessions cannot reopen

**Transcription Rules:**
- BR-101: Try Google Cloud STT first (always)
- BR-102: Fallback to Faster Whisper on failure
- BR-103: AssemblyAI for uploads only

**Scoring Rules:**
- BR-201: Relevance scores are 0-100 integers
- BR-202: Overall = average of all questions
- BR-203: Levels: poor (0-40), good (41-70), excellent (71-100)

---

## ❌ Error Response Format (MUST Follow)

```json
{
  "error": "Human-readable message",
  "error_code": "ERROR_CODE_CONSTANT",
  "details": "Optional details",
  "timestamp": "2024-12-01T10:30:00Z",
  "request_id": "uuid"
}
```

**Common Error Codes:**
- `SESSION_NOT_FOUND` (404)
- `INVALID_AUDIO_FORMAT` (400)
- `STT_SERVICE_UNAVAILABLE` (503)

---

## 🔒 Security (NFR-003)

**MUST implement:**
- ✅ Token-based authentication (all protected endpoints)
- ✅ TLS 1.2+ for all network communication
- ✅ Input sanitization (prevent injection)
- ✅ Secrets in AWS Secrets Manager
- ✅ Data encryption at rest (S3, database)

---

## 📈 Implementation Phases

| Phase | Duration | Focus |
|-------|----------|-------|
| 1 | Week 1-2 | Infrastructure setup |
| 2 | Week 3 | STT integration |
| 3 | Week 4-5 | Real-time interview |
| 4 | Week 6 | Background processing |
| 5 | Week 7-8 | Templates & analytics |
| 6 | Week 9-10 | Testing & optimization |

---

## ✅ Compliance Checklist

Before marking complete:

- [ ] All MUST/SHALL requirements implemented
- [ ] All acceptance criteria pass
- [ ] Test coverage ≥ 70%
- [ ] Performance targets met
- [ ] Security requirements met
- [ ] Error handling complete
- [ ] API documentation updated
- [ ] Code passes linters (Ruff, MyPy)

---

## 🚀 Quick Start

```bash
# 1. Read the spec
cat specs/main.md

# 2. Use AI agent
/load specs/compile.prompt.md

# 3. Validate
pytest tests/ --cov=api --cov-report=html

# 4. Check compliance
python scripts/validate_compliance.py
```

---

## 💡 Pro Tips

1. **Read acceptance criteria first** - They tell you how to test
2. **MUST/SHALL are non-negotiable** - Implement them all
3. **Test as you build** - Don't wait until the end
4. **Document deviations** - If you can't meet SHOULD, explain why
5. **Spec is source of truth** - When in doubt, check spec

---

## 🆘 When Things Go Wrong

**"I can't implement requirement X"**
→ Document non-compliance (see compile.prompt.md)

**"Spec is unclear"**
→ Ask for clarification, propose amendment

**"Implementation doesn't match spec"**
→ Fix code to match spec (spec is normative)

**"Performance target can't be met"**
→ Document and propose alternative target

---

## 📞 Need More Info?

- **Full Spec**: `specs/main.md` (10,000+ words)
- **Build Guide**: `specs/compile.prompt.md`
- **How-To**: `specs/README.md`
- **Existing System**: `specs-report/` folder

---

**Remember: This spec defines what SHALL be built, not what HAS been built!**

**Status**: ✅ NORMATIVE  
**Version**: 1.0  
**Compliance**: RFC 2119





