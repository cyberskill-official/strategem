"""Chart cache keyed on PLAT-002 cache_key — FR-PLAT-006."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from tamthuc_api.cache.redis_cache import InMemoryRedis, RedisCache

log = logging.getLogger("tamthuc_api.cache.chart")

CHART_TTL_S = 24 * 3600
RAG_TOPK_TTL_S = 6 * 3600
RAG_INTERP_TTL_S = 12 * 3600


def chart_key(plat002_cache_key: str) -> str:
    return f"chart:{plat002_cache_key}"


def rag_topk_key(query_hash: str) -> str:
    return f"rag:topk:{query_hash}"


def rag_interp_key(chart_key_hash: str, persona: str) -> str:
    return f"rag:interp:{chart_key_hash}:{persona}"


class ChartCache:
    def __init__(self, redis: RedisCache | None = None) -> None:
        self.redis: RedisCache = redis or InMemoryRedis()

    def get(self, plat002_cache_key: str) -> dict[str, Any] | None:
        try:
            raw = self.redis.get(chart_key(plat002_cache_key))
        except Exception:
            log.warning("chart_cache.get_fail_open")
            return None
        if raw is None:
            return None
        data: dict[str, Any] = json.loads(raw.decode("utf-8"))
        return data

    def set(self, plat002_cache_key: str, envelope: dict[str, Any]) -> None:
        try:
            self.redis.set(
                chart_key(plat002_cache_key),
                json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8"),
                CHART_TTL_S,
            )
        except Exception:
            log.warning("chart_cache.set_fail_open")

    def get_or_cast(
        self,
        plat002_cache_key: str,
        cast: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        hit = self.get(plat002_cache_key)
        if hit is not None:
            return hit
        envelope = cast()
        self.set(plat002_cache_key, envelope)
        return envelope

    def set_rag_topk(self, query_hash: str, payload: dict[str, Any]) -> None:
        try:
            self.redis.set(
                rag_topk_key(query_hash),
                json.dumps(payload).encode("utf-8"),
                RAG_TOPK_TTL_S,
            )
        except Exception:
            log.warning("rag_topk.set_fail_open")

    def get_rag_topk(self, query_hash: str) -> dict[str, Any] | None:
        try:
            raw = self.redis.get(rag_topk_key(query_hash))
        except Exception:
            return None
        if not raw:
            return None
        data: dict[str, Any] = json.loads(raw.decode("utf-8"))
        return data

    def set_rag_interp(self, chart_key_hash: str, persona: str, payload: dict[str, Any]) -> None:
        try:
            self.redis.set(
                rag_interp_key(chart_key_hash, persona),
                json.dumps(payload).encode("utf-8"),
                RAG_INTERP_TTL_S,
            )
        except Exception:
            log.warning("rag_interp.set_fail_open")

    def get_rag_interp(self, chart_key_hash: str, persona: str) -> dict[str, Any] | None:
        try:
            raw = self.redis.get(rag_interp_key(chart_key_hash, persona))
        except Exception:
            return None
        if not raw:
            return None
        data: dict[str, Any] = json.loads(raw.decode("utf-8"))
        return data
