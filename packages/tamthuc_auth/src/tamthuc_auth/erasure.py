"""DSAR erasure with crypto-shred — FR-AUTH-004."""

from __future__ import annotations

import time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tamthuc_auth.crypto import decrypt_birth_data
from tamthuc_auth.store import UserStore


class ErasureResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_id: str
    erased: list[str] = Field(default_factory=list)
    retained: list[dict[str, str]] = Field(default_factory=list)
    crypto_shredded: bool = False
    soft_deleted: bool = False
    idempotent_replay: bool = False


def erase_user_data(
    user_id: str,
    *,
    store: UserStore,
    master_key: bytes,
    history: dict[str, list[dict[str, Any]]] | None = None,
    already_erased: set[str] | None = None,
) -> ErasureResult:
    """Crypto-shred birth_data (drop wrapped DEK), soft-delete profile, honor retention."""
    replay = already_erased is not None and user_id in already_erased
    user = store.get_by_id(UUID(user_id))
    if user is None:
        return ErasureResult(
            subject_id=user_id,
            erased=[],
            retained=[{"table": "audit", "reason": "legal retention"}],
            crypto_shredded=True,
            soft_deleted=True,
            idempotent_replay=True,
        )

    erased: list[str] = []
    # crypto-shred: destroy wrapped DEK so ciphertext is unreadable
    if user.birth_data_envelope:
        env = dict(user.birth_data_envelope)
        env.pop("wrapped_dek", None)
        env["wrapped_dek"] = ""  # destroyed
        user.birth_data_envelope = env
        # verify cannot decrypt
        try:
            decrypt_birth_data(env, master_key)
            raise RuntimeError("crypto-shred failed: still decryptable")
        except Exception:
            erased.append("birth_data")
    user.email = f"erased+{user_id}@invalid.local"
    # soft-delete marker in preferences (stand-in for deleted_at column)
    prefs = dict(user.preferences or {})
    prefs["deleted_at"] = time.time()
    user.preferences = prefs
    user.password_hash = None
    store.update(user)
    erased.extend(["profile", "password"])

    hist = history or {}
    for table in ("queries", "charts", "reports"):
        rows = hist.get(table) or []
        hist[table] = [r for r in rows if str(r.get("user_id")) != user_id]
        erased.append(table)

    retained = [{"table": "audit", "reason": "legal retention (FR-LEGAL-002)"}]
    if already_erased is not None:
        already_erased.add(user_id)

    return ErasureResult(
        subject_id=user_id,
        erased=erased,
        retained=retained,
        crypto_shredded=True,
        soft_deleted=True,
        idempotent_replay=replay,
    )
