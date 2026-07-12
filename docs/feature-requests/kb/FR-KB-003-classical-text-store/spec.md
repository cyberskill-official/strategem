---
id: FR-KB-003
title: "Classical-text three-layer store - per source the nguyen van Han / bach thoai / dich layers segmented into natural units (dieu/phap/khoa/cau), each unit carrying citation_id + system + source; relational store in shared Postgres; the canonical corpus FR-RAG-001 ingests and every citation resolves into"
module: KB
priority: MUST
status: reviewing
phase: P1
slice: 1
lang: python
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-06 s4.2, strategy 4.1, strategy 4.4]
related_frs: [FR-RAG-001, FR-KB-002, FR-KB-005, FR-RAG-003, FR-PLAT-003, FR-EDU-003]
depends_on: [FR-PLAT-001]
blocks: [FR-RAG-001, FR-KB-005]
new_paths:
  - packages/tamthuc_kb/tamthuc_kb/corpus/__init__.py
  - packages/tamthuc_kb/tamthuc_kb/corpus/models.py
  - packages/tamthuc_kb/tamthuc_kb/corpus/store.py
  - packages/tamthuc_kb/tamthuc_kb/corpus/segment.py
  - packages/tamthuc_kb/tamthuc_kb/corpus/load.py
  - packages/tamthuc_kb/migrations/0002_classical_corpus.sql
  - data/corpus/qimen/yen_ba_dieu_tau_ca.json
  - data/corpus/SOURCES.md
  - packages/tamthuc_kb/tests/test_corpus.py
  - packages/tamthuc_kb/tests/fixtures/corpus_sample.json
  - docs/contracts/classical-corpus.schema.json
---

## §1 - Description (BCP-14 normative)

This FR is the source-of-truth store for the classical text of Tam Thuc: per source work it holds three parallel layers - nguyen van chu Han (original), ban bạch thoại (modern-Chinese rendering), and ban dịch (Vietnamese/English translation) - segmented into the natural bibliographic units of the thư tịch, each unit carrying a stable citation id. It is the corpus that FR-RAG-001 ingests and embeds, and the corpus that every citation in a pattern (FR-KB-002) or an interpretation (FR-RAG-003) resolves into. This FR owns the canonical text and its unit segmentation; it does NOT own the embeddings or the vector index (FR-RAG-001) nor the knowledge graph (FR-KB-001).

Text SHALL be segmented by the natural unit of the work - điều (條), pháp (法), khoá (課), or câu (句) - never by fixed token windows (Claude-06 s4.2). Every unit SHALL carry `unit_id`, `source`, `system` (qimen | liuren | taiyi | all), `unit_type`, `citation_id`, `ordinal`, and up to three layer texts (`han`, `bach_thoai`, `dich`), of which at least one SHALL be present. The three layers of a unit SHALL be aligned by construction (one unit row, three layer fields) so a retrieval can return the Han and its translation as the same passage. Segmentation SHALL keep a unit whole: a source is divided at natural-unit boundaries only, and a unit is never split mid-sentence to fit any downstream constraint (sub-unit splitting for embedding context is FR-RAG-001's concern, not this store's).

The store SHALL be pluggable behind a `ClassicalStore` protocol whose MVP default is two relational tables - `classical_source` and `classical_unit` - in the shared Postgres (FR-PLAT-003), matching the cyberos house pattern of keeping stateful data in the one managed Postgres. It SHALL expose a read API that yields units for FR-RAG-001 to ingest and a `resolve_citation(citation_id)` that returns the unit(s) a citation points at, so FR-RAG-003 can render citation cards (Han + bạch thoại + dịch + locator). Every `citation_id` a source declares SHALL be resolvable; a citation referenced by an active pattern (FR-KB-002) that resolves to no unit is a dangling citation and SHALL be reported, because the chain source -> pattern -> cách cục -> cited interpretation must have no link where a citation has no text behind it (strategy 4.4).

## §2 - Why this design (rationale for humans)

The interpretation branch can only be as honest as the text it cites, and the hard fact of this domain is that the primary sources are văn ngôn văn - classical Chinese, a language distinct from both modern Chinese and Vietnamese (Claude-06 s4.2). A single-layer store forces a bad choice: keep only the Han and no Vietnamese user can read the citation card, or keep only a translation and the original's precision is lost and the scholarship is unverifiable. Keeping three aligned layers per unit is what lets a citation card show the nguyen van, a bạch thoại gloss, and a dịch together, so a user sees exactly the passage a claim rests on and a reviewer can check the translation against the original. This is the cultural-respect rule made concrete: cite the classical text, and keep the Han alongside the transliteration and translation (strategy 7).

