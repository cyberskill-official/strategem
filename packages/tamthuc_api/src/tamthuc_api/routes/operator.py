"""Operator-only BYOK LLM settings (admin tier)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from tamthuc_api.errors import error_envelope
from tamthuc_api.operator_llm import get_active_config, public_view, upsert_config

router = APIRouter(tags=["operator"])


class OperatorLlmBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    provider_base_url: str = Field(min_length=1, max_length=512)
    model_id: str = Field(min_length=1, max_length=256)
    backend: str = "openai_compatible"
    api_key: str | None = None
    clear_api_key: bool = False


def _require_admin(request: Request) -> Any | JSONResponse:
    user = getattr(request.state, "current_user", None)
    if user is None:
        return JSONResponse(
            status_code=401,
            content=error_envelope("UNAUTHORIZED", "authentication required"),
        )
    tier = str(getattr(user, "tier", "") or "").lower()
    if tier != "admin":
        return JSONResponse(
            status_code=403,
            content=error_envelope("FORBIDDEN", "operator admin role required"),
        )
    return user


@router.get("/operator/llm-settings", response_model=None)
def get_llm_settings(request: Request) -> dict[str, Any] | JSONResponse:
    gate = _require_admin(request)
    if isinstance(gate, JSONResponse):
        return gate
    cfg = get_active_config(include_secret=False)
    if cfg is None:
        return {
            "configured": False,
            "settings": None,
            "resolution_order": ["operator_settings", "env", "stub"],
        }
    return {
        "configured": True,
        "settings": public_view(cfg),
        "resolution_order": ["operator_settings", "env", "stub"],
    }


@router.put("/operator/llm-settings", response_model=None)
def put_llm_settings(body: OperatorLlmBody, request: Request) -> dict[str, Any] | JSONResponse:
    gate = _require_admin(request)
    if isinstance(gate, JSONResponse):
        return gate
    user = gate
    backend = (body.backend or "openai_compatible").strip().lower()
    allowed = {"openai_compatible", "openai", "lmstudio", "local", "stub", "off"}
    if backend not in allowed:
        return JSONResponse(
            status_code=400,
            content=error_envelope("VALIDATION", f"backend must be one of {sorted(allowed)}"),
        )
    # Never log body.api_key
    cfg = upsert_config(
        provider_base_url=body.provider_base_url.strip(),
        model_id=body.model_id.strip(),
        backend=backend,
        api_key=body.api_key,
        clear_api_key=body.clear_api_key,
        updated_by=UUID(str(user.id)),
    )
    view = public_view(cfg)
    assert "api_key" not in view
    assert body.api_key is None or view.get("api_key_masked") != body.api_key
    return {"configured": True, "settings": view}
