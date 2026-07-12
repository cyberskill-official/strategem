---
id: FR-CORE-004
title: "Derived states (tuan khong + vuong-suy + truong sinh) - empty-branch table, vuong-tuong-huu-tu-tu by season, 12-stage truong sinh with am_duong vs ngu_hanh school flag, all lookup-table data"
module: CORE
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, strategy RISK-2, Claude-05 s5, Claude-05 s5.1, Claude-05 s5.2, Claude-05 s5.3]
related_frs: [FR-CORE-003, FR-CORE-005, FR-CORE-007]
depends_on: [FR-CORE-003]
blocks: [FR-CORE-005]
new_paths:
  - crates/cyberos-lichphap/src/derived.rs
  - crates/cyberos-lichphap/src/data/truong_sinh.rs
  - crates/cyberos-lichphap/tests/derived_tables.rs
---

## §1 - Description (BCP-14 normative)

This FR builds the three derived states that all three engines read when they judge a chart: tuan khong (旬空, empty branches), vuong-tuong-huu-tu-tu (旺相休囚死, seasonal strength of the five phases), and truong sinh muoi hai cung (長生十二宮, the twelve life-stages of a stem). All three are pure lookup tables keyed by can chi and season, digitized as data (Claude-05 s5), computed on top of the pillars from FR-CORE-003.

The module SHALL compute tuan khong from a can-chi pair by locating its tuan giap (the sixty-cycle decad) and returning the two chi with no stem in that decad. It SHALL compute the seasonal strength of a phase from the season implied by the month pillar, following the fixed vuong / tuong / huu / tu / tu rule. It SHALL compute the twelve-stage truong sinh position of a stem across the twelve chi under a school selected by the flag `truong_sinh_phai` (`am_duong` | `ngu_hanh`), which MUST be stamped into `co_lich_phap`. LiuRen defaults to `ngu_hanh`; each engine declares its own default, so this module MUST NOT hardcode a school.

All three outputs SHALL be derived from committed lookup tables, not recomputed heuristically, so that a reviewer can check each table against a classical source and the oracle harness (FR-CORE-006) can diff them per school.

## §2 - Why this design (rationale for humans)

These three states are where a chart stops being a calendar and starts being readable (Claude-05 s5). Tuan khong marks which two branches are hollow in the current decad - ten stems pair twelve branches, so each decad of ten leaves two branches without a stem, and a factor landing on a hollow branch is read as weakened or absent. Vuong-suy grades a phase by the season: the phase of the season is vuong (thriving), the phase the season produces is tuong, and so down to tu (dead). Truong sinh tracks a stem through a twelve-stage life-cycle (birth, bath, cap-and-gown, ... tomb, extinction, conception, nurture) as it moves across the branches.

The one place schools diverge is truong sinh (Claude-05 s5.3), and it changes results, so it is a flag. The am-duong school gives every stem its own starting branch, yang stems running forward and yin stems backward. The ngu-hanh school groups stems by phase and runs one cycle per phase, with Thuy and Tho sharing a palace. LiuRen conventionally uses the ngu-hanh cycle; other systems may prefer am-duong. Hardcoding either would silently cast half of users' charts wrong (strategy RISK-2), so the platform stamps the school and offers both. Keeping all three as data (not code branches) makes them auditable and makes the per-school oracle diff mechanical.

## §3 - Contract (tables and algorithm)

### Tuan khong (Claude-05 s5.1)

Given a can-chi pair (can `c` in 0..10, chi `z` in 0..12), the two empty branches are

```
empty = { (z - c + 10) mod 12,  (z - c + 11) mod 12 }        // 0=子 ... 11=亥
```

which is equivalent to stepping back to the decad's 甲 head and taking the two branches past its tenth. Full table (both forms MUST agree):

| Tuan | Tuan khong | Tuan | Tuan khong |
|---|---|---|---|
| 甲子 Giáp Tý tuần | 戌 亥 Tuất Hợi | 甲午 Giáp Ngọ tuần | 辰 巳 Thìn Tỵ |
| 甲戌 Giáp Tuất tuần | 申 酉 Thân Dậu | 甲辰 Giáp Thìn tuần | 寅 卯 Dần Mão |
| 甲申 Giáp Thân tuần | 午 未 Ngọ Mùi | 甲寅 Giáp Dần tuần | 子 丑 Tý Sửu |

