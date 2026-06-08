---
name: testing-pt-app
description: Run and test the PT app locally (tenx-jobs React frontend + iPersona FastAPI backend). Use when verifying local setup, login/CMS connectivity, or the AI interviewer flow.
---

# Testing the PT app (tenx-jobs frontend + iPersona backend)

Two-part app: a Vite/React frontend (`tenx_jobs_frontend/tenx-jobs-dev`) and a FastAPI
"iPersona" backend (`tenx_ipersonaa_backend/.../tenx_ipersona-main`). The frontend talks to a
Strapi CMS (login, GraphQL) and an iPersona "frog" backend (AI logic).

## Fastest way to test (no keys needed)

The frontend can run against 10 Academy's **hosted dev services**, which hold the LLM keys
server-side. This lets you verify the app boots and connectivity works without AWS or any LLM keys.

```bash
cd tenx_jobs_frontend/tenx-jobs-dev
cp .env.example .env   # pre-filled with hosted dev URLs
npm install
npm run dev            # serves http://localhost:5173
```

`.env` should contain:
```
VITE_API_BACKEND_URL='https://dev-cms.10academy.org'
VITE_API_LEAP_JOB_BACKEND_URL='https://dev-frog.10academy.org'
VITE_API_BACKEND_STAGE='dev'
```

## Golden-path tests

1. **App loads / routing**: open `http://localhost:5173/` → should redirect to `/login` and
   render the 10 Academy logo, "You're back!" heading, Email + Password fields, orange Login
   button. Browser console should be clean.

2. **Connectivity (adversarial invalid login)**: enter any invalid email + password and click
   Login. Expect the inline error **"Invalid identifier or password"** (the Strapi CMS's own
   message). This proves the `.env` → hosted CMS wiring works.
   - The login POSTs to `${VITE_API_BACKEND_URL}/api/auth/local/` (see `src/pages/Auth/Login.tsx`).
   - If `.env` were wrong/missing, you'd instead get a generic antd "Server error." toast with
     NO inline message — so the inline CMS message is the meaningful signal.
   - Confirm the request target via console:
     `performance.getEntriesByType('resource').filter(r=>r.name.includes('auth/local')).map(r=>r.name)`
     → should return `https://dev-cms.10academy.org/api/auth/local/`.

3. **Authenticated / AI interviewer flow**: requires REAL 10 Academy credentials. Without them
   this is UNTESTED. On success the app stores a JWT and routes to `/trainee` or `/team`.

## Backend (Option B, advanced)

The backend imports `api/config.py` at startup, which fetches OpenAI keys from AWS Secrets
Manager and fails with `NoCredentialsError` if AWS isn't configured. Bypass for local boot by
setting a JSON-encoded placeholder env var BEFORE starting:

```bash
export openai_apikey='"sk-placeholder"'   # note: value is a JSON string (quoted)
python app.py                              # serves on PORT (default 5500; docs used 4500)
```

- `get_auth()` checks file → env var → AWS, so the env var prevents the AWS lookup.
- Cosmetic startup error: `port = os.environ.get("PORT", 5500)` is a string and uvicorn logs it
  with `%d`, raising a `TypeError` in the log line only — the server still starts. Casting to
  `int(...)` removes it.
- Smoke test: `GET /`, `/test`, `/docs` should return 200.
- Full AI endpoints (`/cv/...`) need real LLM keys + AWS/Strapi/Postgres/Weaviate/Redis.

## Devin Secrets Needed

- None required for the frontend connectivity tests (uses hosted dev services).
- For the authenticated/AI flow: real 10 Academy login credentials (not stored as a secret yet).
- For full backend Option B: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `TOGETHER_KEY` + AWS access
  (these live in AWS Secrets Manager under `tenx/env/vars`).
