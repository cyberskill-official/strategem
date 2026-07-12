from __future__ import annotations

from dataclasses import dataclass

from tamthuc_rag.embed import Embedder, HashEmbedder
from tamthuc_rag.fuse import RankedHit, rrf_fuse
from tamthuc_rag.graph import GraphRetriever, NullGraphRetriever
from tamthuc_rag.vectorstore import VectorIndex


@dataclass
class RetrievalResult:
    chunks: list[RankedHit]
    graph_arm_used: bool


def retrieve(
    index: VectorIndex,
    query: str,
    *,
    k: int = 5,
    system: str | None = None,
    embedder: Embedder | None = None,
    graph: GraphRetriever | None = None,
) -> RetrievalResult:
    emb = embedder or HashEmbedder(name=index.model, dim=index.dim)
    filters = {"system": system} if system and system != "all" else None
    vec_chunks = index.query(emb.embed(query), k=k * 3, filters=filters)

    # collapse layers per unit_id
    by_unit: dict[str, RankedHit] = {}
    vec_rank: list[tuple[str, float]] = []
    for rank, ch in enumerate(vec_chunks):
        layers = {ch.layer: ch.text}
        if ch.unit_id in by_unit:
            prev = by_unit[ch.unit_id]
            merged = dict(prev.layers)
            merged.update(layers)
            by_unit[ch.unit_id] = RankedHit(
                score=prev.score,
                unit_id=ch.unit_id,
                citation_id=ch.citation_id,
                system=ch.system,
                arms=prev.arms,
                layers=merged,
                unit_type=ch.unit_type,
            )
        else:
            by_unit[ch.unit_id] = RankedHit(
                score=1.0 / (rank + 1),
                unit_id=ch.unit_id,
                citation_id=ch.citation_id,
                system=ch.system,
                arms=("vector",),
                layers=layers,
                unit_type=ch.unit_type,
            )
            vec_rank.append((ch.unit_id, 1.0 / (rank + 1)))

    g = graph if graph is not None else NullGraphRetriever()
    g_hits = g.retrieve(query, system=system, k=k * 2)
    graph_used = len(g_hits) > 0 or not isinstance(g, NullGraphRetriever)
    # Null always empty → graph_arm_used False
    if isinstance(g, NullGraphRetriever):
        graph_used = False

    graph_rank = [(uid, sc) for uid, sc, _ in g_hits]
    for uid, sc, layers in g_hits:
        if system and system != "all":
            # enforce system via index metadata if present
            meta = by_unit.get(uid)
            if meta and meta.system != system and meta.system != "all":
                continue
        if uid in by_unit:
            prev = by_unit[uid]
            arms = tuple(sorted(set(prev.arms) | {"graph"}))
            by_unit[uid] = RankedHit(
                score=prev.score,
                unit_id=uid,
                citation_id=prev.citation_id,
                system=prev.system,
                arms=arms,
                layers={**prev.layers, **layers},
                unit_type=prev.unit_type,
            )
        else:
            by_unit[uid] = RankedHit(
                score=sc,
                unit_id=uid,
                citation_id=uid,
                system=system or "all",
                arms=("graph",),
                layers=layers,
                unit_type="",
            )

    fused = rrf_fuse(vec_rank, graph_rank)
    for uid, sc in fused.items():
        if uid in by_unit:
            hit = by_unit[uid]
            by_unit[uid] = RankedHit(
                score=sc,
                unit_id=hit.unit_id,
                citation_id=hit.citation_id,
                system=hit.system,
                arms=hit.arms,
                layers=hit.layers,
                unit_type=hit.unit_type,
            )

    ranked = sorted(by_unit.values(), key=lambda h: (-h.score, h.unit_id))
    return RetrievalResult(chunks=ranked[:k], graph_arm_used=graph_used)
