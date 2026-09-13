# Lexora AI performance

Status: no published latency/throughput benchmarks. Only measured numbers in repo: `31 passed`, coverage `46%` (README). `DEPLOYMENT.md` lists desired signals (latency histogram, p95>2s alert) — aspirational, not measured.

Do not cite p95/RPS numbers until measured. To add: time upload→processable, retrieval (embed+FAISS+rank), chat (retrieval+LLM) and streaming first-token, at 100/1K/10K chunks per user; report p50/p95 + Redis hit rate + worker queue depth + DB pool waits.
