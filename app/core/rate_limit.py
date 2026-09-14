"""Fixed-window rate limiting for /api/v1.

Single-replica in-memory buckets (client IP + path prefix). This intentionally
trades multi-replica exactness for zero new dependencies — Redis-backed sliding
windows are the documented next step when the app runs behind >1 replica.

429 responses include Retry-After so well-behaved clients back off.
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse

_buckets: dict[str, list[float]] = defaultdict(list)


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def is_allowed(key: str, limit_per_minute: int, now: float | None = None) -> bool:
    now = time.time() if now is None else now
    window_start = now - 60.0
    hits = [t for t in _buckets[key] if t > window_start]
    if len(hits) >= limit_per_minute:
        _buckets[key] = hits
        return False
    hits.append(now)
    _buckets[key] = hits
    return True


def reset() -> None:
    """Test hook: clear all buckets."""
    _buckets.clear()


async def rate_limit_middleware(request: Request, call_next, limit_per_minute: int):
    """Apply only to /api/v1 (health/ready/metrics/docs stay unlimited)."""
    if not request.url.path.startswith("/api/v1"):
        return await call_next(request)
    key = f"{_client_key(request)}"
    if not is_allowed(key, limit_per_minute):
        return JSONResponse(
            status_code=429,
            content={"error": {"code": "RateLimited", "message": "Rate limit exceeded"}},
            headers={"Retry-After": "60"},
        )
    return await call_next(request)
