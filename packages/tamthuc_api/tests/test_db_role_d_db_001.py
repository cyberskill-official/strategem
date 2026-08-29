"""D-DB-001: startup rejects privileged DATABASE_URL; restricted role ok."""

from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse

import psycopg
import pytest
from db_schema.migrate import apply_migrations
from db_schema.runtime_role import assert_unprivileged_runtime_role
from tamthuc_api.persistence import PersistenceService


def _require_live_dsn() -> str:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        pytest.skip("DATABASE_URL not set")
    try:
        with psycopg.connect(dsn) as conn:
            conn.execute("SELECT 1")
    except psycopg.OperationalError as exc:
        pytest.skip(f"Postgres not reachable via DATABASE_URL: {exc}")
    return dsn


def _app_dsn(super_dsn: str) -> str:
    parsed = urlparse(super_dsn)
    host = parsed.hostname or "localhost"
    port = f":{parsed.port}" if parsed.port else ""
    app_netloc = f"strategem_app:strategem_app@{host}{port}"
    return urlunparse((parsed.scheme, app_netloc, parsed.path, "", parsed.query, parsed.fragment))


def test_assert_rejects_superuser_without_break_glass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dsn = _require_live_dsn()
    monkeypatch.delenv("ALLOW_PRIVILEGED_DB", raising=False)
    # CI DATABASE_URL is postgres superuser — must fail closed.
    with pytest.raises(RuntimeError, match="NOSUPERUSER NOBYPASSRLS"):
        assert_unprivileged_runtime_role(dsn)


def test_assert_allows_break_glass(monkeypatch: pytest.MonkeyPatch) -> None:
    dsn = _require_live_dsn()
    monkeypatch.setenv("ALLOW_PRIVILEGED_DB", "1")
    assert_unprivileged_runtime_role(dsn)  # no raise


def test_persistence_from_env_rejects_privileged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dsn = _require_live_dsn()
    monkeypatch.setenv("DATABASE_URL", dsn)
    monkeypatch.delenv("ALLOW_PRIVILEGED_DB", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    with pytest.raises(RuntimeError, match="NOSUPERUSER NOBYPASSRLS"):
        PersistenceService.from_env()


def test_persistence_accepts_strategem_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """Restricted LOGIN from 0017 passes the startup guard."""
    dsn = _require_live_dsn()
    apply_migrations(dsn)
    app_dsn = _app_dsn(dsn)
    # Prove login works before PersistenceService wiring.
    with psycopg.connect(app_dsn) as conn:
        row = conn.execute(
            "SELECT rolsuper, rolbypassrls, rolcreatedb FROM pg_roles "
            "WHERE oid = current_user::regrole"
        ).fetchone()
        assert row is not None
        assert row[0] is False and row[1] is False and row[2] is False

    monkeypatch.delenv("ALLOW_PRIVILEGED_DB", raising=False)
    monkeypatch.setenv("DATABASE_URL", app_dsn)
    monkeypatch.delenv("APP_ENV", raising=False)
    svc = PersistenceService.from_env()
    assert svc.backend == "postgres"
    assert svc.pg is not None
