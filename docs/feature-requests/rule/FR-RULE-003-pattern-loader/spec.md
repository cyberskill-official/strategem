---
id: FR-RULE-003
title: "Pattern loader + per-system filter + in-memory cache + match(la_so) -> Vec<CachCuc> API the casting engines call, over a DB-or-seed PatternRepository"
module: RULE
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 6
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-31, strategy 4.2, strategy 4.3]
related_frs: [FR-RULE-001, FR-RULE-002, FR-PLAT-002, FR-PLAT-003, FR-PLAT-006, FR-QMDG-005, FR-STRAT-001]
depends_on: [FR-RULE-002]
blocks: [FR-QMDG-005, FR-STRAT-001]
new_paths:
  - crates/cyberos-rule/src/repo.rs
  - crates/cyberos-rule/src/cache.rs
  - crates/cyberos-rule/src/matcher.rs
  - crates/cyberos-rule/tests/loader_match.rs
---

## §1 - Description (BCP-14 normative)

This FR is the runtime entry point of the rule engine: the API a casting engine calls to turn a la so into its detected patterns. It SHALL load `active` patterns from a source, filter them to the systems relevant to a chart, cache them in memory, and expose `match(la_so) -> Vec<CachCuc>` that runs the FR-RULE-002 evaluator over every relevant pattern and returns the matches as envelope `CachCuc` records (FR-PLAT-002).

The loader SHALL read from a `PatternRepository` abstraction with two implementations: a Postgres-backed repository over the `knowledge_patterns` table (FR-PLAT-003) for production, and a seed-file repository over the FR-RULE-001 seed for tests and offline runs. The crate SHALL remain cargo-testable with no database: the Postgres repository lives behind a cargo feature, and every test uses the seed repository. Loading SHALL select only `status = active` rows.

The per-system filter SHALL be derived from the chart: `match` reads `la_so.he`, maps it to a `System`, and considers patterns whose `system` is that system or `all` (a QiMen chart matches `qimen` and `all` patterns, never `liuren` or `taiyi`). The result SHALL be deterministic: matches SHALL be returned in a stable order (by polarity, then descending score, then id) and de-duplicated by pattern id. The cache SHALL be invalidatable (by system, or wholesale) so a curated pattern edit (FR-KB-004) or a new deploy takes effect without a restart; cache correctness SHALL never change which patterns fire, only how fast they load.

## §2 - Why this design (rationale for humans)

FR-RULE-001 and FR-RULE-002 give a ruleset and an evaluator; something has to fetch the rows, keep them hot, and hand a casting engine a one-call detector. That is this FR, and it is deliberately thin (6h) because the logic lives in the two FRs beneath it. The value it adds is three separations that keep the system testable and fast. First, the repository abstraction means the deterministic engine crates never link a database driver into their test builds - the oracle-gated engine tests (FR-QMDG-006) run against the seed repository, pure and offline, while production reads the live table. Second, the per-system filter keeps a chart from being scored against patterns that cannot apply, which is both correct (a LiuRen khoa the is meaningless on a QiMen plate) and cheaper. Third, the in-memory cache reflects the engines' cache-friendly, deterministic nature (Claude-06 s2.2): patterns change rarely, charts are scored constantly, so loading the active set once per system and reusing it is the obvious win, and because matching is a pure function the cache can never change a result - only latency.

Returning the envelope `CachCuc` directly is what lets a casting engine assemble its la so without an adapter: the engine builds `ban`, calls `match`, and drops the returned vector into `cach_cuc`. The interpretation branch then reads those detected patterns with their citations already attached, closing the source -> pattern -> cach cuc -> cited interpretation chain.

## §3 - Contract (repository + cache + match API)

### Repository abstraction (`crates/cyberos-rule/src/repo.rs`)

```rust
pub trait PatternRepository: Send + Sync {
    /// All `active` patterns whose system is `system` or `All`.
    fn active_for(&self, system: System) -> Result<Vec<Pattern>, RepoError>;
}

/// Offline / test source: reads the FR-RULE-001 seed directory and validates each row.
pub struct SeedRepository { patterns: Vec<Pattern> }
impl SeedRepository { pub fn load(dir: &Path) -> Result<Self, RepoError>; }

/// Production source over the knowledge_patterns table (FR-PLAT-003).
#[cfg(feature = "pg")]
pub struct PgRepository { pool: sqlx::PgPool }
```

