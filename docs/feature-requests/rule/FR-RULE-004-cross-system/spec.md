---
id: FR-RULE-004
title: "Cross-system pattern support - extend the FR-RULE-002 DSL to patterns spanning more than one chart in a set (system: all over a QiMen + LiuRen chart set for the same question) and nested multi-condition trees with node weights; the totality guarantee generalizes"
module: RULE
priority: COULD
status: done
phase: P2
slice: 1
lang: rust
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.2, strategy 4.3, Grok-31, Claude-06 s2.3]
related_frs: [FR-RULE-001, FR-RULE-002, FR-RULE-003, FR-PLAT-002, FR-QMDG-006, FR-LN-006, FR-STRAT-004]
depends_on: [FR-RULE-002]
blocks: []
new_paths:
  - crates/cyberos-rule/src/cross.rs
  - crates/cyberos-rule/src/score_set.rs
  - crates/cyberos-rule/tests/cross_system.rs
  - crates/cyberos-rule/tests/fixtures/chart_set_qimen_liuren.json
---

## §1 - Description (BCP-14 normative)

This FR extends the FR-RULE-002 condition DSL and evaluator to cross-system patterns: patterns whose condition references more than one chart in a set cast for the same question (for example a QiMen chart together with a LiuRen chart), plus deeper nested multi-condition trees carrying per-node weights. It is the rule-engine support the cross-system validate feature (FR-STRAT-004) runs on (Grok-31).

The module SHALL introduce a `ChartSet` - a map from `He` to the `LaSo` (FR-PLAT-002) cast for one question - and SHALL extend the path grammar with an optional system qualifier: a `field` MAY be prefixed `<he>:` (one of `luc_nham`, `ky_mon`, `thai_at`) to select which chart in the set the rest of the path resolves against, after which the FR-RULE-002 reserved-root rule applies within that chart. A bare (unqualified) path SHALL resolve against a designated primary chart, so a single-chart evaluation is exactly the existing FR-RULE-002 behavior and nothing regresses. The module SHALL evaluate a (possibly cross-system) condition tree over a `ChartSet` (`evaluate_set`) and SHALL make the reserved per-node `weight` (FR-RULE-002) meaningful for cross-system scoring (`score_set`).

The evaluator SHALL stay total and pure exactly as in FR-RULE-002: a qualified path whose chart is absent from the set, or whose field is absent from that chart, SHALL resolve to a defined result (`false` for `eq` / `in` / `gte` / `lte` / `contains`, the presence test for `exists`) and SHALL NOT panic. A cross-system pattern SHALL be a `system: all` row (FR-RULE-001) whose `conditions` reference more than one chart; it SHALL emit a `CachCuc` (FR-PLAT-002) like any pattern, with `cung` optional (a whole-set agreement pattern has no single palace). This FR extends the grammar, the resolver, the evaluator, and the scorer; it SHALL NOT add operators, and it SHALL remain deterministic and offline-testable over the seed repository (FR-RULE-003).

## §2 - Why this design (rationale for humans)

The integration level of the product is cross-checking the systems against each other: cast a question in QiMen and in LiuRen and see whether they agree (strategy 4.2 step 4 for a chart set; Claude-06 s2.3 pattern detection; the L4 curriculum skill of doi chieu ket qua nhieu he). FR-STRAT-004 is that feature. It needs a way to say, as data, "when the QiMen chart shows this cat cach and the LiuRen tam truyen shows that, the two systems concur" - a pattern that spans two charts. FR-RULE-002 evaluates one chart; this FR generalizes it to a set without changing the operator surface or the totality guarantee, so cross-system agreement is expressed as reviewable, cited pattern rows (Grok-31), not as bespoke comparison code.

The system-qualified path is the whole trick, and it is deliberately minimal. FR-RULE-002 already resolves a path against one envelope with a reserved-root rule; prefixing a path with `ky_mon:` or `luc_nham:` just picks which envelope in the set to apply that same rule to. That means a cross-system condition reuses every existing operator and the entire single-chart resolver unchanged - the only new thing is choosing the chart first. Keeping the bare path resolving against a primary chart means every existing FR-RULE-002 pattern and test is a cross-system evaluation with a one-chart set, so there is no fork and no regression.

