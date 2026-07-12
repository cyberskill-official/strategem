from __future__ import annotations

import json
from pathlib import Path

from tamthuc_kb.corpus.models import CorpusFile
from tamthuc_kb.corpus.segment import segment_source
from tamthuc_kb.corpus.store import InMemoryCorpusStore


def load_source_file(path: Path | str, store: InMemoryCorpusStore) -> int:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    doc = CorpusFile.model_validate(data)
    store.upsert_sources([doc.source])
    units = segment_source(doc.source, doc.units)
    store.upsert_units(units)
    return len(units)


def load_directory(dir_path: Path | str, store: InMemoryCorpusStore) -> int:
    root = Path(dir_path)
    total = 0
    for path in sorted(root.rglob("*.json")):
        total += load_source_file(path, store)
    return total
