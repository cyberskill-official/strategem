"""Single payment rail — PayOS (VN QR / bank transfer / e-wallets behind one API).

Exactly one provider. Free cast remains open. No destiny claims in copy.
Webhook verification is fail-closed. Fulfillment is durable-idempotent when
DATABASE_URL is set (payment_fulfillments table).
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from tamthuc_api.errors import error_envelope
from tamthuc_api.payos_webhook import (
    WebhookSignatureError,
    create_signature_of_payment_request,
    verify_payos_signature,
)

router = APIRouter(tags=["payments"])
log = logging.getLogger("tamthuc_api.payments")

# Single rail — do not add a second provider without retiring this one.
PAYMENT_PROVIDER = "payos"
PAYOS_CLIENT_ID_ENV = "PAYOS_CLIENT_ID"
PAYOS_API_KEY_ENV = "PAYOS_API_KEY"
PAYOS_CHECKSUM_KEY_ENV = "PAYOS_CHECKSUM_KEY"
PAYOS_AMOUNT_ENV = "PAYOS_PREMIUM_AMOUNT_VND"
PAYOS_API_BASE = "https://api-merchant.payos.vn"
PAYMENTS_MODE_ENV = "PAYMENTS_MODE"

# In-memory fallbacks (tests / memory persistence).
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


def _checksum_key() -> str:
    return os.environ.get(PAYOS_CHECKSUM_KEY_ENV, "").strip()


def _payos_credentials() -> tuple[str, str, str]:
    return (
        os.environ.get(PAYOS_CLIENT_ID_ENV, "").strip(),
        os.environ.get(PAYOS_API_KEY_ENV, "").strip(),
        _checksum_key(),
    )


def _premium_amount_vnd() -> int:
    raw = (os.environ.get(PAYOS_AMOUNT_ENV) or "79000").strip()
    try:
        amount = int(raw)
    except ValueError:
        amount = 79000
    return max(2000, amount)  # payOS minimum floor for QR


def _is_mock_mode() -> bool:
    mode = _payments_mode()
    if mode == "mock":
        return True
    client_id, api_key, checksum = _payos_credentials()
    return not (client_id and api_key and checksum)


def _event_key(body: dict[str, Any], data_obj: dict[str, Any]) -> str:
    """Durable idempotency key: prefer paymentLinkId+reference, else orderCode."""
    link = str(data_obj.get("paymentLinkId") or "").strip()
    ref = str(data_obj.get("reference") or "").strip()
    order = str(data_obj.get("orderCode") or body.get("id") or "").strip()
    if link and ref:
        return f"payos:{link}:{ref}"
    if link:
        return f"payos:{link}"
    if order:
        return f"payos:order:{order}"
    return f"payos:hash:{hash(json.dumps(body, sort_keys=True))}"


def _already_fulfilled(event_key: str) -> bool:
    if event_key in _handled_events:
        return True
    database_url = (os.environ.get("DATABASE_URL") or "").strip()
    if not database_url:
        return False
    try:
        import psycopg

        with psycopg.connect(database_url) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM payment_fulfillments WHERE event_key = %s",
                (event_key,),
            )
            return cur.fetchone() is not None
    except Exception:
        log.exception("payment_fulfillments lookup failed")
        return False


def _record_fulfillment(event_key: str, user_id: str) -> None:
    _handled_events.add(event_key)
    database_url = (os.environ.get("DATABASE_URL") or "").strip()
    if not database_url:
        return
    try:
        import psycopg

        with psycopg.connect(database_url) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO payment_fulfillments (event_key, user_id, provider)
                VALUES (%s, %s::uuid, %s)
                ON CONFLICT (event_key) DO NOTHING
                """,
                (event_key, user_id, PAYMENT_PROVIDER),
            )
            conn.commit()
    except Exception:
        log.exception("payment_fulfillments insert failed", extra={"event_key": event_key})


def _upgrade_tier(request: Request, user_id: str) -> bool:
    _tier_by_user[user_id] = "premium"
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
    return upgraded


