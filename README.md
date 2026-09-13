# Lexora

Upload documents, ask questions with source attribution.

## Problem

Small teams need grounded Q&A over their own PDFs/TXT/Markdown/DOCX without building retrieval, auth, and background processing from scratch.

## Solution

A FastAPI backend that validates uploads, extracts/chunks/embeds text, stores per-user vectors, and answers via retrieval + LLM with SSE streaming and conversation history.

## Architecture

```text
Client
  ↓
FastAPI (/api/v1: auth, documents, chat)
  ↓
PostgreSQL (users, documents, conversations, messages)
  ↓
Redis / Background Worker (retrieval cache, token blacklist, document jobs)
  ↓
Document Processing (validate → extract → chunk → embed → per-user FAISS)
  ↓
Retrieval (query embed → top-k → rank → context) → LLM (chat / stream)
```

## Key Engineering Decisions

1. PostgreSQL for relational history with async SQLAlchemy pooling; SQLite only for tests.
2. Redis for two jobs: 1h retrieval cache (user-scoped keys) and JWT jti blacklist for logout/rotation.
3. Dual-mode ingestion (`inline` local, `background` via Celery) — same `process_document` path.
4. Per-user FAISS isolation for simplicity; rebuild on delete (documented trade-off, pgvector is the next step).
5. Prometheus `/metrics` + structlog JSON + `/health` + `/ready` (DB + Redis checks).

## Tech Stack

Python · FastAPI · PostgreSQL · Redis · Celery · FAISS · OpenAI · Docker

## Features

1. JWT register/login/refresh/logout + `/me`
2. Validated upload (type/size) + list/status/delete with pagination
3. Chunk + embed pipeline with per-user vector isolation
4. Cached retrieval with source metadata
5. Chat + SSE streaming + conversation history
6. Health/ready/metrics endpoints
7. Docker Compose (Postgres, Redis, app, worker)

## Running Locally

```bash
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
docker compose -f docker/docker-compose.yml up -d postgres redis
cp .env.example .env  # set DATABASE_URL, REDIS_URL, SECRET_KEY, OPENAI_API_KEY
uvicorn app.main:app --reload  # docs: /docs, health: /health
```

## Testing

```bash
python -m pytest        # 31 unit tests, ~46% coverage, SQLite overrides, no real OpenAI calls
python -m pytest tests/unit -q
```

## Performance

No published latency/throughput benchmarks. Only measured: `31 passed`, `46%` coverage. See `docs/performance.md` for what to measure next.

## Limitations

No Alembic dir (uses `create_all`); `nginx.conf`/SSL missing; Celery target fixed to `app.tasks.celery_app`; rate limiting configured but not enforced; no request IDs/idempotency; LLM retries and Sentry not wired; APIKey table without routes. See `docs/` + README history.

## Future Improvements

Alembic from day one; enforce rate limits + request IDs; replace Celery with `BackgroundTasks` or justify queue; replace FAISS with pgvector; drop LangChain wrappers for direct OpenAI calls; remove unused deps (`sentry-sdk`, `tenacity`, `pymupdf`, `alembic` until real); add integration tests.