The totality guarantee generalizing is what keeps this safe. FR-RULE-002's rule that a missing path is cleanly `false` already handles a QiMen-only field on a non-QiMen chart; here the same rule handles a qualified path whose chart is not in the set - a `ky_mon:` path when only a LiuRen chart was cast simply does not fire. So a cross-system pattern degrades gracefully to whatever charts are present, which is the correct behavior for a validate feature the user may run on one or several systems. The `weight` node, reserved but ignored at MVP, becomes the way a scorer expresses "this pattern is a stronger agreement signal when both arms match," feeding the FR-STRAT-004 agreement view without a new scoring language.

## §3 - Contract (chart set + qualified paths + weighted scoring)

### Chart set (`crates/cyberos-rule/src/cross.rs`)

```rust
use laso_envelope::{LaSo, He, CachCuc};   // FR-PLAT-002

/// The charts cast for ONE question, keyed by system. One or several systems.
#[derive(Debug, Clone)]
pub struct ChartSet {
    pub charts: BTreeMap<He, LaSo>,   // e.g. { KyMon: .., LucNham: .. }
    pub primary: He,                  // the chart a bare (unqualified) path resolves against
}

impl ChartSet {
    pub fn single(la_so: LaSo) -> Self;   // one chart; primary = its he (FR-RULE-002 parity)
    pub fn get(&self, he: He) -> Option<&LaSo>;
}
```

### Qualified path resolution

A path MAY carry an optional leading `<he>:` qualifier; the rest resolves by the FR-RULE-002 rule within the selected chart.

- `ky_mon:cung.1.mon` -> the QiMen chart's `ban.cung[1].mon`
- `luc_nham:tam_truyen.0.than` -> the LiuRen chart's `ban.tam_truyen[0].than`
- `ky_mon:cach_cuc` -> the QiMen chart's envelope-root `cach_cuc` (reserved-root rule inside the chosen chart)
- `door` (bare) -> the primary chart's `ban.door` (unchanged FR-RULE-002 behavior)

```rust
/// Resolve a (possibly `<he>:`-qualified) path against a chart set.
/// Absent chart or absent field -> None (leaf then evaluates to false / the exists test).
pub fn resolve_in_set<'a>(path: &str, set: &'a ChartSet) -> Option<&'a serde_json::Value>;
```

### Cross-system evaluator

```rust
use cyberos_rule::eval::Cond;   // FR-RULE-002 Cond / Op unchanged

/// Evaluate a condition tree over a chart set. Total and pure, exactly as FR-RULE-002:
/// identical (cond, set) -> identical bool; no panics; missing path -> defined result.
pub fn evaluate_set(cond: &Cond, set: &ChartSet) -> bool;
```

`evaluate_set` is `evaluate` (FR-RULE-002) with `resolve_in_set` swapped for `resolve` at the leaf; the connective logic (`and` / `or` / `not`, empty-connective rejection) is unchanged. `evaluate(cond, laso)` equals `evaluate_set(cond, ChartSet::single(laso.clone()))`, so the single-chart path is a special case.

### Grammar extension (leaf qualifier + node weight)

The FR-RULE-002 JSON grammar gains two optional, additive fields; `docs/contracts/condition-dsl.schema.json` is amended (not replaced) and its schema note is versioned:

```json
{ "type": "and", "weight": 1.0, "rules": [
  { "field": "ky_mon:cach_cuc", "operator": "contains", "value": "青龍返首" },
  { "field": "luc_nham:tam_truyen.0.than", "operator": "in", "value": ["六合", "青龍"] }
] }
```

`weight` (default `1.0`) is a per-node hint for scoring; `field` MAY begin `<he>:`. A qualifier that is not a valid `He` is a `DslError` (as with an unknown operator in FR-RULE-002).

### Weighted scoring (`crates/cyberos-rule/src/score_set.rs`)

```rust
/// Evaluate a cross-system pattern over a chart set; emit a CachCuc if it fires.
/// score = pattern.confidence, optionally shaped by matched-node weights for the
/// FR-STRAT-004 agreement view. cung is None for whole-set patterns.
pub fn score_match_set(p: &Pattern, set: &ChartSet) -> Option<CachCuc>;
```

