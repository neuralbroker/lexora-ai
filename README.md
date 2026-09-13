# Lexora AI

**Asynchronous document processing and retrieval backend built with FastAPI, PostgreSQL, Redis and Celery.**

```text
Client
  ↓
FastAPI (/api/v1: auth, documents, chat) — JWT (jti) + Redis revocation
  ↓
PostgreSQL (async SQLAlchemy: users, documents, conversations, messages, api_keys)
  ↓
Redis (retrieval cache 1h, token blacklist) ──→ Celery workers (inline or background document processing)
  ↓
Document processing (validate → extract → chunk → embed → per-user FAISS)
  ↓
Retrieval (embed query → FAISS top-k → filter/rank → context) → LLM (chat / SSE stream)
  ↓
Prometheus /metrics + structlog JSON logs + /health + /ready (DB SELECT 1 + Redis ping)
```

Document Q&A with source attribution is the demo workload on top of this backend; the hiring signal is the API, data, queue, cache, auth, and observability engineering below.

## What the project does

1. A user registers and authenticates with JWT access and refresh tokens.
2. The user uploads a supported document.
3. The backend validates and stores the file, extracts text, splits it into chunks, embeds those chunks, and writes vectors plus metadata to FAISS.
4. The user asks a question through the chat API.
5. The retrieval layer embeds the query, searches the user's vector store, optionally filters by selected documents, and builds an LLM context.
6. The LLM service generates either a normal response or a Server-Sent Events streaming response.
7. Conversations, messages, documents, and users are persisted in the database.

## Tech stack

| Area | Technology |
| --- | --- |
| API | FastAPI, Uvicorn |
| Validation/config | Pydantic v2, pydantic-settings |
| Database | SQLAlchemy 2 async ORM, PostgreSQL in production, SQLite for tests/local checks |
| Auth | JWT via python-jose, password hashing via passlib/bcrypt |
| Vector search | FAISS |
| AI orchestration | LangChain, OpenAI chat and embedding models |
| Cache | Redis async client |
| Background jobs | Celery |
| Observability | Prometheus metrics, structlog JSON logging |
| Tests | pytest, pytest-asyncio, httpx ASGI transport |

## Main capabilities

- User registration, login, refresh token flow, and authenticated `/me` endpoint
- Document upload and validation for `pdf`, `txt`, `md`, and `docx`
- Text extraction and chunking utilities
- Per-user vector store isolation with FAISS persistence
- Retrieval-augmented chat with source metadata
- Streaming chat responses over SSE
- Conversation and message history
- Redis-backed retrieval cache
- Prometheus metrics endpoint at `/metrics`
- Health endpoint at `/health` and readiness endpoint at `/ready`
- Docker Compose stack for PostgreSQL, Redis, app, Celery worker, and Nginx

## Project structure

```text
lexoraai/
├── app/
│   ├── api/v1/              FastAPI route modules for auth, documents, and chat
│   ├── core/                Exceptions, logging, and security helpers
│   ├── models/              Pydantic request/response models
│   ├── schemas/             SQLAlchemy ORM models and DB session setup
│   ├── services/            Business logic for documents, chat, embeddings, vectors, cache, retrieval, and LLMs
│   ├── tasks/               Celery worker entry points
│   ├── utils/               Document parsing and text chunking utilities
│   ├── config.py            Environment-driven settings
│   ├── deps.py              FastAPI dependencies
│   └── main.py              Application factory and global routes
├── alembic/                 Database migration assets (PLANNED — directory not present; `init_db` uses `create_all`; see Known limitations)
├── docker/                  Dockerfile, Compose stack (see Known limitations for `nginx.conf`/Celery-target notes)
├── scripts/                 Operational helper scripts
├── tests/                   Unit and integration tests
├── requirements.txt         Runtime dependencies
├── requirements-dev.txt     Test/lint/dev dependencies
└── pyproject.toml           Tooling configuration
```

## Prerequisites

- Python 3.11 is recommended for the pinned dependency set.
- PostgreSQL 15+ for full application use.
- Redis 7+ for cache and Celery broker/result backend.
- OpenAI API key for real embedding and chat generation.
- Docker and Docker Compose if you want the packaged local stack.

> Note: the current pinned dependencies were validated in this workspace with the existing virtual environment, but a full reinstall under Python 3.13 may require dependency upgrades because packages such as `psycopg2-binary==2.9.9` may attempt a source build.

## Environment variables

Create a local `.env` file from the provided template and set at least these values:

| Variable | Purpose | Example |
| --- | --- | --- |
| `DATABASE_URL` | Async SQLAlchemy database URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/lexora` |
| `REDIS_URL` | Redis cache URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key, use a strong 32+ character secret | `change-this-to-a-real-secret-value` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings and chat | `sk-...` |
| `OPENAI_MODEL` | Chat model | `gpt-4-turbo-preview` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `OPENAI_EMBEDDING_DIMENSIONS` | Embedding vector dimension | `1536` |
| `UPLOAD_DIR` | Uploaded file storage path | `./uploads` |
| `FAISS_INDEX_PATH` | FAISS index storage path | `./data/faiss` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | `redis://localhost:6379/2` |
| `DOCUMENT_PROCESSING_MODE` | `inline` for local/dev processing or `background` for Celery-based processing | `inline` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000,http://localhost:8000` |

