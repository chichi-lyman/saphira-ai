# Saphira Elite — First-Principles Efficiency Pass

© 2026 Chelsea Megan Woods

## Design rules applied

1. **No decorative layers** — every class has `__slots__` or minimal attrs; no unused middleware.
2. **Deterministic routing cost = 0 LLM tokens** — fixed pipeline plan, no model call for routing.
3. **Bounded everything** — max_nodes=48, max_parallel=4, max_depth=10, recall max_bytes=8KB.
4. **Explicit metrics on every hot path** — `latency_ms`, `calls`, `avg_ms`, `writes/reads`.
5. **Self-heal without ceremony** — 2 retries + timeout, then `recovered_from_failure`.
6. **Isolation token per invocation** — no shared mutable session state between concurrent runs.
7. **Secret-mask** — internal agent keys never leave the system in user-facing payloads.

## Compute profile (target)

| Path | Expected cost |
|------|----------------|
| Route plan | O(1) dict lookups, 0 tokens |
| TaskGraph cycle check | O(N+E) Kahn, N≤48 |
| Agent safe_run | ≤30s wall, 2 retries |
| Memory recall | in-memory keyword score, top-k≤8, ≤8KB |
| Concurrent agents | semaphore bulkhead ≤4 |

## How to measure

```python
router = EliteRouter(registry)
result = await router.route("turn on the lights")
print(result["latency_ms"], router.metrics)
print(agent.metrics)          # per-agent
print(memory.metrics())       # store
```

## Still optional (next hard pass)

- Replace in-memory store with SQLite mmap or shared-memory ring for multi-process.
- Add token-count estimator at the LLM boundary only (not inside agents).
- Compile critical path with mypyc / Cython if latency budget requires it.
