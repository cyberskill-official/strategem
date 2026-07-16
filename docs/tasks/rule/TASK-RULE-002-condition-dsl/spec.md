---
id: TASK-RULE-002
title: "Condition DSL (and/or/not + eq/in/gte/lte/exists/contains, field paths into the la so) + deterministic evaluator + scoring that returns matched patterns as cach_cuc with citations"
module: RULE
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.2, strategy 4.3, Grok-31, Claude-06 s2.3]
related_frs: [TASK-RULE-001, TASK-RULE-003, TASK-RULE-004, TASK-PLAT-002, TASK-QMDG-005]
depends_on: [TASK-RULE-001]
blocks: [TASK-RULE-003, TASK-RULE-004, TASK-QMDG-005]
new_paths:
  - crates/cyberos-rule/src/dsl.rs
  - crates/cyberos-rule/src/path.rs
  - crates/cyberos-rule/src/eval.rs
  - crates/cyberos-rule/src/score.rs
  - crates/cyberos-rule/tests/dsl_eval.rs
  - crates/cyberos-rule/tests/fixtures/laso_qimen_sample.json
  - docs/contracts/condition-dsl.schema.json
---

## §1 - Description (BCP-14 normative)

This task defines the condition DSL - the small JSON language a pattern's `conditions` field is written in - and a deterministic evaluator that runs it against a la so envelope. This is step 4 of the nine-step query flow: the rule engine scans the chart and detects patterns (strategy 4.2). The module SHALL parse the DSL, SHALL evaluate it against a la so with no side effects and no panics, and SHALL emit each matching pattern as a `CachCuc` (the envelope type from TASK-PLAT-002) carrying the pattern id, name, palace, polarity, score, and citations.

The DSL SHALL support boolean composition by `and`, `or`, and `not`, nestable to arbitrary depth, over leaf rules. A leaf rule SHALL be `{ "field": <path>, "operator": <op>, "value": <json> }` with operators `eq`, `in`, `gte`, `lte`, `exists`, and `contains`. `field` is a dotted path resolved against the la so (default root `ban`, escaping to other envelope sections by a reserved first segment, per section 3). The evaluator SHALL be a pure function of `(conditions, la_so)`: identical inputs SHALL always yield the identical boolean, and evaluation SHALL NOT mutate the chart (the AI/interpretation branch never writes `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai`, and neither does this deterministic detector - it only reads and appends detected patterns).

A missing field path SHALL evaluate to a defined result, never an error or panic: for `eq`, `in`, `gte`, `lte`, and `contains` a missing or null path yields `false`; `exists` is the explicit presence test. Scoring: a matched pattern's score SHALL default to the pattern `confidence` (TASK-RULE-001); the DSL MAY carry an optional per-node `weight` reserved for TASK-RULE-004, ignored at MVP. This task provides the parser, the path resolver, the evaluator, and the scorer; TASK-RULE-003 wraps them with loading, caching, and per-system filtering.

## §2 - Why this design (rationale for humans)

A general boolean-tree DSL with a handful of operators is exactly enough to express the cach cuc and khoa the conditions the Claude source lists (Claude-06 s2.3) and the pattern-as-data approach the Grok source specifies (Grok-31), while staying small enough to evaluate deterministically and audit by eye. QiMen cat/hung patterns are overwhelmingly conjunctions of positional facts ("this door on this palace with this star"), which is `and` over `in`/`eq` leaves; the rarer exclusions need `not`; alternatives need `or`. Six operators cover equality, set membership, ordered thresholds (wang-suy strength, scores), presence, and array/substring membership. Anything the DSL cannot express is a signal that the fact belongs in the engine output (`ban`) as a first-class field, not that the DSL needs more power - keeping the language small is what keeps it deterministic and reviewable.

