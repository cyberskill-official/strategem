"""Shared API test fixtures — auth secrets + development env (TT-003)."""

from __future__ import annotations

import base64

import pytest


@pytest.fixture(autouse=True)
def _auth_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure create_app / AuthService can boot in tests without production secrets."""
    monkeypatch.setenv("ENV", "test")
    # CI / local integration still often use postgres superuser DSN; production
    # compose and APP_ENV=production must use strategem_app (D-DB-001).
    monkeypatch.setenv("ALLOW_PRIVILEGED_DB", "1")
    monkeypatch.setenv(
        "TAMTHUC_AUTH_JWT_SECRET",
        "test-jwt-secret-at-least-32-bytes-long!!",
    )
    monkeypatch.setenv(
        "TAMTHUC_AUTH_MASTER_KEY_B64",
        base64.urlsafe_b64encode(b"t" * 32).decode("ascii"),
    )
    try:
        from tamthuc_auth.config import reset_settings_cache

        reset_settings_cache()
    except ImportError:
        pass
