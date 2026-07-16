# Cache keys (TASK-PLAT-006)

| Cache | Key pattern | Value | TTL | Invalidated by |
|---|---|---|---|---|
| chart | `chart:{plat002_cache_key}` | la so envelope JSON | 24h | TTL; pattern-update (scoped) |
| rag_topk | `rag:topk:{query_hash}` | chunk ids + scores | 6h | KB re-embed; TTL |
| rag_interp | `rag:interp:{chart_key}:{persona}` | common interpretation | 12h | pattern-update; TTL |

`plat002_cache_key` is taken verbatim from TASK-PLAT-002 `cache_key()` — never re-derived.

**Fail-open:** any Redis error recomputes from the engine / re-retrieves. Cache is never source of truth.
