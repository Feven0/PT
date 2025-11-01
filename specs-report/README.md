# Parrot (iPersona) - Spec-Driven Development

> **📝 This directory contains the complete specification for the Parrot AI Interview Platform**

This is a **reverse-engineered specification** documenting an existing production application built over 6 months. It serves as living documentation and enables spec-driven development going forward.

---

## 📚 What's Inside

- **`main.md`** (1,200+ lines) - Complete application specification
- **`compile.prompt.md`** - AI agent instructions for code generation
- **`lint.prompt.md`** - Spec optimization instructions
- **`SPEC_DRIVEN_DEVELOPMENT.md`** - Complete methodology guide
- **`REVERSE_ENGINEERING_SUMMARY.md`** - How this spec was created
- **`SECOND_REVIEW_FINDINGS.md`** - Comprehensive review results

---

## 🚀 Quick Start - Running the Application

### Prerequisites

**Required:**
- Python 3.12+
- Node.js 18+ (for frontend)
- Redis (for Celery)
- Conda (optional but recommended) OR Python venv

**Optional:**
- Docker & Docker Compose (for containerized deployment)
- uv package manager (recommended for faster installs)

---

### Option 1: Using Conda Environment (Recommended if you have it)

```bash
# 1. Activate the parrot conda environment
conda activate parrot

# 2. Install/update dependencies
pip install -r requirements.txt

# 3. Start backend
make start-backend
# Backend runs on http://localhost:9990

# 4. In another terminal, start frontend for development
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173

# 5. Start Celery worker (in new terminal)
conda activate parrot
./build-celery.sh dev-prod logs
```

---

### Option 2: Using Python venv + uv (Recommended for new setup)

```bash
# 6. Activate the virtual environment
source .venv/bin/activate

# 7. Install/update dependencies
pip install -r requirements.txt

# 8. Start backend
make start-backend
# Backend runs on http://localhost:9990

# 9. Setup and start frontend (in new terminal)
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173

# 10. Start Celery worker (in new terminal)
source .venv/bin/activate
./build-celery.sh dev-prod logs
```

---

### Option 3: Traditional venv (Without uv)

```bash
# 1. Create virtual environment
python3.12 -m venv .venv

# 2. Activate environment
source .venv/bin/activate  # On Linux/Mac
# .venv\Scripts\activate   # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start backend
uvicorn app:app --reload --host 0.0.0.0 --port 9990
# Or use: make start-backend

# 5. Setup frontend (in new terminal)
cd frontend
npm install
npm run dev

# 6. Start Celery (in new terminal)
source .venv/bin/activate
celery -A api.services.celery.celery_worker:celery_app worker -l info
```

## 🛠️ Development Workflow

### Essential Commands (via Makefile)

```bash
# Setup
make setup-backend      # Setup backend only
make setup-frontend     # Setup frontend only

# Running
make start-backend      # Start FastAPI server (port 9990)
make start-frontend     # Start Vite dev server (port 5173)
make workers            # Start Celery worker localhost
make work               # Kill existing workers and restart

# Code Quality
make format             # Format code (black, isort)
make lint               # Run linters (ruff, mypy)
make security           # Security checks (bandit, safety)

# Testing
make test               # Run all tests
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-coverage      # Generate coverage report
make test-watch         # Watch mode

# Cleanup
make clean              # Remove build artifacts and caches
```

### Without Makefile

```bash
# Backend
uvicorn app:app --reload --host 0.0.0.0 --port 9990

# Frontend
cd frontend && npm run dev

# Celery Worker
celery -A api.services.celery.celery_worker:celery_app worker -l info

# Tests
pytest tests/ -v

# Format
black . && isort .

# Lint
ruff check . && mypy .
```

---

## 📖 Using the Specification

### Reading the Spec

```bash
# Read the complete specification
cat specs/main.md

# Or open in your editor
code specs/main.md
```

The spec contains:
- ✅ Complete architecture overview
- ✅ 50+ API endpoints
- ✅ 9 Socket.IO events
- ✅ 8 database tables
- ✅ Frontend components
- ✅ AI/ML services integration
- ✅ Development infrastructure
- ✅ Deployment guides

