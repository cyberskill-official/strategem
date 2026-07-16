"""DSAR export — TASK-AUTH-004."""

from __future__ import annotations

import time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tamthuc_auth.crypto import decrypt_birth_data
from tamthuc_auth.store import UserStore


class DsarArchive(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_id: str
    exported_at: float
    profile: dict[str, Any]
    queries: list[dict[str, Any]] = Field(default_factory=list)
    charts: list[dict[str, Any]] = Field(default_factory=list)
    reports: list[dict[str, Any]] = Field(default_factory=list)
    audit: list[dict[str, Any]] = Field(default_factory=list)


class ArchiveDelivery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    archive_ref: str
    expires_at: float
    token: str


class ArchiveStore:
    """Authenticated, time-limited archive delivery (never public URL)."""

    def __init__(self) -> None:
        self._archives: dict[str, tuple[DsarArchive, float, str]] = {}

    def put(self, archive: DsarArchive, *, ttl_s: int = 900) -> ArchiveDelivery:
        import secrets

        token = secrets.token_urlsafe(24)
        ref = f"dsar:{archive.subject_id}:{int(time.time())}"
        exp = time.time() + ttl_s
        self._archives[ref] = (archive, exp, token)
        return ArchiveDelivery(archive_ref=ref, expires_at=exp, token=token)

    def get(self, archive_ref: str, token: str) -> DsarArchive | None:
        row = self._archives.get(archive_ref)
        if row is None:
            return None
        archive, exp, tok = row
        if time.time() > exp:
            return None
        if tok != token:
            return None
        return archive


def export_user_data(
    user_id: str,
    *,
    store: UserStore,
    master_key: bytes,
    history: dict[str, list[dict[str, Any]]] | None = None,
    other_users_guard: set[str] | None = None,
) -> DsarArchive:
    """Gather subject-scoped data; decrypt birth_data for the subject only."""
    user = store.get_by_id(UUID(user_id))
    if user is None:
        raise KeyError(user_id)
    birth: dict[str, Any] | None = None
    if user.birth_data_envelope:
        birth = decrypt_birth_data(user.birth_data_envelope, master_key)
    hist = history or {}

    # RLS-style filter: only this user's rows
    def scoped(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = [r for r in rows if str(r.get("user_id") or r.get("subject_id")) == user_id]
        if other_users_guard:
            for r in out:
                if str(r.get("user_id")) in other_users_guard and str(r.get("user_id")) != user_id:
                    raise RuntimeError("cross-user leakage")
        return out

    return DsarArchive(
        subject_id=user_id,
        exported_at=time.time(),
        profile={
            "email": user.email,
            "tier": user.tier,
            "email_verified": user.email_verified,
            "birth_data": birth,
        },
        queries=scoped(hist.get("queries") or []),
        charts=scoped(hist.get("charts") or []),
        reports=scoped(hist.get("reports") or []),
        audit=scoped(hist.get("audit") or []),
    )
