---
id: FR-RAG-001
title: "Classical-text ingest + multilingual embedding + vector store - 3-layer chunks (Han/bach thoai/dich) by dieu/phap/khoa/cau, pluggable embedder (bge-m3 default), pluggable backend (pgvector default)"
module: RAG
priority: MUST
status: done
phase: P0
slice: 1
lang: python
effort_h: 14
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-06 s4.2, Grok-32, strategy 4.1]
related_frs: [FR-KB-003, FR-RAG-002, FR-KB-005, FR-RAG-005, FR-PLAT-001, FR-PLAT-003]
depends_on: [FR-KB-003, FR-PLAT-001]
blocks: [FR-RAG-002]
new_paths:
  - packages/tamthuc_rag/pyproject.toml
  - packages/tamthuc_rag/tamthuc_rag/__init__.py
  - packages/tamthuc_rag/tamthuc_rag/models.py
  - packages/tamthuc_rag/tamthuc_rag/chunk.py
  - packages/tamthuc_rag/tamthuc_rag/embed.py
  - packages/tamthuc_rag/tamthuc_rag/vectorstore.py
  - packages/tamthuc_rag/tamthuc_rag/ingest.py
  - packages/tamthuc_rag/tamthuc_rag/config.py
  - packages/tamthuc_rag/tests/test_ingest.py
  - packages/tamthuc_rag/tests/fixtures/sample_corpus.jsonl
---

## §1 - Description (BCP-14 normative)