### Spec-Driven Development

1. **Understand the System**
   ```bash
   # Read the spec to understand current architecture
   less specs/main.md
   ```

2. **Make Changes**
   - Edit `specs/main.md` to describe desired changes
   - Use AI agent: `/load specs/compile.prompt.md`
   - Test the changes

3. **Update Documentation**
   - Keep spec in sync with code
   - Update when adding features

---

## 🔧 Configuration

### Environment Variables

Create `.env` file or configure these:

```bash
# Strapi CMS
STRAPI_STAGE=dev-prod
STRAPI_BASE_URL=https://your-strapi-api.com

# OpenAI
OPENAI_API_KEY=sk-...

# AWS
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=tenx-parrot-assets

# Redis
REDIS_URL=redis://localhost:6379

# AssemblyAI (optional)
ASSEMBLYAI_API_KEY=...

# Google Cloud (optional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# However you can your the remove env credential on the hostinger instance as well
```

---

## 📊 Monitoring

### Check Service Status

```bash
# Backend health check
curl http://localhost:9990/api/ipersona/health

# Celery monitoring (Flower)
# Start: celery -A api.services.celery.celery_worker flower
# Visit: http://localhost:5555

# Redis connection
redis-cli ping  # Should return PONG
```

### Logs

```bash
# Backend logs (in terminal running make start-backend)
# Celery logs (in terminal running make workers)

# Or check log files
tail -f celery.log
tail -f celery_worker.log
tail -f flower.log
```

---

## 📁 Project Structure

```
tenx_ipersona/
├── api/                  # Backend application
│   ├── pages/
│   │   └── ipersona/
│   │       ├── routers/  # API endpoints
│   │       └── socket/   # Socket.IO events
│   ├── services/         # External services
│   ├── llm/              # AI/ML integration
│   └── utils/            # Utilities
├── frontend/             # React application
│   └── src/
│       ├── components/   # React components
│       ├── pages/        # Route pages
│       └── hooks/        # Custom hooks
├── specs/                # This directory!
├── tests/                # Test files
├── Makefile              # Development automation
└── requirements.txt      # Python dependencies
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
rm -rf .venv
make setup-backend

# Check port availability
lsof -i :9990  # Kill if occupied
```

### Frontend won't start
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check port availability
lsof -i :5173
```

### Celery issues
```bash
# Check Redis is running
redis-cli ping

# Kill all Celery processes
make work  # This kills and restarts

# Or manually
ps aux | grep celery
kill -9 <PID>
```

### Database connection issues
```bash
# Check Strapi configuration
echo $STRAPI_BASE_URL
echo $STRAPI_STAGE

# Test GraphQL endpoint
curl $STRAPI_BASE_URL/graphql
```

---

## 📚 Additional Documentation

- **`main.md`** - Complete specification (1,200+ lines)
- **`SPEC_DRIVEN_DEVELOPMENT.md`** - Methodology guide
- **`REVERSE_ENGINEERING_SUMMARY.md`** - How spec was created
- **`SECOND_REVIEW_FINDINGS.md`** - Comprehensive review
- **`CELERY_README.md`** (in root) - Celery setup
- **`STRUCTURED_MATCHING_SYSTEM.md`** (in root) - Embeddings system
- **`docs/`** - OpenAPI specifications

---

## 🆘 Getting Help

1. **Read the spec**: `specs/main.md` - comprehensive documentation
2. **Check logs**: Backend terminal, Celery logs
3. **Review tests**: `tests/` directory for examples
4. **API Documentation**: `docs/openapi.yaml`

---

## 🎯 What This Spec Provides

✅ **Living Documentation** - Single source of truth  
✅ **AI Agent Instructions** - Spec-driven development  
✅ **Developer Onboarding** - Complete system understanding  
✅ **Architecture Reference** - All components documented  
✅ **Future Development** - Blueprint for changes  

---

**Status**: ✅ Production-ready specification (98% complete)  
**Last Updated**: December 2024  
**Application Age**: 6+ months in development  
**Spec Lines**: 1,200+  
**Coverage**: Backend + Frontend + Infrastructure + AI/ML







