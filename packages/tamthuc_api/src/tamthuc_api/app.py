from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from tamthuc_api.audit import AuditLog
from tamthuc_api.errors import STATUS_BY_CODE, error_envelope
from tamthuc_api.orchestrator import Orchestrator
from tamthuc_api.persistence import PersistenceService
from tamthuc_api.routes import calculate, knowledge, queries, reports, timing
from tamthuc_api.versioning.router import VersioningMiddleware, mount_versioned


def create_app(
    orch: Orchestrator | None = None,
    *,
    enable_rate_limit: bool = False,
    enable_cors: bool = True,
) -> FastAPI:
    app = FastAPI(title="tamthuc-api", version="0.1.0")
    persistence = PersistenceService()
    audit = AuditLog()
    if orch is None:
        orch = Orchestrator(persistence=persistence, audit=audit)
    elif orch.persistence is None:
        orch.persistence = persistence
    if orch.audit is None:
        orch.audit = audit
    app.state.orch = orch
    app.state.persistence = orch.persistence or persistence
    app.state.audit = orch.audit or audit
    # FR-API-002: URL-primary versioning (/api/v1, …)
    mount_versioned(app, calculate.router)
    mount_versioned(app, knowledge.router)
    mount_versioned(app, reports.router)
    mount_versioned(app, timing.router)
    mount_versioned(app, queries.router)
    app.add_middleware(VersioningMiddleware)

    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if enable_rate_limit:
        from tamthuc_api.middleware.ratelimit import RateLimitMiddleware

        app.add_middleware(RateLimitMiddleware)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(Exception)
    async def _unhandled(_req: Request, exc: Exception) -> JSONResponse:
        code = getattr(exc, "code", "INTERNAL")
        status = STATUS_BY_CODE.get(code, 500)
        return JSONResponse(
            status_code=status,
            content=error_envelope(code if code != "INTERNAL" else "INTERNAL", str(exc)),
        )

    return app
