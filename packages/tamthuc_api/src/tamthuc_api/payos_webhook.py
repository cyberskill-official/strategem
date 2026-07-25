"""PayOS webhook / payment-request signature verification (fail-closed).

Official algorithm (payOS docs — checksum key HMAC-SHA256):
  - Sort object keys alphabetically
  - Join as ``key=value&key2=value2`` (null/undefined → empty string)
  - HMAC-SHA256 hex digest with PAYOS_CHECKSUM_KEY

Comparison is constant-time via ``hmac.compare_digest``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


class WebhookSignatureError(Exception):
    """Raised when the PayOS signature is missing or invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _value_as_string(value: Any) -> str:
    # Match payOS official Python sample: int/float/bool → str(value)
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    if value is None or value in {"null", "NULL", "undefined"}:
        return ""
    if isinstance(value, list):
        sorted_items = [
            sort_obj_data_by_key(item) if isinstance(item, dict) else item for item in value
        ]
        return json.dumps(sorted_items, separators=(",", ":"), ensure_ascii=False).replace(
            "None", "null"
        )
    return str(value)


def sort_obj_data_by_key(obj: dict[str, Any]) -> dict[str, Any]:
    return dict(sorted(obj.items(), key=lambda kv: kv[0]))


def convert_obj_to_query_str(obj: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in obj.items():
        parts.append(f"{key}={_value_as_string(value)}")
    return "&".join(parts)


def create_signature_from_object(data: dict[str, Any], checksum_key: str) -> str:
    """HMAC-SHA256 over alphabetically sorted key=value query string."""
    if not checksum_key:
        raise WebhookSignatureError("WEBHOOK_MISCONFIGURED", "PAYOS_CHECKSUM_KEY unset")
    sorted_data = sort_obj_data_by_key(data)
    query = convert_obj_to_query_str(sorted_data)
    return hmac.new(
        checksum_key.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_signature_of_payment_request(
    *,
    amount: int,
    cancel_url: str,
    description: str,
    order_code: int,
    return_url: str,
    checksum_key: str,
) -> str:
    """Signature for POST /v2/payment-requests (fixed field order per payOS docs)."""
    if not checksum_key:
        raise WebhookSignatureError("WEBHOOK_MISCONFIGURED", "PAYOS_CHECKSUM_KEY unset")
    data = (
        f"amount={amount}&cancelUrl={cancel_url}&description={description}"
        f"&orderCode={order_code}&returnUrl={return_url}"
    )
    return hmac.new(
        checksum_key.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_payos_signature(
    data: dict[str, Any] | None,
    signature: str | None,
    checksum_key: str,
) -> None:
    """Verify PayOS webhook body signature. Raises WebhookSignatureError."""
    if not checksum_key:
        raise WebhookSignatureError("WEBHOOK_MISCONFIGURED", "PAYOS_CHECKSUM_KEY unset")
    if not signature or not str(signature).strip():
        raise WebhookSignatureError("WEBHOOK_UNSIGNED", "missing payOS signature")
    if not isinstance(data, dict) or not data:
        raise WebhookSignatureError("WEBHOOK_BAD_PAYLOAD", "webhook data object required")

    expected = create_signature_from_object(data, checksum_key)
    candidate = str(signature).strip().lower()
    if not hmac.compare_digest(expected.lower(), candidate):
        raise WebhookSignatureError("WEBHOOK_BAD_SIG", "invalid webhook signature")
