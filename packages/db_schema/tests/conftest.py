"""Postgres fixtures for FR-PLAT-003. Skip when DATABASE_URL is unset."""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator

import psycopg
import pytest
from db_schema.migrate import apply_migrations


def _dsn() -> str | None:
    return os.environ.get("DATABASE_URL")


@pytest.fixture(scope="session")
def database_url() -> str:
    dsn = _dsn()
    if not dsn:
        pytest.skip("DATABASE_URL not set — skipping Postgres integration tests")
    return dsn


@pytest.fixture(scope="session")
def migrated_db(database_url: str) -> str:
    """Drop public schema objects and re-apply migrations once per session."""
    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS public CASCADE")
        conn.execute("CREATE SCHEMA public")
        conn.execute("GRANT ALL ON SCHEMA public TO public")
    apply_migrations(database_url)
    return database_url


@pytest.fixture
def conn(migrated_db: str) -> Iterator[psycopg.Connection]:
    with psycopg.connect(migrated_db, autocommit=False) as c:
        yield c
        c.rollback()


@pytest.fixture
def user_ids() -> tuple[uuid.UUID, uuid.UUID]:
    return (
        uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
    )
