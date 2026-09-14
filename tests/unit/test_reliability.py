"""Rate limiting + request IDs (unit-level, no DB/Redis)."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.core.rate_limit import is_allowed, rate_limit_middleware, reset


def test_fixed_window_blocks_over_limit():
    reset()
    key = "test-client"
    assert all(is_allowed(key, 3, now=1000.0 + i * 0.1) for i in range(3))
    assert is_allowed(key, 3, now=1000.5) is False
    # Next window passes.
    assert is_allowed(key, 3, now=1061.0) is True


def test_middleware_skips_non_api_paths():
    reset()
    app = FastAPI()

    @app.middleware("http")
    async def mw(request, call_next):
        return await rate_limit_middleware(request, call_next, 1)

    @app.get("/health")
    def health():
        return {"ok": True}

    client = TestClient(app)
    for _ in range(5):
        assert client.get("/health").status_code == 200


def test_middleware_429s_api_over_limit_with_retry_after():
    reset()
    app = FastAPI()

    @app.middleware("http")
    async def mw(request, call_next):
        return await rate_limit_middleware(request, call_next, 2)

    @app.get("/api/v1/things")
    def things():
        return JSONResponse({"ok": True})

    client = TestClient(app)
    assert client.get("/api/v1/things").status_code == 200
    assert client.get("/api/v1/things").status_code == 200
    r = client.get("/api/v1/things")
    assert r.status_code == 429
    assert r.headers.get("Retry-After") == "60"
    assert r.json()["error"]["code"] == "RateLimited"


def test_llm_generate_retries_transient_failures(monkeypatch):
    """LLM generate() retries twice then succeeds (tenacity wired)."""
    from app.services import llm_service as mod

    calls = {"n": 0}

    class FakeLLM:
        def invoke(self, messages):
            calls["n"] += 1
            if calls["n"] < 3:
                raise ConnectionError("transient 503")

            class R:
                content = "recovered"

            return R()

    # Bypass __init__ (would construct a real ChatOpenAI client); inject a fake.
    svc = mod.LLMService.__new__(mod.LLMService)
    svc.model_name = "test"
    svc.temperature = 0
    svc.max_tokens = 10
    svc.llm = FakeLLM()
    # Call the retry-wrapped function with the fake instance.
    result = mod.LLMService.generate(svc, "q?", "ctx")
    assert result == "recovered"
    assert calls["n"] == 3
