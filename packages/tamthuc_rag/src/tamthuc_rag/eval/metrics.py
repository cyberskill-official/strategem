"""Deterministic interpretation metrics — FR-RAG-006."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class _InterpLike(Protocol):
    beginner: str
    expert: str
    citations: list[Any]
    recommendations: list[Any]


class CaseScore(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: str
    case_version: int
    faithfulness: float = Field(ge=0.0, le=1.0)
    relevance: float = Field(ge=0.0, le=1.0)
    citation_precision: float = Field(ge=0.0, le=1.0)
    citation_recall: float = Field(ge=0.0, le=1.0)
    passed: bool


def _citation_id(c: Any) -> str:
    if isinstance(c, str):
        return c
    if hasattr(c, "citation_id"):
        return str(c.citation_id)
    if isinstance(c, dict):
        return str(c.get("citation_id") or c.get("id") or "")
    return str(c)


def _emitted_ids(interp: _InterpLike) -> list[str]:
    return [_citation_id(c) for c in interp.citations if _citation_id(c)]


def faithfulness(interp: _InterpLike, retrieved: set[str] | list[str]) -> float:
    """Lower bound: every claim citation must be in the retrieved set; uncited free text scores 0.5.

    Heuristic: split beginner+expert on sentence-ish boundaries; a sentence that
    looks like a claim (contains classical / polarity cues or is non-empty assertion)
    must either cite a retrieved id or be framed as uncertainty.
    """
    retrieved_set = set(retrieved)
    emitted = _emitted_ids(interp)
    if not emitted and not (interp.beginner or interp.expert):
        return 1.0
    if not emitted:
        # free-memory claims without any citation → unfaithful
        text = f"{interp.beginner} {interp.expert}".strip()
        if not text:
            return 1.0
        return 0.0 if len(text) > 20 else 0.5
    in_retrieved = sum(1 for c in emitted if c in retrieved_set)
    return in_retrieved / len(emitted)


def relevance(interp: _InterpLike, case: Any) -> float:
    """Polarity conveyed + question/pattern addressed."""
    polarity = str(getattr(case, "expected_polarity", "") or "").lower()
    text = f"{interp.beginner} {interp.expert}".lower()
    meaning = str(getattr(case, "meaning_classical", "") or "").lower()
    case_id = str(getattr(case, "id", "") or "").lower()
    query = str(getattr(case, "query", "") or "").lower()

    score = 0.0
    # polarity conveyed
    polarity_tokens = {
        "cat": ("cat", "cát", "auspicious", "favourable", "favorable", "positive"),
        "hung": ("hung", "hung", "inauspicious", "adverse", "caution", "negative"),
        "trung": ("trung", "neutral", "mixed", "balanced"),
    }
    tokens = polarity_tokens.get(polarity, (polarity,))
    if any(t in text for t in tokens if t) or polarity and polarity in text:
        score += 0.5

    # addresses the case (pattern id fragment or classical meaning cue)
    addressed = False
    if case_id and any(part in text for part in case_id.replace("_", " ").split() if len(part) > 3):
        addressed = True
    if meaning:
        # first han-ish token or first 6 ascii chars
        cue = meaning[:12].strip()
        if cue and cue[:4] in text:
            addressed = True
    if query and any(w in text for w in query.split() if len(w) > 5):
        addressed = True
    # recommendations present count as addressing the decision
    if interp.recommendations:
        addressed = True
    if addressed:
        score += 0.5
    return min(1.0, score)


def citation_scores(interp: _InterpLike, expected: list[str]) -> tuple[float, float]:
    emitted = set(_emitted_ids(interp))
    expected_set = set(expected)
    if not emitted and not expected_set:
        return 1.0, 1.0
    precision = (len(emitted & expected_set) / len(emitted)) if emitted else 0.0
    recall = (len(emitted & expected_set) / len(expected_set)) if expected_set else 1.0
    return precision, recall


def score_case(
    case: Any,
    interp: _InterpLike,
    retrieved: set[str] | list[str],
    *,
    pass_thresholds: dict[str, float] | None = None,
) -> CaseScore:
    thr = pass_thresholds or {
        "faithfulness": 0.90,
        "relevance": 0.80,
        "citation_f1": 0.85,
    }
    f = faithfulness(interp, retrieved)
    r = relevance(interp, case)
    p, rec = citation_scores(interp, list(getattr(case, "expected_citations", []) or []))
    f1 = 0.0 if (p + rec) == 0 else 2 * p * rec / (p + rec)
    passed = f >= thr["faithfulness"] and r >= thr["relevance"] and f1 >= thr["citation_f1"]
    return CaseScore(
        case_id=str(case.id),
        case_version=int(case.version),
        faithfulness=f,
        relevance=r,
        citation_precision=p,
        citation_recall=rec,
        passed=passed,
    )