Segmenting by natural unit rather than token window is a correctness choice that this store must get right because everything downstream inherits it. A điều or a khoá is a complete thought in these texts; a citation points at exactly such a unit, and FR-RAG-001 embeds exactly such a unit. If the store split a unit arbitrarily, citations would point at fragments and retrieval would return half a rule. The store is relational at MVP for the same reason FR-KB-001's graph is: any managed Postgres can host it, it needs no second stateful system to run and back up, and the queries this corpus needs (units of a source in order, a unit by id, a citation resolved to its unit) are trivial in SQL. The `citation_id` is deliberately a first-class field separate from `unit_id` so the citation-id prefixes that FR-KB-002 agrees in `SOURCES.md` resolve here directly, keeping the pattern seed and the corpus aligned on one naming scheme rather than two.

## §3 - Contract (models, store, storage, read API)

### Unit and source models (`tamthuc_kb/corpus/models.py`)

```python
class Layer(str, Enum): han = "han"; bach_thoai = "bach_thoai"; dich = "dich"
class UnitType(str, Enum): dieu = "dieu"; phap = "phap"; khoa = "khoa"; cau = "cau"
# System (qimen | liuren | taiyi | all) is the shared enum defined in FR-KB-001.

class ClassicalSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str                     # e.g. "yen_ba_dieu_tau_ca"
    system: System
    title: str                  # display title
    title_han: str | None       # 煙波釣叟歌
    citation_prefix: str        # the citation-id prefix this source owns (agreed in KB-002 SOURCES.md)
    layers_available: list[Layer]   # which of han/bach_thoai/dich this source provides
    license_note: str | None    # provenance / license of the text used

class ClassicalUnit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    unit_id: str                # stable id, e.g. "yba_dieu_012"
    source: str                 # ClassicalSource.id
    system: System
    unit_type: UnitType
    citation_id: str            # what a pattern/interpretation cites; often == unit_id
    ordinal: int                # position within the source (stable ordering / display)
    han: str | None             # nguyen van chu Han
    bach_thoai: str | None      # ban bach thoai (modern-Chinese rendering)
    dich: str | None            # ban dich (Vietnamese/English)
```

A unit with all three layer fields `None` is invalid; the model validator SHALL require at least one non-empty layer. The `Layer` / `UnitType` vocabulary is the canonical contract in `docs/contracts/classical-corpus.schema.json`; FR-RAG-001 mirrors it in `tamthuc_rag/models.py` and validates against the same schema, so the two packages cannot drift (reconciliation note in section 7).

### ClassicalStore protocol (`tamthuc_kb/corpus/store.py`)

```python
class ClassicalStore(Protocol):
    def upsert_sources(self, sources: list[ClassicalSource]) -> None: ...   # idempotent by id
    def upsert_units(self, units: list[ClassicalUnit]) -> None: ...          # idempotent by unit_id
    def units_of_source(self, source: str) -> list[ClassicalUnit]: ...       # ordered by ordinal
    def iter_units(self, system: System | None = None) -> Iterator[ClassicalUnit]: ...  # FR-RAG-001 ingest feed
    def resolve_citation(self, citation_id: str) -> list[ClassicalUnit]: ...  # citation cards (FR-RAG-003)
    def get_unit(self, unit_id: str) -> ClassicalUnit | None: ...
    def count(self, system: System | None = None) -> int: ...

class RelationalClassicalStore:   # default (MVP): classical_source + classical_unit in the shared Postgres
    ...
class InMemoryClassicalStore:     # tests
    ...
```

`iter_units` is the feed FR-RAG-001 consumes: it yields units as validated rows (dicts under the schema), which `ingest(source_rows: Iterable[dict], ...)` chunks per layer and embeds. The store emits JSON-shaped rows so no Python type crosses the package boundary; the contract is the schema, not an import.

### Relational storage (`packages/tamthuc_kb/migrations/0002_classical_corpus.sql`)

```sql
create table classical_source (
  id              text primary key,
  system          text not null,               -- checked against System
  title           text not null,
  title_han       text,
  citation_prefix text not null,
  layers_available text[] not null,
  license_note    text
);
create table classical_unit (
  unit_id     text primary key,
  source      text not null references classical_source(id),
  system      text not null,                    -- checked against System
  unit_type   text not null,                    -- checked against UnitType
  citation_id text not null,
  ordinal     int  not null,
  han         text,
  bach_thoai  text,
  dich        text,
  check (han is not null or bach_thoai is not null or dich is not null)
);
create index classical_unit_source   on classical_unit(source, ordinal);
create index classical_unit_system   on classical_unit(system);
create unique index classical_unit_citation on classical_unit(citation_id);
```

