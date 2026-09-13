# Lexora AI deployment

See `DEPLOYMENT.md` (template, not applied) + `docker/docker-compose.yml` + `docker/Dockerfile`.

* Local: Python 3.11 venv, `pip install -r requirements.txt -r requirements-dev.txt`, `docker compose -f docker/docker-compose.yml up -d postgres redis`, `cp .env.example .env`, `uvicorn app.main:app --reload`.
* Compose services: `postgres:15-alpine`, `redis:7-alpine`, `app` (FastAPI), `celery-worker` (`celery -A app.tasks.celery_app worker`), `nginx` (requires `docker/nginx.conf` + `ssl/` — both absent, see README).
* Env: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY` (32+ chars, dev default must be overridden), `OPENAI_API_KEY`, `DOCUMENT_PROCESSING_MODE=inline|background`.
* Production notes: keep Redis HA (revocation depends on it), restrict `CORS_ORIGINS`, never commit `.env`, add rate limiting before public exposure.
