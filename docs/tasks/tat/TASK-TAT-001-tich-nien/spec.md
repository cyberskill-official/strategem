---
id: TASK-TAT-001
title: "Tich nien + ky nguyen - accumulate years from an epoch, three remainder reductions (mod 360 / 72 / 60), epoch flag, Thai At through the nine palaces (skips center, lodges Khon 2); emits into the la so ban for he=thai_at"
module: TAT
priority: MUST
status: done
phase: P2
slice: 1
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-04 s2, Grok-30]
related_frs: [TASK-TAT-002, TASK-TAT-003, TASK-TAT-004, TASK-TAT-006, TASK-CORE-005, TASK-PLAT-002]
depends_on: [TASK-CORE-005]
blocks: [TASK-TAT-002, TASK-TAT-004, TASK-TAT-006]
new_paths:
  - crates/cyberos-thaiat/Cargo.toml
  - crates/cyberos-thaiat/src/lib.rs
  - crates/cyberos-thaiat/src/epoch.rs
  - crates/cyberos-thaiat/src/tichnien.rs
  - crates/cyberos-thaiat/src/cuucung.rs
  - crates/cyberos-thaiat/src/flags.rs
  - crates/cyberos-thaiat/tests/tichnien_oracle.rs
  - crates/cyberos-thaiat/tests/fixtures/tichnien_kintaiyi.csv
---

## §1 - Description (BCP-14 normative)

This task builds the base of every Thai At Than So chart: tich nien and the reductions that turn it into the numbers the rest of the engine reads. It owns the birth of the `cyberos-thaiat` crate; TASK-TAT-002..006 extend it.

The module SHALL compute tich nien (積年), a continuous count of years from an epoch to the civil year under examination. It SHALL support an epoch flag: the default `kim_kinh` (tich nien = 10,153,917 + CE, the Kim Kinh / Thong Tong system with the thickest textual base) and a `co_dien` alternative (anchored 1,937,281 at 724 CE). A breaking difference between epochs (roughly sixty years) re-casts the whole chart, so the epoch MUST be selectable and MUST be stamped into every chart.

From tich nien the module SHALL derive three reductions (Claude-04 s2.2): `tich_nien mod 360` = nhap ky nguyen (position in the great cycle), `tich_nien mod 72` = nhap cuc (the cuc number 1..72, the single most important value - it locates Thai At and drives the tuong), and `tich_nien mod 60` = the year can-chi. All three SHALL be computed with integer arithmetic wide enough that a count near 10^7 neither overflows nor loses precision.

The module SHALL model Thai At's movement over the nine palaces. The Thai At layout is rotated 45 degrees counter-clockwise from the ordinary Luoshu: Can 1, Ly 2, Can(艮) 3, Chan 4, Trung 5, Doai 6, Khon 7, Kham 8, Ton 9. Thai At advances one palace every three years, so twenty-four years complete one circuit of the eight outer palaces and seventy-two years (three circuits) close the mod-72 cuc. Thai At SHALL never occupy the center palace (5): it skips the center and lodges in Khon (numbered 2 in the Thai At layout). Direction follows the don: after Dong Chi duong don runs forward from palace 1 (Can); after Ha Chi am don runs backward from palace 9 (Ton).

The module SHALL emit its result (tich nien, the three reductions, the don direction, the Thai At palace) into the `ban` slot of the la so envelope (TASK-PLAT-002) under `he = "thai_at"`, and SHALL stamp the TAT flag set into `co_truong_phai`. The oracle for the whole engine is kintaiyi.

## §2 - Why this design (rationale for humans)

Thai At is the macro system, and its whole determinism starts from one large number. Unlike LiuRen and QiMen, which read the ganzhi and tiet khi of a chosen instant, Thai At reads tich nien - a running count of years from a distant epoch - and that count, through remainder reductions, fixes Thai At's palace and the entire chart (Claude-04 s1.2). Get tich nien wrong and nothing downstream can be right.

The epoch is a mandatory flag for the same reason dinh cuc method is mandatory in QiMen: the sources genuinely disagree, and the disagreement changes the answer. Two common epochs sit about sixty years apart, which is a whole ganzhi cycle - enough to move Thai At and re-cast the board. Stamping the epoch on every chart is what makes a TaiYi result reproducible and defensible; an unstamped epoch is a silent defect (strategy RISK-2).

The arithmetic is called out as integer-only because tich nien is near ten million and the reductions are the load-bearing step. A floating-point count would round; a narrow integer would overflow. This is, after the chinh cung vs gian than counting rule (TASK-TAT-002), the most common TaiYi implementation bug. The nine-palace movement is stated here because Thai At's path is deterministic from the cuc and the don, and the center-skip / Khon-lodge rule is easy to omit.

## §3 - Contract (algorithm and types)

### Tich nien and the three reductions (Claude-04 s2.2, verbatim algorithm)

