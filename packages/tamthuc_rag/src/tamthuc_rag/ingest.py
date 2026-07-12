from __future__ import annotations

import json
from pathlib import Path

from tamthuc_rag.chunk import chunks_for_unit
from tamthuc_rag.embed import Embedder, HashEmbedder
from tamthuc_rag.models import UnitRecord
from tamthuc_rag.vectorstore import VectorIndex, new_index


def load_units_jsonl(path: Path | str) -> list[UnitRecord]:
    units: list[UnitRecord] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        units.append(UnitRecord.model_validate(json.loads(line)))
    return units


def ingest_corpus(
    path: Path | str,
    *,
    embedder: Embedder | None = None,
    index: VectorIndex | None = None,
    backend: str = "memory",
) -> VectorIndex:
    emb = embedder or HashEmbedder()
    idx = index or new_index(emb, backend=backend)
    if idx.model != emb.name or idx.dim != emb.dim:
        raise ValueError("reindex-required: embedder does not match index")
    for unit in load_units_jsonl(path):
        for chunk in chunks_for_unit(unit, model=emb.name, dim=emb.dim):
            idx.upsert(chunk, emb.embed(chunk.text))
    return idx
