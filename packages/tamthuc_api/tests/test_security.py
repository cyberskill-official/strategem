from __future__ import annotations

import pytest
from tamthuc_api.security.headers import security_headers
from tamthuc_api.security.signing import sign_envelope, verify_envelope
from tamthuc_api.security.validation import ValidationError, validate_query_input


def test_security_headers_tls13_hsts() -> None:
    h = security_headers()
    assert h["X-TLS-Min-Version"] == "1.3"
    assert "max-age=" in h["Strict-Transport-Security"]
    assert h["X-Content-Type-Options"] == "nosniff"


def test_validation_rejects_injection_and_bad() -> None:
    ok = validate_query_input(
        {"datetime": "2020-01-01T10:00:00", "question": "career?", "longitude": 106.7}
    )
    assert ok.longitude == 106.7
    with pytest.raises(ValidationError) as e:
        validate_query_input(
            {
                "datetime": "2020-01-01T10:00:00",
                "question": "x; DROP TABLE users",
                "longitude": 0,
            }
        )
    assert e.value.to_envelope()["error"]["code"] == "validation_error"
    with pytest.raises(ValidationError):
        validate_query_input({"datetime": "x", "question": "q", "longitude": 999})


def test_signed_envelope_tamper_detected() -> None:
    secret = b"test-secret-key-32-bytes-minimum!!"
    env = {"he": "ky_mon", "envelope_version": 1}
    sig = sign_envelope(env, secret)
    assert verify_envelope(env, sig, secret)
    env2 = dict(env)
    env2["he"] = "luc_nham"
    assert not verify_envelope(env2, sig, secret)
