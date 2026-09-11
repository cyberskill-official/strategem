"""AUTH-001 follow-up: durable email tokens + session revoke APIs."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from tamthuc_auth.config import reset_settings_cache
from tamthuc_auth.email import FakeEmailSender, reset_email_sender, set_email_sender
from tamthuc_auth.routes import create_auth_app
from tamthuc_auth.service import AuthService
from tamthuc_auth.sessions import InMemorySessionStore, SessionReuseError
from tamthuc_auth.token_store import EmailTokenStore, hash_token
from tamthuc_auth.tokens import RevocationStore, verify_refresh


@pytest.fixture
def mail() -> Generator[FakeEmailSender, None, None]:
    sender = FakeEmailSender()
    set_email_sender(sender)
    yield sender
    reset_email_sender()


@pytest.fixture
def env(
    monkeypatch: pytest.MonkeyPatch, mail: FakeEmailSender
) -> tuple[AuthService, EmailTokenStore, InMemorySessionStore]:
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv(
        "TAMTHUC_AUTH_JWT_SECRET",
        "test-jwt-secret-at-least-32-bytes-long!!",
    )
    reset_settings_cache()
    tokens = EmailTokenStore()
    sessions = InMemorySessionStore()
    rev = RevocationStore()
    svc = AuthService(
        email_tokens=tokens,
        revocation=rev,
        mail=mail,
        sessions=sessions,
    )
    return svc, tokens, sessions


def test_email_token_store_hashed_single_use() -> None:
    store = EmailTokenStore()
    raw = store.issue("user-1", "email_verify", ttl_s=60)
    assert store.has_plaintext() is False
    assert hash_token(raw) in store._by_hash
    rec = store.consume(raw, "email_verify")
    assert rec.user_id == "user-1"
    with pytest.raises(ValueError, match="token_used"):
        store.consume(raw, "email_verify")


def test_session_list_revoke_one_and_all(
    env: tuple[AuthService, EmailTokenStore, InMemorySessionStore],
) -> None:
    svc, _tokens, _sessions = env
    client = TestClient(create_auth_app(svc))
    client.post(
        "/auth/register",
        json={"email": "sess@example.com", "password": "password123"},
    )
    a = client.post(
        "/auth/login",
        json={"email": "sess@example.com", "password": "password123"},
    )
    b = client.post(
        "/auth/login",
        json={"email": "sess@example.com", "password": "password123"},
    )
    assert a.status_code == 200 and b.status_code == 200
    access = a.json()["access"]
    listed = client.get("/auth/sessions", headers={"Authorization": f"Bearer {access}"})
    assert listed.status_code == 200, listed.text
    rows = listed.json()["sessions"]
    assert len(rows) == 2

    claims_a = verify_refresh(a.json()["refresh"], settings=svc.settings, check_revocation=False)
    claims_b = verify_refresh(b.json()["refresh"], settings=svc.settings, check_revocation=False)
    assert claims_a.fid and claims_b.fid

    rev = client.post(
        f"/auth/sessions/{claims_a.fid}/revoke",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert rev.status_code == 200
    assert rev.json()["ok"] is True

    dead_a = client.post("/auth/refresh", json={"refresh": a.json()["refresh"]})
    assert dead_a.status_code == 401
    alive_b = client.post("/auth/refresh", json={"refresh": b.json()["refresh"]})
    assert alive_b.status_code == 200, alive_b.text
    still = alive_b.json()["refresh"]

    all_out = client.post(
        "/auth/sessions/revoke-all",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert all_out.status_code == 200
    assert all_out.json()["ok"] is True
    assert all_out.json()["revoked"] >= 1
    dead = client.post("/auth/refresh", json={"refresh": still})
    assert dead.status_code == 401


def test_refresh_reuse_revokes_family(
    env: tuple[AuthService, EmailTokenStore, InMemorySessionStore],
) -> None:
    svc, _tokens, sessions = env
    client = TestClient(create_auth_app(svc))
    client.post(
        "/auth/register",
        json={"email": "reuse@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "reuse@example.com", "password": "password123"},
    )
    old = login.json()["refresh"]
    claims = verify_refresh(old, settings=svc.settings, check_revocation=False)
    assert claims.fid is not None
    rotated = client.post("/auth/refresh", json={"refresh": old})
    assert rotated.status_code == 200
    new = rotated.json()["refresh"]
    # replay old refresh → family revoked (reuse detection)
    replay = client.post("/auth/refresh", json={"refresh": old})
    assert replay.status_code == 401
    after = client.post("/auth/refresh", json={"refresh": new})
    assert after.status_code == 401
    fam = sessions.get(claims.fid)
    assert fam is not None
    assert fam.revoked_at is not None
    assert fam.reuse_detected_at is not None


def test_password_reset_revokes_all_sessions(
    env: tuple[AuthService, EmailTokenStore, InMemorySessionStore],
    mail: FakeEmailSender,
) -> None:
    svc, _tokens, sessions = env
    client = TestClient(create_auth_app(svc))
    client.post(
        "/auth/register",
        json={"email": "cut@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "cut@example.com", "password": "password123"},
    )
    refresh = login.json()["refresh"]
    mail.sent.clear()
    client.post("/auth/password-reset/request", json={"email": "cut@example.com"})
    raw = mail.sent[0]["_raw"]["token"]
    confirm = client.post(
        "/auth/password-reset/confirm",
        json={"token": raw, "new_password": "brand-new-99"},
    )
    assert confirm.status_code == 200
    assert confirm.json()["sessions_revoked"] is True
    user = svc.store.get_by_email("cut@example.com")
    assert user is not None
    assert sessions.list_active(str(user.id)) == []
    dead = client.post("/auth/refresh", json={"refresh": refresh})
    assert dead.status_code == 401


def test_session_store_rotate_mismatch() -> None:
    store = InMemorySessionStore()
    rec = store.create("u1", "jti-a", expires_at=9e12, family_id="fam-1")
    store.rotate("fam-1", "jti-a", "jti-b", expires_at=9e12)
    with pytest.raises(SessionReuseError):
        store.rotate("fam-1", "jti-a", "jti-c", expires_at=9e12)
    assert store.get(rec.id) is not None
    assert store.get(rec.id).revoked_at is not None  # type: ignore[union-attr]