The defined-on-missing rule matters more than it looks. Charts across systems and school flags do not all carry the same fields; a QiMen-only path is absent from a LiuRen chart. If a missing path threw, a cross-system or `all` pattern would panic on half the charts; if it returned an ambiguous value, matching would be non-deterministic. Making a missing path cleanly `false` (except under the explicit `exists`) means a pattern simply does not fire where its inputs are absent, which is the correct behavior and keeps the evaluator total. Resolving paths against the whole envelope (not just `ban`) lets a QiMen pattern gate on `lich_phap.tiet_khi` or a flag in `co_truong_phai` without the engine having to copy those into `ban`.

## §3 - Contract (DSL grammar + evaluator)

### JSON grammar

A condition node is one of four forms. Connective nodes are tagged by `type`; a leaf node has no `type` and carries `field`.

```json
{ "type": "and", "rules": [ <node>, <node>, ... ] }
{ "type": "or",  "rules": [ <node>, <node>, ... ] }
{ "type": "not", "rule":  <node> }
{ "field": "<dotted.path>", "operator": "eq|in|gte|lte|exists|contains", "value": <json> }
```

Worked example (the QiMen leaf pair from the design):

```json
{ "type": "and", "rules": [
  { "field": "door", "operator": "in", "value": ["Sinh", "Khai", "Tu"] },
  { "field": "star", "operator": "in", "value": ["At", "Binh", "Dinh"] }
] }
```

### Field paths (`crates/cyberos-rule/src/path.rs`)

Dotted segments with numeric indices for arrays, resolved over `serde_json::Value`. Root rule: if the first segment is a reserved envelope key (`lich_phap`, `cach_cuc`, `co_truong_phai`, `he`, `dau_vao`, `provenance`), the path resolves from the envelope root; otherwise it resolves from `ban` (so bare `door`, `star`, `cung.1.mon` address the plate). Examples:

- `door` -> `ban.door`
- `cung.1.thien_ban.can` -> `ban.cung[1].thien_ban.can`
- `lich_phap.tiet_khi.hien_hanh` -> envelope root, the in-force tiet khi
- `co_truong_phai.pan_method` -> the stamped school flag

```rust
pub fn resolve<'a>(path: &str, laso: &'a serde_json::Value) -> Option<&'a serde_json::Value>;
```

### Operators

| Operator | Semantics | Missing/null path |
|---|---|---|
| `eq` | field == value (JSON equality) | false |
| `in` | value is an array; field is a member | false |
| `gte` | field >= value (numbers, or strings lexicographically) | false |
| `lte` | field <= value | false |
| `exists` | path resolves to a non-null value | (this is the test) |
| `contains` | field is an array containing value, or a string containing the substring | false |

### Evaluator (`crates/cyberos-rule/src/eval.rs`)

```rust
#[derive(Debug, Clone)]
pub enum Cond {
    And(Vec<Cond>),
    Or(Vec<Cond>),
    Not(Box<Cond>),
    Leaf { field: String, op: Op, value: serde_json::Value },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Op { Eq, In, Gte, Lte, Exists, Contains }

impl Cond {
    /// Dispatch on the JSON shape: `type` in {and,or,not} -> connective; else leaf (`field`).
    pub fn from_json(v: &serde_json::Value) -> Result<Cond, DslError>;
}

pub fn evaluate(cond: &Cond, laso: &serde_json::Value) -> bool {
    match cond {
        Cond::And(rs) => rs.iter().all(|r| evaluate(r, laso)),
        Cond::Or(rs)  => rs.iter().any(|r| evaluate(r, laso)),
        Cond::Not(r)  => !evaluate(r, laso),
        Cond::Leaf { field, op, value } => eval_leaf(field, *op, value, laso),
    }
}

fn eval_leaf(field: &str, op: Op, value: &serde_json::Value, laso: &serde_json::Value) -> bool {
    let got = path::resolve(field, laso);          // Option<&Value>
    match op {
        Op::Exists => got.map_or(false, |v| !v.is_null()),
        _ => match got {
            None => false,
            Some(v) if v.is_null() => false,
            Some(v) => match op {
                Op::Eq       => v == value,
                Op::In       => value.as_array().map_or(false, |a| a.contains(v)),
                Op::Gte      => cmp(v, value).map_or(false, |o| o.is_ge()),
                Op::Lte      => cmp(v, value).map_or(false, |o| o.is_le()),
                Op::Contains => contains(v, value),
                Op::Exists   => unreachable!(),
            },
        },
    }
}
```

