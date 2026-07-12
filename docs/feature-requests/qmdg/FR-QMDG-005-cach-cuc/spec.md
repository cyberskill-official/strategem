---
id: FR-QMDG-005
title: "Cach cuc detection - thap can khac ung 81-cell base, cat/hung pattern tables as JSON conditions via RULE-002, special states (nhap mo / khong vong / mon bach / luc nghi kich hinh / phan-phuc ngam), gated against kinqimen"
module: QMDG
priority: MUST
status: ready_to_implement
phase: P0
slice: 1
lang: rust
effort_h: 16
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, strategy RISK-2, Claude-03 s7]
related_frs: [FR-QMDG-004, FR-QMDG-006, FR-RULE-002, FR-PLAT-002]
depends_on: [FR-QMDG-004, FR-RULE-003]
blocks: [FR-QMDG-006]
new_paths:
  - crates/cyberos-qimen/src/cach_cuc.rs
  - crates/cyberos-qimen/patterns/qimen_cach_cuc.json
  - crates/cyberos-qimen/tests/cach_cuc_oracle.rs
---

## §1 - Description (BCP-14 normative)

This FR detects cach cuc (格局), the special configurations on a completed QiMen chart that carry condensed cat / hung meaning. It runs the rule engine (FR-RULE-002) over the four-plate chart from FR-QMDG-004 and emits the matches as `CachCuc` entries of the la so envelope (FR-PLAT-002).

The base layer SHALL be thap can khac ung (十干克應), the relation between the sky-plate stem and the earth-plate stem in each palace, forming an 81-cell grid: nine visible sky stems by nine visible earth stems (Giáp is hidden under the nghi, so ten stems reduce to nine). On top of that base the module SHALL detect the named cat and hung cach in §3 (verbatim from s7.2) and the special states nhap mo (入墓), khong vong (空亡), mon bach (門迫), luc nghi kich hinh (六儀擊刑), phan ngam (反吟), and phuc ngam (伏吟).

Each cach and each special state SHALL be a predicate expressed as data (a JSON condition evaluated by FR-RULE-002), not imperative Rust; a palace MAY carry several at once. Every pattern SHALL be validated against the kinqimen oracle, and each emitted `CachCuc` SHALL carry its id, name, palace, polarity (cat / hung / trung), an optional score, and citations, per the envelope contract.

## §2 - Why this design (rationale for humans)

Cach cuc is exactly a rule-engine problem: many small predicates over a computed chart, each independent, each citable (s7.1). Writing them as data - JSON conditions loaded by RULE-002 - rather than as hardcoded Rust means new cach are added, versioned, and reviewed without recompiling the engine, and the same evaluator serves LiuRen and TaiYi later. It also keeps the deterministic / interpretation boundary sharp: the engine detects the pattern (a fact, matched to kinqimen), and the AI layer explains it with citations from Yên Ba Điếu Tẩu Ca and the commentaries (s7.3), never the other way around.

The base being 81 cells and not 100 is the detail that catches a naive implementation: Giáp is hidden by the don-giap rule, so each plate shows nine stems, and the sky-over-earth grid is 9 x 9. Anchoring the base there keeps the thap-can-khac-ung lookup aligned with what is actually on the plate.

## §3 - Contract (patterns as data)

### Base - thap can khac ung (Claude-03 s7.1)

For each palace, read the sky-plate stem over the earth-plate stem and look up the 81-cell (9 sky x 9 earth) relation. The nine visible stems per plate are the six nghi plus the three qi; Giáp is hidden. The base relation feeds the named cach below and is itself a source of read-outs.

### Cat cach (Claude-03 s7.2, verbatim)

| Cách | Điều kiện | Ý nghĩa |
|---|---|---|
| 青龍返首 | 戊 + 丙 | Thanh long hồi đầu, việc lớn thành, đại cát |
| 飛鳥跌穴 | 丙 + 戊 | Chim bay sa huyệt, cơ may đến, thành tựu |
| 天遁 | 丙 + 生門 + 丁 | Thiên độn, ẩn trợ từ trời, tốt cho mưu sự |
| 地遁 | 乙 + 開門 + 己 | Địa độn, ẩn trợ từ đất, tốt cho ẩn tàng |
| 人遁 | 丁 + 休門 + 太陰 | Nhân độn, được người che chở, tốt cầu người |
| 三奇得使 | Kỳ gặp cửa hợp | Ba kỳ được dùng, thuận lợi, có quý trợ |
| 玉女守門 | Đinh thủ cửa cát | Ngọc nữ giữ cửa, tốt cho việc kín, hôn nhân |

