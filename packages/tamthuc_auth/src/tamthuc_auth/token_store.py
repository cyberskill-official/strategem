"""Hashed, single-use, expiring email tokens — TASK-AUTH-003."""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4

Purpose = Literal["email_verify", "password_reset"]


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


class EmailTokenStore:
    """In-memory stand-in for migrations/0002_email_tokens.sql."""

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


_store = EmailTokenStore()


def get_email_token_store() -> EmailTokenStore:
    return _store
