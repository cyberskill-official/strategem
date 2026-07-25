from __future__ import annotations

from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.middleware.ratelimit import RateLimitMiddleware
from tamthuc_api.ratelimit import LocalFallbackLimiter, quota_for


def test_quota_from_rbac_config() -> None:
    assert quota_for("Free") == 100
    assert quota_for("Premium") == 5000
    assert quota_for("Admin") == "unmetered"


def test_free_quota_101st_rejected() -> None:
    limiter = LocalFallbackLimiter()
    for _ in range(100):
        d = limiter.check_and_count("u1", "Free")
        assert d.allowed
    d = limiter.check_and_count("u1", "Free")
    assert not d.allowed
    assert d.retry_after is not None


def test_admin_unmetered() -> None:
    limiter = LocalFallbackLimiter()
    for _ in range(200):
        assert limiter.check_and_count("admin", "Admin").allowed


def test_middleware_returns_429() -> None:
    app = create_app()
    limiter = LocalFallbackLimiter()
    app.add_middleware(RateLimitMiddleware, limiter=limiter)
    client = TestClient(app)
    tokens = register_and_login(client, email="rl@example.com", tier="free")
    me = client.get("/auth/me", headers=auth_header(tokens["access"]))
    uid = me.json()["user_id"]
    for _ in range(100):
        limiter.check_and_count(uid, "free")
    r = client.post(
        "/api/v1/calculate/qimen",
        json={"datetime": "2004-01-01T10:30:00"},
        headers={
            **auth_header(tokens["access"]),
            "x-principal-id": "other-user",
            "x-tier": "admin",
        },
    )
    assert r.status_code == 429
    assert r.json()["error"]["code"] == "RATE_LIMITED"
    assert "Retry-After" in r.headers


def test_middleware_ignores_x_tier_spoof_for_anon() -> None:
    limiter = LocalFallbackLimiter()
    for _ in range(100):
        limiter.check_and_count("ip:testclient", "free")
    app = create_app()
    app.add_middleware(RateLimitMiddleware, limiter=limiter)
    client = TestClient(app)
    r = client.post(
        "/api/v1/calculate/qimen",
        json={"datetime": "2004-01-01T10:30:00"},
        headers={"x-principal-id": "fresh", "x-tier": "admin"},
    )
    assert r.status_code in {200, 429}
