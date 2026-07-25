"""Stripe webhook signature verification (fail-closed).

Uses the Stripe signed-payload format without requiring the Stripe SDK:
  Stripe-Signature: t=<unix>,v1=<hex hmac-sha256>
  signed_payload = f"{t}.{raw_body}"
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass


class WebhookSignatureError(Exception):
    """Raised when the Stripe-Signature header is missing or invalid."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ParsedSignature:
    timestamp: int
    signatures: tuple[str, ...]


def parse_stripe_signature(header: str) -> ParsedSignature:
    """Parse `t=` and `v1=` items from a Stripe-Signature header."""
    timestamp: int | None = None
    signatures: list[str] = []
    for part in header.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, value = part.partition("=")
        key = key.strip()
        value = value.strip()
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError as e:
                raise WebhookSignatureError(
                    "WEBHOOK_BAD_SIG", "invalid stripe-signature timestamp"
                ) from e
        elif key == "v1" and value:
            signatures.append(value)
    if timestamp is None:
        raise WebhookSignatureError("WEBHOOK_BAD_SIG", "stripe-signature missing t=")
    if not signatures:
        raise WebhookSignatureError("WEBHOOK_BAD_SIG", "stripe-signature missing v1=")
    return ParsedSignature(timestamp=timestamp, signatures=tuple(signatures))


def verify_stripe_signature(
    payload: bytes,
    sig_header: str | None,
    secret: str,
    *,
    tolerance_seconds: int = 300,
    now: int | None = None,
) -> None:
    """Verify Stripe webhook HMAC over the raw body. Raises WebhookSignatureError."""
    if not secret:
        raise WebhookSignatureError("WEBHOOK_MISCONFIGURED", "STRIPE_WEBHOOK_SECRET unset")
    if not sig_header or not sig_header.strip():
        raise WebhookSignatureError("WEBHOOK_UNSIGNED", "missing stripe-signature")

    parsed = parse_stripe_signature(sig_header)
    clock = int(time.time()) if now is None else now
    if abs(clock - parsed.timestamp) > tolerance_seconds:
        raise WebhookSignatureError(
            "WEBHOOK_BAD_SIG", "stripe-signature timestamp outside tolerance"
        )

    signed_payload = f"{parsed.timestamp}.".encode() + payload
    expected = hmac.new(
        secret.encode(),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    if not any(hmac.compare_digest(expected, candidate) for candidate in parsed.signatures):
        raise WebhookSignatureError("WEBHOOK_BAD_SIG", "invalid webhook signature")
