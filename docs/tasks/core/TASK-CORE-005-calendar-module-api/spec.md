---
id: TASK-CORE-005
title: "Calendar module API + JSON output + flag set + stamp - the lich_phap sub-object every engine consumes, LichFlags canonical set, fills the TASK-PLAT-002 envelope slot"
module: CORE
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.3, strategy 4.4, Claude-05 s6, Claude-05 s6.1, Claude-05 s6.2]
related_frs: [TASK-CORE-002, TASK-CORE-003, TASK-CORE-004, TASK-CORE-006, TASK-PLAT-002]
depends_on: [TASK-CORE-002, TASK-CORE-003, TASK-CORE-004]
blocks: [TASK-CORE-006, TASK-QMDG-001, TASK-LN-001, TASK-TAT-001, TASK-API-001]
new_paths:
  - crates/cyberos-lichphap/src/api.rs
  - crates/cyberos-lichphap/src/flags.rs
  - crates/cyberos-lichphap/src/output.rs
  - crates/cyberos-lichphap/tests/lichphap_golden.rs
---

## §1 - Description (BCP-14 normative)

This task is the public face of the calendar core: one entry point that takes a civil moment, a timezone, a longitude, and the calendar flags, and returns the `lich_phap` object - the exact sub-object that the la so envelope (TASK-PLAT-002) carries and that all three engines read as their calendar input (Claude-05 s6, strategy 4.3). It composes TASK-CORE-001 (tiet khi), TASK-CORE-002 (chan thai duong), TASK-CORE-003 (tu tru), and TASK-CORE-004 (phai sinh) into a single serializable result.

The module SHALL expose one primary function that accepts `(datetime, tz, longitude, LichFlags)` and returns a `LichPhap` value. It SHALL define the canonical `LichFlags` set (the single source of truth that TASK-CORE-001..004 borrow fields from) and SHALL stamp the complete flag set into `lich_phap.co_lich_phap` on every call. The output SHALL contain: `tu_tru`, `tiet_khi { hien_hanh, bat_dau, tam_nguyen }`, `chan_thai_duong`, `phai_sinh { tuan_khong, vuong_suy, truong_sinh }`, and `co_lich_phap`. The serialized shape MUST be byte-identical to the `lich_phap` slot defined by TASK-PLAT-002; a change to one without the other is a contract defect.

A chart's calendar layer MUST be fully reproducible from `dau_vao` plus `co_lich_phap` alone: any input that changed the calendar result MUST appear in `co_lich_phap`, or it is a defect. Engines MUST NOT recompute the calendar; they read this object.

## §2 - Why this design (rationale for humans)

The whole platform's split between a deterministic engine and an AI layer only works if the calendar is computed once and handed across a hard boundary (strategy 4.3). If each engine recomputed tiet khi or the pillars, three copies would drift and the RISK-1 blast radius would multiply. So the calendar core presents exactly one object, and the three engines consume it read-only.

Stamping the full flag set is not bookkeeping - it is what makes a chart reproducible and auditable (strategy 4.4, Claude-05 s6.2). The calendar layer alone has six school/precision switches (true-solar on/off, longitude, zi rollover, late-zi handling, truong sinh school, delta-T model), each able to change the pillars or the terms. Recording all six in `co_lich_phap` means two users can see under which calendar conventions a chart was cast, and the reproduction test can recast from the stamp and get the same bytes. This is the calendar-core half of the cultural-fairness rule (strategy 7): differences are surfaced, not silently chosen.

## §3 - Contract (types and JSON)

### Canonical flag set (Claude-05 s6.2)

```rust
pub struct LichFlags {
    pub use_true_solar_time: bool,          // default true
    pub longitude: f64,                     // decimal degrees, per place
    pub zi_hour_day_rollover: ZiRollover,   // Twenty3 (23:00) | Midnight (00:00); default Twenty3
    pub late_zi_handling: LateZi,           // TaoZi | DaZi; default TaoZi
    pub truong_sinh_phai: TruongSinhPhai,   // AmDuong | NguHanh; default per engine
    pub delta_t_model: DeltaTModel,         // EspenakMeeus | ...; default EspenakMeeus
}
```