`score_match_set` mirrors FR-RULE-002 `score_match` but runs `evaluate_set`; the emitted `CachCuc` is the same envelope type, so the loader / matcher (FR-RULE-003) and the interpretation branch consume cross-system hits with no adapter.

## §4 - Acceptance criteria

1. `resolve_in_set` resolves a `<he>:`-qualified path to the right chart's field and a bare path to the primary chart; an absent chart or absent field yields `None` (never a panic).
2. `evaluate_set` matches an FR-RULE-002 single-chart result exactly when the set is `ChartSet::single(laso)` (back-compat: the existing FR-RULE-002 truth-table suite passes through `evaluate_set` unchanged).
3. A cross-system `system: all` pattern with one `ky_mon:` arm and one `luc_nham:` arm fires only when both charts are present and both arms hold; with only one chart in the set the qualified path to the missing chart is `false`, so the pattern does not fire (totality generalizes).
4. Arbitrarily nested `and` / `or` / `not` trees mixing qualified and bare leaves evaluate correctly; an empty connective and an invalid `<he>:` qualifier are `DslError`s.
5. `score_match_set` emits a `CachCuc` (FR-PLAT-002 shape) with `cung: None` for a whole-set agreement pattern and applies node `weight` to the score deterministically; the emitted type deserializes as a `laso_envelope::CachCuc`.
6. The evaluator is total and deterministic: a property test over random qualified / bare paths and random chart sets never panics; 1,000 repeat evaluations of one `(pattern, set)` are identical.

## §5 - Verification

- `tests/cross_system.rs`: `resolve_in_set` cases (qualified hit, bare-to-primary, absent chart, absent field); the back-compat suite (run FR-RULE-002 truth tables through `evaluate_set` on single-chart sets); the two-arm cross-system pattern over `fixtures/chart_set_qimen_liuren.json` (both present -> fires; QiMen-only -> does not); nested mixed trees; the `DslError` cases (empty connective, bad qualifier).
- Property test: 10,000 random `(path, operator, value, chart-set)` tuples - `evaluate_set` never panics and is total; a qualified path to a missing chart agrees with `false` (except `exists`).
- Schema: the amended `condition-dsl.schema.json` accepts the `weight` and `<he>:`-qualified forms and still rejects malformed trees; a test asserts `Cond::from_json` accepts exactly what the schema accepts.
- Cross-type: `score_match_set` output deserializes as a `laso_envelope::CachCuc` (FR-PLAT-002 contract); the seed repository (FR-RULE-003) loads a cross-system `system: all` pattern.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-rule -- -D warnings`, `cargo test -p cyberos-rule`.

## §6 - Implementation skeleton

1. `cross.rs`: `ChartSet` (with `single` and `primary`); `resolve_in_set` (split an optional `<he>:` qualifier, then delegate to the FR-RULE-002 `path::resolve` within the chosen chart); `evaluate_set` (FR-RULE-002 `evaluate` with the set-aware leaf).
2. Extend `Cond::from_json` (FR-RULE-002) to accept an optional `weight` on connective nodes and a `<he>:` qualifier on leaves; reject an invalid qualifier as `DslError`.
3. `score_set.rs`: `score_match_set` over `evaluate_set`, weight-aware; emit the envelope `CachCuc`.
4. Amend `docs/contracts/condition-dsl.schema.json` for `weight` and the qualified `field`; bump its schema note.
5. Build `fixtures/chart_set_qimen_liuren.json` (a QiMen + LiuRen set for one question) and wire the back-compat, cross-system, property, and schema tests.

## §7 - Dependencies

Depends on FR-RULE-002 (the DSL grammar, the `Cond` / `Op` evaluator, and the reserved per-node `weight` this FR activates); it extends that crate's `dsl.rs` / `eval.rs` and reuses `path::resolve` unchanged inside the chosen chart. Transitively uses FR-RULE-001 (`Pattern`, `system: all`) and FR-PLAT-002 (`LaSo`, `He`, `CachCuc`), and stays loadable through the FR-RULE-003 matcher over the seed repository. The charts in a set are produced by FR-QMDG-006 and FR-LN-006.

Consumer, flagged for a human: FR-STRAT-004 (cross-system validate, `/calculate/all` + agreement view) is what runs cross-system patterns over a `ChartSet`. The catalog records FR-STRAT-004 `depends_on` [FR-QMDG-006, FR-LN-006] and not FR-RULE-004 (RULE-004 is COULD / P2, a soft enabler), so `blocks` is left empty here; when FR-STRAT-004 is authored, add FR-RULE-004 to its `depends_on` if the agreement view is built on data patterns rather than bespoke comparison, and record the edge there. FR-RULE-004 lists FR-STRAT-004 in `related_frs` to make the runtime edge explicit.

## §8 - Example payloads

A cross-system agreement pattern (a `system: all` row per FR-RULE-001) and the hit it emits:

```json
// conditions - QiMen cat cach AND a concurring LiuRen tam truyen than
{ "type": "and", "weight": 1.0, "rules": [
  { "field": "ky_mon:cach_cuc",            "operator": "contains", "value": "青龍返首" },
  { "field": "luc_nham:tam_truyen.0.than", "operator": "in",       "value": ["六合", "青龍"] }
] }
```

```json
// emitted CachCuc when both charts are present and both arms hold (whole-set: cung null)
{ "id": "cross_qimen_luc_nham_dong_thuan_cat", "name": "Dong thuan cat (Ky Mon + Luc Nham)",
  "cung": null, "polarity": "cat", "score": 0.85,
  "citations": ["yba_thien_can_khac_ung_12", "dllr_tam_truyen_thanh_long_03"] }
