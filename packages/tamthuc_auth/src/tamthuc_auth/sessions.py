"""Refresh-token families (sessions) — AUTH-001 follow-up.

Tracks one family per login. Rotation updates ``current_jti``; presenting a
non-current jti for an active family is reuse → revoke family.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row

log = logging.getLogger("tamthuc_auth.sessions")


@dataclass
class SessionRecord:
    id: str
    user_id: str
    current_jti: str
    expires_at: float
    created_at: float = field(default_factory=time.time)
    last_seen_at: float = field(default_factory=time.time)
    revoked_at: float | None = None
    reuse_detected_at: float | None = None
    label: str | None = None

    @property
    def active(self) -> bool:
        return self.revoked_at is None and self.expires_at > time.time()


class SessionReuseError(Exception):
    """Presented refresh jti is not current for its family (theft / replay)."""


class SessionStoreProtocol(Protocol):
    def create(
        self,
        user_id: str,
        jti: str,
        *,
        expires_at: float,
        label: str | None = None,
        family_id: str | None = None,
    ) -> SessionRecord: ...

    def get(self, family_id: str) -> SessionRecord | None: ...

    def rotate(
        self,
        family_id: str,
        presented_jti: str,
        new_jti: str,
        *,
        expires_at: float,
    ) -> SessionRecord: ...

    def list_active(self, user_id: str) -> list[SessionRecord]: ...

    def revoke(self, family_id: str, *, user_id: str | None = None) -> bool: ...

    def revoke_all(self, user_id: str) -> list[str]: ...

    def clear(self) -> None: ...


class InMemorySessionStore:
    def __init__(self) -> None:
        self._rows: dict[str, SessionRecord] = {}

    def create(
        self,
        user_id: str,
        jti: str,
        *,
        expires_at: float,
        label: str | None = None,
        family_id: str | None = None,
    ) -> SessionRecord:
        fid = family_id or str(uuid4())
        now = time.time()
        rec = SessionRecord(
            id=fid,
            user_id=user_id,
            current_jti=jti,
            expires_at=expires_at,
            created_at=now,
            last_seen_at=now,
            label=label,
        )
        self._rows[fid] = rec
        log.info("session.created", extra={"family_id": fid, "user_id": user_id})
        return rec

    def get(self, family_id: str) -> SessionRecord | None:
        return self._rows.get(family_id)

    def rotate(
        self,
        family_id: str,
        presented_jti: str,
        new_jti: str,
        *,
        expires_at: float,
    ) -> SessionRecord:
        rec = self._rows.get(family_id)
        if rec is None or rec.revoked_at is not None:
            raise SessionReuseError("family_missing_or_revoked")
        if rec.expires_at < time.time():
            raise SessionReuseError("family_expired")
        if rec.current_jti != presented_jti:
            rec.reuse_detected_at = time.time()
            rec.revoked_at = time.time()
            log.info("session.reuse_detected", extra={"family_id": family_id})
            raise SessionReuseError("jti_reuse")
        rec.current_jti = new_jti
        rec.expires_at = expires_at
        rec.last_seen_at = time.time()
        return rec

    def list_active(self, user_id: str) -> list[SessionRecord]:
        return [r for r in self._rows.values() if r.user_id == user_id and r.active]

    def revoke(self, family_id: str, *, user_id: str | None = None) -> bool:
        rec = self._rows.get(family_id)
        if rec is None:
            return False
        if user_id is not None and rec.user_id != user_id:
            return False
        if rec.revoked_at is None:
            rec.revoked_at = time.time()
            log.info("session.revoked", extra={"family_id": family_id})
        return True

    def revoke_all(self, user_id: str) -> list[str]:
        jtis: list[str] = []
        now = time.time()
        for rec in self._rows.values():
            if rec.user_id == user_id and rec.revoked_at is None:
                jtis.append(rec.current_jti)
                rec.revoked_at = now
        log.info("session.revoke_all", extra={"user_id": user_id, "count": len(jtis)})
        return jtis

    def clear(self) -> None:
        self._rows.clear()


class PostgresSessionStore:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    @classmethod
    def from_env(cls) -> PostgresSessionStore | None:
        dsn = os.environ.get("DATABASE_URL")
        return cls(dsn) if dsn else None

    def _conn(self) -> Any:
        return psycopg.connect(self.dsn, row_factory=dict_row)

    @staticmethod
    def _row(row: dict[str, Any]) -> SessionRecord:
        def _ts(v: Any) -> float:
            if isinstance(v, datetime):
                if v.tzinfo is None:
                    v = v.replace(tzinfo=UTC)
                return v.timestamp()
            return float(v)

        return SessionRecord(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            current_jti=str(row["current_jti"]),
            expires_at=_ts(row["expires_at"]),
            created_at=_ts(row["created_at"]),
            last_seen_at=_ts(row["last_seen_at"]),
            revoked_at=_ts(row["revoked_at"]) if row.get("revoked_at") else None,
            reuse_detected_at=_ts(row["reuse_detected_at"])
            if row.get("reuse_detected_at")
            else None,
            label=row.get("label"),
        )

    def create(
        self,
        user_id: str,
        jti: str,
        *,
        expires_at: float,
        label: str | None = None,
        family_id: str | None = None,
    ) -> SessionRecord:
        fid = UUID(family_id) if family_id else uuid4()
        exp = datetime.fromtimestamp(expires_at, tz=UTC)
        with self._conn() as conn:
            row = conn.execute(
                """
                INSERT INTO refresh_token_families (
                  id, user_id, current_jti, expires_at, label
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id, user_id, current_jti, expires_at, created_at,
                          last_seen_at, revoked_at, reuse_detected_at, label
                """,
                (fid, UUID(user_id), jti, exp, label),
            ).fetchone()
            conn.commit()
        assert row is not None
        log.info("session.created", extra={"family_id": str(fid), "user_id": user_id})
        return self._row(row)

    def get(self, family_id: str) -> SessionRecord | None:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT id, user_id, current_jti, expires_at, created_at,
                       last_seen_at, revoked_at, reuse_detected_at, label
                FROM refresh_token_families WHERE id = %s
                """,
                (UUID(family_id),),
            ).fetchone()
        return self._row(row) if row else None

    def rotate(
        self,
        family_id: str,
        presented_jti: str,
        new_jti: str,
        *,
        expires_at: float,
    ) -> SessionRecord:
        exp = datetime.fromtimestamp(expires_at, tz=UTC)
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT id, user_id, current_jti, expires_at, created_at,
                       last_seen_at, revoked_at, reuse_detected_at, label
                FROM refresh_token_families
                WHERE id = %s
                FOR UPDATE
                """,
                (UUID(family_id),),
            ).fetchone()
            if row is None or row.get("revoked_at") is not None:
                conn.rollback()
                raise SessionReuseError("family_missing_or_revoked")
            expires = row["expires_at"]
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=UTC)
            if expires.timestamp() < time.time():
                conn.rollback()
                raise SessionReuseError("family_expired")
            if str(row["current_jti"]) != presented_jti:
                conn.execute(
                    """
                    UPDATE refresh_token_families
                    SET revoked_at = now(), reuse_detected_at = now()
                    WHERE id = %s
                    """,
                    (UUID(family_id),),
                )
                conn.commit()
                log.info("session.reuse_detected", extra={"family_id": family_id})
                raise SessionReuseError("jti_reuse")
            updated = conn.execute(
                """
                UPDATE refresh_token_families
                SET current_jti = %s, expires_at = %s, last_seen_at = now()
                WHERE id = %s
                RETURNING id, user_id, current_jti, expires_at, created_at,
                          last_seen_at, revoked_at, reuse_detected_at, label
                """,
                (new_jti, exp, UUID(family_id)),
            ).fetchone()
            conn.commit()
        assert updated is not None
        return self._row(updated)

    def list_active(self, user_id: str) -> list[SessionRecord]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT id, user_id, current_jti, expires_at, created_at,
                       last_seen_at, revoked_at, reuse_detected_at, label
                FROM refresh_token_families
                WHERE user_id = %s AND revoked_at IS NULL AND expires_at > now()
                ORDER BY last_seen_at DESC
                """,
                (UUID(user_id),),
            ).fetchall()
        return [self._row(r) for r in rows]

    def revoke(self, family_id: str, *, user_id: str | None = None) -> bool:
        with self._conn() as conn:
            if user_id is not None:
                cur = conn.execute(
                    """
                    UPDATE refresh_token_families
                    SET revoked_at = now()
                    WHERE id = %s AND user_id = %s AND revoked_at IS NULL
                    """,
                    (UUID(family_id), UUID(user_id)),
                )
            else:
                cur = conn.execute(
                    """
                    UPDATE refresh_token_families
                    SET revoked_at = now()
                    WHERE id = %s AND revoked_at IS NULL
                    """,
                    (UUID(family_id),),
                )
            conn.commit()
            ok = int(cur.rowcount or 0) > 0
        if ok:
            log.info("session.revoked", extra={"family_id": family_id})
        return ok

    def revoke_all(self, user_id: str) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                UPDATE refresh_token_families
                SET revoked_at = now()
                WHERE user_id = %s AND revoked_at IS NULL
                RETURNING current_jti
                """,
                (UUID(user_id),),
            ).fetchall()
            conn.commit()
        jtis = [str(r["current_jti"]) for r in rows]
        log.info("session.revoke_all", extra={"user_id": user_id, "count": len(jtis)})
        return jtis

    def clear(self) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM refresh_token_families")
            conn.commit()


_default_sessions = InMemorySessionStore()


def get_session_store() -> InMemorySessionStore:
    return _default_sessions
