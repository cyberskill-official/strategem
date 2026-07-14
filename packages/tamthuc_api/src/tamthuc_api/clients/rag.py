"""RAG interpretation client — FR-API-001 + COV-011 production default path."""

from __future__ import annotations

from typing import Any, Protocol

from tamthuc_rag.config import interpret_mode, is_restricted_category, vector_store_available
from tamthuc_rag.fallback import rule_based_interpretation
from tamthuc_rag.fuse import RankedHit
from tamthuc_rag.interpret import interpret as rag_interpret
from tamthuc_rag.llm import llm_from_env
from tamthuc_rag.review.gate import process_interpretation
from tamthuc_rag.review.queue import ReviewQueue
from tamthuc_rag.schema import Interpretation


class RagClient(Protocol):
    def interpret(
        self, envelope: dict[str, Any], patterns: list[dict[str, Any]]
    ) -> dict[str, Any]: ...


class StubRagClient:
    def __init__(self) -> None:
        self.last_envelope: dict[str, Any] | None = None

    def interpret(self, envelope: dict[str, Any], patterns: list[dict[str, Any]]) -> dict[str, Any]:
        self.last_envelope = envelope
        return {
            "beginner": "educational reading",
            "expert": "technical reading",
            "recommendations": [{"text": "reflect", "citations": ["yba_1"]}],
            "ai_disclosure": {
                "is_ai_generated": True,
                "model": "stub",
                "prompt_version": "1",
                "retrieved_citation_ids": ["yba_1"],
            },
        }


def _patterns_to_chunks(patterns: list[dict[str, Any]]) -> list[RankedHit]:
    """Build retrieval-like hits from engine pattern citations (local corpus)."""
    chunks: list[RankedHit] = []
    seen: set[str] = set()
    for i, p in enumerate(patterns):
        cites = list(p.get("citations") or [])
        if not cites:
            # still attach pattern id as a weak unit for template/rag structure
            cid = str(p.get("id") or f"pattern_{i}")
            cites = [cid]
        for c in cites:
            cid = str(c)
            if cid in seen:
                continue
            seen.add(cid)
            name = str(p.get("name") or p.get("id") or cid)
            chunks.append(
                RankedHit(
                    score=1.0 - 0.01 * len(chunks),
                    unit_id=f"unit:{cid}",
                    citation_id=cid,
                    system=str(p.get("system") or "classical"),
                    arms=("vector", "pattern"),
                    layers={
                        "han": name if any("\u4e00" <= ch <= "\u9fff" for ch in name) else "",
                        "bach_thoai": name,
                        "dich": f"Classical unit for {name} (local corpus).",
                    },
                    unit_type="pattern",
                )
            )
    return chunks


def _template_interpretation(
    envelope: dict[str, Any], patterns: list[dict[str, Any]]
) -> Interpretation:
    """Honest template mode — engine-grounded, no fake RAG claims."""
    he = str(envelope.get("he") or "unknown")
    names = [str(p.get("name") or p.get("id") or "") for p in patterns if p]
    pattern_list = ", ".join(n for n in names if n) or "no detected patterns"
    cites = sorted({str(c) for p in patterns for c in (p.get("citations") or []) if c})
    from tamthuc_rag.schema import AIDisclosure, CitationCard

    # Template still requires sources when claiming citations; else refuse free-form
    if not patterns and not cites:
        return Interpretation(
            beginner=(
                "Template mode: no classical sources on this chart. "
                "No free-memory claims are emitted."
            ),
            expert="Anti-hallucination refuse: empty pattern+citation set.",
            recommendations=[],
            citations=[],
            confidence=0.0,
            requires_human_review=True,
            ai_disclosure=AIDisclosure(
                is_ai_generated=False,
                model="template-engine",
                prompt_version="template@1",
                retrieved_citation_ids=[],
                fallback=True,
                degraded=True,
                limits="Template mode badge — not live RAG retrieval.",
            ),
        )

    cards = [
        CitationCard(
            citation_id=c,
            layers={
                "han": "",
                "bach_thoai": c,
                "dich": "Template-mode classical locator (engine pattern citation).",
            },
            locator=f"template:{c}",
        )
        for c in (cites or names[:1] or ["template_local"])
    ]
    beginner = (
        f"[Template mode] Educational reading for {he}. Patterns: {pattern_list}. "
        "Decision support only — you decide."
    )
    expert = (
        f"[Template mode · engine badge] Technical notes for {he}. "
        f"Patterns={names}. Citations={cites or [c.citation_id for c in cards]}."
    )
    return Interpretation(
        beginner=beginner,
        expert=expert,
        recommendations=[
            {
                "text": "Weigh the stamped engine patterns against your real-world context.",
                "citations": [c.citation_id for c in cards[:2]],
            }
        ],
        citations=cards,
        confidence=min(0.75, 0.35 + 0.08 * len(patterns)),
        requires_human_review=len(patterns) == 0,
        ai_disclosure=AIDisclosure(
            is_ai_generated=False,
            model="template-engine",
            prompt_version="template@1",
            retrieved_citation_ids=[c.citation_id for c in cards],
            fallback=True,
            degraded=False,
            limits="Template mode — engine-grounded; not live vector RAG.",
        ),
    )


