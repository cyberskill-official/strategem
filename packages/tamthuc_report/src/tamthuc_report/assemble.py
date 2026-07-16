"""Pure report assembler — TASK-REPORT-001. Copy-only; no engine I/O."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from tamthuc_report.models import (
    AIDisclosure,
    ChartSummary,
    Citation,
    Interpretation,
    ReportPattern,
    StructuredReport,
)


class AssembleError(ValueError):
    pass


def assemble(
    envelope: dict[str, Any],
    interp: dict[str, Any],
    query_id: UUID,
    *,
    report_id: UUID | None = None,
) -> StructuredReport:
    # copy chart fields — never recompute
    he = envelope["he"]
    dau_vao = dict(envelope.get("dau_vao") or {})
    lich = envelope.get("lich_phap") or {}
    summary_line = str(lich.get("summary") or lich.get("tu_tru") or "")
    patterns_raw = envelope.get("cach_cuc") or []
    patterns: list[ReportPattern] = []
    for p in patterns_raw:
        if isinstance(p, dict):
            patterns.append(
                ReportPattern(
                    id=str(p.get("id", "")),
                    name=str(p.get("name", p.get("id", ""))),
                    polarity=str(p.get("polarity", "trung")),
                    cung=p.get("cung"),
                    score=p.get("score"),
                    citations=[
                        Citation(**c) for c in (p.get("citations") or []) if isinstance(c, dict)
                    ],
                )
            )

    beginner = str(interp.get("beginner") or interp.get("text") or "")
    expert = str(interp.get("expert") or beginner)
    citations = [Citation(**c) for c in (interp.get("citations") or []) if isinstance(c, dict)]
    if beginner and not citations:
        raise AssembleError("interpretation claim without citations")

    disc_raw = interp.get("ai_disclosure") or {}
    if not disc_raw or not disc_raw.get("model"):
        raise AssembleError("ai_disclosure required")
    disclosure = AIDisclosure(
        model=str(disc_raw["model"]),
        limits=str(disc_raw.get("limits", "")),
        review_status=str(disc_raw.get("review_status", "not_required")),
    )
    if not disclosure.model.strip():
        raise AssembleError("empty ai_disclosure")

    confidence = float(interp.get("confidence", 0.0))

    return StructuredReport(
        report_id=report_id or uuid4(),
        query_id=query_id,
        chart_summary=ChartSummary(
            he=he,
            dau_vao=dau_vao,
            lich_phap_summary=summary_line,
            key_positions=list(envelope.get("key_positions") or []),
        ),
        detected_patterns=patterns,
        interpretation=Interpretation(
            beginner=beginner,
            expert=expert,
            recommendations=list(interp.get("recommendations") or []),
        ),
        citations=citations,
        confidence=confidence,
        ai_disclosure=disclosure,
        created_at=datetime.now(UTC),
    )