### Hung cach (Claude-03 s7.2, verbatim)

| Cách | Điều kiện | Ý nghĩa |
|---|---|---|
| 青龍逃走 | 乙 + 辛 | Thanh long chạy trốn, mất mát, phản bội |
| 白虎猖狂 | 辛 + 乙 | Bạch hổ hung hăng, tai hoạ, tranh đấu |
| 朱雀投江 | 丁 + 癸 | Chu tước nhảy sông, tin xấu, văn thư hỏng |
| 螣蛇夭矯 | 癸 + 丁 | Đằng xà quằn quại, việc rối, kinh sợ |
| 太白入熒 | 庚 + 丙 | Thái bạch nhập huỳnh, đối phương đến, hao |
| 熒入太白 | 丙 + 庚 | Huỳnh nhập thái bạch, mình động binh, tổn |
| 大格 | 庚 + 癸 | Đại cách, trở ngại lớn, đình trệ nặng |
| 五不遇時 | Thời can khắc nhật can | Ngũ bất ngộ, mất thời, việc khó thành |

Note the polarity flips with stem order: 戊 + 丙 (Thanh long hoi dau, cat) and 丙 + 戊 (Phi dieu diet huyet, cat) are distinct; 乙 + 辛 (青龍逃走) and 辛 + 乙 (白虎猖狂) are distinct hung cach. The condition is ordered (sky stem then earth stem), and the evaluator MUST respect order.

### Special states (Claude-03 s7.2)

Each is a predicate; a palace may carry several together with a named cach:

- nhap mo (入墓): a stem falls into its tomb palace.
- khong vong (空亡): a branch falls in the tuan khong (from CORE derived states).
- mon bach (門迫): the door is克-ed by (or克s against) its palace element.
- luc nghi kich hinh (六儀擊刑): a nghi falls into its hinh (punishment) palace.
- phan ngam (反吟): the chart falls into the opposing palace (xung).
- phuc ngam (伏吟): the chart falls into the same palace (overlap).

### Pattern shape (evaluated by FR-RULE-002)

Patterns live in `patterns/qimen_cach_cuc.json` as data. A cat cach as a condition (illustrative shape; the authoritative operator set is FR-RULE-002):

```json
{
  "id": "qimen_thanh_long_hoi_dau",
  "name": "青龍返首",
  "he": "ky_mon",
  "polarity": "cat",
  "score": 0.9,
  "when": { "all": [ { "field": "cung.thien_can", "eq": "戊" }, { "field": "cung.dia_can", "eq": "丙" } ] },
  "citations": ["Yên Ba Điếu Tẩu Ca"]
}
```

### Public types and entry point

```rust
pub enum Polarity { Cat, Hung, Trung }

pub struct CachCucHit {
    pub id: String,
    pub name: String,        // han, e.g. "青龍返首"
    pub cung: Option<u8>,    // 1..=9, or None for whole-chart states
    pub polarity: Polarity,
    pub score: Option<f32>,
    pub citations: Vec<String>,
}

// Reads the completed four-plate chart plus CORE derived states (tuan khong, mo, hinh).
pub fn detect_cach_cuc(ban: &SaoMonThan, dia: &DiaBan, thien: &TrucPhuSu,
                       ctx: &LichPhap, flags: &QiMenFlags) -> Vec<CachCucHit>;
```

`CachCucHit` maps directly onto the envelope `CachCuc` type (FR-PLAT-002 §3). Under `yin_yang_pan = am` the cach-cuc layer is intentionally light (s6.2); under `duong` it is the primary read-out.

## §4 - Acceptance criteria