`system` and `unit_type` carry SQL check constraints listing the closed enums so the database rejects a bad value even if a caller bypasses the app layer. The `check` on the three layers enforces at-least-one-layer at the storage tier too. Idempotency is by primary key on both tables. The DDL is owned here (KB is the natural owner of the corpus tables) and applied through the PLAT migration runner in the same shared Postgres (soft edge to FR-PLAT-003; the hard `depends_on` stays PLAT-001, mirroring FR-KB-001).

### Segmentation (`tamthuc_kb/corpus/segment.py`)

```python
def segment(raw: RawSource) -> list[ClassicalUnit]:
    # split a committed source work into ClassicalUnits at its marked natural-unit
    # boundaries (dieu/phap/khoa/cau); assign ordinal; derive citation_id from the
    # source's citation_prefix + unit index; carry each present layer; keep units whole.
```

Raw source works live under `data/corpus/<system>/<source>.json` with the natural-unit boundaries already marked by the curator (a structured array per source, one entry per unit with its layer texts). `segment` validates the markers, assigns `ordinal`, and derives `citation_id` from `citation_prefix`. `load.py` runs `segment` over the committed sources and upserts sources + units into the store; it is idempotent and fails the whole load, naming the offending `unit_id`, if any unit is malformed or lacks a layer.

## §4 - Acceptance criteria

1. A committed source (`data/corpus/qimen/yen_ba_dieu_tau_ca.json`) segments into `ClassicalUnit` rows, each with a `unit_type`, a monotonic `ordinal`, a `citation_id` under the source's `citation_prefix`, and at least one non-empty layer; a unit spanning two natural units, or split mid-unit, fails segmentation.
2. `units_of_source` returns a source's units in `ordinal` order; `get_unit` and `resolve_citation` return the aligned three-layer unit for a known `unit_id` / `citation_id`.
3. The at-least-one-layer rule is enforced at both the model validator and the SQL check constraint (two independent guards); a unit with all layers empty is rejected.
4. `upsert_sources` / `upsert_units` are idempotent: re-loading the same corpus leaves source and unit counts unchanged; `citation_id` is unique (a duplicate citation id anywhere fails the load).
5. `iter_units` yields rows valid under `docs/contracts/classical-corpus.schema.json`, and a round-trip through FR-RAG-001's `ingest` chunks one unit into one chunk per present layer sharing the `unit_id` (the KB-003 -> RAG-001 seam works on the fixture).
6. A dangling-citation check reports any `citation_id` referenced by an active FR-KB-002 pattern that resolves to no unit here; on the aligned fixture the report is empty.

## §5 - Verification

- `tests/test_corpus.py`: segmentation correctness per `unit_type`; the at-least-one-layer guard at both tiers; idempotent re-load; `citation_id` uniqueness; `units_of_source` ordering; `resolve_citation` returning aligned layers; the RAG-001 ingest seam on `fixtures/corpus_sample.json` (assert one chunk per present layer, shared `unit_id`).
- Backend parity: run the fixture through the `RelationalClassicalStore` (against a test Postgres or a fake) and the `InMemoryClassicalStore`; assert identical `units_of_source` and `resolve_citation` results.
- Schema conformance: every emitted row validates against `docs/contracts/classical-corpus.schema.json`, which is the same shape FR-RAG-001 validates its ingest input against.
- Cross-FR integrity: the dangling-citation check runs against a small aligned FR-KB-002 pattern fixture and asserts every active pattern's `citations` resolve here.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_kb`, `pytest packages/tamthuc_kb` (default suite uses the in-memory store; the Postgres path runs behind a marker when a test DB is present).

## §6 - Implementation skeleton

1. `corpus/models.py`: `ClassicalSource`, `ClassicalUnit`, the `Layer` / `UnitType` enums, the at-least-one-layer validator; author `docs/contracts/classical-corpus.schema.json` as the source of truth.
2. `corpus/store.py`: the `ClassicalStore` protocol, `RelationalClassicalStore` (default), `InMemoryClassicalStore` (tests).
3. `migrations/0002_classical_corpus.sql`: the two tables, check constraints, indexes.
4. `corpus/segment.py`: natural-unit segmentation from marked source files, ordinal + citation_id derivation, unit-whole guard.
5. `corpus/load.py`: read `data/corpus/**`, segment, upsert idempotently, whole-file fail with the offending id, dangling-citation check against KB-002.
6. Author `data/corpus/qimen/yen_ba_dieu_tau_ca.json` (marked units, the P1 flagship source) and `data/corpus/SOURCES.md` aligned to the FR-KB-002 citation-id prefixes; commit `fixtures/corpus_sample.json`.

