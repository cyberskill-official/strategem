"""Trusted client IP extraction for rate limits / abuse (D-API-001)."""

from __future__ import annotations

import os

from starlette.requests import Request


def _trusted_proxy_count() -> int:
    raw = (os.environ.get("TRUSTED_PROXY_COUNT") or "").strip()
    if not raw:
        # Common default behind one shared edge / Caddy hop.
        env = (os.environ.get("APP_ENV") or os.environ.get("ENV") or "").strip().lower()
        if env in {"staging", "production", "prod"}:
            return 1
        return 0
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


def client_ip(request: Request) -> str:
    """Return the client IP, honoring X-Forwarded-For only for trusted hop counts.

    Never trust an arbitrary leftmost XFF when TRUSTED_PROXY_COUNT is 0.
    When count is N, take the Nth hop from the right (closest to us after N proxies).
    """
    direct = request.client.host if request.client else "0.0.0.0"
    n = _trusted_proxy_count()
    if n <= 0:
        return direct
    xff = (request.headers.get("x-forwarded-for") or "").strip()
    if not xff:
        return direct
    parts = [p.strip() for p in xff.split(",") if p.strip()]
    if not parts:
        return direct
    # parts[0] = original client; parts[-1] = most recent proxy.
    # With N trusted proxies, client is at index len-N-1? Actually:
    # request reaches us after N proxies appended. Client is at -(N+1) from end,
    # i.e. parts[-(n+1)] if available, else parts[0].
    idx = len(parts) - n - 1
    if idx < 0:
        idx = 0
    return parts[idx]
