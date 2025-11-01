# Parrot System Specification

> **📋 NORMATIVE REQUIREMENTS SPECIFICATION**

This directory contains the **authoritative technical requirements specification** for the Parrot AI Interview Platform, written as if building the system from scratch.

---

## 🎯 Purpose

This is a **TRUE SPECIFICATION** (not documentation):

- ✅ **Prescriptive** (defines what SHALL be built)
- ✅ **RFC 2119 Compliant** (uses MUST/SHALL/SHOULD/MAY)
- ✅ **Testable** (includes acceptance criteria)
- ✅ **Complete** (defines all requirements)
- ✅ **Normative** (authoritative source of truth)

**Use this to:**
- Build the system from scratch
- Validate implementation compliance
- Generate test cases
- Understand requirements (not implementation)

---

## 📁 Files

| File | Purpose | Status |
|------|---------|--------|
| **`main.md`** | Master requirements specification | NORMATIVE |
| **`compile.prompt.md`** | AI agent build instructions | NORMATIVE |
| **`README.md`** | This file | INFORMATIVE |

---

## 📖 Reading the Specification

### Understanding Requirement Levels (RFC 2119)

| Keyword | Meaning | Compliance |
|---------|---------|-----------|
| **MUST** / **SHALL** / **REQUIRED** | Absolute requirement | MANDATORY |
| **MUST NOT** / **SHALL NOT** | Absolute prohibition | MANDATORY |
| **SHOULD** / **RECOMMENDED** | Strong recommendation | Can deviate with reason |
| **SHOULD NOT** / **NOT RECOMMENDED** | Strong discouragement | Can deviate with reason |
| **MAY** / **OPTIONAL** | Truly optional | OPTIONAL |

**Example:**
```markdown
The system SHALL use Google Cloud STT as primary transcription service.
```
This means: **You MUST implement this. No exceptions.**

### Understanding Acceptance Criteria

Every feature has acceptance criteria in **Gherkin format**:

```gherkin
GIVEN [precondition]
WHEN [action]
THEN [expected result]
AND [additional expectations]
```

**These define how to test the feature.**

**Example:**
```gherkin
GIVEN a user sends audio via Socket.IO
WHEN the audio is processed
THEN the system SHALL return transcript within 2 seconds
AND SHALL include confidence score
```

---

## 🏗️ Building from This Spec

### Step 1: Read the Specification

```bash
# Read the complete spec
cat specs/main.md

# Or in your editor
code specs/main.md
```

### Step 2: Use AI Agent to Build

```bash
# In GitHub Copilot Chat or Cursor:
/load specs/compile.prompt.md

# The AI will build according to requirements in main.md
```

### Step 3: Validate Compliance

Check that your implementation meets:

1. ✅ All MUST/SHALL requirements implemented
2. ✅ All acceptance criteria pass
3. ✅ Performance targets met (Section 3.1)
4. ✅ Security requirements met (Section 3.3)
5. ✅ Error handling correct (Section 7)

### Step 4: Test

```bash
# Run tests
pytest tests/ -v --cov=api

# Verify acceptance criteria
pytest tests/acceptance/ -v

# Performance tests
pytest tests/performance/ -v
```

---

## 📐 Specification Structure

### Section 1: System Overview
- Purpose, scope, context
- High-level requirements

### Section 2: Functional Requirements (FR-xxx)
- What the system MUST do
- Organized by feature
- Each with acceptance criteria

**Example:**
- FR-001: Real-Time Interview
- FR-002: Session Management
- FR-003: Speech-to-Text Services

### Section 3: Non-Functional Requirements (NFR-xxx)
- Performance (NFR-001)
- Reliability (NFR-002)
- Security (NFR-003)
- Scalability (NFR-004)
- Maintainability (NFR-005)

### Section 4: API Contracts
- Exact endpoint specifications
- Request/response formats
- Socket.IO event contracts

### Section 5: Data Models
- Database schema requirements
- Field definitions
- Constraints and indexes

### Section 6: Business Rules
- Logic and validation rules
- Scoring algorithms
- Service selection logic

### Section 7: Error Handling
- Error response format
- Specific error scenarios
- Recovery procedures

### Section 8: Acceptance Criteria Summary
- Core user journeys
- End-to-end scenarios

### Section 9: Implementation Requirements
- Technology stack (MUST use)
- Code quality standards

### Section 10: Validation & Testing
- Test requirements
- Coverage targets

---

## 🔍 Key Requirements Highlights

### PRIMARY Services (MUST Use)

1. **Google Cloud Speech-to-Text** - Primary STT
2. **OpenAI GPT** - Primary LLM
3. **Strapi CMS** - Database backend
4. **FastAPI** - Backend framework
5. **Socket.IO** - Real-time communication
6. **Celery + Redis** - Background processing
7. **AWS S3** - File storage

### Performance Targets (MUST Meet)

| Operation | Target |
|-----------|--------|
| STT transcription | < 2s |
| AI evaluation | < 3s |
| API response | < 1s |
| Socket.IO connection | < 500ms |

### Test Coverage (MUST Achieve)

- Minimum 70% overall coverage
- 100% coverage for critical paths
- All acceptance criteria as test cases

---

## ✅ Compliance Checklist

Use this to verify your implementation:

### Functional Requirements
- [ ] FR-001: Real-time interview flow works
- [ ] FR-002: Session management complete
- [ ] FR-003: All STT services integrated (Google primary)
- [ ] FR-004: AI evaluation working
- [ ] FR-005: Background processing functional
- [ ] FR-006: Template management working
- [ ] FR-007: Progress tracking implemented

