# Lexora AI security

* Auth: JWT HS256 via `python-jose`, `passlib/bcrypt` hashing, `OAuth2PasswordBearer(/api/v1/auth/login)`. Access 30m, refresh 7d, `jti` + Redis blacklist + refresh rotation.
* Boundaries: all documents/chat routes require current user; queries filtered by `user_id`; per-user FAISS isolation; retrieval cache keys user-scoped.
* Transport: CORS allowlist from `CORS_ORIGINS`; `SECRET_KEY` dev default must be overridden; token revocation needs Redis HA.
* Uploads: `pdf/txt/md/docx` allowlist, empty-file + 50MB cap, stored under `UPLOAD_DIR`.
* Gaps (do not claim otherwise): no rate-limit enforcement, no request IDs, no idempotency, `tenacity` unused (no LLM retries), Sentry DSN uninitialized, `APIKey` table without endpoints. See `SECURITY.md` for reporting.