Check: 甲子 (c=0,z=0) -> {10,11} = 戌 亥; 甲戌 (c=0,z=10) -> {8,9} = 申 酉.

### Vuong-tuong-huu-tu-tu (Claude-05 s5.2)

The season comes from the month pillar. Rule: the phase equal to the season is vuong (旺); the phase the season generates is tuong (相); the phase that generates the season is huu (休); the phase the season controls is tu (囚); the phase that controls the season is tu (死). The four last-month-of-season periods are Tho.

| Mua (hanh) | Vuong | Tuong | Huu | Tu | Tu |
|---|---|---|---|---|---|
| Xuan (Mộc) | 木 | 火 | 水 | 金 | 土 |
| Ha (Hỏa) | 火 | 土 | 木 | 水 | 金 |
| Thu (Kim) | 金 | 水 | 土 | 火 | 木 |
| Dong (Thủy) | 水 | 木 | 金 | 土 | 火 |
| Tu quy (Thổ) | 土 | 金 | 火 | 木 | 水 |

### Truong sinh muoi hai cung (Claude-05 s5.3)

The twelve stages, in order: trường sinh, mộc dục, quan đới, lâm quan, đế vượng, suy, bệnh, tử, mộ, tuyệt, thai, dưỡng.

School `am_duong` - each stem its own start; yang stems forward, yin stems backward:

| Can | Khoi truong sinh | Chieu |
|---|---|---|
| 甲 Giáp (duong) | 亥 | thuan (forward) |
| 乙 Ất (am) | 午 | nghich (backward) |
| 丙 Bính (duong) | 寅 | thuan |
| 丁 Đinh (am) | 酉 | nghich |
| 戊 Mậu (duong) | 寅 | thuan |
| 己 Kỷ (am) | 酉 | nghich |
| 庚 Canh (duong) | 巳 | thuan |
| 辛 Tân (am) | 子 | nghich |
| 壬 Nhâm (duong) | 申 | thuan |
| 癸 Quý (am) | 卯 | nghich |

School `ngu_hanh` - one cycle per phase (Thuy and Tho share a palace), always forward:

| Hanh | Truong sinh khoi |
|---|---|
| Mộc | 亥 |
| Hỏa | 寅 |
| Kim | 巳 |
| Thủy va Thổ | 申 |

LiuRen defaults `ngu_hanh`. Note 巳 (Ty, snake) vs 子 (Ti, rat) are distinct starts - the Han disambiguates.

### Public types

```rust
pub struct PhaiSinh {
    pub tuan_khong: [Chi; 2],
    pub vuong_suy: BTreeMap<NguHanh, VuongSuy>,     // per phase, for the chart's season
    pub truong_sinh: BTreeMap<Can, GiaiDoan>,       // per stem, under the selected school
}
pub enum VuongSuy { Vuong, Tuong, Huu, Tu, Tu2 }    // 旺相休囚死 (Tu2 = 死, distinct from 囚)
pub fn phai_sinh(tru: &BonTru, flags: &LichFlags) -> PhaiSinh;
```

## §4 - Acceptance criteria

1. Tuan khong: the closed-form `{(z-c+10)%12, (z-c+11)%12}` matches the six-row table exhaustively for all 60 pairs; 甲子 -> 戌 亥 and 甲午 -> 辰 巳 are pinned.
2. Vuong-suy: for each of the five seasons the five phases map to the correct one of vuong/tuong/huu/tu/tu; Xuan -> Mộc vuong, Kim tu, Tho tu2 is pinned.
3. Truong sinh am_duong: each stem starts at its listed branch with the correct direction; yang forward, yin backward; 甲 at 亥 forward and 辛 at 子 backward are pinned.
4. Truong sinh ngu_hanh: Mộc 亥, Hỏa 寅, Kim 巳, Thủy and Thổ 申; the two schools give provably different positions for at least one stem (a regression guard that the flag is live).
5. `truong_sinh_phai` selects the school and is stamped into `co_lich_phap`; the module has no default baked in (the caller / engine supplies it).

