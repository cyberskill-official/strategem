---
id: FR-PLAT-006
title: "Redis caching - chart cache 24h TTL keyed on the PLAT-002 cache key, invalidation on pattern-update, cache warming for common patterns, plus RAG top-k and common-interpretation caches"
module: PLAT
priority: SHOULD
status: done
phase: P1
slice: 1
lang: python
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-48, strategy 4.1, strategy 4.3]
related_frs: [FR-PLAT-002, FR-PLAT-003, FR-API-001, FR-API-003, FR-RAG-002, FR-QMDG-006]
depends_on: [FR-PLAT-003]
blocks: []
new_paths:
  - packages/tamthuc_api/tamthuc_api/cache/__init__.py
  - packages/tamthuc_api/tamthuc_api/cache/redis_cache.py
  - packages/tamthuc_api/tamthuc_api/cache/chart_cache.py
  - packages/tamthuc_api/tamthuc_api/cache/invalidation.py
  - packages/tamthuc_api/tamthuc_api/cache/warming.py
  - packages/tamthuc_api/tests/test_chart_cache.py
  - packages/tamthuc_api/tests/test_invalidation.py
  - docs/contracts/cache-keys.md
---

## §1 - Description (BCP-14 normative)

This FR is the Redis caching layer. Redis is the primary cache. It caches the cast chart (the la so envelope) with a 24-hour TTL keyed on the FR-PLAT-002 cache key, invalidates on a pattern-update, warms the cache for common patterns, and additionally caches RAG top-k retrieval results and common interpretations. It owns the cache clients, keys, TTLs, and invalidation; it does NOT own the cache-key definition (FR-PLAT-002) nor the durable store (FR-PLAT-003), and it never becomes a source of truth - a cache miss always recomputes from the engine or re-retrieves, never fails the request.

The chart cache SHALL key entries on the FR-PLAT-002 cache key exactly - the stable hash of `(he, dau_vao rounded to casting granularity, co_truong_phai sorted, lich_phap.co_lich_phap sorted)` - so two identical casts hit the same entry regardless of language or instance, and two casts that differ in any stamped flag do NOT collide. Chart entries SHALL expire after 24 hours. The cache SHALL be read at the orchestrator seam (FR-API-001 step 3) before the engine is called and written after a successful cast; a cache hit SHALL return an envelope byte-identical to what the engine would have produced (the read-only invariant holds through the cache).

