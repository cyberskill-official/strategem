---
id: FR-RULE-001
title: "Pattern-as-data schema + knowledge_patterns table - patterns are versioned JSON rows not code, with a Rust validator, a seed-file format, and a (id, version) stamp"
module: RULE
priority: MUST
status: ready_to_implement
phase: P0
slice: 1
lang: rust
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.1, strategy 4.4, Grok-31, Claude-06 s2.3]
related_frs: [FR-RULE-002, FR-RULE-003, FR-KB-002, FR-KB-004, FR-PLAT-003, FR-QMDG-005]
depends_on: [FR-PLAT-003]
blocks: [FR-RULE-002, FR-KB-002]
new_paths:
  - crates/cyberos-rule/Cargo.toml
  - crates/cyberos-rule/src/lib.rs
  - crates/cyberos-rule/src/pattern.rs
  - crates/cyberos-rule/src/validate.rs
  - crates/cyberos-rule/src/version.rs
  - crates/cyberos-rule/src/seed.rs
  - crates/cyberos-rule/seed/qimen.json
  - crates/cyberos-rule/tests/pattern_schema.rs
  - crates/cyberos-rule/tests/fixtures/patterns_seed_sample.json
  - docs/contracts/knowledge-pattern.schema.json
---

## §1 - Description (BCP-14 normative)

This FR defines the pattern-as-data model that the whole rule engine stands on: a cach cuc (格局) or khoa the (課體) is a row of data, never a branch of code. The module SHALL express every detectable pattern as a `Pattern` record whose match logic lives in a JSON condition tree (the `conditions` field, whose grammar FR-RULE-002 owns) and whose meaning lives in cited text. No pattern SHALL be hardcoded in Rust; adding, editing, or retiring a pattern SHALL be a data change, expert-reviewed and versioned, that ships without recompiling the engine (strategy 4.4, Grok-31).

This FR owns three artifacts and one boundary. It owns (a) the canonical shape of the `knowledge_patterns` table - the column set, types, and enums; (b) the JSON Schema for a single pattern row at `docs/contracts/knowledge-pattern.schema.json`; and (c) a Rust `validate_pattern` function plus the seed-file format. It does not own the migration: FR-PLAT-003 creates the physical table and RLS from this shape, and FR-KB-002 fills the seed with the 150-200 real patterns. The boundary: this FR shape-checks `conditions` only structurally (is it a JSON object with a recognized top-level form); the deep DSL grammar and the evaluator belong to FR-RULE-002, which depends on this FR.

Every pattern SHALL carry a monotonic `version` integer per `id`. A detected pattern SHALL stamp `(id, version)` so a downstream interpretation cites the exact pattern text that fired and is reproducible against it. A semantic edit (to `conditions`, `polarity`, or either meaning) SHALL increment `version`; retiring a pattern SHALL set `status = deprecated` and SHALL NOT delete the row. An `active` pattern SHALL carry at least one citation, because a pattern with no textual source cannot ground a claim under the anti-hallucination rule (strategy 4.4, FR-RAG-003).

## §2 - Why this design (rationale for humans)

Both source sets converge on the same instruction: keep the knowledge out of the code. The Grok source spells the rule engine out as pattern-as-data JSON (Grok-31); the Claude source keeps cach cuc detection deterministic and table-driven rather than buried in branches (Claude-06 s2.3). The reason is operational, not aesthetic. Tam Thuc has hundreds of named patterns across three systems, they are contested between schools, and they will be corrected as experts review them. If each one is an `if` in Rust, every correction is a code change, a deploy, and a regression risk, and no domain expert can read or audit the ruleset. As data, the ruleset is one reviewable table, an expert can propose an edit as JSON, and the change is versioned and traceable.

The `version` stamp is what makes interpretation reproducible over time. An interpretation persisted last month cited a pattern whose meaning an expert has since sharpened; because the detected cach cuc recorded `(id, version)`, the old report still maps to the exact text it was written against, and the eval loop (FR-RAG-006) can tell a genuine regression from an intended revision. The citation-required rule on `active` patterns is the same anti-hallucination principle seen at the data layer: the chain source -> pattern -> detected cach cuc -> cited interpretation has no gap where meaning appears without a source.

## §3 - Contract (schema / types)

### knowledge_patterns columns (this FR fixes the shape; FR-PLAT-003 migrates it)

| Column | Type | Notes |
|---|---|---|
| id | text PK | stable slug, e.g. `qimen_thanh_long_hoi_dau`; never renumbered |
| system | text | enum: `qimen` \| `liuren` \| `taiyi` \| `all` |
| name | text | display name, e.g. Thanh Long Hoi Dau |
| name_han | text | 青龍返首 (nullable) |
| conditions | jsonb | condition DSL tree (FR-RULE-002 grammar); shape-checked here only |
| polarity | text | enum: `cat` \| `hung` \| `trung` |
| meaning_classical | text | classical / bạch thoại gloss |
| meaning_modern | text | decision-support framing (no medical/legal/financial claim) |
| citations | jsonb | array of citation ids into the classical corpus (FR-KB-003) |
| version | int | monotonic per `id`, >= 1; bumped on any semantic edit |
| confidence | real | 0..1 expert prior; the base match score emitted by FR-RULE-002 |
| status | text | enum: `active` \| `draft` \| `deprecated` (FR-RULE-003 loads `active`) |
| reviewed_by | text | expert sign-off handle (FR-KB-004); nullable while `draft` |
| created_at | timestamptz | audit |
| updated_at | timestamptz | audit |

