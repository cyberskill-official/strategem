"""ASGI security response headers middleware."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from tamthuc_api.security.headers import security_headers


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        response = await call_next(request)
        for key, value in security_headers().items():
            response.headers.setdefault(key, value)
        return response
