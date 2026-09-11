"""AUTH-001 route lifecycle: register→verify, reset, refresh rotation, fail-closed email."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from tamthuc_auth.config import reset_settings_cache
from tamthuc_auth.email import FakeEmailSender, reset_email_sender, set_email_sender
from tamthuc_auth.routes import create_auth_app
from tamthuc_auth.service import AuthService
from tamthuc_auth.sessions import InMemorySessionStore
from tamthuc_auth.token_store import EmailTokenStore
from tamthuc_auth.tokens import RevocationStore


@pytest.fixture
def mail() -> Generator[FakeEmailSender, None, None]:
    sender = FakeEmailSender()
    set_email_sender(sender)
    yield sender
    reset_email_sender()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, mail: FakeEmailSender) -> TestClient:
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv(
        "TAMTHUC_AUTH_JWT_SECRET",
        "test-jwt-secret-at-least-32-bytes-long!!",
    )
    reset_settings_cache()
    tokens = EmailTokenStore()
    rev = RevocationStore()
    sessions = InMemorySessionStore()
    svc = AuthService(email_tokens=tokens, revocation=rev, mail=mail, sessions=sessions)
    return TestClient(create_auth_app(svc))


def test_register_verify_path(client: TestClient, mail: FakeEmailSender) -> None:
    reg = client.post(
        "/auth/register",
        json={"email": "verify@example.com", "password": "password123"},
    )
    assert reg.status_code == 200, reg.text
    assert reg.json()["email_verified"] is False
    assert len(mail.sent) == 1
    assert mail.sent[0]["template"] == "email_verify"
    raw = mail.sent[0]["_raw"]["token"]
    confirm = client.post("/auth/verify/confirm", json={"token": raw})
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["email_verified"] is True
    login = client.post(
        "/auth/login",
        json={"email": "verify@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    me = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access']}"},
    )
    assert me.status_code == 200
    assert me.json()["email_verified"] is True


def test_password_reset_flow(client: TestClient, mail: FakeEmailSender) -> None:
    client.post(
        "/auth/register",
        json={"email": "reset@example.com", "password": "password123"},
    )
    mail.sent.clear()
    req = client.post(
        "/auth/password-reset/request",
        json={"email": "reset@example.com"},
    )
    assert req.status_code == 200
    assert req.json()["status"] == "ok"
    # enumeration-safe for unknown
    unknown = client.post(
        "/auth/password-reset/request",
        json={"email": "nobody@example.com"},
    )
    assert unknown.status_code == 200
    assert unknown.json() == req.json()
    raw = mail.sent[0]["_raw"]["token"]
    confirm = client.post(
        "/auth/password-reset/confirm",
        json={"token": raw, "new_password": "new-password-99"},
    )
    assert confirm.status_code == 200, confirm.text
    bad = client.post(
        "/auth/login",
        json={"email": "reset@example.com", "password": "password123"},
    )
    assert bad.status_code == 401
    ok = client.post(
        "/auth/login",
        json={"email": "reset@example.com", "password": "new-password-99"},
    )
    assert ok.status_code == 200


def test_refresh_rotation_and_logout(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "rot@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "rot@example.com", "password": "password123"},
    )
    old_refresh = login.json()["refresh"]
    rotated = client.post("/auth/refresh", json={"refresh": old_refresh})
    assert rotated.status_code == 200, rotated.text
    new_refresh = rotated.json()["refresh"]
    assert new_refresh != old_refresh
    # reuse of old refresh fails (family revoked via reuse detection)
    reuse = client.post("/auth/refresh", json={"refresh": old_refresh})
    assert reuse.status_code == 401
    # family already dead; logout remains idempotent
    out = client.post("/auth/logout", json={"refresh": new_refresh})
    assert out.status_code == 200
    assert out.json()["ok"] is True
    after = client.post("/auth/refresh", json={"refresh": new_refresh})
    assert after.status_code == 401


def test_production_register_fail_closed_without_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import base64

    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv(
        "TAMTHUC_AUTH_JWT_SECRET",
        "prod-jwt-secret-at-least-32-bytes-long!!",
    )
    monkeypatch.setenv(
        "TAMTHUC_AUTH_MASTER_KEY_B64",
        base64.urlsafe_b64encode(b"p" * 32).decode(),
    )
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("AUTH_EMAIL_FAKE", raising=False)
    monkeypatch.delenv("ALLOW_FAKE_EMAIL", raising=False)
    reset_settings_cache()
    set_email_sender(None)
    svc = AuthService()
    # Force resolve path (no injected mail)
    svc.mail = None
    app = create_auth_app(svc)
    c = TestClient(app)
    r = c.post(
        "/auth/register",
        json={"email": "prod@example.com", "password": "password123"},
    )
    assert r.status_code == 503, r.text
    detail = r.json()["detail"]
    assert detail["error"]["code"] == "email_not_configured"
    reset_email_sender()
    monkeypatch.setenv("ENV", "test")
    reset_settings_cache()


def test_dsar_export_requires_auth(client: TestClient) -> None:
    r = client.post("/auth/dsar/export")
    assert r.status_code == 401
