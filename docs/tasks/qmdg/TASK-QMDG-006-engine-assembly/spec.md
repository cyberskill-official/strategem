---
id: TASK-QMDG-006
title: "Engine assembly - run the full QiMen pipeline, emit the la so JSON envelope (he=ky_mon) with the complete flag set, 100% kinqimen oracle gate across ALL flag combinations, cache key per PLAT-002"
module: QMDG
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, strategy RISK-7, Claude-03 s8, Claude-03 s1.2, Claude-03 s10]
related_frs: [TASK-QMDG-005, TASK-CORE-006, TASK-PLAT-002, TASK-CHART-001, TASK-STRAT-001]
depends_on: [TASK-QMDG-005, TASK-CORE-006]
blocks: [TASK-CHART-001, TASK-STRAT-001, TASK-QMDG-007]
new_paths:
  - crates/cyberos-qimen/src/engine.rs
  - crates/cyberos-qimen/src/ban.rs
  - crates/cyberos-qimen/tests/kinqimen_oracle.rs
  - crates/cyberos-qimen/tests/fixtures/kinqimen_all_flags.csv
---

## §1 - Description (BCP-14 normative)

This task assembles the QiMen engine end to end and is its acceptance gate. It runs the pipeline - dinh cuc (TASK-QMDG-001) -> bo dia ban (TASK-QMDG-002) -> truc phu / truc su + thien ban rotation (TASK-QMDG-003) -> cuu tinh / bat mon / bat than (TASK-QMDG-004) -> cach cuc (TASK-QMDG-005) - and emits the result as the la so JSON envelope (TASK-PLAT-002) with `he = "ky_mon"`.

The module SHALL build a strongly-typed `KyMonBan` (the four plates plus dinh cuc, truc phu, truc su) and place it in the envelope `ban` slot; SHALL place the TASK-QMDG-005 hits in the envelope `cach_cuc` array; SHALL carry the CORE calendar output (TASK-CORE-005) in `lich_phap`; and SHALL stamp the complete school-flag set into `co_truong_phai`. The complete flag set (s8.2) is `dingju_method`, `pan_method`, `yin_yang_pan`, `zhong_gong_ky`, and `chan_thai_duong_thoi`.

Acceptance SHALL be a 100% match against the kinqimen oracle across ALL flag combinations, over a large sample covering the 24 tiet khi x 3 nguyen, with dedicated edge tests for sieu than tiep khi, tri nhuan, and the center palace (s8.2). The chart SHALL be reproducible from `dau_vao` + `co_truong_phai` + `lich_phap` flags alone, and the cache key SHALL be computed per the TASK-PLAT-002 rule. The whole pipeline is deterministic once the flags are fixed (s1.2, s10.4), so the chart is cacheable by rounded instant, longitude, and flag set.

## §2 - Why this design (rationale for humans)

Everything upstream is a stage with its own oracle gate; this task proves the stages compose into a chart that matches kinqimen as a whole, under every flag combination. QiMen is the most school-variant engine (three orthogonal flag axes plus two smaller ones), so "passes on the default config" is not acceptance - the matrix must run per flag combination, or a school that a user actually casts under could be silently wrong (strategy RISK-7). Building this discipline here, on the flagship engine, sets the pattern LiuRen and TaiYi inherit.

Mapping the engine-native s8.1 shape onto the shared PLAT-002 envelope is deliberate: the engine keeps its natural four-plate structure inside `ban`, while the cross-cutting fields the interpretation branch reads - `he`, `cach_cuc`, `co_truong_phai`, `lich_phap` - sit at the envelope top level where every module expects them. That is what lets the Python interpretation branch read a QiMen chart without knowing QiMen internals, and lets two users of different schools see exactly which conventions cast the chart.

## §3 - Contract (assembly + envelope)

### Engine-native chart (Claude-03 s8.1, verbatim shape)

```json
{
  "he": "ky_mon",
  "dau_vao": { "datetime": "...", "tz": "+07:00", "kinh_do": 106.7, "chan_thai_duong_thoi": true },
  "tu_tru": { "nam": "...", "thang": "...", "ngay": "...", "gio": "甲子" },
  "dinh_cuc": { "tiet_khi": "冬至", "tam_nguyen": "上元", "duong_don": true, "so_cuc": 1 },
  "dia_ban": {}, "thien_ban": {}, "cuu_tinh": {}, "bat_mon": {}, "bat_than": {},
  "truc_phu": "天蓬", "truc_su": "休門",
  "cach_cuc": ["青龍返首"],
  "co_truong_phai": { "dingju_method": "chaibu", "pan_method": "zhuan", "yin_yang_pan": "duong" }
}
```

