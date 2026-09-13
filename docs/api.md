# Lexora AI API

Base: `/api/v1`. Global: `GET /`, `GET /health`, `GET /ready` (DB `SELECT 1` + Redis `ping` → 200/503), `GET /metrics`.

Auth (`app/api/v1/auth.py`): `POST /register → 201`, `POST /login` (OAuth2 form), `POST /refresh` (rotation, old refresh blacklisted), `POST /logout` (current access blacklisted), `GET /me`. Errors: `{"error":{code,message,details}}`.

Documents (`app/api/v1/documents.py`, auth required, `user_id` scoped): `POST "" → 201` (multipart `file`; validates extension/empty/size), `GET ""?skip&limit`, `GET /{id}`, `GET /{id}/status`, `DELETE /{id} → 204` (rebuilds FAISS without re-embedding when possible).

Chat (`app/api/v1/chat.py`, auth required): `POST /message`, `POST /stream` (`text/event-stream` SSE), `GET /conversations?skip&limit`, `POST /conversations`, `GET /conversations/{id}`, `DELETE /conversations/{id}`.

Not implemented: rate limiting (config only), request IDs, idempotency keys, API-key endpoints (table exists, no routes).