Invalidation SHALL be event-driven: when a `knowledge_patterns` row is updated (FR-RULE-001 / FR-KB-004 curation), entries whose interpretation depends on that pattern SHALL be invalidated, so a corrected pattern never serves stale detection. Cache warming SHALL pre-populate the cache for common patterns/queries (for example the current period's charts and the highest-traffic question types) so the first user of a common cast does not pay the cold-cast cost. The RAG caches SHALL store top-k retrieval results and common interpretations under their own keys and TTLs. All cache operations SHALL fail open to recompute on any Redis error - a cache outage degrades latency, never correctness.

## §2 - Why this design (rationale for humans)

Chart casting is deterministic and pure: identical input plus identical flags yields an identical chart (strategy 4.4). That is exactly the property that makes a cache safe here - the cached value cannot go stale as long as the key captures everything that changed the result, which is precisely what the FR-PLAT-002 cache key is engineered to do. Reusing that key rather than inventing a cache key is the whole game: if the cache keyed on anything less than the full stamped-flag set, two users of different schools would collide and one would silently get the other's chart (RISK-2). Keying on the PLAT-002 hash makes a collision impossible by construction and a 24-hour TTL a simple freshness bound rather than a correctness risk.

Failing open is the non-negotiable posture. A cache is a latency optimization, never a source of truth; a caching layer that fails a request when Redis blinks has converted a performance tool into an availability risk. So every miss and every error recomputes from the engine or re-retrieves from the store. Invalidation on pattern-update matters because the one thing that can make a cached interpretation wrong is a change to the knowledge it was grounded in - so a curation edit to `knowledge_patterns` must reach into the cache and drop the affected entries, or a corrected pattern would be shadowed by a stale reading. Warming common patterns turns the cache from reactive to proactive for the traffic that dominates, which is where the latency budget is actually spent (Grok-48).

## §3 - Contract (keys / TTLs / invalidation)

### Cache clients (`cache/redis_cache.py`, `cache/chart_cache.py`)

```python
class RedisCache(Protocol):
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, ttl_s: int) -> None: ...
    async def delete(self, *keys: str) -> None: ...
    async def scan(self, match: str) -> list[str]: ...     # for pattern-scoped invalidation

class ChartCache:
    # key: chart:{plat002_cache_key}   ; value: the la so envelope JSON ; ttl: 24h
    async def get_or_cast(self, cache_key: str, cast: Callable[[], Awaitable[LaSo]]) -> LaSo: ...
```

### Key + TTL table (`docs/contracts/cache-keys.md`)

| Cache | Key pattern | Value | TTL | Invalidated by |
|---|---|---|---|---|
| chart | `chart:{plat002_cache_key}` | la so envelope (PLAT-002) | 24h | pattern-update (indirect), TTL |
| rag_topk | `rag:topk:{query_hash}` | retrieved chunk ids + scores | 6h | KB re-embed, TTL |
| rag_interp | `rag:interp:{chart_key}:{persona}` | common interpretation | 12h | pattern-update, TTL |

The `plat002_cache_key` is taken verbatim from FR-PLAT-002's `cache_key()`; this FR never re-derives it. `chart:*` values are the envelope byte-for-byte, so a hit is indistinguishable from a fresh cast.

### Invalidation (`cache/invalidation.py`)

```python
async def on_pattern_update(pattern_key: str) -> None:
    # a knowledge_patterns row changed (RULE-001 / KB-004): drop dependent rag_interp entries
    # and any chart entries whose cach_cuc references the pattern
    ...
```

### Warming (`cache/warming.py`)

```python
async def warm_common(now: datetime) -> int:
    # pre-cast and cache the current period's common charts + top question types; returns entries warmed
    ...
```

## §4 - Acceptance criteria

1. A cast is cached under `chart:{plat002_cache_key}` with a 24h TTL; a second identical cast is served from cache and its envelope is byte-identical to the first (read-only invariant through the cache).
2. Two casts that differ in any stamped `co_truong_phai` flag produce different keys and do NOT collide; a test over a flag matrix asserts no cross-school collision.
3. On a Redis error or miss, `get_or_cast` recomputes from the engine and still returns a correct chart; a simulated Redis outage never fails the request (fail open).
4. A `knowledge_patterns` update triggers `on_pattern_update`, which invalidates the dependent `rag_interp` and chart entries; a re-read after invalidation reflects the corrected pattern, not the stale one.
5. `warm_common` pre-populates the cache for common patterns; the first real request for a warmed cast is a hit, not a cold cast.
6. RAG top-k and common-interpretation caches store and expire under their documented keys/TTLs and are consulted by FR-RAG-002 before a fresh retrieval.

## §5 - Verification

- `tests/test_chart_cache.py`: hit/miss/TTL behavior against a fake/embedded Redis; the byte-identical-on-hit assertion; the flag-matrix no-collision test; the fail-open-on-outage test.
- `tests/test_invalidation.py`: a pattern-update invalidates exactly the dependent entries and no others; a re-cast after invalidation reflects the change; warming produces hits for the warmed set.
- Integration: the FR-API-001 orchestrator consults the chart cache before the engine and writes after a successful cast; a metered hit is faster and skips the engine call.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_api`, `pytest packages/tamthuc_api`.

## §6 - Implementation skeleton

1. `cache/redis_cache.py`: the `RedisCache` protocol, a Redis implementation (redis-py async), and an in-memory fake for tests; all operations fail open.
2. `cache/chart_cache.py`: `get_or_cast` keyed on the FR-PLAT-002 `cache_key`, 24h TTL, envelope stored verbatim.
3. `cache/invalidation.py`: `on_pattern_update` scoped invalidation; wire it to the RULE-001 / KB-004 pattern-write path.
4. `cache/warming.py`: `warm_common` for the current period's common charts and top question types; a scheduled trigger (Celery in FR-PLAT-010).
5. Add the RAG top-k and interpretation caches (consumed by FR-RAG-002/003); document all keys/TTLs in `docs/contracts/cache-keys.md`.
6. Wire the chart cache into the FR-API-001 orchestrator seam.

## §7 - Dependencies

Depends on FR-PLAT-003 per the catalog (the durable store the cache sits in front of; a miss recomputes and persists there). Reads the FR-PLAT-002 cache-key rule as a hard contract coupling - the chart cache key IS the PLAT-002 `cache_key`, never a local re-derivation - so PLAT-002 is a contract dependency even though the catalog keeps the hard `depends_on` at PLAT-003. Consumed by FR-API-001 (the orchestrator seam that reads/writes the chart cache), FR-API-003 (Redis also backs the rate-limit counters, same instance), and FR-RAG-002 (top-k and interpretation caches). Warming is scheduled via the FR-PLAT-010 Celery workers.

## §8 - Example payloads

```
# chart cache entry (illustrative)
GET  chart:ck_9f3a...             -> <la so envelope JSON, byte-identical to a fresh cast>
TTL  chart:ck_9f3a...             -> 86400   (24h)
```

```python
# orchestrator seam (FR-API-001 step 3) - cache in front of the engine, fail open
chart = await chart_cache.get_or_cast(
    cache_key=envelope_cache_key(sys, ctx, req),         # FR-PLAT-002 cache_key
    cast=lambda: engine.cast(sys, ctx, req),
)
```

## §9 - Open questions

- Whether the cache module stays inside `tamthuc_api` or becomes a shared `tamthuc_cache` package once RAG also imports the `RedisCache` primitive. Default: keep it in `tamthuc_api` at MVP and export the primitive for RAG to import; extract a shared package only if a third consumer appears.
- Window for chart-cache TTL: fixed 24h vs tied to the next jieqi boundary (a chart's calendar context is stable only within a solar term). Default: a flat 24h TTL now (simple, and casts are keyed on the full lich_phap flags anyway); revisit if term-boundary charts show staleness.
- Cache stampede on a cold common cast under load. Default: a single-flight lock around `get_or_cast` per key so a thundering herd casts once; warming reduces the cold surface further.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Cross-school collision | cache key weaker than the full stamped-flag set | forbidden; the key IS the PLAT-002 hash over all flags; the flag-matrix test asserts no collision (RISK-2) |
| Fail closed on outage | Redis down fails the request | forbidden; every miss/error recomputes from the engine; fail open, latency degrades not correctness |
| Stale after correction | pattern updated but cache serves the old reading | `on_pattern_update` invalidates dependent entries; a re-read reflects the change |
| Cache as source of truth | request served only from cache with no recompute path | cache is never authoritative; a miss always recomputes/re-retrieves |
| Mutated on hit | cached envelope altered before return | stored and returned byte-for-byte; the read-only invariant holds through the cache |
| Unbounded growth | no TTL / no eviction | every entry carries a TTL; keys are scoped and evictable |

## §11 - Notes

This FR is a latency optimization with one hard rule and one hard reuse: fail open (a cache outage never fails a request), and key the chart cache on the FR-PLAT-002 cache key verbatim (never a local re-derivation), so determinism makes the cache trivially safe and the full stamped-flag set makes a cross-school collision impossible. Redis is the primary cache and the same instance backs the FR-API-003 rate-limit counters. Invalidate on pattern-update so a corrected pattern is never shadowed, warm the common patterns so the dominant traffic is never cold, and keep the RAG top-k and interpretation caches under their own keys. It extends the `tamthuc_api` package as one more module on the same app.
