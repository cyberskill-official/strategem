"""DSAR orchestration — FR-AUTH-004."""

from __future__ import annotations

import time
from typing import Any

from tamthuc_auth.erasure import ErasureResult, erase_user_data
from tamthuc_auth.export import ArchiveDelivery, ArchiveStore, DsarArchive, export_user_data
from tamthuc_auth.store import UserStore

# Fresh auth window (seconds)
FRESH_AUTH_WINDOW_S = 300


class FreshAuthRequired(Exception):
    code = "FRESH_AUTH_REQUIRED"


class DsarService:
    def __init__(
        self,
        store: UserStore,
        master_key: bytes,
        *,
        archives: ArchiveStore | None = None,
    ) -> None:
        self.store = store
        self.master_key = master_key
        self.archives = archives or ArchiveStore()
        self._erased: set[str] = set()
        self._audit: list[dict[str, Any]] = []

    def _require_fresh(self, auth_iat: float | None) -> None:
        if auth_iat is None or (time.time() - auth_iat) > FRESH_AUTH_WINDOW_S:
            raise FreshAuthRequired("re-authentication required for DSAR")

    def export(
        self,
        user_id: str,
        *,
        auth_iat: float | None,
        history: dict[str, list[dict[str, Any]]] | None = None,
    ) -> tuple[ArchiveDelivery, DsarArchive]:
        self._require_fresh(auth_iat)
        archive = export_user_data(
            user_id,
            store=self.store,
            master_key=self.master_key,
            history=history,
        )
        delivery = self.archives.put(archive)
        # audit without payload
        self._audit.append(
            {
                "action": "dsar_export",
                "user_id": user_id,
                "archive_ref": delivery.archive_ref,
                # never copy archive payload
            }
        )
        return delivery, archive

    def erase(
        self,
        user_id: str,
        *,
        auth_iat: float | None,
        history: dict[str, list[dict[str, Any]]] | None = None,
    ) -> ErasureResult:
        self._require_fresh(auth_iat)
        result = erase_user_data(
            user_id,
            store=self.store,
            master_key=self.master_key,
            history=history,
            already_erased=self._erased,
        )
        self._audit.append(
            {
                "action": "dsar_erase",
                "user_id": user_id,
                "crypto_shredded": result.crypto_shredded,
            }
        )
        return result
