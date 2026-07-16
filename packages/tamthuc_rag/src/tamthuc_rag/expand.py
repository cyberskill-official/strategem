"""Term-sense query expansion — TASK-RAG-005 (upstream of RAG-002)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tamthuc_rag.glossary import SenseLayer, TermGlossary

System = Literal["qimen", "liuren", "taiyi", "all"]

DEFAULT_LAYERS = {
    SenseLayer.ban_nghia,
    SenseLayer.dan_than,
    SenseLayer.dien_tich,
}  # gia_ta off by default

DEFAULT_MAX_ADDED = 12


class ExpandedTerm(BaseModel):
    model_config = ConfigDict(extra="forbid")
    term: str
    layer: SenseLayer
    form: str
    weight: float


class ExpandedQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    original: str
    system: System
    terms: list[ExpandedTerm] = Field(default_factory=list)
    # original always highest weight signal
    original_weight: float = 1.0


def expand_query(
    query: str,
    system: System,
    glossary: TermGlossary,
    *,
    layers: set[SenseLayer] | None = None,
    max_added: int = DEFAULT_MAX_ADDED,
) -> ExpandedQuery:
    """Deterministic expansion; preserves original as highest-weight signal."""
    enabled = layers if layers is not None else set(DEFAULT_LAYERS)
    matched = glossary.match(query, system)
    added: list[ExpandedTerm] = []
    for entry in matched:
        for sense in entry.senses:
            if sense.layer not in enabled:
                continue
            if sense.layer == SenseLayer.gia_ta and not sense.reliable:
                continue
            for form in sense.surface_forms:
                if form.lower() in query.lower():
                    continue  # already present
                added.append(
                    ExpandedTerm(
                        term=entry.term,
                        layer=sense.layer,
                        form=form,
                        weight=sense.weight,
                    )
                )
                if len(added) >= max_added:
                    break
            if len(added) >= max_added:
                break
        if len(added) >= max_added:
            break
    # stable order: weight desc, then form
    added.sort(key=lambda t: (-t.weight, t.form))
    return ExpandedQuery(original=query, system=system, terms=added[:max_added])
