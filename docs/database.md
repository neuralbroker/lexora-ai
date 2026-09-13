# Lexora AI database

Source: `app/schemas/database.py`, `app/config.py`.

* Engine: `postgresql+asyncpg` in production (`DATABASE_URL`), `pool_size=20, max_overflow=10, pool_pre_ping=True`; SQLite in-memory for tests via dependency override.
* Tables: `users`, `documents`, `conversations`, `messages`, `api_keys`. PKs `String(36)` UUIDs, FKs `ondelete=CASCADE`, `JSON` for `vector_ids/sources/metadata`.
* Init: `Base.metadata.create_all` at startup — no migrations at runtime. `alembic==1.13.1` is a dependency but `alembic/` is missing; `alembic upgrade head` cannot run (see README limitations).
* Vector data (not in SQL): per-user FAISS `IndexFlatL2` at `FAISS_INDEX_PATH/<user_id>/index.faiss + metadata.json` (embeddings stored alongside metadata to avoid re-embed on rebuild). FAISS rebuilds on deletion; high-churn should move to deletion-friendly vector DB.
* Cache (Redis): retrieval cache TTL 1h, keys include user/query-hash/filter to prevent leakage.
