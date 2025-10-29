# Parrot (iPersona) - AI Interview Platform

> **AI-powered interview practice and evaluation platform with real-time feedback**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112+-green.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org)

---

## 🎯 What is Parrot?

Parrot is a comprehensive AI-driven interview platform that helps:
- **Job Seekers**: Practice interviews and get AI-powered feedback
- **HR Professionals**: Assess candidates efficiently  
- **Trainees**: Track progress and improve interview skills over time

### Key Features

✅ **Real-time AI Evaluation** - Instant feedback on answers  
✅ **Multiple STT Services** - AssemblyAI, Whisper, Google Cloud, Gemini  
✅ **Admin Analytics** - Comprehensive dashboards and reports  
✅ **Template Management** - AI-generated interview templates  
✅ **Progress Tracking** - Detailed metrics and visualizations  
✅ **Background Processing** - Celery-powered async tasks  

---

## 🚀 Quick Start

### Using Conda (Current Setup)

```bash
# 1. Activate environment
conda activate parrot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start backend
make start-backend
# Runs on http://localhost:9990

# 4. Start frontend (new terminal)
cd frontend && npm install && npm run dev
# Runs on http://localhost:5173

# 5. Start Celery worker (new terminal)
make workers
```

### Using venv + uv (Recommended for New Setup)

```bash
# 1. Setup backend
make setup-backend
source .venv/bin/activate

# 2. Start services
make start-backend        # Terminal 1
make setup-frontend       # One-time setup
make start-frontend       # Terminal 2
make workers              # Terminal 3
```

### Using Docker

```bash
docker-compose up --build
```

**📖 Full installation guide: [`specs/README.md`](specs/README.md)**

---

## 📚 Documentation

### Main Documentation

- **[`specs/main.md`](specs/main.md)** (1,200+ lines) - **Complete application specification**
  - Architecture overview
  - 50+ API endpoints
  - 9 Socket.IO events
  - 8 database tables
  - Frontend architecture
  - AI/ML services
  - Development guide

- **[`specs/README.md`](specs/README.md)** - **Installation & usage guide**

- **[`specs/SPEC_DRIVEN_DEVELOPMENT.md`](specs/SPEC_DRIVEN_DEVELOPMENT.md)** - Spec-driven methodology

- **[`CELERY_README.md`](CELERY_README.md)** - Celery setup guide

- **[`STRUCTURED_MATCHING_SYSTEM.md`](STRUCTURED_MATCHING_SYSTEM.md)** - Embeddings-based matching

### Architecture Highlights

**Backend:**
- FastAPI (Python 3.12)
- Celery + Redis (background tasks)
- Socket.IO (real-time communication)
- Strapi CMS (database via GraphQL)

**Frontend:**
- React 18 + TypeScript
- Vite build tool
- Ant Design components
- 30+ React components

**AI/ML:**
- OpenAI GPT (primary LLM)
- LiteLLM (multi-provider)
- 5 STT services
- Sentence Transformers (embeddings)
- AutoGen (AI agents)

---

## 🛠️ Development

### Essential Commands

```bash
# Setup
make setup              # Setup everything
make setup-backend      # Backend only
make setup-frontend     # Frontend only

# Run
make start-backend      # Start API server
make start-frontend     # Start Vite dev server
make workers            # Start Celery worker

# Quality
make format             # Format code
make lint               # Run linters
make security           # Security checks
make test               # Run tests
make test-coverage      # Coverage report

# Cleanup
make clean              # Remove artifacts
```

**See all commands:** `make help`

---

## 📁 Project Structure

```
tenx_ipersona/
├── api/                    # Backend (FastAPI)
│   ├── pages/ipersona/     # Routes & Socket.IO
│   ├── services/           # Celery, Strapi, etc.
│   ├── llm/                # AI/ML integration
│   └── utils/              # Utilities
├── frontend/               # React + TypeScript
│   └── src/
│       ├── components/     # UI components
│       ├── pages/          # Route pages
│       └── hooks/          # Custom hooks
├── specs/                  # 📖 COMPLETE SPECIFICATION
│   ├── main.md            # Full spec (1,200+ lines)
│   ├── README.md          # Installation guide
│   └── ...
├── tests/                  # Test files
├── docs/                   # OpenAPI specs
├── Makefile                # Dev automation
└── requirements.txt        # Python deps
```

---

## 🔧 Configuration

Create `.env` file with:

```bash
# Strapi CMS
STRAPI_STAGE=dev-prod
STRAPI_BASE_URL=https://your-strapi-api.com

# OpenAI
OPENAI_API_KEY=sk-...

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=tenx-parrot-assets

# Redis
REDIS_URL=redis://localhost:6379
```

---

## 🧪 Testing

```bash
# All tests
make test

# With coverage
make test-coverage
# View: coverage/index.html

# Specific test
pytest tests/test_s3_connectivity.py -v
```

**Test files:**
- `tests/test_s3_connectivity.py` - S3 integration
- `tests/test_speech_to_text.py` - STT services
- `tests/test_aws_connectivity.py` - AWS services
- And 8 more...

---

## 📊 API Endpoints

**50+ endpoints across 8 categories:**

