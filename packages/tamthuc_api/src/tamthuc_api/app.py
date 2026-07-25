from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from tamthuc_api.audit import AuditLog
from tamthuc_api.clients.engine import probe_cast_cli
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


def create_app(
    orch: Orchestrator | None = None,
    *,
    enable_rate_limit: bool = False,
    enable_cors: bool = True,
) -> FastAPI:
    app = FastAPI(title="tamthuc-api", version="0.1.0")
    # W2 / COV-010: Postgres when DATABASE_URL set (compose default); memory for unit tests;
    # fail-closed in production without DATABASE_URL.
    persistence = PersistenceService.from_env()
    audit = AuditLog()
    metrics = MetricsRegistry()
    if orch is None:
        orch = Orchestrator(persistence=persistence, audit=audit)
    elif orch.persistence is None:
        orch.persistence = persistence
    if orch.audit is None:
        orch.audit = audit
    app.state.orch = orch
    app.state.persistence = orch.persistence or persistence
    app.state.audit = orch.audit or audit
    app.state.metrics = metrics
    app.state.persistence_backend = getattr(app.state.persistence, "backend", "memory")
    # COV-009 / W2: JWT auth mounted. Free single-system cast stays open;
    # premium (/calculate/all) + manage history (/queries) require Bearer JWT.
    try:
        from tamthuc_auth.routes import router as auth_router
        from tamthuc_auth.service import AuthService

        app.state.auth_service = AuthService()
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

    if enable_cors:
        origins_env = os.environ.get("CORS_ORIGINS", "").strip()
        origins = [o.strip() for o in origins_env.split(",") if o.strip()] or ["*"]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if enable_rate_limit:
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

    @app.get("/metrics")
    def metrics_endpoint() -> PlainTextResponse:
        """COV-021: Prometheus text exposition for cast latency / ready failures."""
        return PlainTextResponse(
            render_prometheus(metrics),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    @app.exception_handler(Exception)
    async def _unhandled(_req: Request, exc: Exception) -> JSONResponse:
        code = getattr(exc, "code", "INTERNAL")
        status = STATUS_BY_CODE.get(code, 500)
        return JSONResponse(
            status_code=status,
            content=error_envelope(code if code != "INTERNAL" else "INTERNAL", str(exc)),
        )

    return app
