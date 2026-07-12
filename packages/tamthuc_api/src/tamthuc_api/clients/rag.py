"""RAG interpretation client — FR-API-001."""

from __future__ import annotations

from typing import Any, Protocol


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


class LocalRagClient:
    """Deterministic interpretation grounded in envelope patterns + citations."""

    def __init__(self) -> None:
        self.last_envelope: dict[str, Any] | None = None

    def interpret(self, envelope: dict[str, Any], patterns: list[dict[str, Any]]) -> dict[str, Any]:
        self.last_envelope = envelope
        he = str(envelope.get("he") or "unknown")
        names = [str(p.get("name") or p.get("id") or "") for p in patterns]
        cites: list[str] = []
        for p in patterns:
            for c in p.get("citations") or []:
                cites.append(str(c))
        cites = sorted(set(cites)) or ["local_corpus"]

        polarity_bits = []
        for p in patterns:
            pol = str(p.get("polarity") or "")
            if pol == "cat":
                polarity_bits.append("auspicious (cát)")
            elif pol == "hung":
                polarity_bits.append("inauspicious (hung) — use caution")
            elif pol:
                polarity_bits.append(f"neutral/mixed ({pol})")
        pol_text = "; ".join(polarity_bits) if polarity_bits else "no strong pattern polarity"

        pattern_list = ", ".join(names) if names else "no detected patterns"
        beginner = (
            f"Educational reading for {he}. Detected patterns: {pattern_list}. "
            f"Polarity cues: {pol_text}. Decision support only — you decide."
        )
        expert = (
            f"Technical notes for {he}. Patterns={names}. "
            f"Citations={cites}. Envelope cache_key="
            f"{(envelope.get('provenance') or {}).get('cache_key', 'n/a')}."
        )
        recs = [
            {
                "text": "Weigh the cited classical guidance against your real-world context.",
                "citations": cites[:2],
            }
        ]
        cards = [
            {
                "citation_id": c,
                "source": c,
                "locator": "local",
                "han": names[0] if names else "",
                "bach_thoai": "",
                "dich": "Retrieved classical unit (local / stub corpus).",
            }
            for c in cites[:5]
        ]
        return {
            "beginner": beginner,
            "expert": expert,
            "recommendations": recs,
            "citations": cards,
            "confidence": min(0.9, 0.4 + 0.1 * len(patterns)),
            "requires_human_review": len(patterns) == 0,
            "ai_disclosure": {
                "is_ai_generated": True,
                "model": "local-rag-stub",
                "prompt_version": "e2e@1",
                "retrieved_citation_ids": cites[:5],
                "limits": "Heritage education / decision support; not fortune-telling.",
                "review_status": "not_required",
            },
        }
