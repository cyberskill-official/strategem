"""Auth flow tests (TASK-AUTH-001 §4, §5)."""

from __future__ import annotations

import logging
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from tamthuc_auth.config import AuthSettings, reset_settings_cache
from tamthuc_auth.errors import InvalidCredentials, TokenExpired, TokenInvalid, TokenRevoked
from tamthuc_auth.models import BirthData
from tamthuc_auth.passwords import hash_password, verify_password
from tamthuc_auth.routes import create_auth_app
from tamthuc_auth.service import AuthService, drain_verification_events
from tamthuc_auth.social import mint_test_id_token
from tamthuc_auth.store import InMemoryUserStore
from tamthuc_auth.tokens import (
    RevocationStore,
    issue_access,
    issue_refresh,
    revoke_refresh,
    verify_access,
    verify_refresh,
)


@pytest.fixture
def settings() -> AuthSettings:
    reset_settings_cache()
    return AuthSettings(
        jwt_secret="test-jwt-secret-at-least-32-bytes-long!!",
        master_key_b64=__import__("base64").urlsafe_b64encode(b"m" * 32).decode(),
        access_ttl_seconds=60,
        refresh_ttl_seconds=3600,
    )


@pytest.fixture
def svc(settings: AuthSettings) -> AuthService:
    drain_verification_events()
    store = InMemoryUserStore()
    rev = RevocationStore()
    return AuthService(store=store, settings=settings, revocation=rev)


@pytest.fixture
def client(svc: AuthService) -> TestClient:
    app = create_auth_app(svc)
    return TestClient(app)


def test_password_argon2_not_plaintext() -> None:
    h = hash_password("s3cret-pass")
    assert h != "s3cret-pass"
    assert h.startswith("$argon2")
    assert verify_password("s3cret-pass", h)
    assert not verify_password("wrong", h)


def test_register_login_tokens(svc: AuthService) -> None:
    reg = svc.register("User@Example.com", "password123", BirthData(date="1990-01-01", place="HN"))
    assert reg.email_verified is False
    events = drain_verification_events()
    assert events and events[0]["type"] == "email.verification.requested"

    pair = svc.login("user@example.com", "password123")
    claims = verify_access(pair.access, settings=svc.settings)
    assert claims.sub == str(reg.user_id)
    assert claims.tier == "free"
    assert claims.jti

    user = svc.get_user(reg.user_id)
    assert user is not None
    assert user.password_hash is not None
    assert "password123" not in user.password_hash
    assert user.birth_data_envelope is not None
    assert "1990-01-01" not in str(user.birth_data_envelope)


def test_login_failures_indistinguishable(svc: AuthService) -> None:
    svc.register("a@example.com", "password123")
    with pytest.raises(InvalidCredentials) as e1:
        svc.login("missing@example.com", "password123")
    with pytest.raises(InvalidCredentials) as e2:
        svc.login("a@example.com", "wrong-password")
    assert str(e1.value) == str(e2.value)
    assert e1.value.to_envelope() == e2.value.to_envelope()


def test_verify_access_rejects_expired_tampered_wrong_key(settings: AuthSettings) -> None:
    tok = issue_access("u1", "free", settings=settings, now=int(time.time()) - 10_000)
    # force short ttl token already expired
    short = AuthSettings(
        jwt_secret=settings.jwt_secret,
        master_key_b64=settings.master_key_b64,
        access_ttl_seconds=1,
    )
    expired = issue_access("u1", "free", settings=short, now=int(time.time()) - 100)
    with pytest.raises(TokenExpired):
        verify_access(expired, settings=short)

    good = issue_access("u1", "free", settings=settings)
    parts = good.split(".")
    # tamper payload
    tampered = parts[0] + "." + parts[1][:-2] + "xx" + "." + parts[2]
    with pytest.raises(TokenInvalid):
        verify_access(tampered, settings=settings)

    wrong = AuthSettings(
        jwt_secret="other-secret-other-secret-other-sec!!",
        master_key_b64=settings.master_key_b64,
    )
    with pytest.raises(TokenInvalid):
        verify_access(good, settings=wrong)
    # silence unused
    assert tok


def test_refresh_rotation_and_revocation(svc: AuthService) -> None:
    reg = svc.register("r@example.com", "password123")
    pair = svc.login("r@example.com", "password123")
    rotated = svc.refresh(pair.refresh)
    assert rotated.access != pair.access
    assert rotated.refresh != pair.refresh
    # old refresh revoked
    with pytest.raises(TokenRevoked):
        svc.refresh(pair.refresh)
    # new refresh works
    again = svc.refresh(rotated.refresh)
    assert again.access
    _ = reg