`from_json` is where the untagged leaf is disambiguated (a node with `type` is a connective; a node with `field` is a leaf; anything else is a `DslError`). An empty `and`/`or` is a `DslError` (a pattern must assert something). `cmp` returns `None` for non-orderable/mismatched JSON types, so `gte`/`lte` against a non-number are cleanly `false`.

### Scoring and cach_cuc emission (`crates/cyberos-rule/src/score.rs`)

```rust
use laso_envelope::{LaSo, CachCuc};   // TASK-PLAT-002 types

/// Evaluate one pattern against a chart; emit a CachCuc if it fires.
pub fn score_match(p: &Pattern, laso: &LaSo) -> Option<CachCuc> {
    let cond = Cond::from_json(&p.conditions).ok()?;   // deep-validate here
    if evaluate(&cond, &laso.as_addressing_root()) {
        Some(CachCuc {
            id: p.id.clone(),
            name: p.name.clone(),
            cung: resolve_cung(p, laso),               // Option<u8> from an optional `cung` hint/path
            polarity: p.polarity.into(),               // RULE Polarity -> envelope Polarity
            score: Some(p.confidence),                 // base score = expert prior
            citations: p.citations.clone(),
        })
    } else { None }
}
```

`as_addressing_root()` presents the envelope so paths resolve per the root rule above. The emitted `CachCuc` is exactly the envelope shape from TASK-PLAT-002 so the interpretation branch consumes detected patterns with no adapter.

## §4 - Acceptance criteria

1. `Cond::from_json` parses the worked example and arbitrarily nested `and`/`or`/`not` trees; it rejects an empty `and`, a leaf with an unknown operator, and a node with neither `type` nor `field`.
2. `evaluate` returns the correct boolean for a truth table over all six operators, including a `not` of a nested `or`.
3. A missing field path yields `false` for `eq`/`in`/`gte`/`lte`/`contains` and the correct boolean for `exists`; no input panics the evaluator (property test over random paths and charts).
4. `in` matches set membership; `contains` matches array membership and string substring; `gte`/`lte` order numbers and strings and return `false` on type mismatch.
5. `score_match` emits a `CachCuc` with `score = confidence` and the pattern citations when the tree matches, and `None` when it does not; the emitted type is byte-identical to an TASK-PLAT-002 `CachCuc`.
6. The evaluator is deterministic: 1,000 repeat evaluations of the same `(pattern, chart)` return the identical result and identical `CachCuc` ordering of fields.

## §5 - Verification