| Co | Gia tri | Mac dinh |
|---|---|---|
| use_true_solar_time | true, false | true |
| longitude | kinh do thap phan | theo noi |
| zi_hour_day_rollover | 23:00, 00:00 | 23:00 |
| late_zi_handling | tao_zi, da_zi | tao_zi |
| truong_sinh_phai | am_duong, ngu_hanh | theo he |
| delta_t_model | espenak_meeus, khac | espenak_meeus |

`truong_sinh_phai` has no fixed default here - the calling engine supplies its own (LiuRen -> ngu_hanh), and whatever is used is stamped.

### Output type

```rust
pub struct LichPhap {
    pub tu_tru: BonTru,                     // TASK-CORE-003
    pub tiet_khi: TietKhiHt,                // hien_hanh + bat_dau + tam_nguyen (TASK-CORE-001)
    pub chan_thai_duong: ChanThaiDuong,     // TASK-CORE-002
    pub phai_sinh: PhaiSinh,                // TASK-CORE-004
    pub co_lich_phap: LichFlags,            // the full stamp
}
pub fn tinh_lich_phap(
    dt: NaiveDateTime, tz: FixedOffset, longitude_deg: f64, flags: &LichFlags) -> LichPhap;
```

### Serialized shape (Claude-05 s6.1; MUST match the TASK-PLAT-002 lich_phap slot)

```json
{
  "tu_tru": { "nam": "癸未", "thang": "甲子", "ngay": "戊午", "gio": "丁巳" },
  "tiet_khi": { "hien_hanh": "冬至", "bat_dau": "2003-12-22T08:04:00Z", "tam_nguyen": "thuong" },
  "chan_thai_duong": {
    "ap_dung": true,
    "hieu_chinh_kinh_do_phut": 6.8,
    "phuong_trinh_thoi_gian_phut": -3.5,
    "gio_that": "2004-01-01T10:33:18+07:00"
  },
  "phai_sinh": { "tuan_khong": ["申", "酉"], "vuong_suy": {}, "truong_sinh": {} },
  "co_lich_phap": {
    "use_true_solar_time": true, "longitude": 106.7,
    "zi_hour_day_rollover": "23:00", "late_zi_handling": "tao_zi",
    "truong_sinh_phai": "ngu_hanh", "delta_t_model": "espenak_meeus"
  }
}
```

Enum serde: `zi_hour_day_rollover` serializes to the literals `"23:00"` / `"00:00"`; `late_zi_handling` to `"tao_zi"` / `"da_zi"`; `truong_sinh_phai` to `"am_duong"` / `"ngu_hanh"`; `delta_t_model` to `"espenak_meeus"`.

## §4 - Acceptance criteria

1. `tinh_lich_phap` returns a `LichPhap` whose serialized JSON is byte-identical to the TASK-PLAT-002 `lich_phap` golden slot for the reference input (2004-01-01T10:30:00 +07:00, longitude 106.7, default flags).
2. Every one of the six flags is present in `co_lich_phap` on every call, including defaulted ones; a reproduction test recasts from `dau_vao` + `co_lich_phap` and gets the identical object.
3. Changing any single flag changes the output in the expected field and only there (e.g. flipping `use_true_solar_time` changes `chan_thai_duong` and possibly the hour pillar, nothing else).
4. The enum literals serialize exactly as specified (`"23:00"`, `"tao_zi"`, `"ngu_hanh"`, ...); a schema check against `docs/contracts/laso-envelope.schema.json` passes.
5. Engines can construct the object only through `tinh_lich_phap`; no field is publicly mutable after construction (read-only to consumers).

## §5 - Verification