## Local setup

### 1. Create and activate a virtual environment

Linux/macOS:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 3. Start infrastructure

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
```

### 4. Configure `.env`

```bash
cp .env.example .env
```

Then edit `.env` with your database, Redis, secret, and OpenAI values.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- API root: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Readiness check: http://localhost:8000/ready
- Metrics: http://localhost:8000/metrics

## Docker Compose setup

To run the full containerized stack:

```bash
docker compose -f docker/docker-compose.yml up --build
```

The Compose stack includes:

- `postgres`: PostgreSQL database
- `redis`: Redis cache/broker
- `app`: FastAPI application
- `celery-worker`: Celery worker process
- `nginx`: reverse proxy

## API examples

Register a user:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","full_name":"Demo User"}'
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

Upload a document:

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@path/to/document.pdf"
```

List documents:

```bash
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Ask a non-streaming chat question:

```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is this document about?"}'
```

Ask a streaming chat question:

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Summarize the key points."}'
```

Create a conversation:

```bash
curl -X POST http://localhost:8000/api/v1/chat/conversations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Research notes"}'
```

## Testing

Run the test suite:

```bash
python -m pytest
```

In this workspace, the test suite currently passes:

- `31 passed`
- Coverage: `46%`

Important test notes:

- Tests use an in-memory SQLite database through dependency overrides.
- Tests set local environment variables in `tests/conftest.py`.
- Tests do not call the real OpenAI API.

## Runtime verification performed

The app was started successfully with a SQLite run-check database and test settings. Startup completed, the database initialized, Redis connected, and Uvicorn served the API on `127.0.0.1:8010` before the bounded run command was stopped.

A fresh screenshot of the running app health endpoint was captured from a headless Chromium browser:

![Lexora AI running health check](docs/assets/lexora-running-health.png)

To regenerate this screenshot locally, run:

```bash
venv/Scripts/python.exe scripts/capture_readme_screenshot.py
```

## Implementation notes and current optimizations

- Retrieval filtering happens inside the retrieval/vector-search path instead of filtering only source metadata after context construction. This avoids sending context from documents outside a requested document filter.
- Document processing can run inline for local development or be queued to Celery with `DOCUMENT_PROCESSING_MODE=background`.
- JWTs include `jti` identifiers, logout revokes the current access token in Redis until token expiry, and refresh-token rotation blacklists the used refresh token.
- Database and token timestamps use timezone-aware UTC values instead of deprecated `datetime.utcnow()` calls.
- Chat history is now passed to the LLM as real user/assistant turns instead of user-only messages with blank assistant responses.
- FAISS metadata stores embeddings alongside chunk metadata so index rebuilds after deletion avoid unnecessary re-embedding when possible.
- A module-level `get_file_type()` wrapper exists for compatibility with the test suite and public utility-style imports.
- Test settings cache clearing uses `get_settings.cache_clear()`, which is the actual cached settings function.
- FAISS indexes are isolated per user under `FAISS_INDEX_PATH/<user_id>/`.
- Redis retrieval cache keys include user ID, query hash, and document filter to prevent cross-user or cross-filter leakage.

## Known limitations and next improvements

- FAISS still rebuilds the user index on deletion. Stored embeddings reduce rebuild cost, but high-churn production deployments should still consider a deletion-friendly vector database or FAISS strategy.
- Document processing defaults to `inline` for safer local development. Set `DOCUMENT_PROCESSING_MODE=background` in production when the Celery worker is running.
- Test coverage is improved for chat-history behavior, but document ingestion, retrieval, vector storage, cache, and full chat orchestration should still receive more unit/integration tests.
- `SECRET_KEY` defaults are development-only and must be overridden in production.
- Rate limiting is configured (`rate_limit_per_minute`) but not enforced — there is no rate-limit middleware yet. Do not expose publicly without adding it.
- No request IDs / correlation IDs, no idempotency keys, no LLM/embedding timeouts-retries (`tenacity` is a dependency but unused), Sentry DSN is configured but never initialized.
- `alembic` is a dependency but the `alembic/` directory is missing, so `alembic upgrade head` (referenced in `DEPLOYMENT.md`) cannot run; runtime uses `Base.metadata.create_all`.
- `docker/docker-compose.yml` references `docker/nginx.conf` (+ `ssl`) and Celery target `app.tasks.worker`, but `nginx.conf` is absent and the app object lives in `app.tasks.celery_app` — fix both before `compose up --build` of the full stack.
- `APIKey` table + schemas exist but there are no API-key endpoints yet.
- `.gitignore` ignores `*.json` broadly, which would also ignore FAISS `metadata.json` — narrow it before persisting indexes in-repo.
- No CI yet — see `.github/workflows/ci.yml` (added): lint + unit tests + Docker build check. Integration tests (`tests/integration/` is empty) still to be written.

## Security considerations

- Never commit real `.env` secrets or OpenAI API keys.
- Use a strong production `SECRET_KEY`.
- Restrict `CORS_ORIGINS` to trusted frontend origins.
- Token revocation uses Redis, so production deployments should keep Redis highly available.
- Add rate limiting enforcement before public deployment.

## License

MIT License