### Non-Functional Requirements
- [ ] NFR-001: All performance targets met
- [ ] NFR-002: 99.5% uptime capability
- [ ] NFR-003: Security requirements implemented
- [ ] NFR-004: Horizontally scalable
- [ ] NFR-005: Logging and monitoring in place

### API Contracts
- [ ] All Socket.IO events implemented
- [ ] All REST endpoints implemented
- [ ] Request/response formats match spec
- [ ] Error responses follow format

### Testing
- [ ] Unit tests ≥ 70% coverage
- [ ] Integration tests for all endpoints
- [ ] Acceptance criteria tests passing
- [ ] Performance tests passing

---

## 🚫 Common Mistakes to Avoid

### ❌ DON'T: Implement differently than specified

**Wrong:**
```python
# Spec says: SHALL use Google Cloud STT primary
# Implementation uses: AssemblyAI primary
```

**Right:**
```python
# Use Google Cloud STT as PRIMARY
result = await google_stt.transcribe(audio)
# Fallback to Faster Whisper if Google fails
```

### ❌ DON'T: Ignore acceptance criteria

**Wrong:**
```python
# Just implement transcription without checking:
# - Response time < 2s
# - Confidence score included
# - Error handling
```

**Right:**
```python
# Implement AND test all acceptance criteria
@pytest.mark.asyncio
async def test_transcription_meets_acceptance_criteria():
    # Test: Returns within 2s
    start = time.time()
    result = await transcribe(audio)
    assert time.time() - start < 2.0
    
    # Test: Includes confidence
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1
```

### ❌ DON'T: Skip SHOULD requirements without reason

**Wrong:**
```python
# Spec says: SHOULD provide interim results
# Just skip it
```

**Right:**
```python
# Implement SHOULD unless documented reason
# OR document why you can't:
"""
Non-Compliance: FR-003.1 interim results
Reason: Google Cloud streaming not yet supported in our plan
Alternative: Return final results only
Timeline: Will implement in Q2 2025
"""
```

---

## 📝 Difference from `specs-report/`

| Aspect | `specs/` (This folder) | `specs-report/` |
|--------|----------------------|-----------------|
| **Type** | Requirements Specification | Technical Documentation |
| **Tense** | SHALL/MUST (imperative) | IS/HAS (descriptive) |
| **Purpose** | Define what to build | Explain what exists |
| **Audience** | Builders, AI agents | Maintainers, learners |
| **Style** | Prescriptive | Descriptive |
| **When to use** | Building, modifying | Understanding, onboarding |

**Example:**

**`specs/main.md` (Prescriptive):**
```markdown
The system SHALL use Google Cloud Speech-to-Text as the primary 
transcription service with fallback to Faster Whisper.
```

**`specs-report/main.md` (Descriptive):**
```markdown
The system uses Google Cloud Speech-to-Text as the primary 
transcription service with fallback to Faster Whisper.
```

---

## 🎓 How to Use This Spec

### For New Developers

1. Read `main.md` to understand requirements
2. Don't read code first, read spec first
3. Build mental model from spec
4. Then look at implementation

### For AI Agents

```bash
# Load the compile prompt
/load specs/compile.prompt.md

# AI will build according to main.md
```

### For Code Review

1. Check if PR meets spec requirements
2. Verify acceptance criteria pass
3. Ensure no MUST/SHALL violations

### For Testing

1. Convert acceptance criteria to test cases
2. Verify all MUST/SHALL requirements have tests
3. Check test coverage meets targets

---

## 📊 Specification Metrics

| Metric | Count |
|--------|-------|
| Functional Requirements | 7 major sections |
| Non-Functional Requirements | 5 categories |
| API Endpoints Specified | 50+ |
| Socket.IO Events Specified | 9 |
| Acceptance Criteria | 50+ scenarios |
| Business Rules | 10+ rules |
| Data Models | 8 tables |

---

## 🔄 Keeping Spec Updated

When adding new features:

1. **Update spec FIRST** (in `specs/main.md`)
2. Add requirement with FR-xxx or NFR-xxx ID
3. Include acceptance criteria
4. Then implement feature
5. Verify acceptance criteria pass

When spec and code diverge:

1. **Spec is always right** (normative)
2. Update code to match spec
3. OR update spec with documented reason

---

## 🆘 Questions?

**"Is this requirement mandatory?"**
→ Check keyword: MUST/SHALL = yes, SHOULD = usually, MAY = no

**"How do I test this?"**
→ See acceptance criteria in GIVEN/WHEN/THEN format

**"Can I use a different approach?"**
→ Only if spec says SHOULD or MAY, not for MUST/SHALL

**"Spec doesn't cover X?"**
→ Add requirement to spec first, then implement

---

## 📚 Related Resources

- **Implementation Documentation**: See `specs-report/` folder
- **GitHub Blog Post**: [Spec-Driven Development](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-using-markdown-as-a-programming-language-when-building-with-ai/)
- **RFC 2119**: [Key words for use in RFCs](https://www.rfc-editor.org/rfc/rfc2119)
- **Gherkin**: [Behavior-Driven Development](https://cucumber.io/docs/gherkin/reference/)

---

**Status**: ✅ **NORMATIVE SPECIFICATION**  
**Version**: 1.0  
**Compliance**: RFC 2119  
**Last Updated**: December 2024

**This specification defines what MUST be built, not what HAS BEEN built.**