`SeedRepository::load` calls `seed::load_seed` (FR-RULE-001), so the same validation guards both paths. `PgRepository::active_for` runs `select ... from knowledge_patterns where status = 'active' and system in ($1, 'all')` and deserializes each row through `validate_pattern`, so a bad row from the DB is a typed error, not a silent skip.

### Cache (`crates/cyberos-rule/src/cache.rs`)

An in-memory snapshot per system, behind an `RwLock`, holding an `Arc<Vec<Pattern>>` so readers never block writers mid-scan. Optional TTL for the Postgres repository (default 24h, aligned with the FR-PLAT-006 chart cache); the seed repository is effectively immutable per process.

### Matcher (`crates/cyberos-rule/src/matcher.rs`)

```rust
pub struct Matcher {
    repo: Box<dyn PatternRepository>,
    cache: RwLock<HashMap<System, Arc<Vec<Pattern>>>>,
    ttl: Option<Duration>,
}

impl Matcher {
    pub fn new(repo: Box<dyn PatternRepository>) -> Self;

    /// Preload a system's active patterns (call at startup for warm caches).
    pub fn warm(&self, system: System) -> Result<(), RepoError>;

    /// THE engine-facing API. Reads la_so.he, loads {system, all}, scores each,
    /// returns matches sorted (polarity, -score, id), de-duplicated by id.
    pub fn match_laso(&self, la_so: &LaSo) -> Result<Vec<CachCuc>, RepoError>;

    /// Drop a system's snapshot (call after a curated edit or on deploy).
    pub fn invalidate(&self, system: System);
    pub fn invalidate_all(&self);
}
```

`match_laso` is the operation FR-QMDG-005 and every engine cach cuc step calls, and the operation STRAT-001 leans on to score timing windows. Its body: map `la_so.he` to `System`; get-or-load the cached `Arc<Vec<Pattern>>` for that system (already the union of `system` and `all` from `active_for`); iterate calling `score::score_match(p, la_so)`; collect `Some(_)`; sort and dedup; return.

### Determinism and ordering

Sort key: `polarity` (cat before trung before hung, a fixed enum order), then descending `score`, then ascending `id` as the final tiebreak. De-dup keeps the first occurrence per `id`. The same chart and the same active ruleset always produce the same vector, byte-for-byte, which the engine assembly oracle gates (FR-QMDG-006) depend on.

## §4 - Acceptance criteria

1. `SeedRepository::load` loads the FR-RULE-001 seed and `active_for(Qimen)` returns exactly the `active` patterns whose system is `qimen` or `all`, and none whose system is `liuren`/`taiyi` or whose status is `draft`/`deprecated`.
2. `match_laso` on a QiMen sample chart returns the expected `CachCuc` set, sorted by (polarity, -score, id) and de-duplicated by id.
3. Matching is identical whether patterns come from the seed repository or a stub Postgres repository holding the same rows (repository-parity test).
4. `warm` then `match_laso` performs zero repository reads on the second call for the same system (cache hit); `invalidate(system)` forces a reload.
5. A chart whose `he` has no active patterns returns an empty vector, not an error.
6. A malformed DB row (bad enum, missing field) surfaces as a typed `RepoError` from `active_for`, never a silently dropped pattern.

## §5 - Verification

