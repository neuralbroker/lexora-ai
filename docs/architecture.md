# Lexora AI architecture

Source: `app/main.py`, `app/api/v1/`, `app/services/`, `app/tasks/`, `app/schemas/database.py`, `app/services/cache_service.py`.

```text
Client
  ↓
FastAPI (/api/v1/auth, /api/v1/documents, /api/v1/chat; global /health, /ready, /metrics)
  ↓
PostgreSQL via async SQLAlchemy (users, documents, conversations, messages, api_keys)
  ↓
Redis (token blacklist jti, retrieval cache 1h: retrieval:{user_id}:{query_hash}:{filter})
  ↓
Celery (celery_app broker redis/1 backend redis/2; process_document_task → DocumentService)
  ↓
Document processing (save → validate pdf/txt/md/docx ≤50MB → parse → chunk 1000/200 → embed → per-user FAISS)
  ↓
Retrieval (embed query → FAISS k*2 → dedup/rank k=4 → context) → LLM (LangChain ChatOpenAI, history last 5-10)
  ↓
Prometheus http_requests_total/http_request_duration_seconds + structlog JSON + health/ready
```

Auth: `OAuth2PasswordBearer`, access 30m / refresh 7d, bcrypt, jti revocation + rotation. Versioning: `/api/v1`. Pagination: `skip/limit` on documents/conversations. Upload validation: extension allowlist + empty + size. See `api.md`, `database.md`, `security.md`.
