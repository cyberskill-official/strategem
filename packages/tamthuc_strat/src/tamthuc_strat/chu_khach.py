"""Chu-khach decision framework — FR-STRAT-003.

Reads a la so envelope and a RAG-003 interpretation read-only; never casts or
re-computes a chart. Ends at a user decision handoff, not a verdict.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# Prefer the RAG-003 shape when available; keep a local fallback for isolation.
try:
    from tamthuc_rag.schema import AIDisclosure as _RagAIDisclosure
except ImportError:  # pragma: no cover
    _RagAIDisclosure = None  # type: ignore[misc, assignment]

Lens = Literal["competitor", "risk", "partner"]
Party = Literal["chu", "khach"]

_LENS_LABELS: dict[Lens, tuple[str, str]] = {
    "competitor": ("us", "the competitor"),
    "risk": ("the action we take", "the external event"),
    "partner": ("us", "the partner / hire"),
}

_VERDICT_RE = re.compile(
    r"\b(you will|guaranteed|certain to|must (buy|sell|sue|diagnose)|"
    r"medical advice|legal advice|financial advice)\b",
    re.I,
)


class AIDisclosure(BaseModel):
    """Frame-local disclosure; compatible with FR-RAG-003 fields we carry."""

    model_config = ConfigDict(extra="allow")
    model: str
    limits: str = "decision support, not a verdict; no medical/legal/financial advice"
    review_status: str = "not_required"
    is_ai_generated: bool = True
    prompt_version: str | None = None
    retrieved_citation_ids: list[str] = Field(default_factory=list)


class DungThanAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    party: Party
    role_label: str
    dung_than: str
    cung: int | None = None


class Signal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: str
    reading: str
    citations: list[str] = Field(default_factory=list)


class DecisionHandoff(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str
    disclosure: AIDisclosure


class DecisionFrame(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str
    lens: Lens
    step1_framing: list[DungThanAssignment]
    step2_signals: list[Signal]
    step3_context_prompts: list[str]
    step4_decision: DecisionHandoff


def _interp_citation_ids(interp: Any) -> set[str]:
    ids: set[str] = set()
    citations = getattr(interp, "citations", None)
    if citations is None and isinstance(interp, dict):
        citations = interp.get("citations") or []
    for c in citations or []:
        if isinstance(c, str):
            ids.add(c)
        elif hasattr(c, "citation_id"):
            ids.add(str(c.citation_id))
        elif isinstance(c, dict) and c.get("citation_id"):
            ids.add(str(c["citation_id"]))
    disc = getattr(interp, "ai_disclosure", None)
    if disc is None and isinstance(interp, dict):
        disc = interp.get("ai_disclosure")
    if disc is not None:
        retrieved = getattr(disc, "retrieved_citation_ids", None)
        if retrieved is None and isinstance(disc, dict):
            retrieved = disc.get("retrieved_citation_ids")
        for r in retrieved or []:
            ids.add(str(r))
    return ids


def _disclosure_from_interp(interp: Any) -> AIDisclosure:
    disc = getattr(interp, "ai_disclosure", None)
    if disc is None and isinstance(interp, dict):
        disc = interp.get("ai_disclosure")
    if disc is None:
        return AIDisclosure(model="unknown")
    if isinstance(disc, AIDisclosure):
        return disc
    if _RagAIDisclosure is not None and isinstance(disc, _RagAIDisclosure):
        return AIDisclosure(
            model=disc.model,
            limits=disc.limits,
            review_status="not_required",
            is_ai_generated=disc.is_ai_generated,
            prompt_version=disc.prompt_version,
            retrieved_citation_ids=list(disc.retrieved_citation_ids),
        )
    if isinstance(disc, dict):
        return AIDisclosure(
            model=str(disc.get("model") or "unknown"),
            limits=str(disc.get("limits") or AIDisclosure.model_fields["limits"].default),
            review_status=str(disc.get("review_status") or "not_required"),
            is_ai_generated=bool(disc.get("is_ai_generated", True)),
            prompt_version=disc.get("prompt_version"),
            retrieved_citation_ids=list(disc.get("retrieved_citation_ids") or []),
        )
    return AIDisclosure(
        model=str(getattr(disc, "model", "unknown")),
        limits=str(getattr(disc, "limits", AIDisclosure.model_fields["limits"].default)),
    )


def _signals_from_interp(interp: Any, allowed: set[str]) -> list[Signal]:
    signals: list[Signal] = []
    beginner = getattr(interp, "beginner", None)
    if beginner is None and isinstance(interp, dict):
        beginner = interp.get("beginner")
    expert = getattr(interp, "expert", None)
    if expert is None and isinstance(interp, dict):
        expert = interp.get("expert")
    cite_list = sorted(allowed)[:3] or []
    if not cite_list:
        raise ValueError("interpretation has no citations; cannot build cited signals")

    if beginner:
        signals.append(
            Signal(
                kind="chu_khach_posture",
                reading=str(beginner)[:400],
                citations=[cite_list[0]],
            )
        )
    if expert:
        signals.append(
            Signal(
                kind="dung_than_relation",
                reading=str(expert)[:400],
                citations=[cite_list[0]],
            )
        )

    # pattern / cach cuc style recs
    recs = getattr(interp, "recommendations", None)
    if recs is None and isinstance(interp, dict):
        recs = interp.get("recommendations")
    for rec in recs or []:
        if isinstance(rec, dict):
            text = str(rec.get("text") or rec.get("reading") or rec)
            cites = [str(c) for c in (rec.get("citations") or cite_list[:1]) if str(c) in allowed]
        else:
            text = str(rec)
            cites = [cite_list[0]]
        if not cites:
            cites = [cite_list[0]]
        signals.append(Signal(kind="cach_cuc", reading=text[:400], citations=cites))

    # every signal must cite only allowed ids
    for s in signals:
        if not s.citations or not set(s.citations).issubset(allowed):
            raise ValueError(f"signal citations not subset of interpretation: {s.citations}")
    return signals


def _context_prompts(lens: Lens) -> list[str]:
    if lens == "competitor":
        return [
            "What is the competitor's actual position and timing?",
            "What resources can you commit this window?",
        ]
    if lens == "risk":
        return [
            "What external events are already on the calendar?",
            "What is your true downside if the risk materialises?",
        ]
    return [
        "What do you already know about this partner or hire?",
        "What mutual commitments are non-negotiable?",
    ]


def _dung_than_from_laso(la_so: dict[str, Any]) -> tuple[str, int | None, str, int | None]:
    """Best-effort seed of dung than positions; pure read of envelope."""
    charts = la_so.get("charts") or la_so.get("ban") or {}
    chu_dt, chu_cung = "nhat can", 1
    khach_dt, khach_cung = "ung than", 7
    if isinstance(charts, dict):
        # try qimen-style key_positions / dung_than hints
        for key in ("qimen", "ky_mon", "liuren", "luc_nham"):
            block = charts.get(key) if key in charts else None
            if not isinstance(block, dict):
                continue
            ban = block.get("ban") if isinstance(block.get("ban"), dict) else block
            dt = ban.get("dung_than") if isinstance(ban, dict) else None
            if isinstance(dt, dict):
                chu_dt = str(dt.get("chu") or chu_dt)
                khach_dt = str(dt.get("khach") or khach_dt)
                if "chu_cung" in dt:
                    chu_cung = int(dt["chu_cung"])
                if "khach_cung" in dt:
                    khach_cung = int(dt["khach_cung"])
            break
    return chu_dt, chu_cung, khach_dt, khach_cung


def build_frame(
    la_so: dict[str, Any],
    interp: Any,
    lens: Lens,
    *,
    question: str | None = None,
) -> DecisionFrame:
    """Assemble a four-step DecisionFrame. Pure, read-only, no engine I/O."""
    # snapshot inputs for read-only invariant (callers may deep-compare)
    _ = copy.deepcopy(la_so)
    _ = copy.deepcopy(
        interp if isinstance(interp, dict) else getattr(interp, "model_dump", lambda: interp)()
    )

    allowed = _interp_citation_ids(interp)
    chu_label, khach_label = _LENS_LABELS[lens]
    chu_dt, chu_cung, khach_dt, khach_cung = _dung_than_from_laso(la_so)

    q = question
    if not q:
        if isinstance(interp, dict):
            q = str(interp.get("question") or la_so.get("question") or "Decision under review")
        else:
            q = str(la_so.get("question") or "Decision under review")

    framing = [
        DungThanAssignment(party="chu", role_label=chu_label, dung_than=chu_dt, cung=chu_cung),
        DungThanAssignment(
            party="khach", role_label=khach_label, dung_than=khach_dt, cung=khach_cung
        ),
    ]
    signals = _signals_from_interp(interp, allowed)
    handoff_prompt = "Weigh the signals against your context and decide."
    if _VERDICT_RE.search(handoff_prompt):
        raise ValueError("verdict language in handoff")  # pragma: no cover

    disclosure = _disclosure_from_interp(interp)
    # strip any verdict leakage if interpretation text bled into limits
    if _VERDICT_RE.search(disclosure.limits):
        disclosure = disclosure.model_copy(
            update={"limits": "decision support, not a verdict; no medical/legal/financial advice"}
        )

    return DecisionFrame(
        question=q,
        lens=lens,
        step1_framing=framing,
        step2_signals=signals,
        step3_context_prompts=_context_prompts(lens),
        step4_decision=DecisionHandoff(prompt=handoff_prompt, disclosure=disclosure),
    )
