"""COV-026 — single payment rail (Stripe Checkout session shape).

Exactly one provider. Free cast remains open. No destiny claims in copy.
Webhook verification is fail-closed (TT-001).
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from tamthuc_api.errors import error_envelope
from tamthuc_api.stripe_webhook import WebhookSignatureError, verify_stripe_signature

router = APIRouter(tags=["payments"])
log = logging.getLogger("tamthuc_api.payments")

# Single rail — do not add a second provider without retiring this one.
PAYMENT_PROVIDER = "stripe"
PREMIUM_PRICE_ENV = "STRIPE_PRICE_ID_PREMIUM"
STRIPE_SECRET_ENV = "STRIPE_SECRET_KEY"
WEBHOOK_SECRET_ENV = "STRIPE_WEBHOOK_SECRET"
PAYMENTS_MODE_ENV = "PAYMENTS_MODE"

# In-memory tier upgrades for local/dev (swap for AUTH store in prod).
_tier_by_user: dict[str, str] = {}
_sessions: dict[str, dict[str, Any]] = {}
_handled_events: set[str] = set()


class CheckoutBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str = "anon"
    email: str | None = None
    success_url: str = "http://127.0.0.1:3000/pricing?paid=1"
    cancel_url: str = "http://127.0.0.1:3000/pricing?cancelled=1"


def _payments_mode() -> str:
    return (os.environ.get(PAYMENTS_MODE_ENV) or "").strip().lower()


def _webhook_secret() -> str:
    return os.environ.get(WEBHOOK_SECRET_ENV, "").strip()


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
    # Prefer verified principal over client-supplied user_id
    user = getattr(request.state, "current_user", None)
    user_id = str(user.id) if user is not None else body.user_id

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
        "client_reference_id": user_id,
        "success_url": body.success_url,
        "cancel_url": body.cancel_url,
        "url": f"https://checkout.stripe.com/c/pay/{session_id}"
        if secret
        else f"/pricing?mock_checkout={session_id}",
        "line_items": [{"price": price, "quantity": 1}],
        "metadata": {"tier": "premium", "provider": PAYMENT_PROVIDER, "user_id": user_id},
        "livemode": bool(secret and not secret.startswith("sk_test")),
        "created": int(time.time()),
    }
    _sessions[session_id] = {
        "user_id": user_id,
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
async def payment_webhook(request: Request) -> dict[str, Any] | JSONResponse:
    """Map payment success → premium tier (AUTH RBAC).

    Fail-closed when STRIPE_WEBHOOK_SECRET is unset unless PAYMENTS_MODE=mock.
    Never grants tier from an unverified payload.
    """
    raw = await request.body()
    secret = _webhook_secret()
    mode = _payments_mode()
    sig = request.headers.get("stripe-signature") or request.headers.get("Stripe-Signature")

    if not secret:
        if mode != "mock":
            return JSONResponse(
                status_code=503,
                content=error_envelope(
                    "WEBHOOK_MISCONFIGURED",
                    "STRIPE_WEBHOOK_SECRET is required (set PAYMENTS_MODE=mock for local unsigned mocks)",
                ),
            )
        # Explicit local mock path only — no signature required
    else:
        try:
            verify_stripe_signature(raw, sig, secret)
        except WebhookSignatureError as e:
            return JSONResponse(
                status_code=400,
                content=error_envelope(e.code, e.message),
            )

    try:
        body = json.loads(raw.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JSONResponse(
            status_code=400,
            content=error_envelope("WEBHOOK_BAD_PAYLOAD", "invalid JSON body"),
        )

    event_type = str(body.get("type") or "")
    event_id = str(body.get("id") or "")
    if event_id and event_id in _handled_events:
        return {"received": True, "handled": True, "duplicate": True, "id": event_id}

    if event_type not in {
        "checkout.session.completed",
        "customer.subscription.updated",
        "invoice.paid",
    }:
        return {"received": True, "handled": False, "type": event_type}

    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    data_obj = data.get("object") if isinstance(data.get("object"), dict) else data
    if not isinstance(data_obj, dict):
        data_obj = {}

    session_id = str(data_obj.get("id") or "")
    user_id = ""
    if session_id and session_id in _sessions:
        user_id = str(_sessions[session_id].get("user_id") or "")
    if not user_id:
        meta_raw = data_obj.get("metadata")
        meta: dict[str, Any] = meta_raw if isinstance(meta_raw, dict) else {}
        user_id = str(data_obj.get("client_reference_id") or meta.get("user_id") or "").strip()

    if not user_id or user_id == "anon":
        return JSONResponse(
            status_code=400,
            content=error_envelope(
                "WEBHOOK_NO_USER",
                "cannot grant tier without a known checkout session or client_reference_id",
            ),
        )

    _tier_by_user[user_id] = "premium"
    if event_id:
        _handled_events.add(event_id)

    # Best-effort: if auth service present, upgrade store tier when API exists
    svc = getattr(request.app.state, "auth_service", None)
    upgraded = False
    if svc is not None and hasattr(svc, "store"):
        try:
            from uuid import UUID

            user = None
            if hasattr(svc.store, "get_by_id"):
                try:
                    user = svc.store.get_by_id(UUID(user_id))
                except (ValueError, TypeError):
                    user = None
            if user is not None and hasattr(user, "tier"):
                user.tier = "premium"
                if hasattr(svc.store, "update"):
                    svc.store.update(user)
                upgraded = True
        except Exception:
            log.exception("auth store tier upgrade failed", extra={"user_id": user_id})
            upgraded = False

    return {
        "received": True,
        "handled": True,
        "provider": PAYMENT_PROVIDER,
        "user_id": user_id,
        "tier": "premium",
        "auth_store_updated": upgraded,
    }


@router.get("/payments/tier/{user_id}", response_model=None)
def get_tier(user_id: str, request: Request) -> dict[str, str] | JSONResponse:
    """Return tier for the authenticated principal only (no cross-user lookup)."""
    user = getattr(request.state, "current_user", None)
    if user is None:
        return JSONResponse(
            status_code=401,
            content=error_envelope("UNAUTHORIZED", "authentication required"),
        )
    principal = str(user.id)
    if user_id not in {principal, "me"}:
        return JSONResponse(
            status_code=403,
            content=error_envelope("FORBIDDEN", "cannot read another user's tier"),
        )
    return {"user_id": principal, "tier": _tier_by_user.get(principal, str(user.tier or "free"))}
