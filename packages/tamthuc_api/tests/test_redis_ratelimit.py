"""D-API-001 Redis rate limiter + trusted proxy IP."""

from __future__ import annotations

from tamthuc_api.ratelimit import (
    LocalFallbackLimiter,
    MemoryRedisCounter,
    RedisRateLimiter,
    quota_for,
)
from tamthuc_api.trusted_proxy import client_ip


class _FakeRequest:
    def __init__(self, host: str, xff: str | None = None) -> None:
        self.client = type("C", (), {"host": host})()
        self.headers = {}
        if xff is not None:
            self.headers["x-forwarded-for"] = xff


def test_redis_limiter_enforces_quota() -> None:
    counter = MemoryRedisCounter()
    limiter = RedisRateLimiter(counter)
    for _ in range(100):
        assert limiter.check_and_count("u1", "Free").allowed
    denied = limiter.check_and_count("u1", "Free")
    assert not denied.allowed
    assert denied.retry_after is not None


def test_redis_outage_uses_conservative_cap() -> None:
    class Boom:
        def incr(self, key: str) -> int:
            raise ConnectionError("down")

        def expire(self, key: str, seconds: int) -> None:
            raise ConnectionError("down")

    limiter = RedisRateLimiter(Boom(), local=LocalFallbackLimiter(conservative_cap=3))
    assert limiter.check_and_count("u2", "Free").allowed
    assert limiter.check_and_count("u2", "Free").allowed
    assert limiter.check_and_count("u2", "Free").allowed
    assert not limiter.check_and_count("u2", "Free").allowed


def test_missing_redis_is_conservative() -> None:
    limiter = RedisRateLimiter(None, local=LocalFallbackLimiter(conservative_cap=2))
    assert limiter.check_and_count("u3", "Premium").allowed
    assert limiter.check_and_count("u3", "Premium").allowed
    assert not limiter.check_and_count("u3", "Premium").allowed


def test_admin_unmetered_via_redis() -> None:
    limiter = RedisRateLimiter(MemoryRedisCounter())
    for _ in range(50):
        assert limiter.check_and_count("admin", "Admin").allowed
    assert quota_for("Admin") == "unmetered"


def test_client_ip_ignores_xff_without_trusted_proxies(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("TRUSTED_PROXY_COUNT", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    req = _FakeRequest("10.0.0.5", "1.2.3.4, 10.0.0.5")
    assert client_ip(req) == "10.0.0.5"  # type: ignore[arg-type]


def test_client_ip_uses_xff_with_trusted_count(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("TRUSTED_PROXY_COUNT", "1")
    req = _FakeRequest("10.0.0.5", "203.0.113.9, 10.0.0.5")
    assert client_ip(req) == "203.0.113.9"  # type: ignore[arg-type]
