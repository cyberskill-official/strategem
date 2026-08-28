from __future__ import annotations

import copy
import json
from typing import Any

from tamthuc_rag.disclosure import build_disclosure
from tamthuc_rag.fuse import RankedHit
from tamthuc_rag.guard import framing_ok, strip_unknown_citations
from tamthuc_rag.llm import LlmClient, llm_from_env
from tamthuc_rag.prompt_builder import PROMPT_VERSION, build_prompt
from tamthuc_rag.review.policy import LOW_CONFIDENCE_THRESHOLD
from tamthuc_rag.schema import CitationCard, Interpretation


def interpret(
    laso: dict[str, Any],
    chunks: list[RankedHit],
    *,
    llm: LlmClient | None = None,
) -> Interpretation:
    # Read-only: work on a copy; assert caller envelope unchanged externally
    chart = copy.deepcopy(laso)
    allowed = {c.citation_id for c in chunks}
    # COV-028: default to env-configured client (LMStudio / stub / off)
    client = llm or llm_from_env()

    if not chunks:
        disc = build_disclosure(
            model=client.model,
            prompt_version=PROMPT_VERSION,
            retrieved_citation_ids=[],
            fallback=True,
        )
        return Interpretation(
            beginner="Insufficient classical sources were retrieved for a confident reading.",
            expert="Empty retrieval set; no free-memory claims are emitted.",
            recommendations=[],
            citations=[],
            confidence=0.0,
            requires_human_review=True,
            ai_disclosure=disc,
        )

    prompt = build_prompt(chart, chunks, "beginner")
    raw = client.complete(prompt)
    recs = strip_unknown_citations(list(raw.get("recommendations") or []), allowed)
    beginner = str(raw.get("beginner") or "")
    expert = str(raw.get("expert") or "")
    if not framing_ok(beginner + expert + json.dumps(recs, ensure_ascii=False)):
        raise ValueError("policy framing violation")

    cards = [
        CitationCard(
            citation_id=c.citation_id,
            layers=dict(c.layers),
            locator=c.unit_id,
        )
        for c in chunks
    ]
    conf = min(0.9, 0.3 + 0.1 * len(chunks))
    return Interpretation(
        beginner=beginner,
        expert=expert,
        recommendations=recs,
        citations=cards,
        confidence=conf,
        requires_human_review=conf < LOW_CONFIDENCE_THRESHOLD or not recs,
        ai_disclosure=build_disclosure(
            model=client.model,
            prompt_version=PROMPT_VERSION,
            retrieved_citation_ids=sorted(allowed),
        ),
    )
