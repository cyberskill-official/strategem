"""Query result read path — E2E cast / TASK-API-004."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from tamthuc_api.errors import error_envelope
from tamthuc_api.follow_up import answer_follow_up

router = APIRouter(tags=["queries"])


class FollowUpBody(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    locale: str = Field(default="vi", max_length=16)


def _parse_uuid_or_404(value: str, *, kind: str) -> UUID | JSONResponse:
    try:
        return UUID(value)
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"{kind} {value} not found"),
        )


@router.get("/queries", response_model=None)
def list_queries(
    request: Request,
    he: str | None = Query(default=None),
    question_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any] | JSONResponse:
    """List saved casts for the authenticated principal only (TT-002)."""
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    user = getattr(request.state, "current_user", None)
    if user is None:
        return JSONResponse(
            status_code=401,
            content=error_envelope("UNAUTHORIZED", "authentication required"),
        )
    items = persistence.list_history(
        user_id=str(user.id),
        he=he,
        question_type=question_type,
        limit=limit,
    )
    return {"items": items}


@router.get("/queries/{query_id}", response_model=None)
def get_query(query_id: str, request: Request) -> dict[str, Any] | JSONResponse:
    parsed = _parse_uuid_or_404(query_id, kind="query")
    if isinstance(parsed, JSONResponse):
        return parsed
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    user = getattr(request.state, "current_user", None)
    uid = str(user.id) if user is not None else None
    result: dict[str, Any] | None = persistence.get_query_result(str(parsed), user_id=uid)
    if result is None:
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"query {parsed} not found"),
        )
    return result


@router.post("/queries/{query_id}/follow-up", response_model=None)
def post_follow_up(
    query_id: str,
    body: FollowUpBody,
    request: Request,
) -> dict[str, Any] | JSONResponse:
    """Answer a cited follow-up for an authenticated user's persisted cast."""
    parsed = _parse_uuid_or_404(query_id, kind="query")
    if isinstance(parsed, JSONResponse):
        return parsed
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    user = getattr(request.state, "current_user", None)
    uid = str(user.id) if user is not None else None
    result: dict[str, Any] | None = persistence.get_query_result(str(parsed), user_id=uid)
    if result is None:
        return JSONResponse(
            status_code=404,
            content=error_envelope("NOT_FOUND", f"query {parsed} not found"),
        )
    orch = getattr(request.app.state, "orch", None)
    rag = getattr(orch, "rag", None) if orch is not None else None
    try:
        return answer_follow_up(
            query_result=result,
            message=body.message,
            rag=rag,
            locale=body.locale or "vi",
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=error_envelope("VALIDATION_ERROR", str(exc)),
        )
