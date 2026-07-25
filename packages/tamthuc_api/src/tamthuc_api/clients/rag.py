"""RAG interpretation client — TASK-API-001 + COV-011 production default path."""

from __future__ import annotations

from typing import Any, Protocol

from tamthuc_rag.config import interpret_mode, is_restricted_category, vector_store_available
from tamthuc_rag.fallback import rule_based_interpretation
from tamthuc_rag.fuse import RankedHit
from tamthuc_rag.interpret import interpret as rag_interpret
from tamthuc_rag.llm import llm_from_env
from tamthuc_rag.local_corpus import retrieve_classical
from tamthuc_rag.review.gate import process_interpretation
from tamthuc_rag.review.queue import ReviewQueue
from tamthuc_rag.schema import Interpretation


class RagClient(Protocol):
    def retrieve(self, envelope: dict[str, Any], patterns: list[dict[str, Any]]) -> list[Any]: ...

    def interpret(
        self,
        envelope: dict[str, Any],
        patterns: list[dict[str, Any]],
        *,
        retrieved: list[Any] | None = None,
    ) -> dict[str, Any]: ...


class StubRagClient:
    def __init__(self) -> None:
        self.last_envelope: dict[str, Any] | None = None
        self.last_retrieved: list[Any] | None = None

    def retrieve(self, envelope: dict[str, Any], patterns: list[dict[str, Any]]) -> list[Any]:
        self.last_envelope = envelope
        # Stub retrieval seam — one synthetic hit so call-order tests see step 5.
        return [{"citation_id": "yba_1", "unit_id": "stub:yba_1"}]

    def interpret(
        self,
        envelope: dict[str, Any],
        patterns: list[dict[str, Any]],
        *,
        retrieved: list[Any] | None = None,
    ) -> dict[str, Any]:
        self.last_envelope = envelope
        self.last_retrieved = (
            retrieved if retrieved is not None else self.retrieve(envelope, patterns)
        )
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


def _he_to_system(he: str) -> str | None:
    mapping = {
        "ky_mon": "qimen",
        "qimen": "qimen",
        "luc_nham": "liuren",
        "liuren": "liuren",
        "thai_at": "taiyi",
        "taiyi": "taiyi",
    }
    return mapping.get(he.strip().lower())


def _patterns_to_chunks(patterns: list[dict[str, Any]]) -> list[RankedHit]:
    """Fallback hits from engine pattern fields when corpus retrieval is empty."""
    chunks: list[RankedHit] = []
    seen: set[str] = set()
    for i, p in enumerate(patterns):
        cites = list(p.get("citations") or [])
        if not cites:
            cid = str(p.get("id") or f"pattern_{i}")
            cites = [cid]
        for c in cites:
            cid = str(c)
            if cid in seen:
                continue
            seen.add(cid)
            name = str(p.get("name") or p.get("id") or cid)
            name_han = str(p.get("name_han") or "")
            classical = str(p.get("meaning_classical") or "")
            modern = str(p.get("meaning_modern") or "")
            layers = {
                "han": name_han or (name if any("\u4e00" <= ch <= "\u9fff" for ch in name) else ""),
                "bach_thoai": modern or name,
                "dich": classical or modern or f"Classical unit for {name} (local corpus).",
            }
            layers = {k: v for k, v in layers.items() if v}
            chunks.append(
                RankedHit(
                    score=1.0 - 0.01 * len(chunks),
                    unit_id=f"unit:{cid}",
                    citation_id=cid,
                    system=str(p.get("system") or "classical"),
                    arms=("vector", "pattern"),
                    layers=layers,
                    unit_type="pattern",
                )
            )
    return chunks


def _retrieve_chunks(envelope: dict[str, Any], patterns: list[dict[str, Any]]) -> list[RankedHit]:
    """Prefer classical corpus + KB glosses; fall back to pattern-name hits."""
    he = str(envelope.get("he") or "")
    system = _he_to_system(he)
    names = [str(p.get("name") or p.get("name_han") or p.get("id") or "") for p in patterns if p]
    cites = [str(c) for p in patterns for c in (p.get("citations") or []) if c]
    pids = [str(p.get("id") or "") for p in patterns if p.get("id")]
    query = " ".join(n for n in names if n) or " ".join(cites) or he or "classical"
    hits = retrieve_classical(
        query,
        system=system,
        k=6,
        citation_ids=cites,
        pattern_ids=pids,
    )
    if hits:
        return hits
    return _patterns_to_chunks(patterns)


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
    """Production interpretation: INTERPRET_MODE=rag|template (COV-011).

    Steps 5–6 of the nine-step flow: retrieve grounded chunks, then interpret.
    """

    def __init__(self) -> None:
        self.last_envelope: dict[str, Any] | None = None
        self.last_mode: str | None = None
        self.last_retrieved: list[RankedHit] | None = None
        self._queue = ReviewQueue()

    def retrieve(self, envelope: dict[str, Any], patterns: list[dict[str, Any]]) -> list[RankedHit]:
        """Step 5 — classical corpus / pattern-grounded retrieval."""
        self.last_envelope = envelope
        mode = interpret_mode()
        chunks = (
            _retrieve_chunks(envelope, patterns) if mode == "rag" else _patterns_to_chunks(patterns)
        )
        self.last_retrieved = chunks
        return chunks

    def interpret(
        self,
        envelope: dict[str, Any],
        patterns: list[dict[str, Any]],
        *,
        retrieved: list[RankedHit] | None = None,
    ) -> dict[str, Any]:
        """Step 6 — LLM / template interpretation over retrieved chunks."""
        self.last_envelope = envelope
        mode = interpret_mode()
        chunks = list(retrieved) if retrieved is not None else self.retrieve(envelope, patterns)
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
                llm = self._resolve_llm()
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
                # Explicit degraded path when LM Studio / BYOK backend is down.
                self.last_mode = "rule_based_degraded"
                interp = rule_based_interpretation(envelope, patterns=patterns)
                if interp.ai_disclosure is not None:
                    interp = interp.model_copy(
                        update={
                            "ai_disclosure": interp.ai_disclosure.model_copy(
                                update={
                                    "degraded": True,
                                    "fallback": True,
                                    "limits": (
                                        "LLM backend unreachable — rule-based educational "
                                        "fallback (not live model output)."
                                    ),
                                }
                            )
                        }
                    )

        return self._maybe_gate(envelope, interp)

    def _resolve_llm(self) -> Any:
        """Operator BYOK settings → env → stub (never log secrets)."""
        try:
            from tamthuc_api.operator_llm import get_active_config

            cfg = get_active_config(include_secret=True)
        except Exception:
            cfg = None
        if cfg is not None and cfg.provider_base_url and cfg.model_id:
            return llm_from_env(
                backend=cfg.backend,
                base_url=cfg.provider_base_url,
                model=cfg.model_id,
                api_key=cfg.api_key or "",
            )
        return llm_from_env()

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