### Mapping onto the PLAT-002 envelope

- `he` -> envelope `he = "ky_mon"`.
- `dau_vao` -> envelope `dau_vao`; `chan_thai_duong_thoi` also mirrored in `co_truong_phai`.
- `tu_tru` and `dinh_cuc.tiet_khi` / `tam_nguyen` -> envelope `lich_phap` (from TASK-CORE-005); the engine-native Han tam nguyen (上元/中元/下元) maps to the romanized `lich_phap.tiet_khi.tam_nguyen` (thuong/trung/ha).
- `dinh_cuc` (with `duong_don`, `so_cuc`), `dia_ban`, `thien_ban`, `cuu_tinh`, `bat_mon`, `bat_than`, `truc_phu`, `truc_su` -> envelope `ban` as the typed `KyMonBan`.
- `cach_cuc` -> envelope `cach_cuc` as `CachCuc` objects (TASK-QMDG-005 `CachCucHit`), not bare strings.
- `co_truong_phai` -> envelope `co_truong_phai`, the complete flag set below.

### Complete flag set (Claude-03 s8.2, verbatim)

| Cờ | Giá trị | Mặc định |
|---|---|---|
| dingju_method | chaibu, zhirun, maoshan | chaibu |
| pan_method | zhuan, fei | zhuan |
| yin_yang_pan | duong, am | duong |
| zhong_gong_ky | khon2, giu_nguyen | khon2 |
| chan_thai_duong_thoi | true, false | true |

The default configuration is thoi-gia duong-ban chaibu chuyen-ban: `dingju_method = chaibu`, `pan_method = zhuan`, `yin_yang_pan = duong`, `zhong_gong_ky = khon2`, `chan_thai_duong_thoi = true`.

### Public types and entry point

```rust
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct KyMonBan {
    pub dinh_cuc: DinhCuc,
    pub dia_ban: DiaBan,
    pub thien_ban: [Can; 9],
    pub cuu_tinh: [CuuTinh; 9],
    pub bat_mon: [Option<BatMon>; 9],
    pub bat_than: [Option<BatThan>; 9],
    pub truc_phu: CuuTinh,
    pub truc_su: BatMon,
}

// The single engine entry point: takes the CORE calendar context and the flag set,
// returns the full la so envelope with he = ky_mon.
pub fn cast(ctx: &LichPhap, flags: &QiMenFlags) -> Result<LaSo, QiMenError>;

impl KyMonBan { pub fn cache_key(&self, dau_vao: &DauVao, flags: &QiMenFlags) -> String; }
```

`cache_key` follows TASK-PLAT-002: a stable hash of `(he, dau_vao rounded to the casting granularity, co_truong_phai sorted, lich_phap.co_lich_phap sorted)`; `co_truong_phai` is a sorted map so the key is identical in Rust and Python.

## §4 - Acceptance criteria

1. `cast` matches kinqimen 100% - dia ban, thien ban, cuu tinh, bat mon, bat than, truc phu, truc su, and the cach-cuc set - across a sample covering all 24 tiet khi x 3 nguyen.
2. The oracle gate runs for EVERY flag combination in the product of `dingju_method` x `pan_method` x `yin_yang_pan` x `zhong_gong_ky` x `chan_thai_duong_thoi`, not only the default; a mismatch on any combination fails the build (strategy RISK-7).
3. Dedicated edge tests pass: sieu than tiep khi boundary days, tri nhuan insertion at Mang Chung / Dai Tuyet, and center-palace (Trung 5) lodging.
4. The emitted envelope validates against the PLAT-002 schema; `he = "ky_mon"`, `co_truong_phai` carries all five flags, and `cach_cuc` entries are `CachCuc` objects.
5. Reproducibility: recasting from `dau_vao` + `co_truong_phai` + `lich_phap` alone yields a byte-identical chart; a round-trip test asserts it.
6. `cache_key` is stable and identical across two casts of the same input and flags, and matches the Python `laso_envelope` key for the same fixture.

## §5 - Verification

