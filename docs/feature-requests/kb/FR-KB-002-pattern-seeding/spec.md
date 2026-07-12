---
id: FR-KB-002
title: "Pattern seeding - 150-200 real cach cuc / khoa the / than sat across the three systems as versioned JSON rows per the RULE-001 schema, each cited to classical text, doubling as the RISK-9 interpretation-quality validation dataset"
module: KB
priority: MUST
status: done
phase: P0
slice: 1
lang: python
effort_h: 16
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-24, Grok-37, strategy RISK-9, strategy 4.4]
related_frs: [FR-RULE-001, FR-RULE-002, FR-RULE-003, FR-KB-001, FR-KB-003, FR-KB-004, FR-RAG-003, FR-RAG-006]
depends_on: [FR-RULE-001, FR-KB-001]
blocks: [FR-KB-004, FR-RAG-006]
new_paths:
  - packages/tamthuc_kb/tamthuc_kb/seed/__init__.py
  - packages/tamthuc_kb/tamthuc_kb/seed/build_patterns.py
  - packages/tamthuc_kb/tamthuc_kb/seed/loader.py
  - packages/tamthuc_kb/tamthuc_kb/seed/validation.py
  - data/patterns/qimen.json
  - data/patterns/liuren.json
  - data/patterns/taiyi.json
  - data/patterns/SOURCES.md
  - packages/tamthuc_kb/tests/test_pattern_seed.py
  - packages/tamthuc_kb/tests/fixtures/pattern_seed_sample.json
---

## §1 - Description (BCP-14 normative)

This FR fills the pattern-as-data ruleset with real content: 150-200 named patterns across the three systems, each expressed as a JSON row conforming to the FR-RULE-001 pattern shape (`docs/contracts/knowledge-pattern.schema.json`) and each carrying at least one citation into the classical corpus. It does NOT define the pattern schema (FR-RULE-001) nor the condition DSL grammar (FR-RULE-002); it authors data against them. The same 150-200 rows SHALL double as the interpretation-quality validation dataset named in strategy RISK-9.

The seed SHALL be language-neutral canonical data under `data/patterns/<system>.json`, one file per system, each a JSON array of pattern rows. Every row SHALL populate `id`, `system`, `name`, `name_han` where a Han name exists, `conditions` (a DSL tree valid under FR-RULE-002), `polarity` (cát/hung/trung), `meaning_classical`, `meaning_modern`, `citations` (non-empty for any `active` row), `version` (>= 1), `confidence`, and `status`. No `active` row SHALL ship without a citation, because a pattern with no textual source cannot ground a claim under the anti-hallucination rule (strategy 4.4, FR-RAG-003).

Coverage SHALL be weighted to the P0 flagship: QiMen SHALL receive the largest share (the cát and hung cách cục of the thập can khắc ứng plus the headline named formations - Thanh Long Hồi Đầu 青龍返首, Phi Điểu Diệt Huyệt 飛鳥跌穴, and the like), with LiuRen khóa thể and TaiYi cách cục seeded to a smaller but representative set so the schema is exercised across all three. Every `meaning_modern` SHALL be framed as decision support, never as a medical, legal, or financial verdict, and never as a certain future event (strategy 7). Meanings SHALL present schools fairly: where a pattern is read differently by different schools, the difference SHALL be recorded rather than silently resolved.

The build SHALL validate every row against the FR-RULE-001 validator and the FR-RULE-002 DSL checker before load, and SHALL load `active` rows into the `knowledge_patterns` table (FR-PLAT-003). A malformed or uncited `active` row SHALL fail the whole build with the offending `id` named; nothing partial loads.

## §2 - Why this design (rationale for humans)

