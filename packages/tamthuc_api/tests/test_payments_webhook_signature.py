"""PayOS webhook signature — fail-closed + negative cases + tier grant."""

from __future__ import annotations

import json

from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app
from tamthuc_api.payos_webhook import create_signature_from_object


def _webhook_body(data: dict, checksum_key: str, *, code: str = "00") -> bytes:
    signature = create_signature_from_object(data, checksum_key)
    return json.dumps(
        {
            "code": code,
            "desc": "success",
            "success": True,
            "data": data,
            "signature": signature,
        }
    ).encode()


def test_webhook_fails_closed_without_secret(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("PAYOS_CHECKSUM_KEY", raising=False)
    monkeypatch.delenv("PAYMENTS_MODE", raising=False)
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/payments/webhook",
        content=json.dumps(
            {
                "code": "00",
                "success": True,
                "data": {"orderCode": 1, "code": "00"},
                "signature": "x",
            }
        ).encode(),
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "WEBHOOK_MISCONFIGURED"


def test_webhook_rejects_missing_signature(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("PAYOS_CHECKSUM_KEY", "checksum_test_secret")
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/payments/webhook",
        content=json.dumps(
            {
                "code": "00",
                "success": True,
                "data": {"orderCode": 1, "amount": 1000, "code": "00"},
            }
        ).encode(),
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "WEBHOOK_UNSIGNED"


def test_webhook_rejects_wrong_hmac(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("PAYOS_CHECKSUM_KEY", "checksum_test_secret")
    client = TestClient(create_app())
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
    bad = json.dumps(
        {
            "code": "00",
            "success": True,
            "data": data,
            "signature": "0" * 64,
        }
    ).encode()
    r = client.post(
        "/api/v1/payments/webhook",
        content=bad,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "WEBHOOK_BAD_SIG"


def test_webhook_accepts_valid_hmac_and_grants_tier(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    secret = "checksum_test_secret"
    monkeypatch.setenv("PAYOS_CHECKSUM_KEY", secret)
    monkeypatch.setenv("PAYMENTS_MODE", "live")
    monkeypatch.setenv("PAYOS_CLIENT_ID", "client")
    monkeypatch.setenv("PAYOS_API_KEY", "key")
    client = TestClient(create_app())
    tokens = register_and_login(client, email="pay@example.com")
    me = client.get("/auth/me", headers=auth_header(tokens["access"]))
    uid = me.json()["user_id"]

    # Force mock checkout path by clearing live credentials after login
    monkeypatch.setenv("PAYMENTS_MODE", "mock")
    monkeypatch.delenv("PAYOS_CLIENT_ID", raising=False)
    monkeypatch.delenv("PAYOS_API_KEY", raising=False)
    co = client.post(
        "/api/v1/payments/checkout",
        headers=auth_header(tokens["access"]),
        json={"email": "pay@example.com"},
    )
    assert co.status_code == 200, co.text
    assert co.json()["provider"] == "payos"
    assert co.json()["mode"] == "mock_contract"
    sid = co.json()["checkout_session"]["paymentLinkId"]
    order = co.json()["order_code"]

    # Signed webhook (checksum required even after mock checkout)
    monkeypatch.setenv("PAYOS_CHECKSUM_KEY", secret)
    monkeypatch.delenv("PAYMENTS_MODE", raising=False)
    data = {
        "orderCode": order,
        "amount": 79000,
        "description": "Tam Thuc Premium",
        "accountNumber": "",
        "reference": "REF_TEST_1",
        "transactionDateTime": "2026-07-26 01:00:00",
        "currency": "VND",
        "paymentLinkId": sid,
        "code": "00",
        "desc": "Thành công",
        "counterAccountBankId": "",
        "counterAccountBankName": "",
        "counterAccountName": "",
        "counterAccountNumber": "",
        "virtualAccountName": "",
        "virtualAccountNumber": "",
    }
    payload = _webhook_body(data, secret)
    wh = client.post(
        "/api/v1/payments/webhook",
        content=payload,
        headers={"Content-Type": "application/json"},
    )
    assert wh.status_code == 200, wh.text
    assert wh.json()["tier"] == "premium"
    assert wh.json()["user_id"] == uid

    # Replay is idempotent
    wh2 = client.post(
        "/api/v1/payments/webhook",
        content=payload,
        headers={"Content-Type": "application/json"},
    )
    assert wh2.status_code == 200
    assert wh2.json().get("duplicate") is True

    tier = client.get(
        f"/api/v1/payments/tier/{uid}",
        headers=auth_header(tokens["access"]),
    )
    assert tier.status_code == 200
    assert tier.json()["tier"] == "premium"


def test_provider_is_payos_single_rail(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("PAYMENTS_MODE", "mock")
    client = TestClient(create_app())
    r = client.get("/api/v1/payments/provider")
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "payos"
    assert body["single_rail"] is True
    assert body["free_cast_remains"] is True


def test_mock_complete_upgrades_tier(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("PAYMENTS_MODE", "mock")
    client = TestClient(create_app())
    tokens = register_and_login(client, email="mockpay@example.com")
    r = client.post(
        "/api/v1/payments/mock-complete",
        headers=auth_header(tokens["access"]),
    )
    assert r.status_code == 200
    assert r.json()["tier"] == "premium"