- `tests/kinqimen_oracle.rs` loads `fixtures/kinqimen_all_flags.csv` (day, hour, longitude, full flag tuple, and the expected four plates + truc phu / truc su + cach-cuc set) and asserts an exact match per row, iterating the full flag product. This is the QiMen acceptance gate; it MUST run in CI (strategy RISK-7).
- Edge fixtures: a labelled subset for sieu than tiep khi, tri nhuan, and center palace, asserted per `dingju_method`.
- Envelope tests: schema validation against PLAT-002, the reproducibility round-trip, and the cross-language cache-key equality with `laso_envelope`.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-qimen -- -D warnings`, `cargo test -p cyberos-qimen`; the CORE oracle harness (TASK-CORE-006) must be green first, since QiMen inherits the calendar context.

## §6 - Implementation skeleton

1. Add `ban.rs` with `KyMonBan` (serde) and its mapping to the envelope `ban` slot; add `engine.rs` with `cast`.
2. Wire the pipeline: call TASK-QMDG-001..005 in order, assemble `KyMonBan`, collect `CachCucHit`s.
3. Build the envelope: set `he`, `dau_vao`, `lich_phap` (from TASK-CORE-005), `ban`, `cach_cuc`, `co_truong_phai` (all five flags), `provenance`.
4. Implement `cache_key` per PLAT-002; add the cross-language equality test.
5. Generate `fixtures/kinqimen_all_flags.csv` once from kinqimen across the flag product and the tiet-khi x nguyen sample (script documented, not run in CI); commit it. Wire the oracle test and the edge fixtures.

## §7 - Dependencies

Depends on TASK-QMDG-005 (the last pipeline stage) and TASK-CORE-006 (the calendar oracle harness must be green, since QiMen stands on the CORE context). Emits the TASK-PLAT-002 envelope. Blocks TASK-CHART-001 (the 9-palace UI renders this chart), TASK-STRAT-001 (the Timing Optimizer scans this engine), and TASK-QMDG-007 (dung than reads the assembled chart). This is the QiMen node on the P0 critical path: `CORE-006 + QMDG-006 -> CHART-001 / STRAT-001`.

## §8 - Example payloads

The assembled envelope (abridged; `ban` holds the full `KyMonBan`):

```json
{
  "envelope_version": 1,
  "he": "ky_mon",
  "dau_vao": { "datetime": "2004-01-01T10:30:00", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "trach_thoi" },
  "lich_phap": { "tu_tru": { "gio": "丁巳" }, "tiet_khi": { "hien_hanh": "冬至", "tam_nguyen": "thuong" } },
  "ban": { "dinh_cuc": { "duong_don": true, "so_cuc": 1 }, "truc_phu": "天蓬", "truc_su": "休門",
           "dia_ban": {}, "thien_ban": {}, "cuu_tinh": {}, "bat_mon": {}, "bat_than": {} },
  "cach_cuc": [ { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "cung": 1, "polarity": "cat", "score": 0.9, "citations": ["Yên Ba Điếu Tẩu Ca"] } ],
  "co_truong_phai": { "dingju_method": "chaibu", "pan_method": "zhuan", "yin_yang_pan": "duong", "zhong_gong_ky": "khon2", "chan_thai_duong_thoi": "true" },
  "provenance": { "engine": "qmdg", "engine_version": "0.1.0", "cast_at": "2026-07-08T12:00:00Z", "cache_key": "..." }
}
```

## §9 - Open questions

- Flag-product size: five flags give a modest product (3 x 2 x 2 x 2 x 2 = 48), but `am` (yin_yang_pan) is specified only in principle at MVP. Default: gate the full `duong` product hard and gate `am` as far as kinqimen supports it, marking `am` combinations that are not yet oracle-backed as `ignored` with a tracking note rather than silently skipped.
- Should the engine ship as a service, a PyO3 binding, or both for the Python orchestrator (strategy 4.1 DEC-2)? Default: the crate is the unit of truth; the service / binding wrapper is a PLAT concern and does not change this envelope.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Default-only testing | matrix runs one config | RISK-7 violated; CI must iterate the full flag product |
| Flag not stamped | a used flag missing from co_truong_phai | reproducibility round-trip diverges; test fails before ship |
| Envelope drift | ban shape diverges from PLAT-002 | schema validation fails in the contract test |
| Non-deterministic cache key | flags hashed in map order | cross-language key-equality test fails |
| CORE not green | calendar context wrong | QMDG oracle inherits the error; TASK-CORE-006 gate must pass first |
| Edge case unhandled | sieu than / tri nhuan / center palace | labelled edge fixtures fail; do not ship |

## §11 - Notes

This is the QiMen stop-ship gate: a mismatch with kinqimen on any flag combination is a defect, and the default config (thoi-gia duong-ban chaibu chuyen-ban) is the most-used but not the only tested one. Keep the flag product in one place (`QiMenFlags`) so the matrix is generated, not hand-listed, and it stays complete as flags evolve. The envelope this task emits is the contract every downstream module (CHART, STRAT, RAG via interpretation) consumes; treat any change to it as a PLAT-002 versioned change, not a local edit.