The rule engine is only as good as its ruleset, and both source sets say the ruleset is data an expert authors and reviews, not code (Grok-24 curation, Grok-37 seeding). Seeding 150-200 real patterns is the moment the abstract pattern-as-data machinery meets the actual domain, and it is where quality is won or lost. Concentrating on QiMen first mirrors DEC-4 (QiMen is the P0 flagship) and RISK-7 (build the school-variant-heavy engine's ruleset first so the flag discipline is forced early); LiuRen and TaiYi get a representative sample now and grow in P1 and P2.

Making the seed double as the validation dataset is the direct mitigation for RISK-9: interpretation quality cannot be measured, so regressions ship silently, unless there is a fixed corpus of known cases to score against. Because each pattern already pairs a machine-checkable `conditions` tree with a cited `meaning_classical`, the same 150-200 rows are simultaneously the ruleset the engine detects and the answer key the eval loop (FR-RAG-006) grades interpretation faithfulness against. Authoring them once, cited, and versioned means the ruleset and the test set can never drift apart. The citation-required rule is the anti-hallucination principle at the data layer: the chain source -> pattern -> detected cách cục -> cited interpretation must have no link where meaning appears without a textual source.

## §3 - Contract (data, build, validation)

### Canonical seed files (`data/patterns/<system>.json`)

One array per system, each entry a pattern row in the FR-RULE-001 shape (minus `created_at`/`updated_at`, which the DB sets). Example row:

```json
{
  "id": "qimen_thanh_long_hoi_dau",
  "system": "qimen",
  "name": "Thanh Long Hồi Đầu",
  "name_han": "青龍返首",
  "conditions": { "type": "and", "rules": [
    { "field": "truc_phu.cung", "operator": "eq", "value": "ban.thien_ban.cung_of.丙" },
    { "field": "door", "operator": "in", "value": ["Sinh", "Khai", "Tu"] } ] },
  "polarity": "cat",
  "meaning_classical": "丙加值符, cát khí tụ tập, lợi cho khởi sự và cầu kiến.",
  "meaning_modern": "A strong-timing configuration for initiating or requesting; frame as a favorable window, not a guarantee.",
  "citations": ["yba_thien_can_khac_ung_12", "kmdg_cach_cuc_thanh_long"],
  "version": 1, "confidence": 0.9, "status": "active"
}
```

### Coverage target (indicative, not a hard split)

| System | Target rows | Emphasis |
|---|--:|---|
| qimen | 90-110 | thập can khắc ứng cát/hung pairs, named formations, nhập mộ / không vong / phản-phục ngâm |
| liuren | 35-50 | the khóa thể (課體) families and headline tam truyền configurations |
| taiyi | 20-35 | the cách cục and chủ-khách thắng bại configurations, representative not exhaustive |

Total lands in the 150-200 band; QiMen carries the P0 weight per DEC-4.

### Sources and citation ids (`data/patterns/SOURCES.md`)

Each `citations` entry is a stable id that resolves into the FR-KB-003 classical corpus. Provenance of the seed content:

- QiMen: Yên Ba Điếu Tẩu Ca (煙波釣叟歌) and a Joey Yap QiMen compendium for cross-checking modern glosses.
- LiuRen: Đại Lục Nhâm (大六壬) classical material for the khóa thể and tam truyền readings.
- TaiYi: Thái Ất Kim Kính (太乙金鏡) for the cách cục and toán configurations.

`SOURCES.md` records, per source, the work, the citation-id prefix it owns, and the layer availability (Han / bạch thoại / dịch) so FR-KB-003 can align the corpus to the citations these patterns reference.

### Build and load (`tamthuc_kb/seed/build_patterns.py`, `loader.py`)

```python
def build(paths: list[Path]) -> BuildReport:
    # 1. read each data/patterns/<system>.json
    # 2. validate every row with the FR-RULE-001 validator (envelope + shallow conditions)
    # 3. deep-validate conditions with the FR-RULE-002 DSL checker
    # 4. assert every active row has >= 1 citation and a resolvable citation-id prefix
    # 5. assert id uniqueness within and across files; report counts per system + polarity
    # fail the whole build on any error, naming the offending id

def load(rows: list[Pattern], db) -> LoadReport:
    # upsert active rows into knowledge_patterns (FR-PLAT-003), keyed by id; bump version on change
```

### Validation-dataset view (`tamthuc_kb/seed/validation.py`)

```python
def validation_cases(system: System | None = None) -> list[ValidationCase]:
    # projects each seeded pattern into a {id, version, conditions, expected_polarity,
    # meaning_classical, citations} case; this is the fixed corpus FR-RAG-006 scores
    # interpretation faithfulness and citation accuracy against (RISK-9).
```

## §4 - Acceptance criteria

1. `data/patterns/qimen.json`, `liuren.json`, and `taiyi.json` together contain 150-200 rows, every row valid under the FR-RULE-001 validator and the FR-RULE-002 DSL checker.
2. Every `active` row carries at least one citation whose prefix is declared in `SOURCES.md`; a row with an empty `citations` and `status = active` fails the build with its `id` named.
3. `id` is unique across all three files; a duplicate id anywhere fails the build.
4. Every `meaning_modern` passes a lint that rejects medical / legal / financial verdict phrasing and absolute future-event phrasing (strategy 7); a deliberately non-compliant fixture row is caught.
5. `build` reports counts per system and per polarity, and QiMen is the largest share; `load` upserts `active` rows into `knowledge_patterns` idempotently (re-load changes nothing without a version bump).
6. `validation_cases()` returns one case per seeded pattern with its `(id, version)` stamp, and FR-RAG-006 can consume it as the RISK-9 corpus.

## §5 - Verification

- `tests/test_pattern_seed.py`: validates the committed seed sample (`fixtures/pattern_seed_sample.json`) end to end; asserts the citation-required, id-uniqueness, and meaning-lint cases; asserts `build` fails whole-file on one injected bad row with the `id` surfaced; asserts `validation_cases` parity with the loaded rows.
- Schema conformance: every row validates against `docs/contracts/knowledge-pattern.schema.json` (the FR-RULE-001 contract), so the seed cannot drift from the row shape.
- DSL conformance: every `conditions` tree parses and deep-validates under the FR-RULE-002 checker (fields, operators, depth), run as part of the build test.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_kb`, `pytest packages/tamthuc_kb`. The full 150-200 seed is linted in CI; the DB load runs behind a marker when a test Postgres is present.

## §6 - Implementation skeleton

1. Author `data/patterns/qimen.json` first (the P0 flagship weight), then `liuren.json` and `taiyi.json` to representative coverage, each row cited.
2. Write `data/patterns/SOURCES.md` mapping citation-id prefixes to the classical works and their layer availability.
3. `seed/build_patterns.py`: read, validate (RULE-001 + RULE-002), id-uniqueness, meaning lint, per-system/polarity counts, whole-file fail.
4. `seed/loader.py`: idempotent upsert of `active` rows into `knowledge_patterns` with version-bump-on-change.
5. `seed/validation.py`: the `validation_cases` projection for FR-RAG-006.
6. Commit a small `fixtures/pattern_seed_sample.json` (a handful of rows across systems) as the test exemplar; the full files are the shipped seed.

## §7 - Dependencies

Depends on FR-RULE-001 (the pattern row shape, the validator, and the seed-file format this FR fills) and FR-KB-001 (pattern `conditions` reference graph node ids and relations, and the cách cục / khóa thể / thần sát nodes live in the graph taxonomy). Loads into the `knowledge_patterns` table that FR-PLAT-003 migrates from the FR-RULE-001 shape (soft edge; the physical table is PLAT-003's). Citations resolve into the FR-KB-003 classical corpus (a parallel P1 build; the citation-id prefixes are agreed here in `SOURCES.md` so KB-003 can align to them). Blocks FR-KB-004 (the curation workflow reviews and versions these rows) and FR-RAG-006 (the eval loop scores interpretation against this seed as the RISK-9 validation set). Read at runtime by FR-RULE-003 (the loader serving `active` patterns to the engines) and enriches the chart summary in FR-RAG-003.

## §8 - Example payloads

A LiuRen khóa thể row and a TaiYi cách cục row from the seed:

```json
[
  { "id": "liuren_nguyen_thai", "system": "liuren", "name": "Nguyên Thai", "name_han": "元胎",
    "conditions": { "type": "and", "rules": [
      { "field": "khoa_the", "operator": "eq", "value": "nguyen_thai" } ] },
    "polarity": "trung", "meaning_classical": "Khóa thể cơ bản, chỉ sự sinh khởi.",
    "meaning_modern": "Baseline lesson-type; read the tam truyền for direction, not a fixed outcome.",
    "citations": ["dllr_khoa_the_01"], "version": 1, "confidence": 0.7, "status": "active" },

  { "id": "taiyi_chu_thang", "system": "taiyi", "name": "Chủ Toán Thắng", "name_han": "主算勝",
    "conditions": { "type": "and", "rules": [
      { "field": "chu_toan", "operator": "gt", "value": "khach_toan" } ] },
    "polarity": "cat", "meaning_classical": "Chủ toán vượng hơn khách toán, lợi cho bên chủ.",
    "meaning_modern": "Favors the initiating party in the framed decision; a lens on posture, not a prediction.",
    "citations": ["taks_cach_cuc_chu_thang_03"], "version": 1, "confidence": 0.65, "status": "active" }
]
```

## §9 - Open questions

- Exact QiMen/LiuRen/TaiYi split inside the 150-200 band. Default: QiMen-heavy per DEC-4 and the coverage table; the precise counts follow from how many named formations each source actually documents. Recorded, not fixed, until the QiMen file is authored.
- Whether school-variant readings of the same pattern are separate rows or one row with a variant-keyed meaning. Default: one `id` with the school difference recorded in `meaning_classical` / an `attrs`-style note, so detection stays single-keyed; split into versioned variant rows only if a school reads the polarity itself differently. Coordinate with FR-KB-004.
- How much of the seed is expert-signed before P0 ship vs marked `draft`. Default: rows ship `active` only once cited and reviewed; unreviewed rows stay `draft` and are excluded from the loaded ruleset but kept in the validation corpus for tracking. FR-KB-004 owns the sign-off workflow.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Uncited active pattern | `status = active`, `citations = []` | build fails with the `id`; DB check constraint also rejects (FR-RULE-001) |
| Fortune-telling phrasing | `meaning_modern` asserts a certain outcome or a medical/legal/financial verdict | meaning lint fails the row (strategy 7) |
| Duplicate id | same `id` in two files or twice in one | build fails on the id-uniqueness check |
| Invalid conditions | `conditions` tree malformed or uses an unknown field/operator | FR-RULE-002 DSL checker fails the build at that row |
| Ruleset / test-set drift | someone edits the loaded patterns but not the validation corpus | they are the same rows; `validation_cases` derives from the loaded set, so drift is impossible by construction |
| Partial load | one bad row among many | whole-file fail; nothing loads until the file is clean |

## §11 - Notes

This is the content FR that turns the pattern-as-data machinery into a working interpreter, and it is the single most leverage-heavy quality artifact in P0: the same 150-200 cited rows are the ruleset the engine detects, the answer key the eval loop grades, and the substrate the citation cards render. Keep it language-neutral data under `data/patterns/` so both the Rust engine (offline seed) and the Python DB loader consume one source; the small `crates/cyberos-rule/seed/qimen.json` from FR-RULE-001 stays only as the format exemplar and fixture. Author QiMen first and cite everything - an uncited pattern is not shippable. FR-KB-004 later adds the expert-review and versioning workflow over exactly these rows.
