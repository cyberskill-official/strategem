"""TT-001: Stripe webhook signature — fail-closed + negative cases."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

from auth_helpers import auth_header, register_and_login
from fastapi.testclient import TestClient
from tamthuc_api.app import create_app


def _sign(secret: str, payload: bytes, ts: int | None = None) -> str:
    timestamp = int(time.time()) if ts is None else ts
    signed = f"{timestamp}.".encode() + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def test_webhook_fails_closed_without_secret(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    monkeypatch.delenv("PAYMENTS_MODE", raising=False)
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/payments/webhook",
        content=json.dumps(
            {
                "type": "checkout.session.completed",
                "data": {"object": {"id": "cs_x", "client_reference_id": "u1"}},
            }
        ).encode(),
        headers={"Content-Type": "application/json", "stripe-signature": "t=1"},
    )
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "WEBHOOK_MISCONFIGURED"


def test_webhook_rejects_t_only_signature(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    client = TestClient(create_app())
    payload = json.dumps(
        {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_x", "client_reference_id": "u1"}},
        }
    ).encode()
    r = client.post(
        "/api/v1/payments/webhook",
        content=payload,
        headers={"Content-Type": "application/json", "stripe-signature": "t=1"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "WEBHOOK_BAD_SIG"


def test_webhook_rejects_missing_signature(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/payments/webhook",
        content=b'{"type":"checkout.session.completed","data":{"object":{}}}',
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "WEBHOOK_UNSIGNED"


def test_webhook_rejects_wrong_hmac(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    client = TestClient(create_app())
    payload = json.dumps(
        {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_x", "client_reference_id": "u1"}},
        }
    ).encode()
    bad = _sign("wrong_secret", payload)
    r = client.post(
        "/api/v1/payments/webhook",
        content=payload,
        headers={"Content-Type": "application/json", "stripe-signature": bad},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "WEBHOOK_BAD_SIG"


def test_webhook_accepts_valid_hmac_and_grants_tier(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    secret = "whsec_test_secret"
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", secret)
    client = TestClient(create_app())
    tokens = register_and_login(client, email="pay@example.com")
    me = client.get("/auth/me", headers=auth_header(tokens["access"]))
    uid = me.json()["user_id"]

    co = client.post(
        "/api/v1/payments/checkout",
        headers=auth_header(tokens["access"]),
        json={"email": "pay@example.com"},
    )
    assert co.status_code == 200, co.text
    sid = co.json()["checkout_session"]["id"]

    payload = json.dumps(
        {
            "id": "evt_test_1",
            "type": "checkout.session.completed",
            "data": {"object": {"id": sid, "client_reference_id": uid}},
        }
    ).encode()
    sig = _sign(secret, payload)
    wh = client.post(
        "/api/v1/payments/webhook",
        content=payload,
        headers={"Content-Type": "application/json", "stripe-signature": sig},
    )
    assert wh.status_code == 200, wh.text
    assert wh.json()["tier"] == "premium"
    assert wh.json()["user_id"] == uid

    tier = client.get(
        f"/api/v1/payments/tier/{uid}",
        headers=auth_header(tokens["access"]),
    )
    assert tier.status_code == 200
    assert tier.json()["tier"] == "premium"
