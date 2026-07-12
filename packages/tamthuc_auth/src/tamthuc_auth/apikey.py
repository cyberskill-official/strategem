"""Enterprise API keys: issue (show once), hash at rest, resolve, revoke."""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass, field

from tamthuc_auth.rbac import Role
from tamthuc_auth.tiers import Principal

log = logging.getLogger("tamthuc_auth.apikey")


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class ApiKeyRecord:
    key_id: str
    account_id: str
    key_hash: str
    custom_quota: int
    revoked: bool = False
    created_at: float = field(default_factory=time.time)


class ApiKeyStore:
    def __init__(self) -> None:
        self._by_id: dict[str, ApiKeyRecord] = {}
        self._by_hash: dict[str, str] = {}  # hash -> key_id

    def issue(self, account_id: str, *, custom_quota: int = 50_000) -> tuple[str, str]:
        """Return (key_id, raw_key). raw_key shown once; only hash stored."""
        key_id = secrets.token_hex(8)
        raw = f"tt_{key_id}_{secrets.token_urlsafe(32)}"
        rec = ApiKeyRecord(
            key_id=key_id,
            account_id=account_id,
            key_hash=_hash_key(raw),
            custom_quota=custom_quota,
        )
        self._by_id[key_id] = rec
        self._by_hash[rec.key_hash] = key_id
        log.info("apikey.issued", extra={"key_id": key_id, "account_id": account_id})
        return key_id, raw

    def resolve(self, raw_key: str) -> Principal | None:
        h = _hash_key(raw_key)
        key_id = self._by_hash.get(h)
        if key_id is None:
            return None
        rec = self._by_id[key_id]
        if rec.revoked:
            return None
        return Principal(
            subject=f"apikey:{rec.key_id}",
            role=Role.enterprise,
            account_id=rec.account_id,
            enterprise_quota_override=rec.custom_quota,
            kind="api_key",
        )

    def revoke(self, key_id: str) -> None:
        rec = self._by_id.get(key_id)
        if rec is None:
            return
        rec.revoked = True
        log.info("apikey.revoked", extra={"key_id": key_id})

    def stored_plaintext_present(self) -> bool:
        """Security invariant: store must never hold raw keys."""
        for rec in self._by_id.values():
            if rec.key_hash.startswith("tt_"):
                return True
            if "tt_" in rec.key_hash and len(rec.key_hash) < 64:
                return True
        return False


_default_store = ApiKeyStore()


def issue_api_key(
    account_id: str, *, custom_quota: int = 50_000, store: ApiKeyStore | None = None
) -> tuple[str, str]:
    return (store or _default_store).issue(account_id, custom_quota=custom_quota)


def resolve_api_key(key: str, *, store: ApiKeyStore | None = None) -> Principal | None:
    return (store or _default_store).resolve(key)


def revoke_api_key(key_id: str, *, store: ApiKeyStore | None = None) -> None:
    (store or _default_store).revoke(key_id)


def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())
