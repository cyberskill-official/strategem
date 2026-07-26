"""Unit tests for PayOS signature helpers (constant-time verify)."""

from __future__ import annotations

import pytest
from tamthuc_api.payos_webhook import (
    WebhookSignatureError,
    create_signature_from_object,
    create_signature_of_payment_request,
    verify_payos_signature,
)


def test_create_signature_from_object_stable() -> None:
    # Deterministic fixture only — not a real PayOS checksum key.
    key = "test-payos-checksum-fixture-not-a-secret"
    data = {
        "orderCode": 123,
        "amount": 3000,
        "description": "VQRIO123",
        "accountNumber": "12345678",
        "reference": "TF230204212323",
        "transactionDateTime": "2023-02-04 18:25:00",
        "currency": "VND",
        "paymentLinkId": "124c33293c43417ab7879e14c8d9eb18",
        "code": "00",
        "desc": "Thành công",
        "counterAccountBankId": "",
        "counterAccountBankName": "",
        "counterAccountName": "",
        "counterAccountNumber": "",
        "virtualAccountName": "",
        "virtualAccountNumber": "",
    }
    sig = create_signature_from_object(data, key)
    assert len(sig) == 64
    verify_payos_signature(data, sig, key)


def test_verify_rejects_tamper() -> None:
    key = "checksum_key"
    data = {"amount": 1, "orderCode": 2, "code": "00"}
    sig = create_signature_from_object(data, key)
    with pytest.raises(WebhookSignatureError) as ei:
        verify_payos_signature({**data, "amount": 2}, sig, key)
    assert ei.value.code == "WEBHOOK_BAD_SIG"


def test_payment_request_signature_format() -> None:
    key = "checksum_key"
    sig = create_signature_of_payment_request(
        amount=79000,
        cancel_url="http://localhost/cancel",
        description="Tam Thuc Premium",
        order_code=42,
        return_url="http://localhost/ok",
        checksum_key=key,
    )
    assert len(sig) == 64
