"""FR-PLAT-006 chart cache tests."""

from __future__ import annotations

import json

from tamthuc_api.cache.chart_cache import ChartCache, chart_key
from tamthuc_api.cache.redis_cache import InMemoryRedis


def test_hit_byte_identical() -> None:
    redis = InMemoryRedis()
    cache = ChartCache(redis)
    calls = {"n": 0}

    def cast() -> dict:
        calls["n"] += 1
        return {"envelope_version": 1, "ban": {"x": 1}, "he": "ky_mon"}

    a = cache.get_or_cast("abc123", cast)
    b = cache.get_or_cast("abc123", cast)
    assert a == b
    assert calls["n"] == 1
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert redis.get(chart_key("abc123")) is not None


def test_flag_matrix_no_collision() -> None:
    cache = ChartCache(InMemoryRedis())
    cache.set("key_school_a", {"school": "a"})
    cache.set("key_school_b", {"school": "b"})
    assert cache.get("key_school_a") != cache.get("key_school_b")


def test_fail_open_on_redis_outage() -> None:
    redis = InMemoryRedis(fail=True)
    cache = ChartCache(redis)
    env = cache.get_or_cast("k", lambda: {"ok": True})
    assert env == {"ok": True}


def test_rag_caches_ttls() -> None:
    cache = ChartCache(InMemoryRedis())
    cache.set_rag_topk("qh", {"ids": ["c1"]})
    assert cache.get_rag_topk("qh") == {"ids": ["c1"]}
    cache.set_rag_interp("ck", "beginner", {"text": "x"})
    assert cache.get_rag_interp("ck", "beginner") == {"text": "x"}
