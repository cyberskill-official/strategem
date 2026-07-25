"""Timing Optimizer + Scenario routes (COV-007 mounts STRAT-001)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["timing"])

DISCLAIMER = (
    "Educational decision-support only. Scores rank classical chart patterns "
    "for reflection and learning — not destiny, prophecy, or professional advice."
)


class TimingOptimizeBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    start: datetime
    end: datetime
    granularity: str = "gio"
    loai_cau_hoi: str = "trach_thoi"
    question_type: str | None = None
    tz: str = "+07:00"
    kinh_do: float | None = None
    longitude: float | None = None
    co_truong_phai: dict[str, Any] = Field(default_factory=dict)
    top_n: int = 5


@router.post("/timing/optimize", response_model=None)
def timing_optimize(body: TimingOptimizeBody, request: Request) -> dict[str, Any] | JSONResponse:
    """Mount STRAT-001 Timing Optimizer — deterministic cast scores only."""
    try:
        from tamthuc_strat.models import TimingRequest
        from tamthuc_strat.timing_optimizer import TimingError, optimize_timing
    except ImportError:
        return JSONResponse(
            status_code=501,
            content=error_envelope("NOT_IMPLEMENTED", "tamthuc_strat not installed"),
        )

    # COV-009 / TT-002: tier from verified JWT only (middleware requires auth)
    user = getattr(request.state, "current_user", None)
    if user is None:
        return JSONResponse(
            status_code=401,
            content=error_envelope("UNAUTHORIZED", "authentication required"),
        )
    tier = (user.tier or "free").lower()
    if tier in {"free", ""}:
        return JSONResponse(
            status_code=403,
            content=error_envelope(
                "FORBIDDEN_TIER",
                "timing_optimize requires premium+ (free cast remains open)",
            ),
        )

    orch = request.app.state.orch
    kinh = (
        body.kinh_do
        if body.kinh_do is not None
        else (body.longitude if body.longitude is not None else 106.7)
    )
    loai = body.question_type or body.loai_cau_hoi
    top_n = max(1, min(body.top_n, 20))

    req = TimingRequest(
        start=body.start,
        end=body.end,
        granularity=body.granularity,
        loai_cau_hoi=loai,
        tz=body.tz,
        kinh_do=float(kinh),
        co_truong_phai=dict(body.co_truong_phai or {}),
        top_n=top_n,
    )

    def engine_fn(when: datetime, r: TimingRequest) -> dict[str, Any]:
        # Deterministic cast only — STRAT never re-implements plates.
        lich: dict[str, Any] = {
            "datetime": when.isoformat(timespec="seconds"),
            "tz": r.tz,
            "kinh_do": r.kinh_do,
            "longitude": r.kinh_do,
            "loai_cau_hoi": r.loai_cau_hoi,
            "question_type": r.loai_cau_hoi,
            "co_truong_phai": r.co_truong_phai,
        }
        casted = orch.engine.cast("qimen", lich)
        return casted if isinstance(casted, dict) else dict(casted)

    try:
        result = optimize_timing(req, engine_fn)
    except TimingError as e:
        return JSONResponse(
            status_code=400,
            content=error_envelope("VALIDATION_ERROR", str(e)),
        )

    payload = result.model_dump(mode="json")
    # Soft VI-friendly reasons from pattern names (no AI required for scores).
    windows_out: list[dict[str, Any]] = []
    for w in payload.get("windows") or []:
        cat_names = [c.get("name") or c.get("id") for c in (w.get("cat") or []) if c]
        hung_names = [h.get("name") or h.get("id") for h in (w.get("hung") or []) if h]
        reasons: list[str] = []
        if cat_names:
            reasons.append("cát: " + ", ".join(str(n) for n in cat_names[:5]))
        if hung_names:
            reasons.append("hung: " + ", ".join(str(n) for n in hung_names[:5]))
        if not reasons:
            reasons.append("điểm từ cách cục trên ban (deterministic)")
        windows_out.append({**w, "reasons": reasons})

    return {
        "windows": windows_out,
        "request_echo": payload.get("request_echo"),
        "disclaimer": DISCLAIMER,
        "ai_disclosure": {
            "used_llm": False,
            "mode": "deterministic_cast_scores",
            "note": "Ranking uses engine cach_cuc only; optional prose is not generated here.",
        },
    }


class ScenarioCandidate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    label: str
    start: datetime
    end: datetime
    granularity: str = "gio"
    loai_cau_hoi: str = "trach_thoi"
    tz: str = "+07:00"
    kinh_do: float | None = None
    longitude: float | None = None
    co_truong_phai: dict[str, Any] = Field(default_factory=dict)


class ScenarioCompareBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    scenarios: list[ScenarioCandidate]
    top_n: int = 3


@router.post("/scenario/compare", response_model=None)
def scenario_compare(body: ScenarioCompareBody, request: Request) -> dict[str, Any] | JSONResponse:
    """COV-008: mount STRAT-002 — side-by-side scenarios via Timing Optimizer only."""
    try:
        from tamthuc_strat.models import TimingRequest
        from tamthuc_strat.scenario_compare import Scenario, ScenarioSet, compare_scenarios
        from tamthuc_strat.timing_optimizer import TimingError
    except ImportError:
        return JSONResponse(
            status_code=501,
            content=error_envelope("NOT_IMPLEMENTED", "tamthuc_strat not installed"),
        )

    if not body.scenarios or len(body.scenarios) < 2:
        return JSONResponse(
            status_code=400,
            content=error_envelope("VALIDATION_ERROR", "need 2–4 scenarios"),
        )
    if len(body.scenarios) > 4:
        return JSONResponse(
            status_code=400,
            content=error_envelope("VALIDATION_ERROR", "at most 4 scenarios"),
        )

    orch = request.app.state.orch
    top_n = max(1, min(body.top_n, 10))
    scenarios: list[Scenario] = []
    for sc in body.scenarios:
        kinh = (
            sc.kinh_do
            if sc.kinh_do is not None
            else (sc.longitude if sc.longitude is not None else 106.7)
        )
        scenarios.append(
            Scenario(
                label=sc.label,
                request=TimingRequest(
                    start=sc.start,
                    end=sc.end,
                    granularity=sc.granularity,
                    loai_cau_hoi=sc.loai_cau_hoi,
                    tz=sc.tz,
                    kinh_do=float(kinh),
                    co_truong_phai=dict(sc.co_truong_phai or {}),
                    top_n=top_n,
                ),
            )
        )

    def engine_fn(when: datetime, r: TimingRequest) -> dict[str, Any]:
        lich: dict[str, Any] = {
            "datetime": when.isoformat(timespec="seconds"),
            "tz": r.tz,
            "kinh_do": r.kinh_do,
            "longitude": r.kinh_do,
            "loai_cau_hoi": r.loai_cau_hoi,
            "question_type": r.loai_cau_hoi,
            "co_truong_phai": r.co_truong_phai,
        }
        # Reuse same cast path as timing optimizer — no invented scores
        casted = orch.engine.cast("qimen", lich)
        return casted if isinstance(casted, dict) else dict(casted)

    try:
        cmp = compare_scenarios(ScenarioSet(scenarios=scenarios, top_n=top_n), engine_fn)
    except TimingError as e:
        return JSONResponse(
            status_code=400,
            content=error_envelope("VALIDATION_ERROR", str(e)),
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=error_envelope("VALIDATION_ERROR", str(e)),
        )

    payload = cmp.model_dump(mode="json")
    return {
        "results": payload.get("results"),
        "ranked_labels": payload.get("ranked_labels"),
        "best_overall": payload.get("best_overall"),
        "disclaimer": DISCLAIMER,
        "ai_disclosure": {
            "used_llm": False,
            "mode": "deterministic_scenario_compare",
            "note": "Scores from Timing Optimizer only; no double-cast invention.",
        },
    }


class CrossSystemBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    datetime: datetime
    tz: str = "+07:00"
    kinh_do: float | None = None
    longitude: float | None = None
    loai_cau_hoi: str = "trach_thoi"
    question_type: str | None = None
    systems: list[str] = Field(default_factory=lambda: ["qimen", "liuren", "taiyi"])
    co_truong_phai: dict[str, Any] = Field(default_factory=dict)
    tier: str = "premium"


@router.post("/cross-system/validate", response_model=None)
def cross_system_validate(body: CrossSystemBody, request: Request) -> dict[str, Any] | JSONResponse:
    """COV-012: cast multiple systems and return soft consensus (no merge verdict)."""
    try:
        from tamthuc_strat.cross_system import CrossSystemRequest, validate
    except ImportError:
        return JSONResponse(
            status_code=501,
            content=error_envelope("NOT_IMPLEMENTED", "tamthuc_strat not installed"),
        )

    # Free tier: still allow dual-system; all-three prefers premium (soft)
    orch = request.app.state.orch
    kinh = (
        body.kinh_do
        if body.kinh_do is not None
        else (body.longitude if body.longitude is not None else 106.7)
    )
    he_map = {
        "qimen": "ky_mon",
        "ky_mon": "ky_mon",
        "liuren": "luc_nham",
        "luc_nham": "luc_nham",
        "taiyi": "thai_at",
        "thai_at": "thai_at",
    }
    systems = []
    for s in body.systems or ["qimen", "liuren", "taiyi"]:
        he = he_map.get(s, s)
        if he in {"ky_mon", "luc_nham", "thai_at"} and he not in systems:
            systems.append(he)

    def make_engine(system_key: str) -> Any:
        def _eng(_he: str, payload: dict[str, Any]) -> dict[str, Any]:
            lich = {
                "datetime": payload.get("datetime"),
                "tz": payload.get("tz", "+07:00"),
                "kinh_do": payload.get("kinh_do", 106.7),
                "longitude": payload.get("kinh_do", 106.7),
                "loai_cau_hoi": payload.get("loai_cau_hoi"),
                "question_type": payload.get("loai_cau_hoi"),
                "co_truong_phai": payload.get("co_truong_phai") or {},
            }
            # map he → cast system id
            cast_sys = {
                "ky_mon": "qimen",
                "luc_nham": "liuren",
                "thai_at": "taiyi",
            }.get(system_key, system_key)
            out = orch.engine.cast(cast_sys, lich)
            if not isinstance(out, dict):
                out = dict(out)
            # expose cache_key at top for cast_ref
            if "cache_key" not in out:
                prov = out.get("provenance") or {}
                if isinstance(prov, dict) and prov.get("cache_key"):
                    out = {**out, "cache_key": prov["cache_key"]}
            return out

        return _eng

    engines = {he: make_engine(he) for he in systems}
    req = CrossSystemRequest(
        datetime=body.datetime,
        tz=body.tz,
        kinh_do=float(kinh),
        loai_cau_hoi=body.question_type or body.loai_cau_hoi,
        systems=systems,  # type: ignore[arg-type]
        co_truong_phai={},
    )
    result = validate(req, engines)
    payload = result.model_dump(mode="json")
    # Soft VI summary for UI
    agree = payload.get("agreement") or {}
    summary_vi = agree.get("summary") or ""
    if agree.get("agree"):
        summary_vi = summary_vi or "Các hệ đang cùng hướng — vẫn chỉ là khung hỗ trợ quyết định."
    else:
        summary_vi = (
            summary_vi or "Có khác biệt giữa các hệ — soi từng cột, không gộp thành một lời kết."
        )

    return {
        "reads": payload.get("reads"),
        "agreement": {**agree, "summary_vi": summary_vi},
        "request_echo": payload.get("request_echo"),
        "disclaimer": DISCLAIMER,
        "ai_disclosure": {
            "used_llm": False,
            "mode": "cross_system_validate",
            "note": "Engine outputs only; no invented consensus score.",
        },
    }