def _create_payos_payment_link(
    *,
    order_code: int,
    amount: int,
    description: str,
    return_url: str,
    cancel_url: str,
    buyer_email: str | None,
    user_id: str,
) -> dict[str, Any]:
    client_id, api_key, checksum = _payos_credentials()
    signature = create_signature_of_payment_request(
        amount=amount,
        cancel_url=cancel_url,
        description=description,
        order_code=order_code,
        return_url=return_url,
        checksum_key=checksum,
    )
    payload = {
        "orderCode": order_code,
        "amount": amount,
        "description": description,
        "returnUrl": return_url,
        "cancelUrl": cancel_url,
        "signature": signature,
        "buyerEmail": buyer_email or "",
        "items": [
            {
                "name": "Tam Thuc Premium",
                "quantity": 1,
                "price": amount,
            }
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{PAYOS_API_BASE}/v2/payment-requests",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-client-id": client_id,
            "x-api-key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        raise RuntimeError(f"payos_http_{e.code}: {detail[:400]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"payos_unreachable: {e.reason}") from e

    parsed = json.loads(raw)
    data = parsed.get("data") if isinstance(parsed, dict) else None
    if not isinstance(data, dict) or not data.get("checkoutUrl"):
        raise RuntimeError(f"payos_bad_response: {raw[:400]}")
    data = dict(data)
    data["metadata"] = {"tier": "premium", "provider": PAYMENT_PROVIDER, "user_id": user_id}
    return data


@router.get("/payments/provider")
def payment_provider() -> dict[str, Any]:
    return {
        "provider": PAYMENT_PROVIDER,
        "single_rail": True,
        "tier": "premium",
        "free_cast_remains": True,
        "methods_copy": ["MoMo", "ZaloPay", "chuyen_khoan", "QR"],
        "copy": "Educational decision support — not fortune-telling.",
        "mode": "mock" if _is_mock_mode() else "live",
    }


@router.post("/payments/checkout", response_model=None)
def create_checkout(body: CheckoutBody, request: Request) -> dict[str, Any] | JSONResponse:
    """Create a PayOS payment link (or local mock session)."""
    user = getattr(request.state, "current_user", None)
    user_id = str(user.id) if user is not None else body.user_id
    if user is None:
        return JSONResponse(
            status_code=401,
            content=error_envelope("UNAUTHORIZED", "authentication required"),
        )

    amount = _premium_amount_vnd()
    order_code = int(time.time()) % 1_000_000_000
    description = "Tam Thuc Premium"

    if _is_mock_mode():
        session_id = f"payos_mock_{uuid4().hex[:20]}"
        checkout_url = f"/pricing?mock_checkout={session_id}"
        session = {
            "id": session_id,
            "orderCode": order_code,
            "amount": amount,
            "description": description,
            "paymentLinkId": session_id,
            "status": "PENDING",
            "checkoutUrl": checkout_url,
            "qrCode": None,
            "currency": "VND",
            "metadata": {"tier": "premium", "provider": PAYMENT_PROVIDER, "user_id": user_id},
            "created": int(time.time()),
        }
        _sessions[session_id] = {"user_id": user_id, "email": body.email, "session": session}
        # Mock path also accepts a follow-up mock webhook with orderCode mapping
        _sessions[str(order_code)] = {"user_id": user_id, "email": body.email, "session": session}
        return {
            "provider": PAYMENT_PROVIDER,
            "checkout_session": session,
            "checkout_url": checkout_url,
            "qr_code": None,
            "order_code": order_code,
            "amount": amount,
            "currency": "VND",
            "mode": "mock_contract",
            "note": "Free cast stays open without payment. PAYMENTS_MODE=mock.",
        }

    try:
        data = _create_payos_payment_link(
            order_code=order_code,
            amount=amount,
            description=description,
            return_url=body.success_url,
            cancel_url=body.cancel_url,
            buyer_email=body.email,
            user_id=user_id,
        )
    except Exception:
        log.exception("payos checkout failed")
        return JSONResponse(
            status_code=502,
            content=error_envelope("PAYOS_CHECKOUT_FAILED", "could not create PayOS payment link"),
        )

    link_id = str(data.get("paymentLinkId") or data.get("id") or order_code)
    _sessions[link_id] = {"user_id": user_id, "email": body.email, "session": data}
    _sessions[str(order_code)] = {"user_id": user_id, "email": body.email, "session": data}
    return {
        "provider": PAYMENT_PROVIDER,
        "checkout_session": data,
        "checkout_url": data.get("checkoutUrl"),
        "qr_code": data.get("qrCode"),
        "order_code": order_code,
        "amount": amount,
        "currency": "VND",
        "mode": "live",
        "note": "Free cast stays open without payment.",
    }


@router.post("/payments/webhook", response_model=None)
async def payment_webhook(request: Request) -> dict[str, Any] | JSONResponse:
    """Map PayOS payment success → premium tier (AUTH RBAC).

    Fail-closed when PAYOS_CHECKSUM_KEY is unset unless PAYMENTS_MODE=mock.
    Never grants tier from an unverified payload.
    """
    raw = await request.body()
    secret = _checksum_key()
    mode = _payments_mode()

    try:
        body = json.loads(raw.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JSONResponse(
            status_code=400,
            content=error_envelope("WEBHOOK_BAD_PAYLOAD", "invalid JSON body"),
        )
    if not isinstance(body, dict):
        return JSONResponse(
            status_code=400,
            content=error_envelope("WEBHOOK_BAD_PAYLOAD", "invalid JSON object"),
        )

    data_obj = body.get("data") if isinstance(body.get("data"), dict) else {}
    if not isinstance(data_obj, dict):
        data_obj = {}
    signature = body.get("signature")
    if signature is None:
        signature = request.headers.get("x-payos-signature") or request.headers.get(
            "X-PayOS-Signature"
        )

    if not secret:
        if mode != "mock":
            return JSONResponse(
                status_code=503,
                content=error_envelope(
                    "WEBHOOK_MISCONFIGURED",
                    "PAYOS_CHECKSUM_KEY is required (set PAYMENTS_MODE=mock for local unsigned mocks)",
                ),
            )
    else:
        try:
            verify_payos_signature(data_obj, str(signature) if signature else None, secret)
        except WebhookSignatureError as e:
            return JSONResponse(
                status_code=400,
                content=error_envelope(e.code, e.message),
            )

    # payOS success: code == "00" on envelope and/or data
    envelope_code = str(body.get("code") or "")
    data_code = str(data_obj.get("code") or "")
    success_flag = body.get("success") is True
    paid = success_flag or envelope_code == "00" or data_code == "00"
    if not paid:
        return {"received": True, "handled": False, "reason": "not_paid", "code": envelope_code}

    event_key = _event_key(body, data_obj)
    if _already_fulfilled(event_key):
        return {"received": True, "handled": True, "duplicate": True, "id": event_key}

    # Resolve user from session map, then metadata / description fallback
    user_id = ""
    link_id = str(data_obj.get("paymentLinkId") or "").strip()
    order_code = str(data_obj.get("orderCode") or "").strip()
    for key in (link_id, order_code):
        if key and key in _sessions:
            user_id = str(_sessions[key].get("user_id") or "")
            if user_id:
                break
    if not user_id:
        meta_raw = data_obj.get("metadata")
        meta: dict[str, Any] = meta_raw if isinstance(meta_raw, dict) else {}
        user_id = str(meta.get("user_id") or "").strip()
    if not user_id:
        # Description may carry user uuid in mock; refuse otherwise
        desc = str(data_obj.get("description") or "")
        if desc.startswith("uid:"):
            user_id = desc.removeprefix("uid:").strip()

    if not user_id or user_id == "anon":
        return JSONResponse(
            status_code=400,
            content=error_envelope(
                "WEBHOOK_NO_USER",
                "cannot grant tier without a known checkout session or metadata.user_id",
            ),
        )

    upgraded = _upgrade_tier(request, user_id)
    _record_fulfillment(event_key, user_id)

    return {
        "received": True,
        "handled": True,
        "provider": PAYMENT_PROVIDER,
        "user_id": user_id,
        "tier": "premium",
        "auth_store_updated": upgraded,
        "event_key": event_key,
    }


@router.post("/payments/mock-complete", response_model=None)
def mock_complete_checkout(request: Request) -> dict[str, Any] | JSONResponse:
    """Local-only: complete the latest mock checkout for the authenticated user."""
    if _payments_mode() != "mock" and not _is_mock_mode():
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", "mock-complete only available in mock mode"),
        )
    user = getattr(request.state, "current_user", None)
    if user is None:
        return JSONResponse(
            status_code=401,
            content=error_envelope("UNAUTHORIZED", "authentication required"),
        )
    user_id = str(user.id)
    upgraded = _upgrade_tier(request, user_id)
    event_key = f"payos:mock:{user_id}:{int(time.time())}"
    _record_fulfillment(event_key, user_id)
    return {
        "received": True,
        "handled": True,
        "provider": PAYMENT_PROVIDER,
        "user_id": user_id,
        "tier": "premium",
        "auth_store_updated": upgraded,
        "mode": "mock",
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