- `tests/lichphap_golden.rs` holds the reference-input golden JSON and asserts round-trip (serialize -> deserialize -> serialize) byte stability and equality to the committed `lich_phap` slot from TASK-PLAT-002's fixtures.
- Reproduction test: recast from `dau_vao` + stamped `co_lich_phap`, assert identical `LichPhap`.
- Flag-isolation matrix: for each flag, hold the rest at default and assert the changed field set is exactly as expected (a small property test over the closed flag enums).
- Schema conformance: validate the serialized object against `docs/contracts/laso-envelope.schema.json` (shared with TASK-PLAT-002).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-lichphap -- -D warnings`, `cargo test -p cyberos-lichphap`.

## §6 - Implementation skeleton

1. `flags.rs`: `LichFlags` and the four flag enums with serde `rename` to the exact literals; a `Default` that leaves `truong_sinh_phai` explicit (engine-supplied).
2. `output.rs`: `LichPhap`, `TietKhiHt`, and serde derives; re-export `BonTru`, `ChanThaiDuong`, `PhaiSinh` from their modules so the serialized shape is assembled in one place.
3. `api.rs`: `tinh_lich_phap` - call tiet khi (TASK-CORE-001), chan thai duong (TASK-CORE-002), bon tru (TASK-CORE-003), phai sinh (TASK-CORE-004) in order, then stamp `co_lich_phap`.
4. Add the golden fixture (kept in sync with TASK-PLAT-002's `lich_phap` slot) and the flag-isolation matrix.

## §7 - Dependencies

Depends on TASK-CORE-002, TASK-CORE-003, TASK-CORE-004 (the three producers it composes; TASK-CORE-001 arrives transitively through them). Fills the `lich_phap` slot fixed by TASK-PLAT-002 - the two MUST agree on the serialized shape, so change them together. Blocks TASK-CORE-006 (the oracle harness runs against this API), TASK-QMDG-001 / TASK-LN-001 / TASK-TAT-001 (every engine's first slice reads this object), and TASK-API-001 (the orchestrator resolves the calendar context here).

## §8 - Example payloads

See §3 for the full `lich_phap` object. Minimal call:

```rust
let flags = LichFlags { truong_sinh_phai: TruongSinhPhai::NguHanh, ..Default::default() };
let lp = tinh_lich_phap(dt, FixedOffset::east_opt(7*3600).unwrap(), 106.7, &flags);
// lp.co_lich_phap now carries all six flags, longitude = 106.7
```

## §9 - Open questions

- Should `tam_nguyen` (thuong/trung/ha) be computed here or left to QMDG? Decision (inherited from TASK-CORE-001 §9): this object carries the raw current term + its instant and a coarse tam_nguyen marker; the QiMen-specific thuong/trung/ha for dinh cuc is computed in TASK-QMDG-001 from the phu dau. Keep the two aligned when QMDG-001 lands.
- Do we expose a `want_derived` switch so timing scans can skip `phai_sinh`? Decision: yes - a request-level flag (not a school flag, so not stamped) controls whether `phai_sinh` is populated; default on for interpretation, off for bulk timing scans (STRAT-001).

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Shape drift from PLAT-002 | field renamed on one side only | schema/golden test fails in CI before it can ship |
| Missing flag in stamp | a defaulted flag omitted from `co_lich_phap` | reproduction test diverges; all six MUST always be present |
| Enum literal mismatch | serde emits `"Twenty3"` not `"23:00"` | schema conformance fails |
| Engine recomputed calendar | consumer bypasses this API | code review + no alternate calendar entry point exposed |
| Mutable output | consumer mutates `LichPhap` after cast | fields exposed read-only; no public setter |

## §11 - Notes

This task and TASK-PLAT-002 are two views of one contract: PLAT-002 fixes the slot and the version/cache-key rules, this task fills the slot and owns the `LichFlags` set. Keep the golden `lich_phap` JSON identical in both crates' fixtures so a drift is a failing test, not a production surprise. Same crate `cyberos-lichphap` - this task adds `api.rs`, `flags.rs`, `output.rs` and turns the calendar core into one callable, testable unit.