- `tests/loader_match.rs`: seed load + `active_for` filtering; `match_laso` over `fixtures/laso_qimen_sample.json` (shared with FR-RULE-002) asserting the exact sorted, de-duplicated vector; the cache hit/invalidation behavior with a counting repository stub; the repository-parity test (seed vs in-memory stub Pg).
- Determinism: run `match_laso` 1,000 times and assert vector equality every time.
- Offline guarantee: the default `cargo test -p cyberos-rule` compiles and passes with the `pg` feature off (no database in CI for this crate).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-rule -- -D warnings`, `cargo test -p cyberos-rule`; `cargo clippy -p cyberos-rule --features pg` for the Postgres path.

## §6 - Implementation skeleton

1. `repo.rs`: the `PatternRepository` trait, `SeedRepository` over FR-RULE-001's `load_seed`, and the feature-gated `PgRepository` (query + row validation).
2. `cache.rs`: the `RwLock<HashMap<System, Arc<Vec<Pattern>>>>` snapshot store with optional TTL.
3. `matcher.rs`: `Matcher::new/warm/match_laso/invalidate`; the sort-and-dedup; the `he -> System` mapping.
4. Wire the loader/match/cache tests with a counting repository stub to prove cache hits and invalidation.

## §7 - Dependencies

Depends on FR-RULE-002 (`score_match`, the evaluator) and, transitively, FR-RULE-001 (`Pattern`, seed) and FR-PLAT-002 (`LaSo`, `CachCuc`). The Postgres repository depends on FR-PLAT-003 (the `knowledge_patterns` table) and pairs well with FR-PLAT-006 (the chart cache TTL convention).

Consumers: this is the match API the casting engines call for cach cuc detection. FR-QMDG-005 is the first consumer (its QiMen cach cuc step calls `match_laso`); FR-STRAT-001 (Timing Optimizer) scores candidate windows through it. Note on the dependency spine (flagged for a human): the master FR table records FR-QMDG-005 `depends_on` FR-RULE-002 (the evaluator, a hard build dependency), while FR-QMDG-005 consumes patterns at runtime through this FR's `match_laso`. When FR-QMDG-005 is authored, add FR-RULE-003 to its `depends_on` (RULE-003 already depends on RULE-002, so there is no cycle). This FR lists FR-QMDG-005 in `blocks` to make that runtime edge explicit.

## §8 - Example payloads

```rust
// Engine assembly (FR-QMDG-005/006) usage
let matcher = Matcher::new(Box::new(SeedRepository::load(Path::new("crates/cyberos-rule/seed"))?));
matcher.warm(System::Qimen)?;                 // startup
let cach_cuc: Vec<CachCuc> = matcher.match_laso(&la_so)?;   // per chart
// la_so.cach_cuc = cach_cuc;  (the engine fills the envelope slot)
```

```json
// match_laso(qimen_chart) result (sorted, de-duplicated)
[
  { "id": "qimen_thanh_long_hoi_dau", "name": "Thanh Long Hoi Dau", "cung": 1,
    "polarity": "cat", "score": 0.9, "citations": ["yba_thien_can_khac_ung_12"] },
  { "id": "chung_khong_vong", "name": "Khong Vong", "cung": 3,
    "polarity": "hung", "score": 0.6, "citations": ["chung_tuan_khong_01"] }
]
```

## §9 - Open questions

- TTL vs event-driven invalidation for the Postgres repository. Default: a 24h TTL plus an explicit `invalidate` hook the FR-KB-004 curation flow calls on publish; a pub/sub invalidation is a later optimization if editors need instant propagation.
- Should `match_laso` also accept a pre-fetched `&[Pattern]` for callers that manage their own loading (e.g. FR-STRAT-001 scanning many charts against one warmed set)? Default: expose a lower-level `match_with(&self, patterns, la_so)` used internally and by STRAT to avoid re-locking the cache per chart in a tight scan.
- Whether the cache belongs in this crate or in a shared FR-PLAT-006 cache layer. Default: keep the in-memory pattern snapshot local (it is tiny and hot); reserve Redis for chart results.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| DB unavailable at match time | Postgres down, cache cold | typed `RepoError`; caller (engine) degrades per FR-PLAT-008; a warm cache serves the last-known active set |
| Stale cache after edit | pattern curated but cache not invalidated | TTL bounds staleness; FR-KB-004 publish calls `invalidate`; correctness unaffected (only which text, same fire set until reload) |
| Cross-system leak | filter admits a `liuren` pattern to a `qimen` chart | `active_for` SQL/seed filter is `system in (he, all)`; test asserts no foreign-system pattern appears |
| Non-deterministic order | matches sorted by map order | fixed sort (polarity, -score, id) + dedup; 1,000x determinism test |
| Silent bad row | DB row with a legacy enum | `active_for` validates each row; a bad row is a typed error, not a skip |
| Test needs a database | crate not offline-testable | seed repository is the default; `pg` feature off in the crate's CI test job |

## §11 - Notes

This completes the P0 RULE spine: FR-RULE-001 (data), FR-RULE-002 (evaluator), FR-RULE-003 (loader/match API). The three together are one `cyberos-rule` crate, deterministic and shared by all three casting systems, with no hardcoded pattern anywhere. Keep it offline-testable: the moment an engine test needs a live database to detect a cach cuc, the seed-repository discipline has been broken. FR-RULE-004 (cross-system patterns, P2) extends the DSL and the matcher for multi-system nesting; it is listed in the module table and authored later.
