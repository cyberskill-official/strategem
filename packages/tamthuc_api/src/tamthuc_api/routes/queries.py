"""Query result read path — E2E cast / TASK-API-004.

Auth boundary:
  GET  /queries/{id}              — public by id (cast journey after anonymous cast)
  POST /queries/{id}/follow-up    — public by id (follow-up chat on results/report)
  GET  /queries                   — JWT required (manage history; scoped to principal)
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from tamthuc_api.auth_deps import require_user, user_id_from
from tamthuc_api.errors import error_envelope
from tamthuc_api.follow_up import answer_follow_up

router = APIRouter(tags=["queries"])


class FollowUpBody(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    locale: str = Field(default="vi", max_length=16)


@router.get("/queries", response_model=None)
def list_queries(
    request: Request,
    user: Annotated[object, Depends(require_user)],
    he: str | None = Query(default=None),
    question_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any] | JSONResponse:
    """List saved casts for manage history — JWT required, scoped to caller."""
    persistence = getattr(request.app.state, "persistence", None)
    if persistence is None:
        return JSONResponse(
            status_code=503,
            content=error_envelope("INTERNAL", "persistence not configured"),
        )
    uid = user_id_from(user)
    items = persistence.list_history(
        user_id=uid,
        he=he,
        question_type=question_type,
        limit=limit,
    )
    return {"items": items}


@router.get("/queries/{query_id}", response_model=None)
def get_query(query_id: str, request: Request) -> dict[str, Any] | JSONResponse:
    """Fetch a cast by id — open for the anonymous cast → results journey."""
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


@router.post("/queries/{query_id}/follow-up", response_model=None)
def post_follow_up(
    query_id: str,
    body: FollowUpBody,
    request: Request,
) -> dict[str, Any] | JSONResponse:
    """Cited follow-up turn on a persisted cast — never invents chart numbers."""
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
    orch = getattr(request.app.state, "orch", None)
    rag = getattr(orch, "rag", None) if orch is not None else None
    try:
        return answer_follow_up(
            query_result=result,
            message=body.message,
            rag=rag,
            locale=body.locale or "vi",
        )
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content=error_envelope("VALIDATION_ERROR", str(e)),
        )
