from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class RankedHit:
    score: float
    unit_id: str
    citation_id: str
    system: str
    arms: tuple[str, ...]
    layers: dict[str, str] = field(compare=False)
    unit_type: str = field(compare=False, default="")


def rrf_fuse(
    vector: list[tuple[str, float]],
    graph: list[tuple[str, float]],
    *,
    k: int = 60,
) -> dict[str, float]:
    """Reciprocal rank fusion over unit_id keys."""
    scores: dict[str, float] = {}
    for rank, (uid, _) in enumerate(vector):
        scores[uid] = scores.get(uid, 0.0) + 1.0 / (k + rank + 1)
    for rank, (uid, _) in enumerate(graph):
        scores[uid] = scores.get(uid, 0.0) + 1.0 / (k + rank + 1)
    return scores
