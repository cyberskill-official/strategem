"""Cross-system validation — TASK-STRAT-004.

Calls engines; never re-casts or merges into a single verdict.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Stance = Literal["favorable", "mixed", "unfavorable"]
He = Literal["ky_mon", "luc_nham", "thai_at"]

SCOPE: dict[str, str] = {
    "luc_nham": "tactical/hourly",
    "ky_mon": "tactical/layout",
    "thai_at": "strategic/long-range",
}

EngineFn = Callable[[str, dict[str, Any]], dict[str, Any]]


class CrossSystemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    datetime: datetime
    tz: str = "+07:00"
    kinh_do: float = 106.7
    loai_cau_hoi: str = "trach_thoi"
    co_truong_phai: dict[str, dict[str, Any]] = Field(default_factory=dict)
    systems: list[He] = Field(default_factory=list)


class SystemRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    he: str
    stance: Stance
    scope: str
    cat: list[dict[str, Any]] = Field(default_factory=list)
    hung: list[dict[str, Any]] = Field(default_factory=list)
    cast_ref: str
    interp_ref: str | None = None
    available: bool = True
    reason: str | None = None


class AgreementView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agree: bool
    summary: str
    by_scope: list[dict[str, Any]] = Field(default_factory=list)


class CrossSystemResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reads: list[SystemRead]
    agreement: AgreementView
    request_echo: CrossSystemRequest


def stance_from_cach_cuc(cach_cuc: list[dict[str, Any]] | None) -> Stance:
    """Documented pure rule: net cat vs hung among envelope cach_cuc."""
    cat = 0
    hung = 0
    for c in cach_cuc or []:
        pol = str(c.get("polarity") or "").lower()
        if pol == "cat":
            cat += 1
        elif pol == "hung":
            hung += 1
    if cat > hung:
        return "favorable"
    if hung > cat:
        return "unfavorable"
    return "mixed"


def _extract_patterns(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(envelope.get("cach_cuc"), list):
        return list(envelope["cach_cuc"])
    ban = envelope.get("ban")
    if isinstance(ban, dict) and isinstance(ban.get("cach_cuc"), list):
        return list(ban["cach_cuc"])
    return []


def validate(
    request: CrossSystemRequest,
    engines: dict[str, EngineFn],
) -> CrossSystemResult:
    """Call each engine once; build per-system reads + agreement view. No merge verdict."""
    reads: list[SystemRead] = []
    call_count: dict[str, int] = {}
    systems: list[He] = request.systems or ["ky_mon", "luc_nham"]

    for he in systems:
        eng = engines.get(he)
        if eng is None:
            reads.append(
                SystemRead(
                    he=he,
                    stance="mixed",
                    scope=SCOPE.get(he, "unknown"),
                    cast_ref="",
                    available=False,
                    reason="system unavailable",
                )
            )
            continue
        body = {
            "datetime": request.datetime.isoformat(),
            "tz": request.tz,
            "kinh_do": request.kinh_do,
            "loai_cau_hoi": request.loai_cau_hoi,
            "co_truong_phai": request.co_truong_phai.get(he, {}),
        }
        envelope = eng(he, body)
        call_count[he] = call_count.get(he, 0) + 1
        patterns = _extract_patterns(envelope)
        cat = [p for p in patterns if str(p.get("polarity")).lower() == "cat"]
        hung = [p for p in patterns if str(p.get("polarity")).lower() == "hung"]
        reads.append(
            SystemRead(
                he=he,
                stance=stance_from_cach_cuc(patterns),
                scope=SCOPE.get(he, "unknown"),
                cat=cat,
                hung=hung,
                cast_ref=str(envelope.get("cache_key") or envelope.get("cast_ref") or he),
                available=True,
            )
        )

    # Agreement: compare only systems that share a comparable scope bucket prefix
    available = [r for r in reads if r.available]
    by_scope: list[dict[str, Any]] = []
    scopes = sorted({r.scope for r in available})
    for sc in scopes:
        group = [r for r in available if r.scope == sc]
        if len(group) < 2:
            by_scope.append(
                {
                    "scope": sc,
                    "systems": [r.he for r in group],
                    "label": "single-system-at-scope",
                    "stances": {r.he: r.stance for r in group},
                }
            )
            continue
        stances = {r.stance for r in group}
        by_scope.append(
            {
                "scope": sc,
                "systems": [r.he for r in group],
                "label": "agree" if len(stances) == 1 else "divergence-same-scope",
                "stances": {r.he: r.stance for r in group},
            }
        )

    # Cross-scope note: different scopes are not contradictions
    if len({r.scope for r in available}) > 1 and len({r.stance for r in available}) > 1:
        by_scope.append(
            {
                "scope": "cross",
                "label": "different-scope-not-contradiction",
                "stances": {r.he: r.stance for r in available},
            }
        )

    same_scope_groups = [
        g for g in by_scope if g.get("label") in ("agree", "divergence-same-scope")
    ]
    stance_set = {r.stance for r in available}
    stance_agree = len(available) >= 2 and len(stance_set) == 1
    same_scope_agree = bool(same_scope_groups) and all(
        g["label"] == "agree" for g in same_scope_groups
    )
    agree = stance_agree or same_scope_agree
    if stance_agree and not same_scope_groups:
        summary = "stances align across different scopes (not a contradiction): " + ", ".join(
            f"{r.he}({r.scope})={r.stance}" for r in available
        )
    elif agree:
        summary = "comparable systems align: " + ", ".join(f"{r.he}={r.stance}" for r in available)
    else:
        summary = "divergence at comparable scope or across scopes: " + ", ".join(
            f"{r.he}({r.scope})={r.stance}" for r in available
        )

    return CrossSystemResult(
        reads=reads,
        agreement=AgreementView(agree=agree, summary=summary, by_scope=by_scope),
        request_echo=request,
    )
