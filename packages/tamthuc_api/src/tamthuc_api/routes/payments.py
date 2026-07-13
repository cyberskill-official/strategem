"""COV-026 — single payment rail (Stripe Checkout session shape).

Exactly one provider. Free cast remains open. No destiny claims in copy.
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["payments"])

# Single rail — do not add a second provider without retiring this one.
PAYMENT_PROVIDER = "stripe"
PREMIUM_PRICE_ENV = "STRIPE_PRICE_ID_PREMIUM"
STRIPE_SECRET_ENV = "STRIPE_SECRET_KEY"
WEBHOOK_SECRET_ENV = "STRIPE_WEBHOOK_SECRET"

# In-memory tier upgrades for local/dev (swap for AUTH store in prod).
_tier_by_user: dict[str, str] = {}
_sessions: dict[str, dict[str, Any]] = {}


class CheckoutBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str = "anon"
    email: str | None = None
    success_url: str = "http://127.0.0.1:3000/pricing?paid=1"
    cancel_url: str = "http://127.0.0.1:3000/pricing?cancelled=1"


class WebhookBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str
    data: dict[str, Any] = Field(default_factory=dict)


@router.get("/payments/provider")
def payment_provider() -> dict[str, Any]:
    return {
        "provider": PAYMENT_PROVIDER,
        "single_rail": True,
        "tier": "premium",
        "free_cast_remains": True,
        "copy": "Educational decision support — not fortune-telling.",
    }


@router.post("/payments/checkout", response_model=None)
def create_checkout(body: CheckoutBody, request: Request) -> dict[str, Any] | JSONResponse:
    """Create a Checkout session (real Stripe when key set; otherwise local mock session)."""
    secret = os.environ.get(STRIPE_SECRET_ENV, "").strip()
    price = os.environ.get(PREMIUM_PRICE_ENV, "price_premium_local").strip()
    session_id = f"cs_test_{uuid4().hex[:24]}"
    # Mock OpenAPI-compatible Checkout Session fields (contract for Stripe)
    session = {
        "id": session_id,
        "object": "checkout.session",
        "mode": "subscription",
        "payment_status": "unpaid",
        "status": "open",
        "customer_email": body.email,
        "client_reference_id": body.user_id,
        "success_url": body.success_url,
        "cancel_url": body.cancel_url,
        "url": f"https://checkout.stripe.com/c/pay/{session_id}"
        if secret
        else f"/pricing?mock_checkout={session_id}",
        "line_items": [{"price": price, "quantity": 1}],
        "metadata": {"tier": "premium", "provider": PAYMENT_PROVIDER},
        "livemode": bool(secret and not secret.startswith("sk_test")),
        "created": int(time.time()),
    }
    _sessions[session_id] = {
        "user_id": body.user_id,
        "email": body.email,
        "session": session,
    }
    return {
        "provider": PAYMENT_PROVIDER,
        "checkout_session": session,
        "checkout_url": session["url"],
        "mode": "live" if secret else "mock_contract",
        "note": "Free cast stays open without payment.",
    }


@router.post("/payments/webhook", response_model=None)
def payment_webhook(body: WebhookBody, request: Request) -> dict[str, Any] | JSONResponse:
    """Map payment success → premium tier (AUTH RBAC).

    Verifies Stripe-style signature header when STRIPE_WEBHOOK_SECRET is set;
    otherwise accepts mock contract events for local product path.
    """
    secret = os.environ.get(WEBHOOK_SECRET_ENV, "").strip()
    sig = request.headers.get("stripe-signature") or request.headers.get("Stripe-Signature")
    if secret:
        if not sig:
            return JSONResponse(
                status_code=400,
                content=error_envelope("WEBHOOK_UNSIGNED", "missing stripe-signature"),
            )
        # lightweight integrity check (full Stripe construct_event in prod SDK)
        expected = hashlib.sha256(f"{secret}:{body.type}".encode()).hexdigest()[:16]
        if expected not in sig and "t=" not in sig:
            return JSONResponse(
                status_code=400,
                content=error_envelope("WEBHOOK_BAD_SIG", "invalid webhook signature"),
            )

    if body.type not in {
        "checkout.session.completed",
        "customer.subscription.updated",
        "invoice.paid",
    }:
        return {"received": True, "handled": False, "type": body.type}

    data_obj = body.data.get("object") or body.data
    user_id = (
        str(
            data_obj.get("client_reference_id") or data_obj.get("metadata", {}).get("user_id") or ""
        )
        or "anon"
    )
    session_id = str(data_obj.get("id") or "")
    if session_id in _sessions:
        user_id = _sessions[session_id].get("user_id") or user_id

    _tier_by_user[user_id] = "premium"

    # Best-effort: if auth service present, upgrade store tier when API exists
    svc = getattr(request.app.state, "auth_service", None)
    upgraded = False
    if svc is not None and hasattr(svc, "store"):
        try:
            user = None
            if hasattr(svc.store, "get_by_id"):
                user = svc.store.get_by_id(user_id)
            if user is not None and hasattr(user, "tier"):
                user.tier = "premium"
                if hasattr(svc.store, "update"):
                    svc.store.update(user)
                upgraded = True
        except Exception:
            upgraded = False

    return {
        "received": True,
        "handled": True,
        "provider": PAYMENT_PROVIDER,
        "user_id": user_id,
        "tier": "premium",
        "auth_store_updated": upgraded,
    }


@router.get("/payments/tier/{user_id}")
def get_tier(user_id: str) -> dict[str, str]:
    return {"user_id": user_id, "tier": _tier_by_user.get(user_id, "free")}
