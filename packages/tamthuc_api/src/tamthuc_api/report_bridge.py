"""Assemble StructuredReport from calculate outputs — FR-REPORT-001 bridge."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from tamthuc_report.assemble import AssembleError, assemble


def _citation_dicts(raw: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c in raw:
        if isinstance(c, dict):
            source = str(c.get("source") or c.get("citation_id") or c.get("id") or "source")
            out.append(
                {
                    "source": source,
                    "locator": str(c.get("locator") or "local"),
                    "han": c.get("han"),
                    "bach_thoai": c.get("bach_thoai"),
                    "dich": c.get("dich"),
                }
            )
        elif isinstance(c, str) and c:
            out.append(
                {"source": c, "locator": "local", "han": None, "bach_thoai": None, "dich": None}
            )
    return out


def normalize_for_assemble(
    envelope: dict[str, Any],
    interpretation: dict[str, Any],
    patterns: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Shape engine/RAG payloads to FR-REPORT-001 assemble() inputs."""
    env = dict(envelope)
    # ensure cach_cuc has Citation-shaped citations for patterns
    fixed_cc: list[dict[str, Any]] = []
    for p in env.get("cach_cuc") or patterns or []:
        if not isinstance(p, dict):
            continue
        cites = p.get("citations") or []
        if cites and isinstance(cites[0], str):
            cites = [{"source": c, "locator": "pattern"} for c in cites]
        else:
            cites = _citation_dicts(list(cites))
        fixed_cc.append(
            {
                "id": p.get("id") or "pattern",
                "name": p.get("name") or p.get("id") or "pattern",
                "polarity": p.get("polarity") or "trung",
                "cung": p.get("cung"),
                "score": p.get("score"),
                "citations": cites,
            }
        )
    env["cach_cuc"] = fixed_cc

    interp = dict(interpretation)
    recs_raw = interp.get("recommendations") or []
    recs: list[str] = []
    for r in recs_raw:
        if isinstance(r, str):
            recs.append(r)
        elif isinstance(r, dict):
            recs.append(str(r.get("text") or r.get("reading") or r))
    interp["recommendations"] = recs

    cites = _citation_dicts(list(interp.get("citations") or []))
    if not cites:
        # fall back to pattern citation strings so assemble() accepts
        for p in fixed_cc:
            for c in p.get("citations") or []:
                if isinstance(c, dict):
                    cites.append(c)
        if not cites:
            cites = [
                {
                    "source": "local_corpus",
                    "locator": "assemble",
                    "han": None,
                    "bach_thoai": None,
                    "dich": "Decision-support reading; not a verdict.",
                }
            ]
    interp["citations"] = cites

    disc = dict(interp.get("ai_disclosure") or {})
    if not disc.get("model"):
        disc["model"] = "local-rag-stub"
    if not disc.get("limits"):
        disc["limits"] = "Heritage education / decision support; not fortune-telling."
    if not disc.get("review_status"):
        disc["review_status"] = "not_required"
    interp["ai_disclosure"] = disc

    if not env.get("he"):
        env["he"] = "ky_mon"
    if not env.get("dau_vao"):
        env["dau_vao"] = {}
    lich = env.get("lich_phap") or {}
    if isinstance(lich, dict) and not lich.get("summary") and not lich.get("tu_tru"):
        lich = dict(lich)
        lich["summary"] = str(lich.get("year") or lich.get("datetime") or env.get("he"))
        env["lich_phap"] = lich

    return env, interp


def build_report_dict(
    envelope: dict[str, Any],
    interpretation: dict[str, Any],
    patterns: list[dict[str, Any]],
    query_id: str,
) -> dict[str, Any]:
    env, interp = normalize_for_assemble(envelope, interpretation, patterns)
    try:
        qid = UUID(query_id)
    except ValueError:
        qid = uuid4()
    try:
        report = assemble(env, interp, qid)
    except AssembleError:
        # last-resort minimal report without raising calculate
        from datetime import UTC, datetime

        from tamthuc_report.models import (
            AIDisclosure,
            ChartSummary,
            Citation,
            Interpretation,
            StructuredReport,
        )

        disc = interp.get("ai_disclosure") or {}
        report = StructuredReport(
            report_id=uuid4(),
            query_id=qid,
            chart_summary=ChartSummary(
                he=str(env.get("he") or "ky_mon"),
                dau_vao=dict(env.get("dau_vao") or {}),
                lich_phap_summary=str((env.get("lich_phap") or {}).get("summary") or ""),
                key_positions=[],
            ),
            detected_patterns=[],
            interpretation=Interpretation(
                beginner=str(interp.get("beginner") or ""),
                expert=str(interp.get("expert") or ""),
                recommendations=list(interp.get("recommendations") or []),
            ),
            citations=[Citation(**c) for c in (interp.get("citations") or [])[:3]],
            confidence=float(interp.get("confidence") or 0.0),
            ai_disclosure=AIDisclosure(
                model=str(disc.get("model") or "local"),
                limits=str(disc.get("limits") or "decision support"),
                review_status=str(disc.get("review_status") or "not_required"),
            ),
            created_at=datetime.now(UTC),
        )
    data = report.model_dump(mode="json")
    # stringify UUIDs for JSON clients
    data["report_id"] = str(data["report_id"])
    data["query_id"] = str(data["query_id"])
    return data
