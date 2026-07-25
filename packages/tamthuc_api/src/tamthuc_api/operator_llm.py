"""Operator BYOK LLM settings store (encrypted API key; never return raw keys)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

log = logging.getLogger("tamthuc_api.operator_llm")

# In-memory fallback when DATABASE_URL unset (dev/tests).
_memory_active: dict[str, Any] | None = None


@dataclass(frozen=True)
class OperatorLlmConfig:
    provider_base_url: str
    model_id: str
    backend: str
    has_api_key: bool
    api_key_masked: str | None
    # Decrypted key only for server-side LLM client construction — never serialize.
    api_key: str | None = None


def _mask_key(raw: str | None) -> str | None:
    if not raw:
        return None
    if len(raw) <= 8:
        return "********"
    return f"{raw[:4]}…{raw[-4:]}"


def _master_key() -> bytes:
    from tamthuc_auth.config import get_settings

    return get_settings().master_key()


def _encrypt_secret(plaintext: str) -> dict[str, str]:
    from tamthuc_auth.crypto import encrypt_birth_data

    return encrypt_birth_data({"api_key": plaintext}, _master_key())


def _decrypt_secret(envelope: dict[str, Any] | None) -> str | None:
    if not envelope:
        return None
    from tamthuc_auth.crypto import decrypt_birth_data

    try:
        data = decrypt_birth_data(envelope, _master_key())
    except Exception:
        log.exception("operator llm key decrypt failed")
        return None
    key = data.get("api_key")
    return str(key) if key else None


def get_active_config(*, include_secret: bool = False) -> OperatorLlmConfig | None:
    """Load active operator settings. Raw key only when include_secret=True (server use)."""
    global _memory_active
    database_url = (os.environ.get("DATABASE_URL") or "").strip()
    row: dict[str, Any] | None = None
    if database_url:
        try:
            import psycopg
            from psycopg.rows import dict_row

            with (
                psycopg.connect(database_url, row_factory=dict_row) as conn,
                conn.cursor() as cur,
            ):
                cur.execute(
                    """
                    SELECT provider_base_url, model_id, backend, api_key_envelope
                    FROM operator_llm_settings
                    WHERE effective_to IS NULL
                    ORDER BY effective_from DESC
                    LIMIT 1
                    """
                )
                fetched = cur.fetchone()
                if fetched:
                    row = dict(fetched)
        except Exception:
            log.exception("operator_llm_settings read failed")
            row = None
    elif _memory_active is not None:
        row = dict(_memory_active)

    if row is None:
        return None

    envelope = row.get("api_key_envelope")
    if isinstance(envelope, str):
        import json

        try:
            envelope = json.loads(envelope)
        except json.JSONDecodeError:
            envelope = None
    secret = _decrypt_secret(envelope if isinstance(envelope, dict) else None)
    return OperatorLlmConfig(
        provider_base_url=str(row.get("provider_base_url") or ""),
        model_id=str(row.get("model_id") or ""),
        backend=str(row.get("backend") or "openai_compatible"),
        has_api_key=bool(secret),
        api_key_masked=_mask_key(secret),
        api_key=secret if include_secret else None,
    )


def upsert_config(
    *,
    provider_base_url: str,
    model_id: str,
    backend: str,
    api_key: str | None,
    updated_by: UUID | None,
    clear_api_key: bool = False,
) -> OperatorLlmConfig:
    """Create a new active row; supersede previous. Never log api_key."""
    global _memory_active
    envelope: dict[str, str] | None = None
    if clear_api_key:
        envelope = None
    elif api_key:
        envelope = _encrypt_secret(api_key)
    else:
        # Preserve existing key when not provided
        prev = get_active_config(include_secret=True)
        if prev and prev.api_key:
            envelope = _encrypt_secret(prev.api_key)

    database_url = (os.environ.get("DATABASE_URL") or "").strip()
    if database_url:
        try:
            import json

            import psycopg

            with (
                psycopg.connect(database_url) as conn,
                conn.cursor() as cur,
            ):
                cur.execute(
                    """
                    UPDATE operator_llm_settings
                    SET effective_to = now()
                    WHERE effective_to IS NULL
                    """
                )
                cur.execute(
                    """
                    INSERT INTO operator_llm_settings
                      (id, provider_base_url, model_id, api_key_envelope, backend, updated_by)
                    VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                    """,
                    (
                        str(uuid4()),
                        provider_base_url,
                        model_id,
                        json.dumps(envelope) if envelope else None,
                        backend,
                        str(updated_by) if updated_by else None,
                    ),
                )
                conn.commit()
        except Exception:
            log.exception("operator_llm_settings write failed")
            raise
    else:
        _memory_active = {
            "provider_base_url": provider_base_url,
            "model_id": model_id,
            "backend": backend,
            "api_key_envelope": envelope,
        }

    cfg = get_active_config(include_secret=False)
    assert cfg is not None
    return cfg


def public_view(cfg: OperatorLlmConfig) -> dict[str, Any]:
    """Safe client payload — never includes raw api_key."""
    return {
        "provider_base_url": cfg.provider_base_url,
        "model_id": cfg.model_id,
        "backend": cfg.backend,
        "has_api_key": cfg.has_api_key,
        "api_key_masked": cfg.api_key_masked,
    }


def reset_memory_for_tests() -> None:
    global _memory_active
    _memory_active = None
