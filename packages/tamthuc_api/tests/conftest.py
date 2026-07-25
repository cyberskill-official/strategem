"""API test fixtures — apply DB migrations when DATABASE_URL is set (CI / W2)."""

from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _migrate_postgres_if_configured() -> None:
    """Ensure PLAT-003 + app_query_store exist before Postgres-backed API tests."""
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        return
    try:
        from db_schema.migrate import apply_migrations

        apply_migrations(dsn)
    except Exception:
        # Individual tests skip when Postgres is unreachable.
        return
