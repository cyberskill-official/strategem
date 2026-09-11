"""Rate limiting — TASK-API-003 / D-API-001. Quotas from AUTH-002 / rbac-tiers.json."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol

TierLimit = int | Literal["unmetered", "custom"]

log = logging.getLogger("tamthuc_api.ratelimit")


def load_tier_quotas(path: Path | None = None) -> dict[str, TierLimit]:
    root = Path(__file__).resolve().parents[4]  # repo root from packages/.../src/tamthuc_api
    p = path or root / "docs" / "contracts" / "rbac-tiers.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    out: dict[str, TierLimit] = {}
    for tier, cfg in data.items():
        raw = cfg["requests_per_day"]
        if raw == "unmetered":
            out[tier] = "unmetered"
        elif raw == "custom":
            out[tier] = "custom"
        else:
            out[tier] = int(raw)
    return out


def quota_for(tier: str, *, enterprise_custom: int | None = None) -> TierLimit:
    quotas = load_tier_quotas()
    # normalize Free/free
    key = tier[:1].upper() + tier[1:] if tier else "Free"
    if key.lower() == "free":
        key = "Free"
    elif key.lower() == "premium":
        key = "Premium"
    elif key.lower() == "enterprise":
        key = "Enterprise"
    elif key.lower() == "admin":
        key = "Admin"
    q = quotas.get(key, quotas.get("Free", 100))
    if q == "custom":
        return enterprise_custom if enterprise_custom is not None else 10_000
    return q


@dataclass
class RateDecision:
    allowed: bool
    limit: TierLimit
    remaining: int
    reset_at: int
    retry_after: int | None = None


class RateLimiter(Protocol):
    def check_and_count(self, principal_id: str, tier: str) -> RateDecision: ...


class RedisCounter(Protocol):
    """Minimal counter surface: atomic INCR + EXPIRE."""

    def incr(self, key: str) -> int: ...

    def expire(self, key: str, seconds: int) -> None: ...


@dataclass
class MemoryRedisCounter:
    """Process-local stand-in for Redis INCR (tests / single-process)."""

    counters: dict[str, int] = field(default_factory=dict)
    ttls: dict[str, float] = field(default_factory=dict)

    def incr(self, key: str) -> int:
        exp = self.ttls.get(key)
        if exp is not None and exp < time.time():
            self.counters.pop(key, None)
            self.ttls.pop(key, None)
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def expire(self, key: str, seconds: int) -> None:
        self.ttls[key] = time.time() + max(1, seconds)


@dataclass
class LocalFallbackLimiter:
    """In-memory fail-safe limiter (also used when Redis is unavailable)."""

    counters: dict[str, int] = field(default_factory=dict)
    day_key: str = field(default_factory=lambda: time.strftime("%Y%m%d"))
    # conservative per-instance cap when redis down and quota unknown
    conservative_cap: int = 50

    def _reset_if_new_day(self) -> None:
        today = time.strftime("%Y%m%d")
        if today != self.day_key:
            self.counters.clear()
            self.day_key = today

    def check_and_count(
        self,
        principal_id: str,
        tier: str,
        *,
        enterprise_custom: int | None = None,
        redis_unavailable: bool = False,
    ) -> RateDecision:
        self._reset_if_new_day()
        limit = quota_for(tier, enterprise_custom=enterprise_custom)
        reset_at = int(time.time()) + 86_400

        if limit == "unmetered":
            return RateDecision(True, "unmetered", remaining=10**9, reset_at=reset_at)

        cap = self.conservative_cap if redis_unavailable else int(limit)
        key = f"{principal_id}:{self.day_key}"
        used = self.counters.get(key, 0)
        if used >= cap:
            return RateDecision(
                allowed=False,
                limit=cap if redis_unavailable else limit,
                remaining=0,
                reset_at=reset_at,
                retry_after=max(1, reset_at - int(time.time())),
            )
        self.counters[key] = used + 1
        remaining = max(0, cap - self.counters[key])
        return RateDecision(
            allowed=True,
            limit=cap if redis_unavailable else limit,
            remaining=remaining,
            reset_at=reset_at,
        )


class RedisRateLimiter:
    """Atomic daily counters via Redis; conservative local fallback on outage."""

    def __init__(
        self,
        redis_client: RedisCounter | None = None,
        *,
        local: LocalFallbackLimiter | None = None,
    ) -> None:
        self.redis = redis_client
        self.local = local or LocalFallbackLimiter()

    def check_and_count(
        self,
        principal_id: str,
        tier: str,
        *,
        enterprise_custom: int | None = None,
    ) -> RateDecision:
        if self.redis is None:
            return self.local.check_and_count(
                principal_id, tier, enterprise_custom=enterprise_custom, redis_unavailable=True
            )
        limit = quota_for(tier, enterprise_custom=enterprise_custom)
        day = time.strftime("%Y%m%d")
        # Reset at next UTC midnight approximation (+86400 from now is fine for headers).
        reset_at = int(time.time()) + 86_400
        if limit == "unmetered":
            return RateDecision(True, "unmetered", remaining=10**9, reset_at=reset_at)
        key = f"rl:{principal_id}:{day}"
        try:
            used = int(self.redis.incr(key))
            if used == 1:
                # Expire shortly after day boundary (26h buffer for clock skew / TZ).
                self.redis.expire(key, 86_400 + 7200)
        except Exception:
            log.warning("ratelimit.redis_unavailable", exc_info=True)
            return self.local.check_and_count(
                principal_id, tier, enterprise_custom=enterprise_custom, redis_unavailable=True
            )
        cap = int(limit)
        if used > cap:
            return RateDecision(
                allowed=False,
                limit=limit,
                remaining=0,
                reset_at=reset_at,
                retry_after=max(1, reset_at - int(time.time())),
            )
        return RateDecision(
            allowed=True,
            limit=limit,
            remaining=max(0, cap - used),
            reset_at=reset_at,
        )


class _RedisPyCounter:
    """Adapter around redis-py client (optional dependency)."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def incr(self, key: str) -> int:
        return int(self._client.incr(key))

    def expire(self, key: str, seconds: int) -> None:
        self._client.expire(key, seconds)


def connect_redis_counter(url: str | None = None) -> RedisCounter | None:
    """Connect when REDIS_URL is set. Returns None if unset or connection fails."""
    url = (url if url is not None else os.environ.get("REDIS_URL", "")).strip()
    if not url:
        return None
    try:
        import redis
    except ImportError:
        log.error("ratelimit.redis_package_missing")
        return None
    try:
        client = redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=1.5)
        client.ping()
        return _RedisPyCounter(client)
    except Exception:
        log.warning("ratelimit.redis_connect_failed", exc_info=True)
        return None


def build_rate_limiter_from_env() -> RateLimiter:
    """Production: Redis when available; otherwise conservative local fallback.

    Local/test without REDIS_URL keeps full in-process quotas (single worker).
    """
    from tamthuc_auth.config import is_local_or_test_env

    counter = connect_redis_counter()
    if counter is not None:
        return RedisRateLimiter(counter)
    if (
        is_local_or_test_env()
        or not (os.environ.get("APP_ENV") or os.environ.get("ENV") or "").strip()
    ):
        return LocalFallbackLimiter()
    # Staging/production without Redis: fail closed to conservative per-instance caps.
    return RedisRateLimiter(None)
