"""Durable refresh-token revocation — TT-024.

Protocol matches in-memory RevocationStore; Postgres implementation uses
`refresh_token_revocations` (db/migrations/0013).
"""

from __future__ import annotations

import logging
import os
import time
from datetime import UTC, datetime
from typing import Any, Protocol

import psycopg

log = logging.getLogger("tamthuc_auth.revocation")


class RevocationStoreProtocol(Protocol):
    def revoke(self, jti: str, exp: float | None = None) -> None: ...
    def is_revoked(self, jti: str) -> bool: ...
    def clear(self) -> None: ...


class PostgresRevocationStore:
    """jti denylist backed by refresh_token_revocations."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    @classmethod
    def from_env(cls) -> PostgresRevocationStore | None:
        dsn = os.environ.get("DATABASE_URL")
        return cls(dsn) if dsn else None

    def revoke(self, jti: str, exp: float | None = None) -> None:
        expires = exp if exp is not None else time.time() + 86400 * 30
        expires_at = datetime.fromtimestamp(expires, tz=UTC)
        with psycopg.connect(self.dsn) as conn:
            conn.execute(
                """
                INSERT INTO refresh_token_revocations (jti, expires_at)
                VALUES (%s, %s)
                ON CONFLICT (jti) DO UPDATE SET expires_at = EXCLUDED.expires_at
                """,
                (jti, expires_at),
            )
            conn.commit()
        log.info("refresh.revoked", extra={"jti": jti})

    def is_revoked(self, jti: str) -> bool:
        with psycopg.connect(self.dsn) as conn:
            row = conn.execute(
                """
                SELECT 1 FROM refresh_token_revocations
                WHERE jti = %s AND expires_at > now()
                """,
                (jti,),
            ).fetchone()
        return row is not None

    def clear(self) -> None:
        with psycopg.connect(self.dsn) as conn:
            conn.execute("DELETE FROM refresh_token_revocations")
            conn.commit()


def prune_expired(dsn: str) -> int:
    """Delete expired revocation rows. Returns rows deleted."""
    with psycopg.connect(dsn) as conn:
        cur = conn.execute("DELETE FROM refresh_token_revocations WHERE expires_at <= now()")
        conn.commit()
        return int(cur.rowcount or 0)


# Silence unused Any import for type checkers that want Protocol helpers.
_ = Any