This FR builds the ingestion side of the RAG branch: it takes the canonical classical text held by FR-KB-003, chunks it by its natural bibliographic units, embeds each chunk with a multilingual model, and writes the vectors plus metadata into a vector store. It is the birth of the `tamthuc_rag` Python package. This FR SHALL NOT own the source-of-truth text (that is FR-KB-003's three-layer store); it SHALL read from that store and produce the searchable index over it.

Classical text SHALL be stored and chunked in three parallel layers - nguyen van chu Han (original), ban bạch thoại (modern-Chinese rendering), and ban dịch (Vietnamese/English translation) - and chunked by the natural unit of the thư tịch: điều (條), pháp (法), khoá (課), or câu (句), never by fixed token windows (Claude-06 s4.2). Every chunk SHALL carry metadata: `system` (qimen | liuren | taiyi | all), `source` (the work), `layer` (han | bach_thoai | dich), `unit_type`, `unit_id`, `citation_id`, and `ordinal`. Chunks sharing a `unit_id` across layers SHALL be linkable so retrieval can return the Han and its aligned translation together.

Embedding SHALL be pluggable behind an `Embedder` protocol, defaulting to a multilingual model (bge-m3) so a Vietnamese query retrieves Han text in one shared space; an OpenAI `text-embedding-3-small` adapter SHALL be provided as an alternative. The vector store SHALL be pluggable behind a `VectorStore` protocol, defaulting to pgvector for the MVP, with Chroma and Pinecone adapters selectable by config. Ingestion SHALL be idempotent: re-ingesting a unit updates in place, keyed by `(unit_id, layer, model)`. The index SHALL record which embedding model and dimension produced it, and a model change SHALL force a reindex rather than silently mixing vector spaces.

## §2 - Why this design (rationale for humans)

The hard part of interpreting Tam Thuc is that the sources are văn ngôn văn - classical Chinese, a language distinct from both modern Chinese and Vietnamese (Claude-06 s4.2). A naive index that embeds only a Vietnamese translation loses the original's precision; one that embeds only the Han cannot be reached by a Vietnamese user's query. Storing three aligned layers and embedding them into one multilingual space is what lets a query in any of the three languages surface the right passage and return it with its original and its translation side by side. That is also the substrate the anti-hallucination rule needs: an interpretation cites a specific `citation_id`, and the citation card (FR-RAG-003) shows the Han, the bạch thoại, and the dịch of exactly that unit.

Chunking by natural unit rather than token window is a correctness choice, not a nicety. A điều or a khoá is a complete thought in these texts; splitting it mid-sentence to fit a window would retrieve half a rule and mislead the model. The bibliographic unit is also what a citation points at, so unit-aligned chunks make citations exact. Pluggability on both the embedder and the store is deliberate hedging: bge-m3 is a strong open multilingual default that can run locally (no per-query cost, no data egress of sensitive queries), while pgvector keeps the MVP on the same Postgres the rest of the platform already runs (strategy 4.1); both can be swapped for a hosted model or a dedicated vector DB later without touching ingest or retrieval logic.

## §3 - Contract (models, protocols, pipeline)

### Chunk and metadata (`tamthuc_rag/models.py`)

```python
class Layer(str, Enum): han = "han"; bach_thoai = "bach_thoai"; dich = "dich"
class UnitType(str, Enum): dieu = "dieu"; phap = "phap"; khoa = "khoa"; cau = "cau"
class System(str, Enum): qimen = "qimen"; liuren = "liuren"; taiyi = "taiyi"; all = "all"

class Chunk(BaseModel):
    model_config = ConfigDict(extra="forbid")
    unit_id: str          # stable id of the bibliographic unit (shared across layers)
    layer: Layer
    text: str             # the chunk text in this layer
    system: System
    source: str           # the work, e.g. "yen_ba_dieu_tau_ca"
    unit_type: UnitType
    citation_id: str      # what an interpretation cites; often == unit_id
    ordinal: int          # position within the source, for stable ranking / display
```

### Embedder protocol (`tamthuc_rag/embed.py`)

```python
class Embedder(Protocol):
    name: str            # e.g. "bge-m3", "text-embedding-3-small"
    dim: int
    def embed(self, texts: list[str]) -> list[list[float]]: ...   # batched, order-preserving

class BgeM3Embedder:      # default, local, multilingual (Han/Viet/Eng one space)
    ...
class OpenAIEmbedder:     # text-embedding-3-small; used when configured
    ...
```

### Vector store protocol (`tamthuc_rag/vectorstore.py`)

```python
class StoredChunk(Chunk): vector: list[float]; model: str

class VectorStore(Protocol):
    def upsert(self, chunks: list[StoredChunk]) -> None: ...          # idempotent by (unit_id, layer, model)
    def query(self, vector: list[float], k: int,
              flt: dict | None = None) -> list["Hit"]: ...            # metadata-filtered ANN search
    def count(self, flt: dict | None = None) -> int: ...

class Hit(BaseModel): chunk: Chunk; score: float                     # cosine similarity, higher is nearer

class PgVectorStore:  ...   # default (MVP), same Postgres as FR-PLAT-003
class ChromaStore:    ...   # behind config
class PineconeStore:  ...   # behind config
```

The pgvector table stores `(unit_id, layer, model)` as the idempotency key plus the metadata columns for filtering and an `embedding vector(dim)` column with an ANN index; `query` applies the metadata filter (`system`, `layer`, `source`) in SQL before/with the ANN search.

### Ingest pipeline (`tamthuc_rag/ingest.py`)

```python
def ingest(source_rows: Iterable[dict],        # from FR-KB-003's three-layer store
           chunker: Chunker,
           embedder: Embedder,
           store: VectorStore,
           batch: int = 64) -> IngestReport:
    # 1. chunk each source unit into per-layer Chunks (chunk.py)
    # 2. batch-embed chunk.text with the embedder
    # 3. wrap as StoredChunk(vector=..., model=embedder.name)
    # 4. store.upsert(batch)  (idempotent)
    # 5. accumulate counts, model/dim, skipped/failed units -> IngestReport
```

`Chunker` (`chunk.py`) splits FR-KB-003 units by `unit_type` and emits one `Chunk` per present layer, preserving `unit_id`/`citation_id` linkage. `config.py` selects the embedder and store from environment/config (`RAG_EMBEDDER=bge-m3`, `RAG_VECTOR_BACKEND=pgvector`) and records `model`+`dim` into the index metadata.

## §4 - Acceptance criteria

1. Ingesting `fixtures/sample_corpus.jsonl` (a few units in three layers across two systems) produces one chunk per present layer per unit, each with complete metadata and the correct `unit_type`.
2. A Vietnamese query embedding retrieves the aligned Han chunk of the relevant unit from the vector store (cross-lingual retrieval works with the default multilingual embedder or a stub multilingual embedder in CI).
3. `store.query` honors a metadata filter: a `system=qimen` filter never returns a `liuren`-only chunk; a `layer=han` filter returns only Han chunks.
4. Re-ingesting the same corpus is idempotent: chunk count and ids are unchanged (upsert by `(unit_id, layer, model)`), not duplicated.
5. Switching `RAG_VECTOR_BACKEND` from pgvector to a Chroma stub yields identical retrieval results on the fixture (backend-parity).
6. The index records `model` and `dim`; querying with an embedder of a different `dim`/`name` than the index raises a clear reindex-required error rather than returning garbage.

## §5 - Verification

- `tests/test_ingest.py`: chunking correctness per `unit_type`; metadata completeness; idempotent re-ingest; the metadata-filter cases; cross-lingual retrieval with a deterministic stub multilingual embedder (fixed vectors) so CI needs no model download; the dim/model mismatch guard.
- Backend parity: run the fixture through the pgvector adapter (against a test Postgres or a fake) and a Chroma/in-memory adapter; assert identical top-k unit_ids.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_rag`, `pytest packages/tamthuc_rag` (the default suite uses stub embedder + in-memory store; the pgvector path runs behind a marker when a test DB is present).

## §6 - Implementation skeleton

1. Create the `tamthuc_rag` package (`pyproject.toml`, `uv`-managed per FR-PLAT-001); this FR owns its birth, FR-RAG-002/003 add modules.
2. `models.py`: `Chunk`, enums, `StoredChunk`, `Hit`.
3. `chunk.py`: `Chunker` splitting FR-KB-003 units by natural unit into per-layer chunks.
4. `embed.py`: `Embedder` protocol, `BgeM3Embedder`, `OpenAIEmbedder`, and a `StubEmbedder` for tests.
5. `vectorstore.py`: `VectorStore` protocol, `PgVectorStore` (default), `ChromaStore`, `PineconeStore`, `InMemoryStore` (tests).
6. `ingest.py` + `config.py`: the pipeline and the backend/embedder selection; `IngestReport`.

## §7 - Dependencies

Depends on FR-KB-003 (the three-layer classical-text store this FR reads and indexes; its chunk units define `unit_id`/`citation_id`) and FR-PLAT-001 (the Python workspace and, for pgvector, the shared Postgres from FR-PLAT-003). Blocks FR-RAG-002, which queries this vector store as the semantic arm of hybrid retrieval. FR-RAG-005 (term-sense expansion) later builds on the same three-layer chunks.

## §8 - Example payloads

```json
// one source unit from FR-KB-003 (input)
{ "unit_id": "yba_dieu_012", "system": "qimen", "source": "yen_ba_dieu_tau_ca",
  "unit_type": "dieu", "citation_id": "yba_dieu_012", "ordinal": 12,
  "han": "丙加值符，青龍返首...", "bach_thoai": "丙加在值符上，称青龙返首...",
  "dich": "Binh gia truc phu, goi la Thanh Long Hoi Dau..." }
```

```json
// chunks produced (one per present layer, shared unit_id)
[ { "unit_id": "yba_dieu_012", "layer": "han", "text": "丙加值符，青龍返首...",
    "system": "qimen", "source": "yen_ba_dieu_tau_ca", "unit_type": "dieu",
    "citation_id": "yba_dieu_012", "ordinal": 12 },
  { "unit_id": "yba_dieu_012", "layer": "dich", "text": "Binh gia truc phu...",
    "system": "qimen", "source": "yen_ba_dieu_tau_ca", "unit_type": "dieu",
    "citation_id": "yba_dieu_012", "ordinal": 12 } ]
```

## §9 - Open questions

- One chunk per layer (three rows per unit) vs one chunk with layers as payload. Default: one chunk per layer sharing `unit_id`, so each layer is independently searchable in the multilingual space and retrieval can align them; revisit if index size becomes a concern.
- bge-m3 vs a hosted embedder for production. Default: bge-m3 local (cost, privacy of sensitive queries per strategy 4.4); the OpenAI adapter is the fallback/benchmark. Decide from the FR-RAG-006 eval loop's retrieval quality.
- Where sub-unit chunking (a very long điều) is needed. Default: keep the natural unit whole; only split when a unit exceeds the embedder context, and then keep the split ids traceable to the parent unit.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Token-window chunking | splitting mid-điều/câu to fit a window | forbidden; chunk by natural unit; a unit over context is split traceably to its parent, not blindly |
| Mixed vector spaces | index built with model A, queried with model B | index records `model`/`dim`; mismatch raises reindex-required, never silent bad hits |
| Cross-system leak | query returns a foreign-system chunk | metadata filter (`system in {system, all}`) enforced in the store query; test asserts isolation |
| Duplicate on re-ingest | upsert not keyed properly | idempotency key `(unit_id, layer, model)`; re-ingest updates in place |
| Lost layer linkage | translation not tied to its Han | shared `unit_id`/`citation_id` across layers; a test asserts a unit's layers co-retrieve |
| CI needs a GPU/model | default suite downloads bge-m3 | `StubEmbedder` (fixed deterministic vectors) is the CI default; real model behind a marker |

## §11 - Notes

This FR is the foundation of retrieval-grounded interpretation: no citation card, no anti-hallucination check, and no hybrid retrieval exists without an index over the classical text. Keep the boundary with FR-KB-003 clean - that FR owns the canonical three-layer text and its chunk units; this FR owns the embeddings and the searchable vector index over them. The package `tamthuc_rag` is shared with FR-RAG-002/003; they add the retriever and the interpreter to it, so the RAG branch is one installable, mypy-clean unit.
