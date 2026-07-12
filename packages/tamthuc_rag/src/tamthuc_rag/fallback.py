"""Rule-based interpretation fallback — FR-RAG-007."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tamthuc_rag.disclosure import build_disclosure
from tamthuc_rag.resilience import LLMUnavailable, ResilientLLM
from tamthuc_rag.schema import CitationCard, Interpretation


def rule_based_interpretation(
    la_so: dict[str, Any],
    *,
    patterns: list[dict[str, Any]] | None = None,
    persona: str = "beginner",
) -> Interpretation:
    """Assemble from cach_cuc + cited pattern meanings only — no free-form LLM text."""
    # read-only
    detected = list(la_so.get("cach_cuc") or patterns or [])
    lines: list[str] = []
    cards: list[CitationCard] = []
    for cc in detected:
        if not isinstance(cc, dict):
            continue
        name = str(cc.get("name") or cc.get("id") or "pattern")
        meaning = str(
            cc.get("meaning_modern")
            or cc.get("meaning_classical")
            or cc.get("summary")
            or "See cited classical source."
        )
        lines.append(f"- {name}: {meaning}")
        for c in cc.get("citations") or []:
            if isinstance(c, dict) and c.get("source"):
                cards.append(
                    CitationCard(
                        citation_id=str(c.get("citation_id") or c.get("source")),
                        layers={"vi": str(c.get("text") or meaning)},
                        locator=str(c.get("locator") or ""),
                    )
                )
    body = (
        "Degraded reading (rule-based). Patterns detected:\n" + "\n".join(lines)
        if lines
        else "Degraded reading: no patterns detected on chart."
    )
    conf = min(0.4, 0.15 + 0.05 * len(lines))
    disc = build_disclosure(
        model="rule-based-fallback",
        prompt_version="fallback-1.0.0",
        retrieved_citation_ids=[c.citation_id for c in cards],
        fallback=True,
        degraded=True,
    )
    return Interpretation(
        beginner=body if persona == "beginner" else body,
        expert=body,
        recommendations=[],
        citations=cards,
        confidence=conf,
        requires_human_review=True,
        ai_disclosure=disc,
    )


def interpret_resilient(
    la_so: dict[str, Any],
    interpret_fn: Any,
    llm: Any,
    chunks: list[Any],
    *,
    breaker: Any | None = None,
) -> Interpretation:
    from tamthuc_rag.resilience import CircuitBreaker

    resilient = ResilientLLM(inner=llm, breaker=breaker or CircuitBreaker(fail_threshold=3))
    try:
        return interpret_fn(la_so, chunks, llm=resilient)
    except (LLMUnavailable, Exception):
        return rule_based_interpretation(la_so)
