# Lexora AI engineering decisions

* Why PostgreSQL (async SQLAlchemy)? Relational history (users/documents/conversations/messages) with pooling (`20+10`, pre-ping); SQLite only for tests/local checks.
* Why Redis? Two jobs: token blacklist (jti, TTL = token TTL) for logout/rotation, and 1h retrieval cache (user+query-hash+filter keys) to avoid re-embedding/re-searching.
* Why Celery + `inline|background` mode? `inline` for safe local dev without workers; `background` for production (`process_document_task`, 1h limit). Trade-off: dual paths must stay in sync.
* Why per-user FAISS? Strong isolation with zero ops; trade-off: rebuild on delete, local disk only, unsuitable for high-churn/multi-replica — Pinecone/Weaviate or deletion-friendly FAISS strategy is the documented next step.
* Why JWT+jti rotation? Stateless auth with revocation: logout blacklists access, refresh rotates and blacklists old.
* Why Prometheus + structlog + /ready? `http_requests_total`/`http_request_duration_seconds` + JSON logs + DB/Redis readiness give minimal prod visibility without APM.
* What was deferred: Alembic migrations, rate limiting, request IDs, idempotency, LLM retries, Sentry init, API-key routes, integration tests.
