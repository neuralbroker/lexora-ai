# Lexora AI performance

Measured 2026-09-14 (commit after rate-limit/LLM-retry/dep-trim work):

- Unit tests: `35 passed`, coverage `49%` (SQLite overrides, no real OpenAI calls).
- Retrieval recall probe: `python scripts/eval_retrieval.py --top-k 3` → `3/3`
  (deterministic keyword-recall floor over chunking; no API keys needed).

Latency/throughput benchmarks are NOT yet measured — they need PG + Redis +
an OpenAI key. `DEPLOYMENT.md` lists desired signals (latency histogram,
p95>2s alert) — aspirational, not measured. Do not cite p95/RPS numbers.

To add next: time upload→processable, retrieval (embed+FAISS+rank), chat
(retrieval+LLM) and streaming first-token, at 100/1K/10K chunks per user;
report p50/p95 + Redis hit rate + worker queue depth + DB pool waits.
Extend the eval beyond the keyword probe: embedding recall@k on a labeled
doc set, then faithfulness (cited-span support) judgments.
