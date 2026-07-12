"""AES-256-GCM envelope tests (FR-AUTH-001 §4.5, §5)."""

from __future__ import annotations

import base64

import pytest
from cryptography.exceptions import InvalidTag
from tamthuc_auth.crypto import decrypt_birth_data, encrypt_birth_data, rewrap_dek

MASTER = b"k" * 32
OTHER = b"o" * 32
PLAIN = {
    "date": "1990-05-01",
    "time": "10:30",
    "place": "Ha Noi",
    "tz": "+07:00",
    "kinh_do": 105.85,
}


def test_round_trip() -> None:
    env = encrypt_birth_data(PLAIN, MASTER)
    assert decrypt_birth_data(env, MASTER) == PLAIN


def test_envelope_has_no_plaintext_fields() -> None:
    env = encrypt_birth_data(PLAIN, MASTER)
    blob = str(env)
    assert "1990-05-01" not in blob
    assert "Ha Noi" not in blob
    assert env["alg"] == "AES-256-GCM"
    for k in ("iv", "ct", "tag", "wrapped_dek"):
        assert k in env
        # base64-ish
        base64.urlsafe_b64decode(env[k].encode("ascii"))


def test_wrong_master_key_fails_gcm() -> None:
    env = encrypt_birth_data(PLAIN, MASTER)
    with pytest.raises(InvalidTag):
        decrypt_birth_data(env, OTHER)


def test_rewrap_dek_without_reencrypt() -> None:
    env = encrypt_birth_data(PLAIN, MASTER)
    rotated = rewrap_dek(env, MASTER, OTHER)
    assert rotated["ct"] == env["ct"]
    assert rotated["iv"] == env["iv"]
    assert rotated["wrapped_dek"] != env["wrapped_dek"]
    assert decrypt_birth_data(rotated, OTHER) == PLAIN
    with pytest.raises(InvalidTag):
        decrypt_birth_data(rotated, MASTER)


def test_master_key_length() -> None:
    with pytest.raises(ValueError):
        encrypt_birth_data(PLAIN, b"short")