1. The 81-cell thap-can-khac-ung base is complete (9 sky x 9 earth) and each cell has a defined relation; a unit test asserts full coverage with Giáp absent.
2. Every named cat and hung cach in §3 is present in `patterns/qimen_cach_cuc.json` with the correct ordered condition and polarity; a unit test cross-checks the pattern file against the §3 tables.
3. Order sensitivity holds: 戊 + 丙 matches 青龍返首 and not 飛鳥跌穴, and vice versa; a unit test asserts both directions.
4. The six special states each fire on a constructed chart that satisfies them and stay silent otherwise; a unit test covers each.
5. A palace can carry multiple hits simultaneously; a test asserts co-occurrence.
6. `detect_cach_cuc` matches the kinqimen cach-cuc list across a sample, for every relevant flag combination (patterns validated as data).

## §5 - Verification

- `tests/cach_cuc_oracle.rs` loads chart + expected-cach rows from the kinqimen fixture and asserts the detected set equals the oracle set (order-independent set equality) per row.
- Pattern-file cross-check: the JSON conditions reproduce the §3 tables exactly (names, ordered stems, polarity).
- Constructed-chart unit tests for order sensitivity, each special state, and multi-hit co-occurrence.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-qimen -- -D warnings`, `cargo test -p cyberos-qimen`; the RULE-002 evaluator is exercised through these patterns.

## §6 - Implementation skeleton

1. Add `cach_cuc.rs`; define `Polarity` and `CachCucHit` (aligned to the envelope `CachCuc`).
2. Encode the 81-cell thap-can-khac-ung base as a static table; add the coverage test.
3. Author `patterns/qimen_cach_cuc.json` with every named cach from §3 and the six special states, as RULE-002 conditions with citations.
4. Load and evaluate the patterns via FR-RULE-002 against the completed chart plus CORE derived states (tuan khong, mo, hinh, xung).
5. Wire the pattern-file cross-check, the constructed-chart tests, and the kinqimen oracle test.

## §7 - Dependencies

Depends on FR-QMDG-004 (the completed star / door / god rings and the sky/earth stems) and FR-RULE-002 (the condition DSL and evaluator). Blocks FR-QMDG-006 (assembly emits the detected cach cuc into the envelope). Consumes CORE derived states (tuan khong, tomb, hinh) via the `LichPhap` context from FR-CORE-005 / FR-CORE-004.

## §8 - Example payloads

The `cach_cuc` array as it appears in the envelope (FR-PLAT-002 shape):

```json
{ "cach_cuc": [
    { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "cung": 1, "polarity": "cat", "score": 0.9, "citations": ["Yên Ba Điếu Tẩu Ca"] },
    { "id": "qimen_khong_vong", "name": "空亡", "cung": 7, "polarity": "hung", "citations": [] }
] }
```

## §9 - Open questions

- Scoring: are the `score` values a fixed per-cach constant, or context-weighted? Default: a fixed per-cach constant seeded in the pattern file; revisit if the interpretation eval loop (FR-RAG-006) shows ranking needs context weighting.
- Coverage completeness: s7.2 lists representative cat / hung cach, not an exhaustive canon. Default: seed the named set plus the six special states, then expand from kinqimen divergences and KB-002 pattern seeding; every addition stays data and re-gates against the oracle.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Order ignored | condition treats 戊+丙 and 丙+戊 as equal | order-sensitivity test fails; conditions are ordered |
| Base wrong size | grid built as 10 x 10 with Giáp | coverage test fails (Giáp must be absent, 9 x 9) |
| Missing special state | phan/phuc ngam not detected | constructed-chart test fails |
| Pattern drift | JSON conditions diverge from §3 tables | pattern-file cross-check fails |
| Over/under-firing | detected set != oracle set | cach-cuc oracle set-equality test fails |
| Hardcoded cach | a pattern written in Rust not data | code review rejects; all cach live in the pattern file |

## §11 - Notes

Cach cuc is where the QiMen engine meets the shared rule engine, so keep every pattern as data in `patterns/qimen_cach_cuc.json` and let FR-RULE-002 evaluate it - no cach in imperative Rust. The engine's job ends at the matched fact; the cited explanation is the AI layer's job (s7.3), and because QiMen has many schools the interpretation must name which school it reads under. The oracle gate is set equality against kinqimen, so a spurious extra hit fails just as hard as a missing one.
