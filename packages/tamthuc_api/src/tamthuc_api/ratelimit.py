"""Rate limiting — FR-API-003. Quotas from AUTH-002 / rbac-tiers.json."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol

TierLimit = int | Literal["unmetered", "custom"]


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
    """Placeholder Redis limiter; falls back to LocalFallbackLimiter."""

    def __init__(self, redis_client: Any | None = None) -> None:
        self.redis = redis_client
        self.local = LocalFallbackLimiter()

    def check_and_count(self, principal_id: str, tier: str) -> RateDecision:
        if self.redis is None:
            return self.local.check_and_count(principal_id, tier, redis_unavailable=True)
        # real Redis path would INCR rl:{principal}:{yyyymmdd}
        return self.local.check_and_count(principal_id, tier)
