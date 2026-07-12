from __future__ import annotations

import os


def vector_backend() -> str:
    return os.environ.get("RAG_VECTOR_BACKEND", "pgvector")