Uniqueness is on `id` (the current row). Version history is retained per the FR-KB-004 curation workflow; at MVP a single-current-row table plus an append-only `pattern_audit` row (FR-PLAT-003) is sufficient, and `(id, version)` is the reproducibility key.

### Pattern row JSON (one seed entry / one table row)

```json
{
  "id": "qimen_thanh_long_hoi_dau",
  "system": "qimen",
  "name": "Thanh Long Hoi Dau",
  "name_han": "青龍返首",
  "conditions": {
    "type": "and",
    "rules": [
      { "field": "truc_phu.cung", "operator": "eq", "value": "ban.thien_ban.cung_of.丙" },
      { "field": "door", "operator": "in", "value": ["Sinh", "Khai", "Tu"] }
    ]
  },
  "polarity": "cat",
  "meaning_classical": "丙加值符, cat khi tu tap, loi cho khoi su va cau kien.",
  "meaning_modern": "A strong-timing configuration for initiating or requesting; frame as favorable window, not a guarantee.",
  "citations": ["yba_thien_can_khac_ung_12", "kmdg_cach_cuc_thanh_long"],
  "version": 1,
  "confidence": 0.9,
  "status": "active"
}
```

### Rust types (`crates/cyberos-rule/src/pattern.rs`)

```rust
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct Pattern {
    pub id: String,
    pub system: System,
    pub name: String,
    #[serde(default)] pub name_han: Option<String>,
    pub conditions: serde_json::Value,   // parsed + deep-validated by FR-RULE-002
    pub polarity: Polarity,
    pub meaning_classical: String,
    pub meaning_modern: String,
    #[serde(default)] pub citations: Vec<String>,
    pub version: u32,                    // >= 1
    pub confidence: f32,                 // 0.0..=1.0
    #[serde(default = "Status::active")] pub status: Status,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum System { Qimen, Liuren, Taiyi, All }

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Polarity { Cat, Hung, Trung }

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Status { Active, Draft, Deprecated }

impl Pattern { pub fn stamp(&self) -> (String, u32) { (self.id.clone(), self.version) } }
```

`conditions` is `serde_json::Value` at this layer on purpose: the shared crate must not depend on the DSL evaluator (FR-RULE-002 depends on this FR, not the reverse). This FR validates the pattern envelope and does a shallow structural check of `conditions`; FR-RULE-002 parses and deep-validates it.

### Validator (`crates/cyberos-rule/src/validate.rs`)

```rust
pub fn validate_pattern(v: &serde_json::Value) -> Result<Pattern, Vec<ValidationError>>;
```

Checks, accumulating all failures (not fail-on-first):
1. Deserializes into `Pattern` with `deny_unknown_fields`; unknown/missing fields are errors.
2. `system`, `polarity`, `status` parse to their enums.
3. `confidence` in `[0.0, 1.0]`; `version >= 1`.
4. `conditions` is a non-empty JSON object whose top-level form is recognized: either a connective (`type` in {`and`, `or`, `not`}) or a leaf (has a `field` key). Depth and operator validity are deferred to FR-RULE-002.
5. If `status == active`: `citations` is non-empty and `reviewed_by` is present at the DB layer (the seed loader warns; the DB enforces).

### Seed-file format (`crates/cyberos-rule/seed/<system>.json`)

One JSON file per system (`qimen.json`, `liuren.json`, `taiyi.json`, `all.json`), each a JSON array of pattern rows in the shape above minus `created_at`/`updated_at`. `load_seed(dir) -> Result<Vec<Pattern>, SeedError>` validates every entry with `validate_pattern` and rejects the whole file on any error (so a malformed pattern never reaches the DB). This seed is the source FR-KB-002 fills with 150-200 patterns, the fixture FR-RULE-002 tests against, and the offline repository FR-RULE-003 reads when no DB is present.

## §4 - Acceptance criteria

1. `docs/contracts/knowledge-pattern.schema.json` validates the sample row and rejects a row with an unknown field, a bad `system`, a `confidence` of 1.5, or `version` 0.
2. `validate_pattern` returns `Ok(Pattern)` for a valid row and an error vector listing every violation for an invalid one (multiple violations reported at once).
3. An `active` pattern with an empty `citations` array fails validation with a citation-required error.
4. `conditions` that is a JSON array, a scalar, an empty object, or an object lacking both `type` and `field` fails the shallow structural check.
5. `load_seed` loads `seed/qimen.json`, validates every entry, and returns them; injecting one malformed entry fails the whole load with the offending `id` named.
6. `Pattern::stamp()` returns `(id, version)`; the Rust struct and the JSON Schema expose the identical field set (a test asserts parity).

## §5 - Verification

