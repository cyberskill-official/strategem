"""COV-009: auth mounted on API; free cast open; timing gated for free tier."""

from __future__ import annotations

import pytest
from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv(
        "TAMTHUC_AUTH_JWT_SECRET",
        "test-jwt-secret-at-least-32-bytes-long!!",
    )
    from tamthuc_auth.config import reset_settings_cache

    reset_settings_cache()
    from tamthuc_api.app import create_app

    return TestClient(create_app())


def test_auth_register_login_me(client: TestClient) -> None:
    r = client.post(
        "/auth/register",
        json={"email": "cov009@example.com", "password": "password123"},
    )
    assert r.status_code == 200, r.text
    login = client.post(
        "/auth/login",
        json={"email": "cov009@example.com", "password": "password123"},
    )
    assert login.status_code == 200, login.text
    body = login.json()
    assert body.get("access")
    assert body.get("refresh")
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access']}"})
    assert me.status_code == 200, me.text
    assert me.json().get("email", "").lower() == "cov009@example.com"


def test_free_cast_without_auth(client: TestClient) -> None:
    r = client.post(
        "/api/v1/calculate/qimen",
        json={
            "datetime": "2004-01-01T10:30:00",
            "tz": "+07:00",
            "longitude": 106.7,
            "systems": ["qimen"],
            "question_type": "trach_thoi",
            "persona_level": "beginner",
        },
    )
    assert r.status_code == 200, r.text
    assert r.json().get("charts", {}).get("qimen")


def test_timing_gated_for_free_authenticated(client: TestClient) -> None:
    tokens = register_and_login(client, email="freeuser@example.com", tier="free")
    r = client.post(
        "/api/v1/timing/optimize",
        headers=auth_header(tokens["access"]),
        json={
            "start": "2004-01-01T08:00:00",
            "end": "2004-01-01T14:00:00",
            "top_n": 2,
        },
    )
    assert r.status_code == 403, r.text
    assert r.json().get("error", {}).get("code") == "FORBIDDEN_TIER"


def test_timing_requires_auth(client: TestClient) -> None:
    r = client.post(
        "/api/v1/timing/optimize",
        json={
            "start": "2004-01-01T08:00:00",
            "end": "2004-01-01T14:00:00",
            "top_n": 2,
        },
    )
    assert r.status_code == 401
