"""FR-PLAT-006 invalidation + warming tests."""

from __future__ import annotations

from datetime import UTC, datetime

from tamthuc_api.cache.chart_cache import ChartCache, rag_interp_key
from tamthuc_api.cache.invalidation import on_pattern_update
from tamthuc_api.cache.redis_cache import InMemoryRedis
from tamthuc_api.cache.warming import warm_common


def test_pattern_update_invalidates_rag_interp() -> None:
    redis = InMemoryRedis()
    cache = ChartCache(redis)
    cache.set_rag_interp("ck1", "beginner", {"text": "stale"})
    cache.set("other_chart", {"ban": 1})
    assert cache.get_rag_interp("ck1", "beginner") is not None
    n = on_pattern_update("qimen_thanh_long_hoi_dau", redis)
    assert n >= 1
    assert cache.get_rag_interp("ck1", "beginner") is None
    # unrelated chart entry remains
    assert cache.get("other_chart") == {"ban": 1}


def test_warm_common_produces_hits() -> None:
    cache = ChartCache(InMemoryRedis())
    casts = [
        ("warm1", lambda: {"id": 1}),
        ("warm2", lambda: {"id": 2}),
    ]
    n = warm_common(datetime.now(UTC), cache=cache, casts=casts)
    assert n == 2
    calls = {"n": 0}

    def should_not_run() -> dict:
        calls["n"] += 1
        return {"id": 99}

    assert cache.get_or_cast("warm1", should_not_run) == {"id": 1}
    assert calls["n"] == 0


def test_scan_deletes_pattern_scoped() -> None:
    redis = InMemoryRedis()
    redis.set("pattern:p1:chart:x", b"{}", 60)
    redis.set(rag_interp_key("c", "expert"), b'{"t":1}', 60)
    assert on_pattern_update("p1", redis) >= 1
