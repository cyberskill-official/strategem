# RULE - rule engine / pattern matching

The deterministic pattern engine: it scans a la so and detects the named patterns - cach cuc (格局) for QiMen, khoa the (課體) for LiuRen, and the equivalent configurations for TaiYi - as step 4 of the query flow (strategy 4.2). Language is Rust (DEC-2); everything lives in one crate, `cyberos-rule`. Primary sources: Grok 31 (rule engine, pattern-as-data), Claude 06 s2.3 (cach cuc detection). See the unified plan sections 4.1-4.2 and 5 for rationale.

The one hard rule of this module: patterns are data, not code. A pattern is a row in `knowledge_patterns` whose match logic is a JSON condition tree and whose meaning is cited classical text. There is no code path that detects a pattern outside the data ruleset.

## FRs

| FR | Pri | Phase | h | depends_on | Spec | Title |
|---|---|---|--:|---|---|---|
| RULE-001 | MUST | P0 | 8 | PLAT-003 | [FR-RULE-001](FR-RULE-001-pattern-schema/spec.md) | Pattern-as-data schema + knowledge_patterns table + versioning |
| RULE-002 | MUST | P0 | 12 | RULE-001 | [FR-RULE-002](FR-RULE-002-condition-dsl/spec.md) | Condition DSL (AND/OR/NOT, field operators) + evaluator + scoring |
| RULE-003 | MUST | P0 | 6 | RULE-002 | [FR-RULE-003](FR-RULE-003-pattern-loader/spec.md) | Pattern loader + per-system filter + match API |
| RULE-004 | COULD | P2 | 8 | RULE-002 | [FR-RULE-004](FR-RULE-004-cross-system/spec.md) | Cross-system pattern support (nested, multi-system) |

Three P0 FRs are authored. RULE-004 (cross-system patterns) is P2 / COULD, authored; it extends the FR-RULE-002 DSL and the FR-RULE-003 matcher for multi-system, nested patterns and the reserved per-node `weight`.

## Internal spine

```
RULE-001 (pattern-as-data schema + knowledge_patterns shape + validator + seed format)
   -> RULE-002 (condition DSL grammar + deterministic evaluator + scoring -> CachCuc)
        -> RULE-003 (loader + per-system filter + cache + match(la_so) -> Vec<CachCuc>)
        -> RULE-004 (cross-system nesting; P2)
```

## Cross-module dependencies

- Depends on PLAT-003, which creates the physical `knowledge_patterns` table, indexes, and RLS from the schema shape FR-RULE-001 owns. Depends on PLAT-002 for the la so envelope types (`LaSo`, `CachCuc`) that FR-RULE-002 emits.
- Blocks QMDG-005 and every engine's cach cuc detection: QMDG-005 lists RULE-002 (the evaluator) as its hard build dependency in the master table, and RULE-003's `match(la_so)` is the runtime API all three casting engines call to fill the `cach_cuc` envelope slot. Also blocks STRAT-001 (Timing Optimizer), which scores candidate windows through the match API.
- Fed by KB-002 (pattern seeding, 150-200 patterns into the FR-RULE-001 seed/table) and KB-004 (curation, expert review, versioning). Citations on each pattern resolve into the KB-003 classical corpus.

## Module notes

- Pattern-as-data is a hard rule. No cach cuc, khoa the, or than sat is hardcoded in Rust; each is a versioned row with JSON conditions and cited meaning. Adding or correcting a pattern is a data change that ships without recompiling the engine.
- Patterns are expert-reviewable and versioned. Every row carries a monotonic `version`; a detected pattern stamps `(id, version)` so an interpretation is reproducible against the exact text that fired, and the eval loop (RAG-006) can tell an intended revision from a regression. Retiring a pattern deprecates it, never deletes it. An `active` pattern must carry a citation - no source, no claim.
- The engine is deterministic and shared by all three systems. One `cyberos-rule` crate, one evaluator, one match API, run over QiMen, LiuRen, and TaiYi charts and every school-flag combination. It is offline-testable by design: the evaluator is a pure, panic-free function, and tests use the seed repository, never a live database. The deterministic output ordering is something the engine-assembly oracle gates (QMDG-006 and the other engines) depend on.