def test_social_google_and_apple(svc: AuthService) -> None:
    gtok = mint_test_id_token(
        provider="google", email="g@example.com", subject="g-sub", settings=svc.settings
    )
    pair = svc.login_social("google", gtok)
    claims = verify_access(pair.access, settings=svc.settings)
    user = svc.get_user(uuid.UUID(claims.sub))
    assert user is not None
    assert user.email == "g@example.com"
    assert user.email_verified is True
    assert user.password_hash is None

    # link existing email on second provider
    svc.register("both@example.com", "password123")
    atok = mint_test_id_token(
        provider="apple", email="both@example.com", subject="a-sub", settings=svc.settings
    )
    pair2 = svc.login_social("apple", atok)
    c2 = verify_access(pair2.access, settings=svc.settings)
    u2 = svc.get_user(uuid.UUID(c2.sub))
    assert u2 is not None
    assert u2.social_provider == "apple"


def test_social_invalid_and_wrong_audience(svc: AuthService) -> None:
    from tamthuc_auth.errors import SocialTokenInvalid

    with pytest.raises(SocialTokenInvalid):
        svc.login_social("google", "not-a-jwt")

    bad_aud = mint_test_id_token(
        provider="google",
        email="x@example.com",
        audience="wrong-aud",
        settings=svc.settings,
    )
    with pytest.raises(SocialTokenInvalid):
        svc.login_social("google", bad_aud)

    expired = mint_test_id_token(
        provider="google", email="x@example.com", exp_delta=-10, settings=svc.settings
    )
    with pytest.raises(SocialTokenInvalid):
        svc.login_social("google", expired)


