from __future__ import annotations

from tamthuc_rag.schema import AIDisclosure


def build_disclosure(
    *,
    model: str,
    prompt_version: str,
    retrieved_citation_ids: list[str],
    fallback: bool = False,
    degraded: bool = False,
) -> AIDisclosure:
    return AIDisclosure(
        is_ai_generated=not degraded,
        model=model,
        prompt_version=prompt_version,
        retrieved_citation_ids=list(retrieved_citation_ids),
        fallback=fallback,
        degraded=degraded,
    )