```
# nam_ce = civil year; epoch selects the origin
def tich_nien(nam_ce, epoch="kim_kinh"):
    if epoch == "kim_kinh":
        tn = 10_153_917 + nam_ce
    elif epoch == "co_dien":
        tn = 1_937_281 + (nam_ce - 724)   # anchored at 724 CE
    nhap_ky_nguyen = tn % 360
    nhap_cuc       = tn % 72     # mapped to 1..72 (see below); the most important number
    can_chi        = tn % 60
    return tn, nhap_ky_nguyen, nhap_cuc, can_chi
```

The cuc number is stated 1..72, so a bare `tn % 72` of 0 (a tich nien divisible by 72) SHALL map to 72, not 0: `nhap_cuc = if tn % 72 == 0 { 72 } else { tn % 72 }`.

### Worked example (Claude-04 s5.1)

For nam_ce = 2004 under `kim_kinh`: tich nien = 10,153,917 + 2,004 = 10,155,921. Then `mod 60` = 21 (Giap Than), `mod 72` = 33 (duong don, cuc 33). These are the golden numbers the unit test pins.

### Thai At over the nine palaces (Claude-04 s2.3)

Layout (rotated 45 degrees CCW from Luoshu), palace number in the Thai At scheme:

| Palace | 乾 Can | 離 Ly | 艮 Can(gen) | 震 Chan | 中 Trung | 兌 Doai | 坤 Khon | 坎 Kham | 巽 Ton |
|---|---|---|---|---|---|---|---|---|---|
| Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |

Rules: three years per palace; twenty-four years per circuit of the eight outer palaces; seventy-two years (three circuits) close the cuc. Thai At never enters the center (5) - it skips the center and lodges in Khon (2). Duong don (after Dong Chi) advances forward from palace 1 (Can); am don (after Ha Chi) advances backward from palace 9 (Ton). The path is fully determined by the cuc and the don.

### Public types (`crates/cyberos-thaiat/src/`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Epoch { KimKinh, CoDien }

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TichNien {
    pub tich_nien: u64,
    pub nhap_ky_nguyen: u16,   // mod 360
    pub nhap_cuc: u8,          // 1..=72
    pub can_chi: u8,           // mod 60, 1..=60
    pub duong_don: bool,       // true after Dong Chi, false after Ha Chi
    pub epoch: Epoch,
}

pub fn tich_nien(nam_ce: i32, epoch: Epoch, duong_don: bool) -> TichNien;
pub fn thai_at_cung(nhap_cuc: u8, duong_don: bool) -> u8;  // 1..=9, never 5; center -> Khon (2)
```

## §4 - Acceptance criteria

1. `tich_nien(2004, KimKinh, true)` yields tich nien 10,155,921, `nhap_cuc` 33, `can_chi` 21 (Giap Than) - the Claude-04 s5.1 worked example.
2. All three reductions use `u64` on the count and `u32`+ intermediates; a wide year range (say 1 CE .. 4000 CE) is checked with no overflow and exact mod values.
3. The epoch flag changes the result: for the same year, `kim_kinh` and `co_dien` give different `nhap_cuc`; each result carries `epoch` and it is stamped into `co_truong_phai`.
4. `nhap_cuc` is 1..=72: a tich nien divisible by 72 returns 72, never 0.
5. `thai_at_cung` never returns 5; when the movement would land on the center it returns Khon (2); the direction respects the don (Dong Chi vs Ha Chi anchor); the palace is constant across each three-year block and advances one palace per block along the fixed Thai At order.
6. The emitted `ban` (tich, Thai At palace) round-trips through the la so envelope (TASK-PLAT-002) under `he = "thai_at"`.

## §5 - Verification

- Unit: the s5.1 numbers (2004); the 1..=72 mapping at a tich nien divisible by 72; the epoch-difference test.
- Property: on a wide year span, `tich_nien` mod values are exact under `u64` (no overflow, no f64 rounding); `thai_at_cung` is total over 1..=72 x {duong, am} and never yields 5.
- Oracle: `tests/tichnien_oracle.rs` loads `fixtures/tichnien_kintaiyi.csv` (generated once from kintaiyi, per epoch, spanning multiple decades and both dons) and asserts the tich nien, cuc, can-chi, and Thai At palace match exactly. This is the base of the TAT-006 100% gate - it must pass for every epoch.
- Boundary: dedicated cases around the don-switch (Dong Chi / Ha Chi) and the cuc wrap (72 -> 1).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-thaiat -- -D warnings`, `cargo test -p cyberos-thaiat`.

## §6 - Implementation skeleton

