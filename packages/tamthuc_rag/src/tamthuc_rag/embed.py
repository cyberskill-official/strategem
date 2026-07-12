from __future__ import annotations

import hashlib
import math
from typing import Protocol


class Embedder(Protocol):
    name: str
    dim: int

    def embed(self, text: str) -> list[float]: ...


class HashEmbedder:
    """Deterministic stub multilingual-ish embedder for CI (dim-stable)."""

    def __init__(self, name: str = "hash-m3-stub", dim: int = 32) -> None:
        self.name = name
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        # bag of hashed tokens → fixed dim unit vector
        vec = [0.0] * self.dim
        for tok in text.lower().split():
            h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        # also mix char ngrams for cross-script rough overlap
        for i in range(len(text)):
            h = int(hashlib.md5(text[i : i + 2].encode("utf-8", errors="ignore")).hexdigest(), 16)
            vec[h % self.dim] += 0.25
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]
