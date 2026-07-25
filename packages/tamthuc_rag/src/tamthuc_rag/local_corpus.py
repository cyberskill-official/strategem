"""Bundled classical corpus + KB pattern glosses for default RAG (no LMStudio)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from tamthuc_rag.fuse import RankedHit


def _repo_root() -> Path:
    # packages/tamthuc_rag/src/tamthuc_rag/local_corpus.py → repo root (4 up)
    return Path(__file__).resolve().parents[4]


def _corpus_dir() -> Path:
    return _repo_root() / "data" / "corpus"


def _patterns_dir() -> Path:
    return _repo_root() / "data" / "patterns"


@lru_cache(maxsize=1)
def load_corpus_units() -> list[dict[str, Any]]:
    """Load classical units from data/corpus/**/*.json (triple-layer when present)."""
    root = _corpus_dir()
    units: list[dict[str, Any]] = []
    if not root.is_dir():
        return units
    for path in sorted(root.rglob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        source = doc.get("source") or {}
        system = str(source.get("system") or "classical")
        for u in doc.get("units") or []:
            if not isinstance(u, dict):
                continue
            cid = str(u.get("citation_id") or u.get("unit_id") or "")
            if not cid:
                continue
            units.append(
                {
                    "unit_id": str(u.get("unit_id") or cid),
                    "citation_id": cid,
                    "system": system,
                    "unit_type": str(u.get("unit_type") or "dieu"),
                    "layers": {
                        "han": str(u.get("nguyen_van_han") or ""),
                        "bach_thoai": str(u.get("bach_thoai") or ""),
                        "dich": str(u.get("dich") or ""),
                    },
                    "text_blob": " ".join(
                        str(u.get(k) or "")
                        for k in ("nguyen_van_han", "bach_thoai", "dich", "citation_id")
                    ).lower(),
                }
            )
    return units


@lru_cache(maxsize=1)
def load_pattern_glosses() -> list[dict[str, Any]]:
    """Load KB pattern meanings as retrieval units (substantive gloss, not bare names)."""
    root = _patterns_dir()
    rows: list[dict[str, Any]] = []
    if not root.is_dir():
        return rows
    for system in ("qimen", "liuren", "taiyi"):
        path = root / f"{system}.json"
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for p in data:
            if not isinstance(p, dict):
                continue
            pid = str(p.get("id") or "")
            name = str(p.get("name") or pid)
            name_han = str(p.get("name_han") or "")
            classical = str(p.get("meaning_classical") or "")
            modern = str(p.get("meaning_modern") or "")
            cites = [str(c) for c in (p.get("citations") or []) if c]
            primary_cite = cites[0] if cites else pid
            rows.append(
                {
                    "unit_id": f"pattern:{pid}",
                    "citation_id": primary_cite,
                    "pattern_id": pid,
                    "system": str(p.get("system") or system),
                    "unit_type": "pattern",
                    "layers": {
                        "han": name_han or name,
                        "bach_thoai": modern or name,
                        "dich": classical or modern or name,
                    },
                    "extra_citations": cites,
                    "text_blob": " ".join([pid, name, name_han, classical, modern, *cites]).lower(),
                }
            )
    return rows


def _tokenize(q: str) -> list[str]:
    parts = re.split(r"[\s,;/|]+", q.lower())
    return [p for p in parts if len(p) >= 2]


def _score_blob(blob: str, terms: list[str]) -> float:
    if not terms:
        return 0.0
    hits = sum(1 for t in terms if t in blob)
    return hits / len(terms)


def retrieve_classical(
    query: str,
    *,
    system: str | None = None,
    k: int = 6,
    citation_ids: list[str] | None = None,
    pattern_ids: list[str] | None = None,
) -> list[RankedHit]:
    """Rank classical corpus + pattern glosses for a cast interpretation query."""
    want_sys = (system or "").strip().lower()
    if want_sys in {"ky_mon", "qimen"}:
        want_sys = "qimen"
    elif want_sys in {"luc_nham", "liuren"}:
        want_sys = "liuren"
    elif want_sys in {"thai_at", "taiyi"}:
        want_sys = "taiyi"

    cite_set = {c.lower() for c in (citation_ids or []) if c}
    pattern_set = {p.lower() for p in (pattern_ids or []) if p}
    terms = _tokenize(query)

    scored: list[tuple[float, dict[str, Any]]] = []
    for unit in load_corpus_units():
        if want_sys and unit["system"] not in {want_sys, "all", "classical"}:
            continue
        blob = unit["text_blob"]
        score = _score_blob(blob, terms)
        if unit["citation_id"].lower() in cite_set:
            score += 1.5
        if score <= 0 and not cite_set:
            continue
        if score > 0:
            scored.append((score, unit))

    for unit in load_pattern_glosses():
        if want_sys and unit["system"] != want_sys:
            continue
        blob = unit["text_blob"]
        score = _score_blob(blob, terms)
        if unit["pattern_id"].lower() in pattern_set:
            score += 1.2
        if unit["citation_id"].lower() in cite_set:
            score += 1.0
        for ec in unit.get("extra_citations") or []:
            if str(ec).lower() in cite_set:
                score += 0.8
                break
        if score <= 0 and not (cite_set or pattern_set):
            continue
        if score > 0:
            scored.append((score, unit))

    scored.sort(key=lambda x: (-x[0], x[1]["unit_id"]))
    hits: list[RankedHit] = []
    seen: set[str] = set()
    for score, unit in scored:
        uid = unit["unit_id"]
        if uid in seen:
            continue
        seen.add(uid)
        layers = {k: v for k, v in (unit.get("layers") or {}).items() if v}
        if not layers:
            continue
        hits.append(
            RankedHit(
                score=float(score),
                unit_id=uid,
                citation_id=str(unit["citation_id"]),
                system=str(unit["system"]),
                arms=("corpus", "kb"),
                layers=layers,
                unit_type=str(unit.get("unit_type") or ""),
            )
        )
        if len(hits) >= k:
            break
    return hits
