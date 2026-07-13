from __future__ import annotations

import os
from pathlib import Path


def vector_backend() -> str:
    return os.environ.get("RAG_VECTOR_BACKEND", "pgvector")


def interpret_mode() -> str:
    """COV-011: INTERPRET_MODE=rag|template.

    Default: rag when a vector store path/env is available, else template.
    """
    explicit = (os.environ.get("INTERPRET_MODE") or "").strip().lower()
    if explicit in {"rag", "template"}:
        return explicit
    # Auto: rag if vector backend configured and not forced off
    backend = vector_backend().strip().lower()
    if backend in {"", "none", "off", "disabled"}:
        return "template"
    # Optional marker file or env for local corpus readiness
    if os.environ.get("RAG_CORPUS_READY", "").strip().lower() in {"1", "true", "yes"}:
        return "rag"
    # pgvector / chroma / memory defaults to rag intent; product may still fall back
    if backend in {"pgvector", "chroma", "memory", "local"}:
        return "rag"
    return "template"


def vector_store_available() -> bool:
    """Heuristic: vector store path or corpus flag present."""
    if os.environ.get("RAG_CORPUS_READY", "").strip().lower() in {"1", "true", "yes"}:
        return True
    path = os.environ.get("RAG_VECTOR_PATH") or os.environ.get("PGVECTOR_URL")
    if path:
        p = Path(path)
        if p.exists() or path.startswith("postgresql"):
            return True
    return vector_backend() not in {"", "none", "off", "disabled"}


RESTRICTED_QUESTION_TYPES = frozenset(
    {
        "medical",
        "legal",
        "financial",
        "y_te",
        "phap_ly",
        "tai_chinh",
        "restricted",
        "health",
        "lawsuit",
        "investment",
    }
)


def is_restricted_category(question_type: str | None) -> bool:
    if not question_type:
        return False
    return question_type.strip().lower() in RESTRICTED_QUESTION_TYPES
