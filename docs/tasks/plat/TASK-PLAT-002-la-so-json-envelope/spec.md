---
id: TASK-PLAT-002
title: "La so JSON envelope contract - one shape for all three engines, Rust+Python shared types, versioned, contract-tested on both sides"
module: PLAT
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.3, strategy 4.4, Claude-06 s2.3, Claude-06 s1.1, Grok-45, Grok-46]
related_frs: [TASK-CORE-005, TASK-QMDG-006, TASK-LN-006, TASK-TAT-006, TASK-RAG-002, TASK-API-001]
depends_on: [TASK-PLAT-001]
blocks: [TASK-CORE-005, TASK-QMDG-006, TASK-LN-006, TASK-TAT-006, TASK-RULE-002, TASK-RAG-002, TASK-API-004]
new_paths:
  - crates/laso-envelope/Cargo.toml
  - crates/laso-envelope/src/lib.rs
  - crates/laso-envelope/src/version.rs
  - crates/laso-envelope/tests/golden.rs
  - packages/laso_envelope/__init__.py
  - packages/laso_envelope/models.py
  - packages/laso_envelope/tests/test_contract.py
  - docs/contracts/laso-envelope.schema.json
---

## §1 - Description (BCP-14 normative)

The la so (chart) JSON envelope is the single boundary contract between the deterministic engine branch (Rust) and the interpretation branch (Python), per strategy section 4.3. This task defines that envelope once and ships it as (a) a Rust crate `laso-envelope` of serde types, (b) a Python package `laso_envelope` of Pydantic models generated from or checked against the same JSON Schema, and (c) a canonical JSON Schema at `docs/contracts/laso-envelope.schema.json`.

Every casting engine (CORE consumers QMDG, LN, TAT) MUST emit exactly this envelope. The interpretation branch (RULE, RAG, REPORT) and the API MUST consume it and MUST NOT write the `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai` fields. A chart MUST be fully reproducible from `dau_vao` plus `co_truong_phai` plus `lich_phap` flags; any input that changed the result MUST be stamped into one of those three, or it is a contract defect.

The envelope is versioned with an `envelope_version` integer. A breaking change SHALL increment it and SHALL be accompanied by a migration note; consumers SHALL reject an envelope whose version they do not support with a typed error rather than silently mis-parsing.

## §2 - Why this design (rationale for humans)

The whole platform rests on the split between a deterministic engine and an AI layer (strategy 4.1, Claude-06 s1.2). That split is only real if the boundary is a hard, typed, testable contract. If Rust and Python drift on the chart shape, the AI layer starts reading fields that moved and interpretation silently corrupts (RISK-8). Owning the shape in one schema and generating both sides from it makes drift a failing CI check, not a production incident.

The `co_truong_phai` (school flags) stamp is not decoration. QiMen alone has three orthogonal flag axes (dinh-cuc method, chuyen/phi ban, am/duong ban) that change the chart; users of different schools reject each other's charts (Claude-03 s6). Stamping every flag makes a chart reproducible and auditable, and lets two users see under which conventions a chart was cast. This is also the technical expression of the cultural-fairness rule (strategy 7).

## §3 - Contract (schema / types)

### Envelope shape

```json
{
  "envelope_version": 1,
  "he": "ky_mon",
  "dau_vao": {
    "datetime": "2004-01-01T10:30:00",
    "tz": "+07:00",
    "kinh_do": 106.7,
    "loai_cau_hoi": "trach_thoi"
  },
  "lich_phap": {
    "tu_tru": { "nam": "癸未", "thang": "甲子", "ngay": "戊午", "gio": "丁巳" },
    "tiet_khi": { "hien_hanh": "冬至", "bat_dau": "2003-12-22T08:04:00Z", "tam_nguyen": "thuong" },
    "chan_thai_duong": { "ap_dung": true, "gio_that": "2004-01-01T10:33:18", "hieu_chinh_phut": 3.3 },
    "phai_sinh": { "tuan_khong": ["申", "酉"], "vuong_suy": {}, "truong_sinh": {} },
    "co_lich_phap": {
      "use_true_solar_time": true, "longitude": 106.7,
      "zi_hour_day_rollover": "23:00", "late_zi_handling": "tao_zi",
      "truong_sinh_phai": "ngu_hanh", "delta_t_model": "espenak_meeus"
    }
  },
  "ban": { "...": "engine-specific; opaque to the interpretation branch except by `he`-typed readers" },
  "cach_cuc": [
    { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "cung": 1, "polarity": "cat", "score": 0.9,
      "citations": ["Yen Ba Dieu Tau Ca"] }
  ],
  "co_truong_phai": { "dingju_method": "chaibu", "pan_method": "zhuan", "yin_yang_pan": "duong" },
  "provenance": { "engine": "qmdg", "engine_version": "0.1.0", "cast_at": "2026-07-08T12:00:00Z", "cache_key": "..." }
}
```

### Rust types (`crates/laso-envelope/src/lib.rs`)

```rust
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct LaSo {
    pub envelope_version: u16,           // MUST be checked by consumers
    pub he: He,                          // enum: LucNham | KyMon | ThaiAt
    pub dau_vao: DauVao,
    pub lich_phap: LichPhap,             // the full CORE output (TASK-CORE-005)
    pub ban: serde_json::Value,          // engine-specific; typed views live in each engine crate
    pub cach_cuc: Vec<CachCuc>,
    pub co_truong_phai: BTreeMap<String, String>,  // stable ordering for cache-key hashing
    pub provenance: Provenance,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum He { LucNham, KyMon, ThaiAt }

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct CachCuc {
    pub id: String, pub name: String, pub cung: Option<u8>,
    pub polarity: Polarity,             // Cat | Hung | Trung
    pub score: Option<f32>,
    pub citations: Vec<String>,
}
```

