from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tamthuc_api.audit import AuditLog
from tamthuc_api.errors import STATUS_BY_CODE, error_envelope
from tamthuc_api.orchestrator import Orchestrator
from tamthuc_api.persistence import PersistenceService
from tamthuc_api.routes import calculate, knowledge, reports, timing


def create_app(
    orch: Orchestrator | None = None,
    *,
    enable_rate_limit: bool = False,
) -> FastAPI:
    app = FastAPI(title="tamthuc-api", version="0.1.0")
    app.state.orch = orch or Orchestrator()
    app.state.persistence = PersistenceService()
    app.state.audit = AuditLog()
    app.include_router(calculate.router, prefix="/api/v1")
    app.include_router(knowledge.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")
    app.include_router(timing.router, prefix="/api/v1")

    if enable_rate_limit:
        from tamthuc_api.middleware.ratelimit import RateLimitMiddleware

        app.add_middleware(RateLimitMiddleware)

    @app.exception_handler(Exception)
    async def _unhandled(_req: Request, exc: Exception) -> JSONResponse:
        code = getattr(exc, "code", "INTERNAL")
        status = STATUS_BY_CODE.get(code, 500)
        return JSONResponse(
            status_code=status,
            content=error_envelope(code if code != "INTERNAL" else "INTERNAL", str(exc)),
        )

    return app