- `tests/dsl_eval.rs`: a truth-table suite over the six operators; nested-tree cases; the missing-path matrix; the QiMen worked example evaluated against `fixtures/laso_qimen_sample.json` (a real la so envelope emitted by the QMDG engine or hand-built to the TASK-PLAT-002 schema).
- Property test: for 10,000 random `(field-path, operator, value, chart)` tuples, `evaluate` never panics and is total; `exists` agrees with a direct `resolve(path).is_some_and(non-null)`.
- Schema: `docs/contracts/condition-dsl.schema.json` validates every `conditions` tree in the TASK-RULE-001 seed and rejects malformed trees; a test cross-checks that `Cond::from_json` accepts exactly what the schema accepts.
- Cross-type: `score_match` output deserializes as a `laso_envelope::CachCuc` (contract with TASK-PLAT-002).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-rule -- -D warnings`, `cargo test -p cyberos-rule`.

## §6 - Implementation skeleton

1. `path.rs`: the dotted-path resolver with the reserved-root rule and numeric array indexing over `serde_json::Value`.
2. `dsl.rs`: `Cond`, `Op`, `Cond::from_json`, `DslError`; author `docs/contracts/condition-dsl.schema.json` to match.
3. `eval.rs`: `evaluate`, `eval_leaf`, `cmp`, `contains`; the total, panic-free leaf semantics.
4. `score.rs`: `score_match`, `resolve_cung`, the RULE-to-envelope `Polarity` conversion; depend on the `laso-envelope` crate (TASK-PLAT-002).
5. Build `fixtures/laso_qimen_sample.json` and wire the truth-table, property, and schema-parity tests.

## §7 - Dependencies

Depends on TASK-RULE-001 (the `Pattern` type and the `conditions` field this task parses) and, for the emitted `CachCuc`, on TASK-PLAT-002 (the la so envelope crate). Blocks TASK-RULE-003 (the loader/match API wraps this evaluator), TASK-RULE-004 (cross-system nesting extends this grammar and the reserved `weight`), and TASK-QMDG-005, whose cach cuc detection runs this evaluator over the QiMen plate through the TASK-RULE-003 loader.

## §8 - Example payloads

Input pattern `conditions` and the emitted cach_cuc:

```json
// conditions (qimen_thanh_long_hoi_dau, abbreviated)
{ "type": "and", "rules": [
  { "field": "cung.1.mon", "operator": "in", "value": ["Sinh", "Khai"] },
  { "field": "cung.1.sao", "operator": "eq", "value": "Thien Nham" },
  { "field": "co_truong_phai.pan_method", "operator": "eq", "value": "zhuan" }
] }
```

```json
// emitted CachCuc (TASK-PLAT-002 shape) when the tree matches
{ "id": "qimen_thanh_long_hoi_dau", "name": "Thanh Long Hoi Dau", "cung": 1,
  "polarity": "cat", "score": 0.9, "citations": ["yba_thien_can_khac_ung_12"] }
```

## §9 - Open questions

- Do we need a `regex` or `range` operator for wang-suy strength bands, or is `gte`/`lte` enough? Default: the six operators; add only when a real seed pattern cannot be expressed, to keep the evaluator total and auditable.
- Where does `cung` on a multi-palace pattern come from - a fixed hint field on the pattern, or resolved from a field path at match time? Default: an optional `cung` hint on the pattern row, else `None`; TASK-RULE-004 may compute it for multi-palace cross-system patterns.
- Should `gte`/`lte` on strings be allowed at all, or numbers only? Default: allow lexicographic string order (some can/chi orderings use it) but document it; revisit if it causes surprise.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Panic on missing field | pattern path absent from this chart | resolver returns `None`; leaf is `false` (or the `exists` test); never panics |
| Non-deterministic match | reliance on map iteration order or float NaN | canonical JSON equality; `cmp` returns `None` on non-orderable, giving stable `false` |
| Empty connective | `{ "type": "and", "rules": [] }` | `from_json` is a `DslError`; the pattern fails TASK-RULE-001 review before load |
| Fabricated operator | `"operator": "matches"` | `from_json` rejects; schema rejects; the seed never loads |
| Escaped write | detector tries to mutate `ban` | impossible by type: evaluator takes `&Value`, emits new `CachCuc`; no setter path exists |
| Cross-system field leak | a QiMen-only path used by an `all` pattern | resolves to `None` on non-QiMen charts -> `false`; the `all` pattern simply does not fire there |

## §11 - Notes

The evaluator is the deterministic heart shared by all three systems: QiMen cach cuc, LiuRen khoa the, and TaiYi patterns are all rows whose `conditions` this one function runs. Keeping it total (no panics, defined-on-missing) is what lets a single ruleset span three chart shapes and every school-flag combination without special-casing. Do not add operators speculatively; each one widens the test surface and the review burden. This task plus TASK-RULE-001 make the ruleset fully data-driven; TASK-RULE-003 only adds the plumbing to load and cache it.