`ban` is deliberately `serde_json::Value` at the envelope level so the shared crate does not depend on every engine. Each engine crate defines its own strongly-typed `KyMonBan` etc. and (de)serializes into that slot; a `he`-typed reader in Python/Rust downcasts by the `he` tag.

### Python models (`packages/laso_envelope/models.py`)

Pydantic v2 models mirroring the Rust types, `model_config = ConfigDict(extra="forbid")` so an unexpected field fails loudly. Generated from `docs/contracts/laso-envelope.schema.json` (single source of truth) via `datamodel-code-generator` in CI; the check fails if the committed models drift from the schema.

### Cache-key rule

The chart cache key (used by PLAT-006 and every engine per Claude-06 s2.2) is a stable hash of `(he, dau_vao rounded to the casting granularity, co_truong_phai sorted, lich_phap.co_lich_phap sorted)`. `co_truong_phai` is a `BTreeMap` / sorted dict precisely so the hash is stable across languages.

## §4 - Acceptance criteria

1. `laso-envelope` crate and `laso_envelope` package both build and expose the same field set; a round-trip (Rust serialize -> Python parse -> Python serialize -> Rust parse) is byte-stable for a golden fixture.
2. `docs/contracts/laso-envelope.schema.json` validates every golden fixture; the Python models are generated from it and a CI check fails on drift.
3. A consumer that receives `envelope_version` it does not support returns a typed `UnsupportedEnvelopeVersion` error, never a partial parse.
4. `extra="forbid"` on the Python side and `#[serde(deny_unknown_fields)]` on the Rust structs (except the opaque `ban`) reject unknown fields.
5. Two charts cast from identical `dau_vao` + `co_truong_phai` produce identical cache keys in both languages.

## §5 - Verification

- Rust: `crates/laso-envelope/tests/golden.rs` loads three golden fixtures (one per `he`), asserts round-trip equality and schema validity.
- Python: `packages/laso_envelope/tests/test_contract.py` parses the same three fixtures, asserts field parity, asserts `extra="forbid"` rejects an injected field, asserts version rejection.
- Cross-language: a CI job runs the Rust serializer and the Python parser on the same fixture and diffs; a mismatch fails the build (this is the contract test named in RISK-8 mitigation).
- Gates: `cargo fmt --check`, `cargo clippy -p laso-envelope -- -D warnings`, `cargo test -p laso-envelope`, `python -m pytest packages/laso_envelope`.

## §6 - Implementation skeleton

1. Author `docs/contracts/laso-envelope.schema.json` from the shape in §3 (this is the source of truth).
2. Hand-write the Rust serde structs to match; add `tests/golden.rs` with three fixtures under `crates/laso-envelope/tests/fixtures/`.
3. Generate Python models from the schema; commit them; add the drift-check CI step.
4. Implement `cache_key()` in both languages against the sorted-flags rule; add the cross-language equality test.
5. Implement version checking helpers (`require_version(&self, supported: &[u16])`).

## §7 - Dependencies

Depends on TASK-PLAT-001 (workspace layout that hosts `crates/` and `packages/`). Blocks every engine assembly task and the interpretation branch, because they all (de)serialize this type.

## §8 - Example payloads

See §3 for the full envelope. Minimal LiuRen skeleton the LN engine will fill:

```json
{ "envelope_version": 1, "he": "luc_nham",
  "dau_vao": { "datetime": "2004-01-01T10:30:00", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "hon_nhan" },
  "lich_phap": { "...": "from TASK-CORE-005" },
  "ban": { "thien_dia_ban": {}, "tu_khoa": [], "tam_truyen": [], "thien_tuong": {} },
  "cach_cuc": [], "co_truong_phai": { "khoi_quy_nhan": "trú_quý", "truong_sinh_phai": "ngu_hanh" },
  "provenance": { "engine": "ln", "engine_version": "0.1.0", "cast_at": "..." } }
```

## §9 - Open questions

- Should `ban` be a tagged union in the shared crate later (once all three engines exist) instead of `serde_json::Value`? Deferred: keeping it opaque now avoids the shared crate depending on three engine crates. Revisit at TAT-006.
- Do we need a compact binary form (e.g. for the cache) or is JSON-in-Redis fine at MVP scale? Default JSON; revisit under PLAT-006 if p95 shows serialization cost.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Version mismatch | consumer older than envelope | typed `UnsupportedEnvelopeVersion`, HTTP 500 with error envelope, alert |
| Unknown field | producer added a field without bumping schema | deserialize fails loudly in CI contract test before it can ship |
| Unstamped flag | engine used a school variant not in `co_truong_phai` | reproduction test (recast from stamped flags) diverges -> engine CI fails |
| Non-deterministic cache key | flags serialized in map order | cross-language key-equality test fails |
| AI wrote to `ban` | interpretation branch mutates chart | forbidden by types on read-only consumers; code review + no setter exposed |

## §11 - Notes

This task is the contract that makes DEC-2 (hybrid stack) safe. Do it before any engine assembly. The `lich_phap` sub-object is defined in full by TASK-CORE-005; this task only fixes its slot and the version/stamp/cache-key rules. Keep the schema file under `docs/contracts/` so it is reviewable independently of either language's build.
