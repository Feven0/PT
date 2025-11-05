# Parrot (iPersona) Constitution

## Core Principles

### I. Real-Time Performance (NON-NEGOTIABLE)

The system MUST deliver sub-second response times for real-time interview interactions. All user-facing operations SHALL meet strict performance targets:
- Socket.IO connections MUST establish within 500ms
- Speech-to-text transcription MUST complete within 2 seconds
- AI evaluation responses MUST be delivered within 3 seconds
- API endpoints MUST respond within 1 second

**Rationale**: Interview practice requires immediate feedback to simulate real-world conditions. Any delay breaks immersion and reduces learning effectiveness.

### II. Primary Service Reliability

The system MUST use Google Cloud Speech-to-Text as the primary STT service. All real-time interview transcription SHALL route through Google Cloud STT first. Fallback services SHALL only activate when primary service fails.

**Rationale**: Consistency in transcription quality is critical for accurate AI evaluation. Users expect reliable real-time transcription during interviews.

### III. AI-Powered Evaluation

The system MUST use OpenAI GPT as the primary LLM for interview evaluation. All answer assessments, question generation, and feedback generation SHALL leverage OpenAI GPT models.

**Rationale**: OpenAI GPT provides the most accurate and nuanced evaluation of interview responses, enabling meaningful feedback that helps users improve.

### IV. Real-Time Communication Architecture

The system MUST use Socket.IO for all real-time bidirectional communication. WebSocket connections SHALL handle:
- Audio streaming for transcription
- Real-time evaluation results
- Session state synchronization
- Background task notifications

**Rationale**: HTTP polling introduces unacceptable latency for real-time interview interactions. WebSocket connections provide instant bidirectional communication.

### V. Background Processing for Heavy Operations

The system MUST use Celery with Redis for asynchronous task processing. All operations that exceed 5 seconds SHALL be offloaded to background workers:
- Large audio file processing
- Batch transcriptions
- Complex analytics calculations
- Report generation

**Rationale**: Keeping the main API responsive requires non-blocking operations. Users must receive immediate acknowledgment while heavy processing occurs asynchronously.

### VI. Data Persistence via Strapi CMS

The system MUST use Strapi CMS (accessed via GraphQL) as the primary data persistence layer. All domain entities SHALL be stored in Strapi:
- Interview sessions
- User profiles
- Job profiles
- Interview templates
- Evaluation results
- Chat messages

**Rationale**: Strapi provides flexible content management, GraphQL API, and built-in authentication that aligns with the platform's needs.

### VII. Security-First Authentication

The system MUST implement token-based authentication for all protected endpoints. All API requests SHALL include Bearer tokens validated against Strapi user authentication.

**Rationale**: Protecting user data and ensuring only authorized access to interview sessions and personal information is non-negotiable.

### VIII. Error Handling and Resilience

The system MUST gracefully handle service failures. All external service integrations (STT, LLM, Storage) SHALL implement:
- Automatic fallback to alternative services
- Clear error messages to users
- Retry logic with exponential backoff
- Circuit breaker patterns for degraded services

**Rationale**: Users expect uninterrupted service even when external dependencies fail. Graceful degradation ensures reliability.

### IX. Testability and Quality Assurance

The system MUST maintain test coverage ≥ 70% overall, with ≥ 80% coverage for critical paths. All features SHALL include:
- Unit tests for business logic
- Integration tests for API endpoints
- End-to-end tests for core user journeys
- Performance tests validating NFR-001 targets

**Rationale**: Testability ensures reliability, prevents regressions, and enables confident refactoring.

### X. Specification-Driven Development

The system MUST be built from prescriptive specifications. All features SHALL:
- Be defined in user stories with acceptance criteria
- Include measurable success criteria
- Follow RFC 2119 keyword standards (MUST/SHALL/SHOULD/MAY)
- Have traceable requirements

**Rationale**: Clear specifications ensure alignment between stakeholders, reduce ambiguity, and guide implementation decisions.

## Technology Stack Constraints

### Backend Requirements

- **Framework**: FastAPI (Python 3.12+)
- **Real-Time**: Socket.IO (python-socketio)
- **Background Jobs**: Celery with Redis broker
- **Database**: Strapi CMS (GraphQL API)
- **Storage**: AWS S3 for audio files and assets
- **Secrets**: AWS Secrets Manager

### AI/ML Services

- **Primary LLM**: OpenAI GPT (gpt-4o-mini or gpt-4o)
- **Primary STT**: Google Cloud Speech-to-Text
- **Fallback STT**: Faster Whisper (local), AssemblyAI (batch), OpenAI Whisper API, Google Gemini

## Development Workflow

### Code Quality Standards

- **Formatting**: Black for Python
- **Linting**: Ruff and MyPy for Python
- **Security**: Bandit for Python security scanning
- **Type Safety**: Pydantic models for Python with strict type hints

### Version Control

- Feature branches MUST be created for all changes
- Pull requests MUST include:
  - Description of changes
  - Test coverage evidence
  - Updated specifications if requirements change
- Commit messages SHALL follow Conventional Commits format

### Deployment

- All deployments MUST be tested in staging environment first
- Database migrations MUST be backward compatible
- Rollback procedures MUST be documented and tested
- Monitoring and alerting MUST be configured for production

## Performance Standards

### Non-Functional Requirements (NFR-001)

The system MUST support:
- **Concurrent Sessions**: 100 simultaneous interview sessions
- **API Throughput**: 1000 requests per minute
- **File Uploads**: 50 uploads per minute
- **Database Queries**: < 100ms average response time
- **Uptime**: 99.5% availability target

## Governance

This constitution supersedes all other practices and decisions. Amendments require:
1. Documentation of rationale for change
2. Impact analysis on existing implementations
3. Update to related specifications and plans
4. Version bump following semantic versioning

All pull requests and code reviews MUST verify compliance with these principles. Complexity MUST be justified; simplicity is preferred.

**Version**: 1.0.0 | **Ratified**: 2024-12-01 | **Last Amended**: 2024-12-01