class LocalRagClient:
    """Production interpretation: INTERPRET_MODE=rag|template (COV-011)."""

    def __init__(self) -> None:
        self.last_envelope: dict[str, Any] | None = None
        self.last_mode: str | None = None
        self._queue = ReviewQueue()

    def interpret(self, envelope: dict[str, Any], patterns: list[dict[str, Any]]) -> dict[str, Any]:
        self.last_envelope = envelope
        mode = interpret_mode()
        # Prefer template if rag requested but no store / no sources
        chunks = _patterns_to_chunks(patterns)
        if mode == "rag" and not vector_store_available() and not chunks:
            mode = "template"
        if mode == "rag" and not chunks:
            # anti-hallucination: refuse free-form when no sources
            from tamthuc_rag.schema import AIDisclosure

            interp = Interpretation(
                beginner="RAG mode: no sources retrieved; refuse free-form interpretation.",
                expert="Empty retrieval — no live RAG claims.",
                recommendations=[],
                citations=[],
                confidence=0.0,
                requires_human_review=True,
                ai_disclosure=AIDisclosure(
                    is_ai_generated=False,
                    model="rag-refuse",
                    prompt_version="rag@1",
                    retrieved_citation_ids=[],
                    fallback=True,
                    degraded=True,
                    limits="Anti-hallucination refuse when no sources.",
                ),
            )
            self.last_mode = "rag-refuse"
            return self._maybe_gate(envelope, interp)

        self.last_mode = mode
        if mode == "template":
            interp = _template_interpretation(envelope, patterns)
        else:
            try:
                llm = llm_from_env()
                interp = rag_interpret(envelope, chunks, llm=llm)
                # ensure ≥1 citation with triple-layer when corpus present
                if chunks and not interp.citations:
                    from tamthuc_rag.schema import CitationCard

                    c0 = chunks[0]
                    interp = interp.model_copy(
                        update={
                            "citations": [
                                CitationCard(
                                    citation_id=c0.citation_id,
                                    layers=dict(c0.layers),
                                    locator=c0.unit_id,
                                )
                            ]
                        }
                    )
            except Exception:
                interp = rule_based_interpretation(envelope, patterns=patterns)

        return self._maybe_gate(envelope, interp)

    def _maybe_gate(self, envelope: dict[str, Any], interp: Interpretation) -> dict[str, Any]:
        qtype = None
        if isinstance(envelope.get("dau_vao"), dict):
            qtype = envelope["dau_vao"].get("question_type") or envelope["dau_vao"].get(
                "loai_cau_hoi"
            )
        qtype = qtype or (envelope.get("lich_phap") or {}).get("loai_cau_hoi")
        restricted = is_restricted_category(str(qtype) if qtype else None)
        # also check body-level tags
        if not restricted:
            restricted = is_restricted_category(str(envelope.get("question_type") or ""))

        if restricted or interp.requires_human_review:
            gated = process_interpretation(interp, self._queue, high_stakes=restricted)
            if not gated.get("released"):
                view = dict(gated.get("withheld_view") or {})
                view["mode"] = self.last_mode
                view["human_review_gate"] = "pending"
                return view
            out = dict(gated["interpretation"])
            out["mode"] = self.last_mode
            # Soft-review releases keep review_status=pending; only mark released when not_required
            if out.get("review_status") == "not_required":
                out["human_review_gate"] = "released"
            else:
                out.setdefault("human_review_gate", "pending")
            return out

        out = dict(interp.model_dump())
        out["mode"] = self.last_mode
        out["review_status"] = "not_required"
        # surface mode badge for web
        disc = dict(out.get("ai_disclosure") or {})
        if self.last_mode == "template":
            disc["mode_badge"] = "template"
            disc["is_ai_generated"] = False
        else:
            disc["mode_badge"] = "rag"
        out["ai_disclosure"] = disc
        return out
