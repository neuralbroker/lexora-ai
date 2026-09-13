# Security Policy

## Supported Versions

Security fixes are provided for `main` only.

## Reporting a Vulnerability

Email `abdullasajad01@gmail.com` with: affected commit, reproduction steps, and impact. Do not open public issues for sensitive reports. Expect an initial response within 7 days.

## Scope notes (truthful)

* Auth: JWT + Redis revocation; production requires strong `SECRET_KEY`, trusted `CORS_ORIGINS`, and highly available Redis.
* Known gaps: rate limiting not enforced, no request IDs/idempotency, LLM retries and Sentry not wired, `APIKey` table without endpoints. Do not deploy publicly without addressing these (see `docs/security.md`).
* Never commit `.env` or OpenAI keys.
