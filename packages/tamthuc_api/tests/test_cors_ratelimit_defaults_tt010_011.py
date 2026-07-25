"""TT-010 CORS fail-closed; TT-011 rate-limit defaults."""

from __future__ import annotations

import pytest
from tamthuc_api.app import _cors_origins, _resolve_rate_limit, create_app


def test_cors_rejects_star(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.example.com,*")
    with pytest.raises(RuntimeError, match=r"\*"):
        _cors_origins()


def test_cors_required_outside_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        _cors_origins()


def test_cors_optional_in_test(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "test")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    assert _cors_origins() is None


def test_cors_parses_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://app.example.com, https://preview.example.com",
    )
    assert _cors_origins() == [
        "https://app.example.com",
        "https://preview.example.com",
    ]


def test_rate_limit_off_in_test_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "test")
    monkeypatch.delenv("ENABLE_RATE_LIMIT", raising=False)
    monkeypatch.delenv("DISABLE_RATE_LIMIT", raising=False)
    assert _resolve_rate_limit(None) is False


def test_rate_limit_on_in_production_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("ENABLE_RATE_LIMIT", raising=False)
    monkeypatch.delenv("DISABLE_RATE_LIMIT", raising=False)
    assert _resolve_rate_limit(None) is True


def test_create_app_prod_needs_cors(monkeypatch: pytest.MonkeyPatch) -> None:
    import base64

    from tamthuc_auth.config import reset_settings_cache

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv(
        "TAMTHUC_AUTH_JWT_SECRET",
        "prod-jwt-secret-at-least-32-bytes-long!!",
    )
    monkeypatch.setenv(
        "TAMTHUC_AUTH_MASTER_KEY_B64",
        base64.urlsafe_b64encode(b"p" * 32).decode("ascii"),
    )
    reset_settings_cache()
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        create_app()
