"""Deterministic retrieval-quality probe (no API keys, no network).

Measures what can be measured without an LLM: does chunking keep answers
findable by keyword recall? For each (document, question, must_contain) case,
chunk the document, score chunks by keyword overlap with the question, and
check whether a top-k chunk contains the expected answer span.

Usage:
    python scripts/eval_retrieval.py
    python scripts/eval_retrieval.py --top-k 3

This is a floor, not a ceiling: real evals need embedding recall +
faithfulness judgments. But a pipeline that fails keyword recall will fail
semantic recall too — fix chunking first (it's free).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.utils.text_chunker import TextChunker  # noqa: E402

CASES = [
    {
        "name": "refund_policy",
        "document": (
            "Our refund policy allows returns within 30 days of purchase. "
            "To request a refund, contact support@example.com with your order ID. "
            "Refunds are processed within 5 business days to the original payment method. "
            "Shipping costs are non-refundable except for damaged items. " * 4
        ),
        "question": "How do I request a refund?",
        "must_contain": "support@example.com",
    },
    {
        "name": "rate_limits",
        "document": (
            "The API enforces a rate limit of 60 requests per minute per API key. "
            "Exceeding the limit returns HTTP 429 with a Retry-After header. "
            "Enterprise plans raise the limit to 10000 requests per minute. "
            "Rate limit state resets on a fixed 60-second window. " * 4
        ),
        "question": "What happens when I exceed the rate limit?",
        "must_contain": "429",
    },
    {
        "name": "postgres_setup",
        "document": (
            "Connect to PostgreSQL with postgresql+asyncpg://user:pass@localhost/db. "
            "Run migrations with alembic upgrade head before starting the server. "
            "The connection pool defaults to 20 with max overflow 10. "
            "Health is checked with SELECT 1 on startup and readiness probes. " * 4
        ),
        "question": "How do I run database migrations?",
        "must_contain": "alembic upgrade head",
    },
]


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower())) - {
        "the",
        "a",
        "an",
        "to",
        "of",
        "in",
        "on",
        "is",
        "it",
        "how",
        "do",
        "i",
        "what",
        "when",
        "with",
        "for",
    }


def score_chunk(question: str, chunk: str) -> int:
    return len(_tokens(question) & _tokens(chunk))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=3)
    args = ap.parse_args()

    chunker = TextChunker()
    passed = 0
    for case in CASES:
        chunks = chunker.chunk_text(case["document"])
        ranked = sorted(chunks, key=lambda c: score_chunk(case["question"], c), reverse=True)
        top = ranked[: args.top_k]
        hit = any(case["must_contain"].lower() in c.lower() for c in top)
        passed += hit
        print(
            f"{'PASS' if hit else 'FAIL'} {case['name']}: "
            f"{len(chunks)} chunks, top-{args.top_k} "
            f"{'contains' if hit else 'MISSING'} {case['must_contain']!r}"
        )
    print(f"\nrecall@{args.top_k}: {passed}/{len(CASES)}")
    sys.exit(0 if passed == len(CASES) else 1)


if __name__ == "__main__":
    main()
