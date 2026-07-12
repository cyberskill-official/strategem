"""Query result read path — E2E cast / FR-API-004."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["queries"])


@router.get("/queries", response_model=None)
def list_queries(
    request: Request,
    he: str | None = Query(default=None),
    question_type: str | None = Query(default=None),
    user_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any] | JSONResponse:
    """List saved casts for manage history (FR-WEB-007)."""
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    items = persistence.list_history(
        user_id=user_id,
        he=he,
        question_type=question_type,
        limit=limit,
    )
    return {"items": items}


@router.get("/queries/{query_id}", response_model=None)
def get_query(query_id: str, request: Request) -> dict[str, Any] | JSONResponse:
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    result: dict[str, Any] | None = persistence.get_query_result(query_id)
    if result is None:
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"query {query_id} not found"),
        )
    return result
