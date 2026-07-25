"""Route authz — verified JWT only; explicit public allowlist (TT-002)."""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from tamthuc_api.errors import error_envelope

# Exact public paths (unversioned ops + OpenAPI).
_PUBLIC_EXACT: frozenset[str] = frozenset(
    {
        "/healthz",
        "/ready",
        "/openapi.json",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
    }
)

# Versioned (and unversioned) public API path suffixes after /api/vN or absolute.
_PUBLIC_API_SUFFIXES: frozenset[str] = frozenset(
    {
        # Free cast demo (COV-009) — intentional anonymous surface
        "/calculate/qimen",
        "/calculate/liuren",
        "/calculate/taiyi",
        # Supporting free-cast UX
        "/calendar/convert",
        # Educational / knowledge (read-mostly, no entitlement)
        "/knowledge/patterns",
        "/knowledge/graph/neighbors",
        "/knowledge/graph/nodes",
        "/edu/library",
        "/edu/onboarding",
        "/edu/practice/grade",
        # Payments: provider is marketing; webhook uses Stripe signature
        "/payments/provider",
        "/payments/webhook",
    }
)

_AUTH_PUBLIC_PREFIXES: tuple[str, ...] = (
    "/auth/register",
    "/auth/login",
    "/auth/refresh",
)

_API_PREFIX_RE = re.compile(r"^/api/v\d+")


def auth_required_enabled() -> bool:
    """REQUIRE_AUTH defaults on; set REQUIRE_AUTH=0 only for explicit break-glass."""
    raw = os.environ.get("REQUIRE_AUTH", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _api_suffix(path: str) -> str | None:
    m = _API_PREFIX_RE.match(path)
    if not m:
        return None
    return path[m.end() :] or "/"


def is_public_path(path: str) -> bool:
    if path in _PUBLIC_EXACT or path.startswith("/docs"):
        return True
    for prefix in _AUTH_PUBLIC_PREFIXES:
        if path == prefix or path.startswith(prefix + "/"):
            return True
    # /auth/me and other /auth/* stay protected via their own Depends
    if path.startswith("/auth/"):
        return False
    suffix = _api_suffix(path)
    if suffix is not None and suffix in _PUBLIC_API_SUFFIXES:
        return True
    return path in _PUBLIC_API_SUFFIXES


def _bearer_token(request: Request) -> str | None:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return None
    scheme, _, rest = auth.partition(" ")
    if scheme.lower() != "bearer" or not rest.strip():
        return None
    return rest.strip()


def resolve_principal(request: Request) -> tuple[str, str] | None:
    """Return (principal_id, tier) from verified JWT when present and valid."""
    user = getattr(request.state, "current_user", None)
    if user is not None:
        return str(user.id), str(getattr(user, "tier", None) or "free").lower()
    token = _bearer_token(request)
    if not token:
        return None
    svc = getattr(request.app.state, "auth_service", None)
    if svc is None:
        return None
    try:
        current = svc.current_user(token)
    except Exception:
        return None
    request.state.current_user = current
    return str(current.id), str(current.tier or "free").lower()


class RequireAuthMiddleware(BaseHTTPMiddleware):
    """401 on non-public routes without a valid Bearer token."""

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        if not auth_required_enabled() or is_public_path(request.url.path):
            # Still attach principal when a valid token is present (rate limit / soft gates)
            resolve_principal(request)
            resp = await call_next(request)
            return resp  # type: ignore[no-any-return]

        token = _bearer_token(request)
        if token is None:
            return JSONResponse(
                status_code=401,
                content=error_envelope("UNAUTHORIZED", "authentication required"),
            )
        svc = getattr(request.app.state, "auth_service", None)
        if svc is None:
            return JSONResponse(
                status_code=503,
                content=error_envelope("INTERNAL", "auth service unavailable"),
            )
        try:
            user = svc.current_user(token)
        except Exception:
            return JSONResponse(
                status_code=401,
                content=error_envelope("UNAUTHORIZED", "authentication failed"),
            )
        request.state.current_user = user
        resp = await call_next(request)
        return resp  # type: ignore[no-any-return]