- **STT**: 4 endpoints (Whisper, Gemini, OpenAI, Google)
- **Session Management**: 10 endpoints
- **Analytics**: 4 endpoints  
- **Admin**: 14 endpoints
- **Templates**: 6 endpoints
- **Challenges**: 2 endpoints
- **Audio Processing**: 4 endpoints (Celery)
- **Health**: 1 endpoint

**Full documentation:** [`specs/main.md`](specs/main.md)

---

## 🔄 Socket.IO Events

**Real-time communication with 9 events:**

**Client → Server:**
- `initial connect` - Session setup
- `audio transcribe whisper` - Whisper STT
- `audio transcribe google` - Google STT
- `audio chat sentence` - Real-time interview
- `interview chat` - Text chat
- And more...

**Server → Client:**
- `audio_realtime` - Evaluation results
- `task_status` - Background task updates
- `notification` - System notifications

---

## 🗄️ Database

**8 Strapi CMS tables:**
- `ipersona-session` - Interview sessions
- `ipersona-chat` - Messages
- `ipersona-session-observer` - Evaluations
- `ipersona-trainee` - User profiles
- `tinder-job-profile` - Job listings
- `tinder-template` - Interview templates
- `challenge-document` - Challenges
- `ipersona-session-overall-observer` - Progress tracking

---

## 🤖 AI/ML Services

- **OpenAI GPT** - Primary LLM for evaluations
- **LiteLLM** - Multi-provider LLM gateway
- **Instructor** - Structured outputs
- **AssemblyAI** - Professional STT
- **Faster Whisper** - Local STT
- **Google Cloud STT** - Enterprise STT
- **Google Gemini** - AI-powered STT
- **OpenAI Whisper API** - Cloud STT
- **Sentence Transformers** - Embeddings for matching
- **AutoGen** - AI agent framework

---

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:9990/api/ipersona/health
```

### Celery Dashboard (Flower)
```bash
celery -A api.services.celery.celery_worker flower
# Visit: http://localhost:5555
```

### Logs
```bash
tail -f celery.log
tail -f celery_worker.log
```

---

## 🐛 Troubleshooting

**Backend issues:**
```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
rm -rf .venv
make setup-backend
```

**Frontend issues:**
```bash
cd frontend
rm -rf node_modules
npm install
```

**Celery issues:**
```bash
# Check Redis
redis-cli ping

# Restart workers
make work
```

**Full troubleshooting guide:** [`specs/README.md#troubleshooting`](specs/README.md#-troubleshooting)

---

## 📖 Spec-Driven Development

This project uses **spec-driven development** - a methodology where:

1. Specifications are written in Markdown ([`specs/main.md`](specs/main.md))
2. AI agents compile specs into code
3. Specs serve as living documentation

**This spec was reverse-engineered from the existing production application.**

### Using the Spec

```bash
# Read complete specification
cat specs/main.md

# Use AI agent to make changes
# 1. Edit specs/main.md
# 2. Load specs/compile.prompt.md in AI agent
# 3. Test changes
```

**Learn more:** [`specs/SPEC_DRIVEN_DEVELOPMENT.md`](specs/SPEC_DRIVEN_DEVELOPMENT.md)

---

## 👥 For New Developers

1. **Read the spec**: [`specs/main.md`](specs/main.md) - Your onboarding guide
2. **Install & run**: Follow [`specs/README.md`](specs/README.md)
3. **Explore code**: Backend in `api/`, frontend in `frontend/`
4. **Run tests**: `make test`
5. **Make changes**: Update spec first, then code

---

## 🎯 Key Technologies

| Category | Technologies |
|----------|-------------|
| **Backend** | FastAPI, Python 3.12, Celery, Redis, Socket.IO |
| **Frontend** | React 18, TypeScript, Vite, Ant Design |
| **Database** | Strapi CMS (GraphQL API) |
| **AI/ML** | OpenAI GPT, LiteLLM, Sentence Transformers, AutoGen |
| **STT** | AssemblyAI, Whisper, Google Cloud, Gemini |
| **Storage** | AWS S3, AWS Secrets Manager |
| **DevOps** | Docker, Docker Compose, Makefile |
| **Testing** | Pytest, Coverage |
| **Quality** | Black, isort, Ruff, MyPy, Bandit |

---

## 📊 Project Stats

- **Lines of Code**: 100,000+ (estimated)
- **API Endpoints**: 50+
- **Socket.IO Events**: 9
- **Database Tables**: 8
- **React Components**: 30+
- **Test Files**: 11
- **Python Dependencies**: 137
- **Specification**: 1,200+ lines

---

## 📝 License

[Your License Here]

---

## 🤝 Contributing

1. Read [`specs/main.md`](specs/main.md) to understand architecture
2. Create feature branch
3. Update spec if adding features
4. Write tests
5. Run `make format lint test`
6. Submit PR

---

## 🆘 Support

- **Documentation**: [`specs/`](specs/)
- **API Docs**: [`docs/openapi.yaml`](docs/openapi.yaml)
- **Issues**: [GitHub Issues](#)

---

**Built with ❤️ for better interview preparation**

_Last Updated: December 2024_  
_Status: Production Ready_  
_Spec Coverage: 98%_

