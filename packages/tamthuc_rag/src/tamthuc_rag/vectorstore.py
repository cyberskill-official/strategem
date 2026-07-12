from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tamthuc_rag.embed import Embedder
from tamthuc_rag.models import Chunk


@dataclass
class VectorIndex:
    model: str
    dim: int
    backend: str
    rows: dict[str, tuple[Chunk, list[float]]] = field(default_factory=dict)

    def upsert(self, chunk: Chunk, vector: list[float]) -> None:
        if len(vector) != self.dim:
            raise ValueError("reindex-required: vector dim mismatch")
        if chunk.model != self.model or chunk.dim != self.dim:
            raise ValueError("reindex-required: embedder model/dim mismatch")
        self.rows[chunk.chunk_id] = (chunk, vector)

    def query(
        self,
        vector: list[float],
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[Chunk]:
        if len(vector) != self.dim:
            raise ValueError("reindex-required: query embedder dim mismatch")
        scored: list[tuple[float, Chunk]] = []
        for chunk, vec in self.rows.values():
            if filters:
                if filters.get("system") and chunk.system != filters["system"]:
                    continue
                if filters.get("layer") and chunk.layer != filters["layer"]:
                    continue
            scored.append((_cos(vector, vec), chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k]]


def _cos(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def new_index(embedder: Embedder, *, backend: str = "memory") -> VectorIndex:
    return VectorIndex(model=embedder.name, dim=embedder.dim, backend=backend)
