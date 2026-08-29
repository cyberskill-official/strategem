"""Runtime DB role guard — D-DB-001 / TASK-DB-001.

API connections must use a NOSUPERUSER NOBYPASSRLS role (``strategem_app``).
Privileged logins bypass FORCE ROW LEVEL SECURITY and defeat tenant isolation.
"""

from __future__ import annotations

import os
from typing import Any

import psycopg

_PRIVILEGED_MSG = (
    "DATABASE_URL must use a NOSUPERUSER NOBYPASSRLS runtime role "
    "(strategem_app). Apply migrations with a privileged role via "
    "DATABASE_URL_MIGRATE, then point DATABASE_URL at strategem_app. "
    "Set ALLOW_PRIVILEGED_DB=1 only for explicit break-glass."
)


def allow_privileged_db() -> bool:
    return os.environ.get("ALLOW_PRIVILEGED_DB", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def connection_is_privileged(conn: Any) -> bool:
    """Return True when current_user is superuser or has BYPASSRLS."""
    row = conn.execute(
        """
        SELECT rolsuper OR rolbypassrls
        FROM pg_roles
        WHERE oid = current_user::regrole
        """
    ).fetchone()
    return bool(row and row[0])


def assert_unprivileged_runtime_role(dsn: str) -> None:
    """Connect and raise RuntimeError if the login is privileged.

    Skipped when ``ALLOW_PRIVILEGED_DB=1`` (break-glass / some CI fixtures).
    """
    if allow_privileged_db():
        return
    with psycopg.connect(dsn) as conn:
        if connection_is_privileged(conn):
            raise RuntimeError(_PRIVILEGED_MSG)


__all__ = [
    "allow_privileged_db",
    "assert_unprivileged_runtime_role",
    "connection_is_privileged",
]
