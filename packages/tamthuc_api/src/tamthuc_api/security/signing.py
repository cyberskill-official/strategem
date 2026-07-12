from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


def sign_envelope(envelope: dict[str, Any], secret: bytes) -> str:
    body = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(secret, body.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_envelope(envelope: dict[str, Any], signature: str, secret: bytes) -> bool:
    expected = sign_envelope(envelope, secret)
    return hmac.compare_digest(expected, signature)
