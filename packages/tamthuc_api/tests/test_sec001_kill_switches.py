"""SEC-001: payments/social kill-switches + public /ready redaction."""

from __future__ import annotations

import base64

import pytest
from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_auth.config import reset_settings_cache


def _production_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ALLOW_MEMORY_AUTH", "1")
    monkeypatch.setenv("ALLOW_MEMORY_PERSISTENCE", "1")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.example.com")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PAYMENTS_MODE", raising=False)
    monkeypatch.delenv("PAYOS_CLIENT_ID", raising=False)
    monkeypatch.delenv("PAYOS_API_KEY", raising=False)
    monkeypatch.delenv("PAYOS_CHECKSUM_KEY", raising=False)
    monkeypatch.setenv(
        "TAMTHUC_AUTH_JWT_SECRET",
        "prod-jwt-secret-at-least-32-bytes-long!!",
    )
    monkeypatch.setenv(
        "TAMTHUC_AUTH_MASTER_KEY_B64",
        base64.urlsafe_b64encode(b"p" * 32).decode("ascii"),
    )
    reset_settings_cache()


def test_production_payments_routes_are_404(monkeypatch: pytest.MonkeyPatch) -> None:
    _production_surface(monkeypatch)
    monkeypatch.setenv("PAYMENTS_MODE", "mock")
    client = TestClient(create_app())
    tokens = register_and_login(client, email="sec001-pay@example.com")
    headers = auth_header(tokens["access"])

    provider = client.get("/api/v1/payments/provider")
    assert provider.status_code == 200
    body = provider.json()
    assert body["enabled"] is False
    assert body["mode"] == "disabled"

    checkout = client.post(
        "/api/v1/payments/checkout",
        headers=headers,
        json={"email": "sec001-pay@example.com"},
    )
    assert checkout.status_code == 404
    assert checkout.json()["error"]["code"] == "NOT_FOUND"

    webhook = client.post(
        "/api/v1/payments/webhook",
        json={"code": "00", "success": True, "data": {"orderCode": 1}},
    )
    assert webhook.status_code == 404

    mock_complete = client.post("/api/v1/payments/mock-complete", headers=headers)
    assert mock_complete.status_code == 404


def test_missing_payos_credentials_do_not_enable_mock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PAYMENTS_MODE", raising=False)
    monkeypatch.delenv("PAYOS_CLIENT_ID", raising=False)
    monkeypatch.delenv("PAYOS_API_KEY", raising=False)
    monkeypatch.delenv("PAYOS_CHECKSUM_KEY", raising=False)
    client = TestClient(create_app())
    tokens = register_and_login(client, email="sec001-nomock@example.com")
    r = client.post(
        "/api/v1/payments/checkout",
        headers=auth_header(tokens["access"]),
        json={"email": "sec001-nomock@example.com"},
    )
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "PAYMENTS_MISCONFIGURED"


def test_production_social_login_is_404(monkeypatch: pytest.MonkeyPatch) -> None:
    _production_surface(monkeypatch)
    client = TestClient(create_app())
    google = client.post("/auth/login/google", json={"id_token": "x"})
    apple = client.post("/auth/login/apple", json={"id_token": "x"})
    assert google.status_code == 404
    assert apple.status_code == 404
    assert google.json()["error"]["code"] == "NOT_FOUND"
    assert apple.json()["error"]["code"] == "NOT_FOUND"


def test_ready_redacts_internal_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CAST_CLI", raising=False)
    monkeypatch.delenv("READY_REQUIRE_CAST_CLI", raising=False)
    monkeypatch.setenv("LLM_BACKEND", "stub")
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
    client = TestClient(create_app())
    r = client.get("/ready")
    assert r.status_code == 200
    checks = r.json()["checks"]
    assert "llm_base_url" not in checks
    assert "llm_models_sample" not in checks
    assert "cast_cli_path" not in checks
    assert "llm_backend" in checks
    assert "payments_enabled" in checks
    assert checks["payments_enabled"] is True


def test_ready_payments_disabled_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    _production_surface(monkeypatch)
    monkeypatch.delenv("READY_REQUIRE_CAST_CLI", raising=False)
    client = TestClient(create_app())
    r = client.get("/ready")
    assert r.status_code == 200
    checks = r.json()["checks"]
    assert checks["payments_enabled"] is False
    assert "llm_base_url" not in checks
    assert "cast_cli_path" not in checks
