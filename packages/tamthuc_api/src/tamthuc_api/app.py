from __future__ import annotations

import logging
import os
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

from tamthuc_api.audit import AuditLog
from tamthuc_api.authz import RequireAuthMiddleware
from tamthuc_api.clients.engine import LocalEngineClient, default_engine, probe_cast_cli
from tamthuc_api.errors import STATUS_BY_CODE, error_envelope
from tamthuc_api.observability.metrics import MetricsRegistry, render_prometheus
from tamthuc_api.orchestrator import Orchestrator
from tamthuc_api.persistence import PersistenceService
from tamthuc_api.routes import (
    calculate,
    calendar,
    edu,
    knowledge,
    payments,
    queries,
    reports,
    timing,
)
from tamthuc_api.versioning.router import VersioningMiddleware, mount_versioned

log = logging.getLogger("tamthuc_api")


class HttpMetricsMiddleware(BaseHTTPMiddleware):
    """TT-017: count every request for http_requests_total / ErrorRateHigh."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        metrics = getattr(request.app.state, "metrics", None)
        if metrics is not None:
            metrics.record_request(
                method=request.method,
                path=request.url.path,
                status=response.status_code,
            )
            if response.status_code >= 500:
                metrics.record_error()
        return response


def _app_env() -> str:
    return (os.environ.get("APP_ENV") or os.environ.get("ENV") or "").strip().lower()


def _is_dev_or_test_env() -> bool:
    return _app_env() in {"development", "dev", "test"}


def _resolve_rate_limit(enable_rate_limit: bool | None) -> bool:
    """TT-011: rate limit on by default outside development/test."""
    if enable_rate_limit is not None:
        return enable_rate_limit
    flag = os.environ.get("ENABLE_RATE_LIMIT", "").strip().lower()
    if flag in {"1", "true", "yes"}:
        return True
    if flag in {"0", "false", "no"}:
        return False
    disable = os.environ.get("DISABLE_RATE_LIMIT", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if _is_dev_or_test_env():
        return False
    return not disable


def _cors_origins() -> list[str] | None:
    """TT-010: never allow ``*`` with credentials; require CORS_ORIGINS outside dev/test.

    Returns origin list to install, or None to skip CORS middleware (dev/test with
    no configured origins). Raises RuntimeError when production/staging omit
    CORS_ORIGINS or list ``*``.
    """
    origins_env = os.environ.get("CORS_ORIGINS", "").strip()
    origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    if any(o == "*" for o in origins):
        raise RuntimeError(
            "CORS_ORIGINS must not include '*' when credentials are enabled (TT-010)"
        )
    if origins:
        return origins
    # Empty ENV: local convenience (same posture as auth memory default).
    if _is_dev_or_test_env() or not _app_env():
        return None
    raise RuntimeError("CORS_ORIGINS is required outside ENV/APP_ENV=development|dev|test (TT-010)")


def create_app(
    orch: Orchestrator | None = None,
    *,
    enable_rate_limit: bool | None = None,
    enable_cors: bool = True,
) -> FastAPI:
    app = FastAPI(title="tamthuc-api", version="0.1.0")
    # COV-010: Postgres when DATABASE_URL set; memory in dev/test; fail-closed in prod
    persistence = PersistenceService.from_env()
    audit = AuditLog()
    metrics = MetricsRegistry()
    if orch is None:
        orch = Orchestrator(
            persistence=persistence,
            audit=audit,
            engine=default_engine(metrics=metrics),
        )
    elif orch.persistence is None:
        orch.persistence = persistence
    if orch.audit is None:
        orch.audit = audit
    # Attach metrics to LocalEngineClient when present (TT-022).
    eng = orch.engine
    if isinstance(eng, LocalEngineClient) and eng.metrics is None:
        eng.metrics = metrics
    app.state.orch = orch
    app.state.persistence = orch.persistence or persistence
    app.state.audit = orch.audit or audit
    app.state.metrics = metrics
    # TT-024: durable UserStore + refresh revocation when DATABASE_URL set;
    # in-memory only for explicit development/test (see require_auth_backend).
    try:
        from tamthuc_auth.routes import router as auth_router
        from tamthuc_auth.wiring import build_auth_service

        app.state.auth_service = build_auth_service()
        app.include_router(auth_router)
    except ImportError:
        app.state.auth_service = None
    # TASK-API-002: URL-primary versioning (/api/v1, …)
    mount_versioned(app, calculate.router)
    mount_versioned(app, calendar.router)
    mount_versioned(app, edu.router)
    mount_versioned(app, knowledge.router)
    mount_versioned(app, payments.router)
    mount_versioned(app, reports.router)
    mount_versioned(app, timing.router)
    mount_versioned(app, queries.router)
    app.add_middleware(VersioningMiddleware)
    # TT-002: auth on all non-public routes (explicit allowlist in authz.py)
    app.add_middleware(RequireAuthMiddleware)
    app.add_middleware(HttpMetricsMiddleware)

    if enable_cors:
        origins = _cors_origins()
        if origins is not None:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    if _resolve_rate_limit(enable_rate_limit):
        from tamthuc_api.middleware.ratelimit import RateLimitMiddleware

        app.add_middleware(RateLimitMiddleware)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        """Liveness — process is up."""
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> JSONResponse:
        """Readiness — diagnostics for CAST_CLI / engine mode.

        Set READY_REQUIRE_CAST_CLI=1 to return 503 when cast-cli is missing.
        """
        checks = probe_cast_cli()
        require_cli = os.environ.get("READY_REQUIRE_CAST_CLI", "").strip() in {
            "1",
            "true",
            "yes",
        }
        ok = True
        if require_cli and not checks["cast_cli_present"]:
            ok = False
            metrics.record_ready_failure("cast_cli_missing")
        body = {
            "status": "ok" if ok else "not_ready",
            "checks": checks,
        }
        return JSONResponse(status_code=200 if ok else 503, content=body)

    @app.get("/metrics", response_model=None)
    def metrics_endpoint(request: Request) -> PlainTextResponse | JSONResponse:
        """COV-021: Prometheus text exposition — requires auth (TT-002)."""
        if getattr(request.state, "current_user", None) is None:
            # Middleware should already 401; defensive for REQUIRE_AUTH=0
            return JSONResponse(
                status_code=401,
                content=error_envelope("UNAUTHORIZED", "authentication required"),
            )
        return PlainTextResponse(
            render_prometheus(metrics),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    @app.exception_handler(Exception)
    async def _unhandled(req: Request, exc: Exception) -> JSONResponse:
        # Safe envelope: never return str(exc) / driver internals to clients (TT-009).
        code = getattr(exc, "code", None)
        if isinstance(code, str) and code in STATUS_BY_CODE:
            status = STATUS_BY_CODE[code]
            message = str(getattr(exc, "message", None) or "request failed")
            return JSONResponse(
                status_code=status,
                content=error_envelope(code, message),
            )
        request_id = str(uuid4())
        log.exception(
            "unhandled_exception",
            extra={"request_id": request_id, "path": str(req.url.path)},
        )
        metrics.record_error()
        return JSONResponse(
            status_code=500,
            content=error_envelope(
                "INTERNAL",
                "an unexpected error occurred",
                request_id=request_id,
            ),
        )

    return app