1. Create the `cyberos-thaiat` crate (this task owns its birth; TASK-TAT-002..006 add modules).
2. `epoch.rs`: `Epoch` enum and the two origin constants (10,153,917 `kim_kinh`; 1,937,281 at 724 CE `co_dien`).
3. `tichnien.rs`: `tich_nien`, the three reductions, the 1..=72 cuc mapping.
4. `cuucung.rs`: the Thai At nine-palace layout array (Can1 Ly2 Can(gen)3 Chan4 Trung5 Doai6 Khon7 Kham8 Ton9), the three-years-per-palace / twenty-four-year-circuit movement, the center-skip -> Khon(2) rule, and the don direction.
5. `flags.rs`: the TAT flag set (`epoch` default `kim_kinh`, `dem_toan` default `truoc_thai_at`) with defaults, stamped whole.
6. Emit `TichNien` + Thai At palace into the `ban` slot for `he = "thai_at"`; wire the envelope.
7. Generate the kintaiyi fixture once per epoch (documented script, not run in CI) and commit; wire the oracle, property, and boundary tests.

## §7 - Dependencies

Depends on TASK-CORE-005 (the calendar module API). Nien ke needs only the civil year, but the don direction keys off the Dong Chi / Ha Chi instants from TASK-CORE-001, and the nhat/thoi ke tich (TASK-TAT-004) anchor on Dong Chi - so TaiYi and the calendar core must agree on the solstice instants. Blocks TASK-TAT-002 (an Thai At + the sixteen than read `nhap_cuc` and the Thai At palace), TASK-TAT-004 (the four time levels reuse this epoch / reduction machinery), and TASK-TAT-006 (assembly + oracle gate). Emits into the TASK-PLAT-002 envelope.

## §8 - Example payloads

Nien ke for 2004 under `kim_kinh`:

```json
{ "envelope_version": 1, "he": "thai_at",
  "dau_vao": { "nam_ce": 2004, "cap": "nien_ke", "epoch": "kim_kinh" },
  "lich_phap": { "...": "from TASK-CORE-005; supplies the Dong Chi / Ha Chi anchor for the don" },
  "ban": {
    "tich": { "tich_nien": 10155921, "nhap_ky_nguyen": 81, "nhap_cuc": 33,
              "can_chi": "甲申", "duong_don": true },
    "thai_at_cung": 1,
    "thap_luc_than": {}, "bat_tuong": {}, "cac_toan": {}
  },
  "cach_cuc": [],
  "co_truong_phai": { "epoch": "kim_kinh", "dem_toan": "truoc_thai_at" },
  "provenance": { "engine": "tat", "engine_version": "0.1.0", "cast_at": "..." } }
```

(`thai_at_cung` and `nhap_ky_nguyen` shown illustratively; both are pinned to kintaiyi by the oracle test.)

## §9 - Open questions

- Default epoch: `kim_kinh` (thickest textual base, Claude-04 s2.1); `co_dien` behind the flag. The ~60-year gap is a real school split, so the flag is mandatory and stamped, exactly like QiMen dinh cuc method.
- Does Thai At placement key off the mod-72 cuc directly, or off the mod-360 nhap ky nguyen for the circuit index? Default: the cuc (mod 72) drives placement (three circuits x 24 years = 72, Claude-04 s2.3); cross-check with kintaiyi and adjust only if it diverges.
- Nien ke needs only the year; nguyet/nhat/thoi ke (TASK-TAT-004) need tich nguyet/nhat/thoi and the Dong Chi anchor. The tich formulas are TAT-004's, but the epoch + reduction machinery lives here. Confirm the boundary when TAT-004 lands.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Tich nien overflow / f64 rounding | using f64 for a 10^7-scale count | use u64/i64; a wide-range test asserts exact mod values |
| Epoch not stamped | chart cast under co_dien but stamped kim_kinh | reproduction test recasts from the stamp and diverges -> fail |
| Thai At enters center 5 | center-skip rule missing | assertion `thai_at_cung != 5` for all cuc; center maps to Khon (2) |
| nhap_cuc 0 instead of 1..72 | naive `tn % 72` at a multiple of 72 | mapping test at a tich nien divisible by 72 returns 72 |
| Wrong don direction | Dong Chi / Ha Chi anchor swapped | boundary test around both solstices vs kintaiyi |

## §11 - Notes

The crate name `cyberos-thaiat` is shared with TASK-TAT-002..006; they extend this crate rather than spawn new ones, so the TaiYi engine is one cargo-testable unit. TaiYi is the macro / long-cycle system, so its base is tich nien rather than the instant-based ganzhi of LiuRen and QiMen - which is why the epoch flag is as load-bearing here as dinh cuc is in QiMen. Oracle kintaiyi; acceptance is 100% match per epoch AND (via TASK-TAT-004 / TAT-006) per time level. The tich-nien / epoch / reduction machinery built here is reused by all four time levels (nien / nguyet / nhat / thoi ke). Guard the large-integer arithmetic: it is the load-bearing step, and after the chinh cung vs gian than counting rule it is the most common TaiYi bug.
