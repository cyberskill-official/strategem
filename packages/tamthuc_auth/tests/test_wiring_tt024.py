"""TT-024: durable auth wiring + fail-closed."""

from __future__ import annotations

import pytest
from tamthuc_auth.store import InMemoryUserStore
from tamthuc_auth.wiring import build_auth_service, require_auth_backend


def test_test_env_uses_memory_even_with_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.delenv("AUTH_USE_POSTGRES", raising=False)
    assert require_auth_backend() == "memory"
    svc = build_auth_service()
    assert isinstance(svc.store, InMemoryUserStore)


def test_prod_fail_closed_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("ALLOW_MEMORY_AUTH", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        require_auth_backend()


def test_dev_with_database_url_selects_postgres(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    assert require_auth_backend() == "postgres"
