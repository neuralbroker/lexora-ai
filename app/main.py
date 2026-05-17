"""Main FastAPI application."""

import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from sqlalchemy import text
from starlette.responses import Response

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.exceptions import LexoraException
from app.core.logging import configure_logging, get_logger
from app.schemas.database import init_db
from app.services.cache_service import cache_service

settings = get_settings()
configure_logging()
logger = get_logger(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("application_starting", version=settings.app_version)

    await init_db()

    try:
        await cache_service.connect()
    except Exception as e:
        logger.warning("cache_connection_failed_at_startup", error=str(e))

    logger.info("application_ready")

    yield

    try:
        await cache_service.disconnect()
    except Exception:
        pass
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise Knowledge Intelligence Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(LexoraException)
async def lexora_exception_handler(request: Request, exc: LexoraException):
    """Handle custom Lexora exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    """Middleware for Prometheus metrics."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    from app.schemas.database import engine
    from app.services.cache_service import cache_service

    checks = {"database": "disconnected", "cache": "disconnected"}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception:
        pass

    try:
        if cache_service.redis:
            await cache_service.redis.ping()
            checks["cache"] = "connected"
    except Exception:
        pass

    all_connected = all(v == "connected" for v in checks.values())

    return JSONResponse(
        status_code=200 if all_connected else 503,
        content={"status": "ready" if all_connected else "not_ready", **checks},
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain",
    )


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