- `tests/pattern_schema.rs`: round-trips the sample fixture (`fixtures/patterns_seed_sample.json`) Rust -> JSON -> Rust byte-stable; asserts each acceptance case above with a table of good/bad rows.
- Schema parity: a test loads `knowledge-pattern.schema.json` and asserts every `required` property maps to a `Pattern` field and vice versa, so the two cannot drift.
- Seed validation: `load_seed` over the committed `seed/qimen.json` sample must pass; a second fixture with a deliberately broken entry must fail with the entry `id` in the error.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-rule -- -D warnings`, `cargo test -p cyberos-rule`.

## §6 - Implementation skeleton

1. Create the `cyberos-rule` crate (this FR owns its birth; FR-RULE-002/003 add modules to it, mirroring how `cyberos-lichphap` is born in FR-CORE-001).
2. Author `docs/contracts/knowledge-pattern.schema.json` from §3 (source of truth for the row shape).
3. `pattern.rs`: the `Pattern` struct, `System` / `Polarity` / `Status` enums, `stamp()`.
4. `validate.rs`: `validate_pattern` with accumulating `ValidationError`; the shallow `conditions` structural check.
5. `version.rs`: helpers for the `(id, version)` stamp and a `bump()` guard used by FR-KB-004.
6. `seed.rs`: `load_seed(dir)`; commit a small `seed/qimen.json` (a handful of patterns) as the format exemplar and test fixture. FR-KB-002 grows it.

## §7 - Dependencies

Depends on FR-PLAT-003, which creates the physical `knowledge_patterns` table, indexes, and RLS from the shape this FR defines. Blocks FR-RULE-002 (the DSL parses the `conditions` field this FR carries) and FR-KB-002 (pattern seeding fills the seed-file format and the table this FR shapes). FR-QMDG-005 consumes detected patterns downstream through FR-RULE-003.

## §8 - Example payloads

A LiuRen khoa the row and a cross-system row:

```json
[
  { "id": "liuren_nguyen_thai", "system": "liuren", "name": "Nguyen Thai",
    "name_han": "元胎", "conditions": { "type": "and", "rules": [
      { "field": "khoa_the", "operator": "eq", "value": "nguyen_thai" } ] },
    "polarity": "trung", "meaning_classical": "Khoa the co ban, chi su sinh khoi.",
    "meaning_modern": "Baseline lesson-type; read the tam truyen for direction.",
    "citations": ["dllr_khoa_the_01"], "version": 1, "confidence": 0.7, "status": "active" },

  { "id": "chung_khong_vong", "system": "all", "name": "Khong Vong",
    "name_han": "空亡", "conditions": { "type": "and", "rules": [
      { "field": "dung_than.tuan_khong", "operator": "eq", "value": true } ] },
    "polarity": "hung", "meaning_classical": "Dung than lac tuan khong, su kho thanh.",
    "meaning_modern": "Key significator falls void; treat timing as unripe, not doomed.",
    "citations": ["chung_tuan_khong_01"], "version": 2, "confidence": 0.6, "status": "active" }
]
```

## §9 - Open questions

- Full version history table vs single-current-row + audit. Default for MVP: one current row per `id` plus a `pattern_audit` append row in FR-PLAT-003; a dedicated `pattern_versions` table is a FR-KB-004 concern if experts need diffs across many revisions.
- Should `citations` be typed objects rather than string ids at this layer? Default: string ids that resolve against the FR-KB-003 corpus, so this crate stays free of corpus types; the citation card is assembled in FR-RAG-003. Revisit if the rule engine needs locator ranges.
- `confidence` provenance: expert-set constant now; whether FR-RAG-006 evals ever feed a learned prior back into it is deferred, and would itself be a versioned edit.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Hardcoded pattern | a cach cuc encoded as Rust `if` instead of a row | code review rejects; no detection path exists outside the data ruleset |
| Silent pattern edit | `conditions`/meaning changed without version bump | FR-KB-004 guard + reproducibility test (old stamp no longer matches text) fails |
| Uncited active pattern | `status = active`, `citations = []` | `validate_pattern` fails; DB check constraint (FR-PLAT-003) rejects insert |
| Schema drift | Rust `Pattern` and JSON Schema diverge | parity test fails in CI before ship |
| Malformed seed | one bad entry in a seed file | `load_seed` fails the whole file with the offending `id`; nothing partial loads |
| Bad enum from DB | a legacy `system` string not in the enum | typed deserialize error, surfaced by FR-RULE-003 loader, not silently skipped |

## §11 - Notes

This is the smallest P0 RULE FR but it sets a hard rule for the entire product: patterns are data. Everything else in the module (FR-RULE-002 evaluator, FR-RULE-003 loader) and the KB seeding (FR-KB-002) and curation (FR-KB-004) assume this shape. The crate name `cyberos-rule` is shared with FR-RULE-002/003; they extend this crate rather than create new ones, so the rule engine is one deterministic, cargo-testable unit shared by all three casting systems. Keep the schema under `docs/contracts/` beside `laso-envelope.schema.json` so the contract is reviewable independently of the build.