def test_http_register_login_me_no_birth_data(client: TestClient, svc: AuthService) -> None:
    r = client.post(
        "/auth/register",
        json={
            "email": "web@example.com",
            "password": "password123",
            "birth_data": {"date": "1991-02-03", "place": "SG"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["email_verified"] is False
    assert "birth" not in str(body).lower() or "birth_data" not in body

    bad = client.post("/auth/login", json={"email": "nope@example.com", "password": "x"})
    wrong = client.post("/auth/login", json={"email": "web@example.com", "password": "nope!!!!"})
    assert bad.status_code == 401 and wrong.status_code == 401
    assert bad.json()["detail"]["error"]["message"] == wrong.json()["detail"]["error"]["message"]

    ok = client.post("/auth/login", json={"email": "web@example.com", "password": "password123"})
    assert ok.status_code == 200
    tokens = ok.json()
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access']}"})
    assert me.status_code == 200
    data = me.json()
    assert data["email"] == "web@example.com"
    assert "birth_data" not in data
    assert "1991-02-03" not in me.text


def test_http_refresh_and_social(client: TestClient, svc: AuthService) -> None:
    client.post("/auth/register", json={"email": "rr@example.com", "password": "password123"})
    login = client.post("/auth/login", json={"email": "rr@example.com", "password": "password123"})
    refresh = client.post("/auth/refresh", json={"refresh": login.json()["refresh"]})
    assert refresh.status_code == 200
    assert "access" in refresh.json()

    gtok = mint_test_id_token(provider="google", email="gg@example.com", settings=svc.settings)
    gl = client.post("/auth/login/google", json={"id_token": gtok})
    assert gl.status_code == 200
    atok = mint_test_id_token(provider="apple", email="aa@example.com", settings=svc.settings)
    al = client.post("/auth/login/apple", json={"id_token": atok})
    assert al.status_code == 200


def test_passwords_never_logged(svc: AuthService, caplog: pytest.LogCaptureFixture) -> None:
    from contextlib import suppress

    secret = "SuperSecretPassword!!99"
    with caplog.at_level(logging.DEBUG):
        svc.register("log@example.com", secret)
        with suppress(InvalidCredentials):
            svc.login("log@example.com", "wrong-wrong")
    joined = " ".join(r.message for r in caplog.records)
    assert secret not in joined
    assert "SuperSecret" not in joined


def test_revoke_refresh_helper(settings: AuthSettings) -> None:
    store = RevocationStore()
    tok = issue_refresh("u1", settings=settings)
    claims = verify_refresh(tok, settings=settings, store=store)
    revoke_refresh(claims.jti, store=store)
    with pytest.raises(TokenRevoked):
        verify_refresh(tok, settings=settings, store=store)


def test_conflict_register_duplicate(svc: AuthService) -> None:
    from tamthuc_auth.errors import ConflictError

    svc.register("dup@example.com", "password123")
    with pytest.raises(ConflictError):
        svc.register("dup@example.com", "password123")


def test_me_service_and_token_service(svc: AuthService) -> None:
    from contextlib import suppress

    reg = svc.register("me@example.com", "password123")
    pair = svc.login("me@example.com", "password123")
    profile = svc.me(pair.access)
    assert profile.user_id == reg.user_id
    cu = svc.current_user(pair.access)
    assert cu.email == "me@example.com"
    # TokenService facade
    pair2 = svc.tokens.issue_pair(str(reg.user_id), "free")
    assert verify_access(pair2["access"], settings=svc.settings).sub == str(reg.user_id)
    rotated = svc.tokens.rotate_refresh(pair2["refresh"])
    assert rotated["access"]
    with suppress(InvalidCredentials):
        svc.login("missing@x.com", "nope")


def test_store_update_and_clear(svc: AuthService) -> None:
    from tamthuc_auth.store import InMemoryUserStore, new_user

    store = InMemoryUserStore()
    u = new_user("s@example.com", password_hash="x")
    store.create(u)
    u2 = u.model_copy(update={"tier": "premium"})
    store.update(u2)
    assert store.get_by_id(u.id) is not None
    assert store.get_by_id(u.id).tier == "premium"  # type: ignore[union-attr]
    store.clear()
    assert store.get_by_email("s@example.com") is None


def test_config_master_key_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    import base64

    from tamthuc_auth.config import (
        AuthSettings,
        get_settings,
        master_key_from_env,
        reset_settings_cache,
    )

    reset_settings_cache()
    s = AuthSettings(
        jwt_secret="explicit-test-jwt-secret-at-least-32b!!",
        master_key_b64=base64.urlsafe_b64encode(b"z" * 32).decode(),
    )
    assert len(s.master_key()) == 32
    with pytest.raises(ValueError):
        AuthSettings(
            jwt_secret="explicit-test-jwt-secret-at-least-32b!!",
            master_key_b64=base64.urlsafe_b64encode(b"short").decode(),
        ).master_key()
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("TAMTHUC_AUTH_JWT_SECRET", "from-env-secret-at-least-32-bytes!!")
    monkeypatch.setenv(
        "TAMTHUC_AUTH_MASTER_KEY_B64",
        base64.urlsafe_b64encode(b"e" * 32).decode(),
    )
    reset_settings_cache()
    assert get_settings().jwt_secret == "from-env-secret-at-least-32-bytes!!"
    reset_settings_cache()
    assert len(master_key_from_env()) == 32


def test_config_refuses_defaults_outside_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    import base64

    from tamthuc_auth.config import AuthSettings, reset_settings_cache

    monkeypatch.setenv("ENV", "production")
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("TAMTHUC_AUTH_JWT_SECRET", raising=False)
    monkeypatch.delenv("TAMTHUC_AUTH_MASTER_KEY_B64", raising=False)
    reset_settings_cache()
    with pytest.raises(ValueError, match="required"):
        AuthSettings()

    with pytest.raises(ValueError, match="refusing known development"):
        AuthSettings(
            jwt_secret="dev-only-change-me-jwt-secret-min-32-bytes!!",
            master_key_b64=base64.urlsafe_b64encode(b"0" * 32).decode(),
        )


def test_config_allows_dev_placeholders_in_development(monkeypatch: pytest.MonkeyPatch) -> None:
    from tamthuc_auth.config import AuthSettings, reset_settings_cache

    monkeypatch.setenv("ENV", "development")
    monkeypatch.delenv("TAMTHUC_AUTH_JWT_SECRET", raising=False)
    monkeypatch.delenv("TAMTHUC_AUTH_MASTER_KEY_B64", raising=False)
    reset_settings_cache()
    s = AuthSettings()
    assert len(s.jwt_secret) >= 32
    assert len(s.master_key()) == 32


def test_deps_and_http_errors(client: TestClient, svc: AuthService) -> None:
    # no bearer
    r = client.get("/auth/me")
    assert r.status_code == 401
    # conflict via HTTP
    client.post("/auth/register", json={"email": "c@example.com", "password": "password123"})
    r2 = client.post("/auth/register", json={"email": "c@example.com", "password": "password123"})
    assert r2.status_code == 409
    # bad refresh
    r3 = client.post("/auth/refresh", json={"refresh": "nope"})
    assert r3.status_code == 401
    # bad social
    r4 = client.post("/auth/login/google", json={"id_token": "nope"})
    assert r4.status_code == 401
    r5 = client.post("/auth/login/apple", json={"id_token": "nope"})
    assert r5.status_code == 401


def test_password_empty_raises() -> None:
    with pytest.raises(ValueError):
        hash_password("")


def test_deps_missing_service_and_bad_token() -> None:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tamthuc_auth.routes import router

    bare = FastAPI()
    bare.include_router(router)
    c = TestClient(bare, raise_server_exceptions=False)
    # get_auth_service raises RuntimeError -> 500
    r = c.post("/auth/login", json={"email": "a@b.com", "password": "password123"})
    assert r.status_code >= 400

    # invalid bearer on configured app
    svc = AuthService(
        store=InMemoryUserStore(),
        settings=AuthSettings(
            jwt_secret="test-jwt-secret-at-least-32-bytes-long!!",
            master_key_b64=__import__("base64").urlsafe_b64encode(b"m" * 32).decode(),
        ),
    )
    app = create_auth_app(svc)
    c2 = TestClient(app)
    r2 = c2.get("/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert r2.status_code == 401
