"""Postgres-backed UserStore — TT-024 durable identity.

Writes to the shared `users` table (db/migrations/0002 + 0012). Birth data is
stored as the AES-GCM envelope JSON in `birth_data` (never plaintext).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from tamthuc_auth.errors import ConflictError
from tamthuc_auth.models import UserRecord

log = logging.getLogger("tamthuc_auth.pg_store")


def database_url() -> str | None:
    return os.environ.get("DATABASE_URL") or None


class PostgresUserStore:
    """UserStore Protocol implementation over Postgres."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    @classmethod
    def from_env(cls) -> PostgresUserStore | None:
        dsn = database_url()
        return cls(dsn) if dsn else None

    def _conn(self) -> Any:
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _set_guc(self, conn: Any, user_id: UUID | None) -> None:
        # Owner RLS on users compares id to app.current_user_id.
        # Service paths (register/login by email) need admin or bypass;
        # production DSNs are typically table-owner/superuser which bypasses FORCE
        # for superuser only. Set GUC when we know the principal.
        if user_id is not None:
            conn.execute(
                "SELECT set_config('app.current_user_id', %s, true)",
                (str(user_id),),
            )

    def create(self, user: UserRecord) -> UserRecord:
        with self._conn() as conn:
            self._set_guc(conn, user.id)
            try:
                conn.execute(
                    """
                    INSERT INTO users (
                      id, email, password_hash, tier, email_verified, preferences,
                      birth_data, social_provider, social_subject, created_at, updated_at
                    ) VALUES (
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        user.id,
                        user.email.lower(),
                        user.password_hash,
                        user.tier,
                        user.email_verified,
                        Jsonb(user.preferences or {}),
                        Jsonb(user.birth_data_envelope)
                        if user.birth_data_envelope is not None
                        else None,
                        user.social_provider,
                        user.social_subject,
                        user.created_at,
                        user.updated_at,
                    ),
                )
                conn.commit()
            except psycopg.errors.UniqueViolation as e:
                conn.rollback()
                raise ConflictError("email already registered") from e
        log.info("user.created", extra={"user_id": str(user.id)})
        return user

    def get_by_id(self, user_id: UUID) -> UserRecord | None:
        with self._conn() as conn:
            self._set_guc(conn, user_id)
            row = conn.execute(
                """
                SELECT id, email, password_hash, tier, email_verified, preferences,
                       birth_data, social_provider, social_subject, created_at, updated_at,
                       deleted_at
                FROM users WHERE id = %s AND deleted_at IS NULL
                """,
                (user_id,),
            ).fetchone()
        return _row_to_user(row) if row else None

    def get_by_email(self, email: str) -> UserRecord | None:
        key = email.lower()
        with self._conn() as conn:
            # Lookup by email before we know id — rely on connection role bypass
            # or permissive SELECT for service account. Set a sentinel so owner
            # policy alone does not accidentally match.
            conn.execute("SELECT set_config('app.current_user_id', %s, true)", ("",))
            row = conn.execute(
                """
                SELECT id, email, password_hash, tier, email_verified, preferences,
                       birth_data, social_provider, social_subject, created_at, updated_at,
                       deleted_at
                FROM users WHERE lower(email::text) = %s AND deleted_at IS NULL
                """,
                (key,),
            ).fetchone()
        return _row_to_user(row) if row else None

    def update(self, user: UserRecord) -> UserRecord:
        with self._conn() as conn:
            self._set_guc(conn, user.id)
            cur = conn.execute(
                """
                UPDATE users SET
                  email = %s,
                  password_hash = %s,
                  tier = %s,
                  email_verified = %s,
                  preferences = %s,
                  birth_data = %s,
                  social_provider = %s,
                  social_subject = %s,
                  updated_at = %s
                WHERE id = %s AND deleted_at IS NULL
                """,
                (
                    user.email.lower(),
                    user.password_hash,
                    user.tier,
                    user.email_verified,
                    Jsonb(user.preferences or {}),
                    Jsonb(user.birth_data_envelope)
                    if user.birth_data_envelope is not None
                    else None,
                    user.social_provider,
                    user.social_subject,
                    user.updated_at
                    if user.updated_at.tzinfo
                    else user.updated_at.replace(tzinfo=UTC),
                    user.id,
                ),
            )
            if cur.rowcount == 0:
                conn.rollback()
                raise KeyError(user.id)
            conn.commit()
        return user


def _row_to_user(row: Any) -> UserRecord:
    prefs = row.get("preferences") or {}
    if isinstance(prefs, str):
        prefs = json.loads(prefs)
    birth = row.get("birth_data")
    if isinstance(birth, str):
        birth = json.loads(birth)
    return UserRecord(
        id=row["id"] if isinstance(row["id"], UUID) else UUID(str(row["id"])),
        email=str(row["email"]),
        password_hash=row.get("password_hash"),
        birth_data_envelope=dict(birth) if isinstance(birth, dict) else None,
        preferences=dict(prefs) if isinstance(prefs, dict) else {},
        email_verified=bool(row.get("email_verified")),
        tier=str(row.get("tier") or "free"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        social_provider=row.get("social_provider"),
        social_subject=row.get("social_subject"),
    )
