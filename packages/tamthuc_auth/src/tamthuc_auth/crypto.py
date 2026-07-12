"""AES-256-GCM envelope encryption for birth_data with wrapped DEK (FR-AUTH-001)."""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

log = logging.getLogger("tamthuc_auth.crypto")

ALG = "AES-256-GCM"
# Simple wrap: master_key AES-GCM encrypts the DEK (same class as data encryption).
_WRAP_AAD = b"tamthuc-auth-dek-v1"


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text.encode("ascii"))


def _wrap_dek(dek: bytes, master_key: bytes) -> str:
    if len(master_key) != 32:
        raise ValueError("master_key must be 32 bytes")
    iv = os.urandom(12)
    ct = AESGCM(master_key).encrypt(iv, dek, _WRAP_AAD)
    # ct includes trailing 16-byte tag
    return _b64e(iv + ct)


def _unwrap_dek(wrapped: str, master_key: bytes) -> bytes:
    blob = _b64d(wrapped)
    iv, ct = blob[:12], blob[12:]
    return AESGCM(master_key).decrypt(iv, ct, _WRAP_AAD)


def encrypt_birth_data(plaintext: dict[str, Any], master_key: bytes) -> dict[str, str]:
    """Encrypt birth_data; returns envelope with no plaintext fields."""
    if len(master_key) != 32:
        raise ValueError("master_key must be 32 bytes")
    if not isinstance(plaintext, dict):
        raise TypeError("plaintext must be a dict")
    # Refuse empty / non-JSON-serializable payloads
    payload = json.dumps(plaintext, sort_keys=True, separators=(",", ":")).encode("utf-8")
    dek = AESGCM.generate_key(bit_length=256)
    iv = os.urandom(12)
    packed = AESGCM(dek).encrypt(iv, payload, None)
    ct, tag = packed[:-16], packed[-16:]
    envelope = {
        "alg": ALG,
        "iv": _b64e(iv),
        "ct": _b64e(ct),
        "tag": _b64e(tag),
        "wrapped_dek": _wrap_dek(dek, master_key),
    }
    log.info("birth_data.encrypted", extra={"bytes": len(ct)})
    return envelope


def decrypt_birth_data(envelope: dict[str, Any], master_key: bytes) -> dict[str, Any]:
    if envelope.get("alg") != ALG:
        raise ValueError("unsupported envelope alg")
    dek = _unwrap_dek(str(envelope["wrapped_dek"]), master_key)
    iv = _b64d(str(envelope["iv"]))
    ct = _b64d(str(envelope["ct"]))
    tag = _b64d(str(envelope["tag"]))
    packed = ct + tag
    raw = AESGCM(dek).decrypt(iv, packed, None)
    out: dict[str, Any] = json.loads(raw.decode("utf-8"))
    log.info("birth_data.decrypted")
    return out


def rewrap_dek(envelope: dict[str, Any], old_master: bytes, new_master: bytes) -> dict[str, Any]:
    """Key-rotation path: re-wrap DEK without re-encrypting the payload."""
    dek = _unwrap_dek(str(envelope["wrapped_dek"]), old_master)
    rotated = dict(envelope)
    rotated["wrapped_dek"] = _wrap_dek(dek, new_master)
    return rotated
