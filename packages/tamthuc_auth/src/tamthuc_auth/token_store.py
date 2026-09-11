"""Hashed, single-use, expiring email tokens — TASK-AUTH-003 / AUTH-001 follow-up.

In-memory store for unit tests; PostgresEmailTokenStore for DATABASE_URL deployments
(db/migrations/0018_email_tokens.sql).
"""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row

Purpose = Literal["email_verify", "password_reset"]

log = logging.getLogger("tamthuc_auth.token_store")


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class EmailTokenRecord:
    id: str
    user_id: str
    purpose: Purpose
    token_hash: str
    expires_at: float
    consumed_at: float | None = None
    created_at: float = field(default_factory=time.time)


class EmailTokenStoreProtocol(Protocol):
    def issue(
        self,
        user_id: str,
        purpose: Purpose,
        *,
        ttl_s: int = 3600,
        invalidate_priors: bool = True,
    ) -> str: ...

    def invalidate_outstanding(self, user_id: str, purpose: Purpose) -> int: ...

    def consume(self, raw: str, purpose: Purpose) -> EmailTokenRecord: ...

    def has_plaintext(self) -> bool: ...

    def clear(self) -> None: ...


class EmailTokenStore:
    """In-memory stand-in for migrations/0002_email_tokens.sql / 0018_email_tokens."""

    def __init__(self) -> None:
        self._rows: dict[str, EmailTokenRecord] = {}  # id -> row
        self._by_hash: dict[str, str] = {}  # hash -> id

    def issue(
        self,
        user_id: str,
        purpose: Purpose,
        *,
        ttl_s: int = 3600,
        invalidate_priors: bool = True,
    ) -> str:
        if invalidate_priors:
            self.invalidate_outstanding(user_id, purpose)
        raw = secrets.token_urlsafe(32)
        th = hash_token(raw)
        rec = EmailTokenRecord(
            id=str(uuid4()),
            user_id=user_id,
            purpose=purpose,
            token_hash=th,
            expires_at=time.time() + ttl_s,
        )
        self._rows[rec.id] = rec
        self._by_hash[th] = rec.id
        return raw  # returned once; never stored

    def invalidate_outstanding(self, user_id: str, purpose: Purpose) -> int:
        n = 0
        for rec in list(self._rows.values()):
            if rec.user_id == user_id and rec.purpose == purpose and rec.consumed_at is None:
                rec.consumed_at = time.time()
                n += 1
        return n

    def consume(self, raw: str, purpose: Purpose) -> EmailTokenRecord:
        th = hash_token(raw)
        rid = self._by_hash.get(th)
        if rid is None:
            raise ValueError("invalid_token")
        rec = self._rows[rid]
        if rec.purpose != purpose:
            raise ValueError("invalid_token")
        if rec.consumed_at is not None:
            raise ValueError("token_used")
        if rec.expires_at < time.time():
            raise ValueError("token_expired")
        rec.consumed_at = time.time()
        return rec

    def has_plaintext(self) -> bool:
        """Security: store never holds raw tokens (only hashes)."""
        return False

    def clear(self) -> None:
        self._rows.clear()
        self._by_hash.clear()


class PostgresEmailTokenStore:
    """Durable email tokens backed by ``email_tokens`` (db/migrations/0018)."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    @classmethod
    def from_env(cls) -> PostgresEmailTokenStore | None:
        dsn = os.environ.get("DATABASE_URL")
        return cls(dsn) if dsn else None

    def issue(
        self,
        user_id: str,
        purpose: Purpose,
        *,
        ttl_s: int = 3600,
        invalidate_priors: bool = True,
    ) -> str:
        if invalidate_priors:
            self.invalidate_outstanding(user_id, purpose)
        raw = secrets.token_urlsafe(32)
        th = hash_token(raw)
        token_id = uuid4()
        expires = datetime.fromtimestamp(time.time() + ttl_s, tz=UTC)
        with psycopg.connect(self.dsn) as conn:
            conn.execute(
                """
                INSERT INTO email_tokens (id, user_id, purpose, token_hash, expires_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (token_id, UUID(user_id), purpose, th, expires),
            )
            conn.commit()
        log.info("email_token.issued", extra={"purpose": purpose, "user_id": user_id})
        return raw

    def invalidate_outstanding(self, user_id: str, purpose: Purpose) -> int:
        with psycopg.connect(self.dsn) as conn:
            cur = conn.execute(
                """
                UPDATE email_tokens
                SET consumed_at = now()
                WHERE user_id = %s AND purpose = %s AND consumed_at IS NULL
                """,
                (UUID(user_id), purpose),
            )
            conn.commit()
            return int(cur.rowcount or 0)

    def consume(self, raw: str, purpose: Purpose) -> EmailTokenRecord:
        th = hash_token(raw)
        with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                """
                SELECT id, user_id, purpose, token_hash, expires_at, consumed_at, created_at
                FROM email_tokens
                WHERE token_hash = %s
                FOR UPDATE
                """,
                (th,),
            ).fetchone()
            if row is None:
                conn.rollback()
                raise ValueError("invalid_token")
            if str(row["purpose"]) != purpose:
                conn.rollback()
                raise ValueError("invalid_token")
            if row["consumed_at"] is not None:
                conn.rollback()
                raise ValueError("token_used")
            expires = row["expires_at"]
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=UTC)
            if expires.timestamp() < time.time():
                conn.rollback()
                raise ValueError("token_expired")
            conn.execute(
                "UPDATE email_tokens SET consumed_at = now() WHERE id = %s",
                (row["id"],),
            )
            conn.commit()
            consumed = time.time()
            created = row["created_at"]
            if created.tzinfo is None:
                created = created.replace(tzinfo=UTC)
            return EmailTokenRecord(
                id=str(row["id"]),
                user_id=str(row["user_id"]),
                purpose=purpose,
                token_hash=str(row["token_hash"]),
                expires_at=expires.timestamp(),
                consumed_at=consumed,
                created_at=created.timestamp(),
            )

    def has_plaintext(self) -> bool:
        return False

    def clear(self) -> None:
        with psycopg.connect(self.dsn) as conn:
            conn.execute("DELETE FROM email_tokens")
            conn.commit()


_store = EmailTokenStore()


def get_email_token_store() -> EmailTokenStore:
    return _store