## §5 - Verification

- `tests/derived_tables.rs` enumerates all 60 can-chi pairs for tuan khong, all 5 seasons x 5 phases for vuong-suy, and all 10 stems x both schools for truong sinh, against the tables above.
- Per-school cross-check: a manual fixture (hand-computed from a classical text) for tuan khong, vuong-suy, and both truong sinh schools, diffed by FR-CORE-006 (this is the "per school" clause of the RISK-1 gate).
- Regression guard: assert `truong_sinh(am_duong) != truong_sinh(ngu_hanh)` for at least stem 乙 so a collapsed flag fails loudly.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-lichphap -- -D warnings`, `cargo test -p cyberos-lichphap`.

## §6 - Implementation skeleton

1. `data/truong_sinh.rs`: the two school tables as `const` data (am_duong: start + direction per stem; ngu_hanh: start per phase), plus the twelve stage names.
2. `derived.rs`: `tuan_khong` (closed form, checked against the committed six-row table), `vuong_suy` (season from month pillar -> the five-way map), `truong_sinh` (walk twelve stages from the flag-selected start/direction), and the `PhaiSinh` assembler.
3. Reuse FR-CORE-007 for `Can`/`Chi`/`NguHanh` and the sinh/khac relations used by vuong-suy.
4. Add the enumerated tests and the hand-computed per-school fixture.

## §7 - Dependencies

Depends on FR-CORE-003 (the pillars supply the can-chi pairs and the season). Uses FR-CORE-007 for phase/relation primitives (soft; joinable at integration). Blocks FR-CORE-005 (the `phai_sinh` sub-object of the calendar output). The `truong_sinh_phai` flag it reads is defined in the canonical `LichFlags` owned by FR-CORE-005.

## §8 - Example payloads

```json
{
  "phai_sinh": {
    "tuan_khong": ["申", "酉"],
    "vuong_suy": { "Mộc": "vuong", "Hỏa": "tuong", "Thủy": "huu", "Kim": "tu", "Thổ": "tu2" },
    "truong_sinh": { "甲": "trường sinh @ 亥", "乙": "trường sinh @ 午" }
  }
}
```

The `vuong_suy` example is a Xuan (Mộc season) chart; the `truong_sinh` example is under `am_duong`.

## §9 - Open questions

- Do we always emit all three derived states, or only on request to save work? Decision: FR-CORE-005 gates emission behind a `want_derived` request flag (they are not needed for pure timing scans); when emitted they are complete. Default on for interpretation paths.
- Should vuong-suy expose the four Tho "tu quy" transition months as a distinct season, or fold Tho into the adjacent season? Decision: keep the five-row table (Tho as tu quy) exactly as the classical source; the month-to-season mapping for the last 18 days of each season is a documented refinement deferred to the engine that needs it.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Tuan khong off by a branch | wrong sign in (z - c) | closed form disagrees with six-row table; do not ship |
| Vuong-suy 囚/死 swapped | tu (囚) and tu (死) conflated | enumerated season test fails; keep the two distinct (VuongSuy::Tu vs Tu2) |
| Truong sinh direction | yin stem run forward | 辛/乙 backward probe fails |
| 巳 vs 子 start confused | Ty (snake) vs Ti (rat) diacritic loss | Canh (巳) / Tan (子) start test fails; keep Han in the table |
| School hardcoded | flag ignored, one school always used | am_duong == ngu_hanh regression guard fails |
| Flag unstamped | `truong_sinh_phai` missing from `co_lich_phap` | FR-CORE-005 reproduction test diverges |

## §11 - Notes

Keep every table as committed `const` data with the classical Han in place - these are the kind of tables a domain reviewer reads directly, and normalizing 巳/子 or 囚/死 to ASCII would erase exactly the distinctions that matter. The per-school truong sinh diff is the clearest expression of the flag-and-stamp discipline in the calendar core. Same crate `cyberos-lichphap` - this FR adds `derived.rs` and `data/truong_sinh.rs`.