```

With only a QiMen chart in the set, `luc_nham:tam_truyen.0.than` resolves to `None` -> `false`, so the pattern does not fire - the cross-system signal degrades to the single system present.

## §9 - Open questions

- Weight semantics for the agreement view: is `weight` a linear coefficient on the sub-score, or a count of concurring systems? Default: a linear per-node coefficient on `confidence` at MVP, enough for FR-STRAT-004 to rank agreement; a richer agreement metric (fraction of systems concurring) is a STRAT-004 concern layered on top, not a new operator here.
- Primary-chart choice when a bare path appears in a cross-system pattern: implicit (the set's `primary`) or required-explicit. Default: keep `primary` on the set and allow bare paths, but lint cross-system (`system: all`) seed patterns to prefer explicit `<he>:` qualifiers so intent is legible; a bare path still works for single-chart back-compat.
- TaiYi arm: the fixture and the worked example use QiMen + LiuRen (the P0 / P1 engines); a `thai_at:` arm is valid grammar and activates when FR-TAT-006 lands, needing only a fixture, not a code change.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Panic on missing chart | a `ky_mon:` path when no QiMen chart is in the set | `resolve_in_set` returns `None`; leaf is `false` (or the `exists` test); never panics |
| Back-compat regression | `evaluate_set` diverges from FR-RULE-002 on one chart | the FR-RULE-002 truth-table suite run through `evaluate_set` fails; single-chart parity is required |
| Bad qualifier | `field` begins `xx:` (not a `He`) | `Cond::from_json` and the schema reject it as a `DslError` |
| Operator creep | a new operator added for cross-system | rejected in review; this FR adds a chart selector and `weight`, not operators (FR-RULE-002 surface is fixed) |
| Non-deterministic score | weight applied via map-order iteration | fixed traversal; 1,000x determinism test; canonical JSON equality |
| Cross-system leak | a bare path silently reads the wrong chart | seed lint prefers explicit `<he>:` on `system: all` patterns; a bare path resolves only against the declared `primary` |

## §11 - Notes

This is the rule-engine half of cross-system validate (FR-STRAT-004): it lets an agreement between QiMen and LiuRen be written as a data pattern (Grok-31) rather than bespoke comparison code, using one new idea - a `<he>:` chart selector on the front of an otherwise unchanged FR-RULE-002 path. Everything else is inherited: the operators, the resolver, the totality guarantee, the offline seed-testability. Because a missing chart resolves cleanly to `false`, a cross-system pattern degrades to whatever systems the user actually cast, which is the right behavior for a validate feature. Do not widen the operator set here; the only additions are the chart selector and the `weight` node FR-RULE-002 already reserved. refs Grok-31, Claude-06 s2.3.