## §7 - Dependencies

Depends on FR-PLAT-001 (the Python workspace and, for the relational store, the shared Postgres from FR-PLAT-003 - a soft edge like FR-KB-001's graph tables). Blocks FR-RAG-001 (which reads and embeds this corpus; its `Chunker` splits these units into per-layer chunks and its `citation_id`/`unit_id` come from here) and FR-KB-005 (whose graph query collects citations that resolve into this store). Aligns with FR-KB-002 on the citation-id prefixes: KB-002's `SOURCES.md` declares the prefixes, and this FR's `data/corpus/SOURCES.md` provides the units those prefixes resolve into, so a cited pattern always has text behind it. Read at runtime by FR-RAG-003 (citation cards) and FR-EDU-003 (the bilingual classical library). Reconciliation note: FR-RAG-001 declares `Layer` / `UnitType` enums in `tamthuc_rag`; both packages validate against `docs/contracts/classical-corpus.schema.json`, which this FR owns, so the vocabularies are one contract enforced in CI, not two that can drift.

## §8 - Example payloads

```json
// a marked source unit under data/corpus/qimen/yen_ba_dieu_tau_ca.json
{ "unit_id": "yba_dieu_012", "source": "yen_ba_dieu_tau_ca", "system": "qimen",
  "unit_type": "dieu", "citation_id": "yba_dieu_012", "ordinal": 12,
  "han": "丙加值符，青龍返首...", "bach_thoai": "丙加在值符上，称青龙返首...",
  "dich": "Binh gia truc phu, goi la Thanh Long Hoi Dau..." }
```

```json
// resolve_citation("yba_dieu_012") -> the aligned three-layer unit (for a citation card)
[ { "unit_id": "yba_dieu_012", "source": "yen_ba_dieu_tau_ca", "system": "qimen",
    "unit_type": "dieu", "citation_id": "yba_dieu_012", "ordinal": 12,
    "han": "丙加值符，青龍返首...", "bach_thoai": "丙加在值符上...",
    "dich": "Binh gia truc phu, goi la Thanh Long Hoi Dau..." } ]
```

## §9 - Open questions

- Whether a `citation_id` may span several units (a long điều split into câu). Default: one `citation_id` resolves to one unit at MVP; if a citation must cover a range, `resolve_citation` returns the ordered set and the citation card renders the range. Decide when the first multi-câu source is authored.
- How the Han text is normalized (traditional vs simplified, variant characters). Default: store the source's own form verbatim in `han`, keep a normalized field only if retrieval quality (FR-RAG-006) shows variant-character misses; do not silently transcode the original.
- How much of a source ships before P1 vs stays `draft`. Default: only cited, curator-checked units load; the citation-id prefixes are fixed early (with FR-KB-002) so patterns can reference units before every layer is translated. FR-KB-004 owns the sign-off.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Token-window segmentation | splitting mid-điều/câu to fit a size | forbidden; segment at natural-unit boundaries only; keep units whole |
| Layerless unit | a unit with all three layers empty | rejected by the model validator and the SQL check constraint (two guards) |
| Dangling citation | a pattern cites an id no unit resolves | dangling-citation check reports the id; the citation chain is not shippable with a gap |
| Duplicate citation id | same `citation_id` on two units | unique index / load check fails, naming the id |
| Layer misalignment | a translation stored against the wrong Han | aligned by construction (one row, three fields); a test asserts a unit's layers co-resolve |
| Silent Han transcode | original quietly simplified/normalized | store the source form verbatim; normalization is an explicit, flagged step, never silent |

## §11 - Notes

This FR is the textual ground the whole anti-hallucination contract stands on: no citation card, no cited interpretation, and no dangling-citation check exists without a store that holds the classical text as cited, aligned, natural units. Keep the boundary clean - this FR owns the canonical three-layer text and its unit segmentation; FR-RAG-001 owns the embeddings and the vector index over it; FR-KB-001 owns the graph. The one contract that binds this FR to FR-RAG-001 is `docs/contracts/classical-corpus.schema.json`; author it first and let both packages validate against it. The package `tamthuc_kb` is shared with FR-KB-001/002/004/005; this FR adds the `corpus/` module to it, so the knowledge base stays one installable, mypy-clean unit.
