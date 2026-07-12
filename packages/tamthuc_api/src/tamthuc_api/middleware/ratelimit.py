"""ASGI rate-limit middleware — FR-API-003."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from tamthuc_api.abuse import AbuseDetector, RequestEvent
from tamthuc_api.errors import error_envelope
from tamthuc_api.ratelimit import LocalFallbackLimiter, RateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        limiter: RateLimiter | None = None,
        abuse: AbuseDetector | None = None,
    ) -> None:
        super().__init__(app)
        self.limiter: RateLimiter = limiter or LocalFallbackLimiter()
        self.abuse = abuse or AbuseDetector()

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        # only meter calculate routes
        path = request.url.path
        if not path.startswith("/api/v1/calculate"):
            resp: Response = await call_next(request)
            return resp

        principal_id = request.headers.get("x-principal-id", "anon")
        tier = request.headers.get("x-tier", "free")
        source_ip = request.client.host if request.client else "0.0.0.0"

        decision = self.limiter.check_and_count(principal_id, tier)
        if not decision.allowed:
            headers = {}
            if decision.retry_after is not None:
                headers["Retry-After"] = str(decision.retry_after)
            return JSONResponse(
                status_code=429,
                content=error_envelope(
                    "RATE_LIMITED",
                    f"Daily request quota exceeded for the {tier} tier.",
                    details={
                        "limit": decision.limit,
                        "remaining": decision.remaining,
                        "reset_at": decision.reset_at,
                    },
                ),
                headers=headers,
            )

        verdict = self.abuse.evaluate(principal_id, source_ip, RequestEvent(path=path))
        if verdict.action == "lockout":
            return JSONResponse(
                status_code=423,
                content=error_envelope(
                    "RATE_LIMITED",
                    "Temporary lockout due to abuse signal",
                    details={"signal": verdict.signal.value if verdict.signal else None},
                ),
            )
        if verdict.action == "throttle":
            return JSONResponse(
                status_code=429,
                content=error_envelope(
                    "RATE_LIMITED",
                    "Throttled due to velocity spike",
                    details={"signal": verdict.signal.value if verdict.signal else None},
                ),
                headers={"Retry-After": str(verdict.window_s or 60)},
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(decision.limit)
        response.headers["X-RateLimit-Remaining"] = str(decision.remaining)
        response.headers["X-RateLimit-Reset"] = str(decision.reset_at)
        return response
