# Local Setup — tenx-jobs (frontend) + iPersona (backend)

This repo contains two apps for the 10 Academy AI interviewer / jobs platform:

| Part | Path | Stack |
|------|------|-------|
| Frontend | `tenx_jobs_frontend/tenx-jobs-dev` | Vite + React + TypeScript |
| Backend ("frog" / iPersona) | `tenx_ipersonaa_backend/tenx_ipersona-main (1)/tenx_ipersona-main` | FastAPI (Python) |

The frontend talks to **two** backends, configured with env vars:
- `VITE_API_BACKEND_URL` → Strapi CMS (GraphQL + login)
- `VITE_API_LEAP_JOB_BACKEND_URL` → the iPersona FastAPI backend ("frog")

---

## Option A — Frontend only, against 10 Academy hosted DEV services (recommended)

Fastest path to a fully working app. No LLM keys, no AWS, no database needed — the
hosted dev backend already holds the API keys server-side.

```bash
cd "tenx_jobs_frontend/tenx-jobs-dev"
cp .env.example .env          # already points at the hosted dev services
npm install
npm run dev                   # http://localhost:5173
```

`.env` (dev):
```
VITE_API_BACKEND_URL='https://dev-cms.10academy.org'
VITE_API_LEAP_JOB_BACKEND_URL='https://dev-frog.10academy.org'
VITE_API_BACKEND_STAGE='dev'
```

Log in with your 10 Academy account. That's it.

Requirements: Node 18+ (tested on Node 22), npm.

---

## Option B — Run the backend locally too (advanced)

The backend is wired into 10 Academy's AWS infrastructure. At **import time** it reads
the OpenAI keys, and at runtime its data/AI endpoints need Strapi, Postgres, Weaviate,
Redis and the LLM provider keys.

Secret resolution order for each key (see `api/services/secret.py:get_auth`):
1. local file `/tmp/<name>.json`
2. environment variable
3. AWS Secrets Manager (secret `tenx/env/vars`)

### Minimal: just get the server to boot
```bash
cd "tenx_ipersonaa_backend/tenx_ipersona-main (1)/tenx_ipersona-main"
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r api/requirements.txt

export STRAPI_STAGE=dev
export PORT=4500
# JSON-encoded string; satisfies the import-time OpenAI key lookup and avoids AWS.
# Use a REAL OpenAI key here for the AI endpoints to actually work.
export openai_apikey='"sk-REPLACE_WITH_REAL_KEY"'

python app.py     # serves http://localhost:4500  (try GET /, /test, /docs)
```

### To make the AI / data endpoints actually work
You need the real provider keys and backing services:

- LLM keys (env vars): `OPENAI_API_KEY`, `GEMINI_API_KEY`, `TOGETHER_KEY`
  - the import-time lookup specifically uses `openai_apikey` (JSON string) as shown above
- AWS credentials (so it can read secret `tenx/env/vars`) **or** local overrides for:
  Strapi token, Postgres (`POSTGRES_*`), Weaviate (`WEAVIATE_URL` / `WEAVIATE_API_KEY`), Redis

Where to get LLM keys if you don't have AWS access:
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://aistudio.google.com/app/apikey
- Together AI: https://api.together.xyz/settings/api-keys

### Point the frontend at your local backend
In `tenx_jobs_frontend/tenx-jobs-dev/.env`:
```
VITE_API_LEAP_JOB_BACKEND_URL='http://localhost:4500'
```
(Keep `VITE_API_BACKEND_URL` on the hosted dev CMS unless you also run Strapi locally.)

### Backend exposed routes
`GET /`, `GET /test`, `POST /cv/upload`, `POST /cv/get_cv_analysis`

---

## Notes
- Backend `app.py` logs a harmless `TypeError: %d format` when `PORT` is set as a string;
  the server still starts fine. (Casting `port = int(os.environ.get("PORT", 5500))` removes it.)
- Docker paths exist (`docker-compose.yml`, `build.sh`) but target 10 Academy's deploy
  pipeline; the steps above are the simplest local route.
