---
id: FR-CORE-002
title: "True solar time (equation of time + longitude correction + flags) - chan thai duong thoi, Meeus EoT with signed extrema, 4 minutes per degree off the VN 105E meridian, use_true_solar_time + longitude flags, feeds the hour-pillar boundary"
module: CORE
priority: MUST
status: reviewing
phase: P0
slice: 1
lang: rust
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, strategy RISK-1, Claude-05 s3, Claude-05 s3.1, Claude-05 s3.2, Claude-05 s3.3]
related_frs: [FR-CORE-001, FR-CORE-003, FR-CORE-005, FR-CORE-006]
depends_on: [FR-CORE-001]
blocks: [FR-CORE-003, FR-CORE-005]
new_paths:
  - crates/cyberos-lichphap/src/truesolar.rs
  - crates/cyberos-lichphap/src/eot.rs
  - crates/cyberos-lichphap/tests/truesolar_oracle.rs
---

## §1 - Description (BCP-14 normative)

This FR implements chan thai duong thoi (真太陽時), the true (apparent) solar time at the place of observation, on top of the astronomy layer built in FR-CORE-001. Clock time is mean zone time; the Eastern hour boundaries (gio Ty, gio Suu, ...) are defined by the real position of the sun, not by the clock. This module converts one from the other so the hour pillar (FR-CORE-003) keys off the correct branch.

The module SHALL compute true solar time as `clock_time + longitude_correction + equation_of_time`, where every term is expressed in the same signed convention fixed in §3. It SHALL compute the equation of time (均時差) by the Jean Meeus method (Astronomical Algorithms ch. 28), reusing the apparent-longitude and obliquity routines from FR-CORE-001 so the two layers never diverge on the sun's position. It SHALL compute the longitude correction as four minutes per degree of offset from the timezone standard meridian; for Vietnam (UTC+07) the standard meridian is 105 degrees East.

The module SHALL expose two calendar flags that change the result and MUST be stamped into `co_lich_phap`: `use_true_solar_time` (default `true`) and `longitude` (decimal degrees, defaulted per place). When `use_true_solar_time` is `false` the module SHALL return clock time unchanged and SHALL still record `ap_dung: false` so the chart remains reproducible. The correction MUST be applied before any hour-branch assignment, because near a two-hour boundary a total offset of up to twenty-odd minutes is enough to push a moment into the neighbouring gio and change the chart of all three engines.

## §2 - Why this design (rationale for humans)

Two independent effects separate clock time from real solar time (Claude-05 s3.1). First, a timezone applies one clock across many degrees of longitude; a place east of its standard meridian sees the sun earlier, so its local solar time runs ahead. Vietnam's zone (+07) is anchored to 105E, so Ho Chi Minh City at 106.7E gains about +6.8 minutes and Ha Noi at 105.85E about +3.4 minutes. Second, the equation of time - born of the Earth's elliptical orbit and axial tilt - swings the sundial ahead of and behind the mean clock through the year, up to roughly a quarter of an hour each way (Claude-05 s3.2). Summed, the two can exceed twenty minutes.

That total is exactly the danger size. The Eastern two-hour gio are 120 minutes wide; a twenty-minute error near a boundary flips the hour branch, which changes the gio chi and (via Ngu Thu Don) the gio can, which changes the LiuRen chiem hour, the QiMen truc phu / truc su hour stem-branch, and the TaiYi thoi ke. Because different schools disagree on whether to apply true solar time at all, and on which longitude to use, the choice is a flag stamped into the chart rather than a hardcoded constant. Reusing FR-CORE-001's solar routines (rather than a second, simpler EoT series) keeps a single source of truth for the sun's position, so a fix there propagates here automatically.

## §3 - Contract (algorithm)

### Sign convention (normative - pin this once)

Let `E` be the equation of time in the sense `E = apparent_solar - mean_solar` (minutes). This is the quantity ADDED to zone mean time to obtain true solar time. Let the longitude correction be

```
longitude_correction_minutes = 4.0 * (longitude_deg - standard_meridian_deg)
standard_meridian_deg          = utc_offset_hours * 15.0        // VN (+07) -> 105.0
```

so a place east of its meridian yields a positive correction. Then

```
true_solar_time = clock_time + longitude_correction_minutes + E        // minutes added to the clock
```

Worked check (Claude-05 s6.1 payload): clock 2004-01-01T10:30:00, longitude 106.7, tz +07:00 gives `longitude_correction = 4*(106.7-105.0) = +6.8 min` and `E ~= -3.5 min`, so `gio_that = 10:30:00 + 6.8 - 3.5 = 10:33:18`. This exact triple (6.8, -3.5, 10:33:18) is a golden fixture.

### Equation of time (Meeus ch. 28, reusing FR-CORE-001)

```
fn equation_of_time_minutes(jde: f64) -> f64 {
    // L0  = sun mean longitude (already in FR-CORE-001 solar.rs)
    // lam = apparent longitude (kinh_do_mat_troi), eps = true obliquity of the ecliptic
    // alpha = apparent right ascension: atan2(cos(eps)*sin(lam), cos(lam))
    // E_deg = L0 - 0.0057183 - alpha_deg (+ nutation term); reduce to (-180,180]
    // return 4.0 * E_deg   // 1 degree = 4 minutes; result reduced to about (-20, +20)
}
```

The 0.0057183 constant is the aberration/light-time term from Meeus; `alpha` MUST be reduced into the same revolution as `L0` before differencing, and the result reduced to the small (-20, +20) minute band.

### Annual extrema (Claude-05 s3.2) - convention cross-table

The classical figures are usually quoted as "clock ahead of sundial" (`mean - apparent`); this FR's `E` is the negative of that. Both columns are locked as oracle targets.

| Date (approx) | Classical quote (mean - apparent) | Signed E used here (apparent - mean) |
|---|---|---|
| ~11 February | +14m22s | -14m22s |
| ~4 November | -16m23s | +16m23s |

### Longitude correction for Vietnam (Claude-05 s3.3)

| Place | Longitude | Correction = 4*(lon - 105) |
|---|---|---|
| VN standard meridian | 105.00 E | 0.0 min |
| Ha Noi | 105.85 E | +3.4 min |
| Ho Chi Minh City | 106.70 E | +6.8 min |

### Public types

```rust
pub struct ChanThaiDuong {
    pub ap_dung: bool,                    // = use_true_solar_time
    pub gio_that: DateTime<FixedOffset>,  // true solar time in the input's zone offset
    pub hieu_chinh_kinh_do_phut: f64,     // longitude correction, minutes
    pub phuong_trinh_thoi_gian_phut: f64, // E (apparent - mean), minutes
    pub hieu_chinh_phut: f64,             // total = longitude + E (the number stamped in the envelope)
}
pub fn chan_thai_duong_thoi(
    clock: DateTime<FixedOffset>, longitude_deg: f64, flags: &LichFlags) -> ChanThaiDuong;
```

## §4 - Acceptance criteria

1. `equation_of_time_minutes` matches a reference ephemeris within 3 seconds of time across 1900-2100 spot checks, and reproduces the two annual extrema (-14m22s ~Feb 11, +16m23s ~Nov 4) within 5 seconds.
2. The golden triple holds exactly: clock 2004-01-01T10:30:00 +07:00 at longitude 106.7 yields correction +6.8 min, E about -3.5 min, `gio_that` 2004-01-01T10:33:18 +07:00.
3. Longitude correction equals 4 minutes per degree from the standard meridian; Ha Noi (+3.4) and HCMC (+6.8) are unit-tested; the standard meridian is derived from the UTC offset, not hardcoded to 105.
4. With `use_true_solar_time = false`, `gio_that == clock` and `ap_dung == false`; the field is still emitted for reproducibility.
5. The sign is correct: at a longitude east of the meridian and a date where E is negative, `gio_that` is later than the clock by exactly `longitude_correction + E`.

## §5 - Verification

- `tests/truesolar_oracle.rs` asserts the golden triple, the two EoT extrema (both convention columns), and the Ha Noi / HCMC corrections.
- Property test: for 10,000 random instants across the year, `-20 < E < 20` minutes, `E` is continuous, and `true_solar_time - clock == longitude_correction + E` to floating tolerance.
- Cross-check the EoT curve against the `equation_of_time` produced by an independent library (skyfield or the sxwnl mean-time delta) at monthly samples over one decade, within a few seconds (feeds FR-CORE-006).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-lichphap -- -D warnings`, `cargo test -p cyberos-lichphap`.

## §6 - Implementation skeleton

1. `eot.rs`: `equation_of_time_minutes(jde)`, computing `alpha` from FR-CORE-001's `kinh_do_mat_troi` (lambda) plus obliquity, then `4*(L0 - 0.0057183 - alpha)`.
2. `truesolar.rs`: `chan_thai_duong_thoi`, standard-meridian-from-offset, longitude correction, flag handling, the `ChanThaiDuong` struct.
3. Expose `hieu_chinh_phut = longitude + E` so FR-CORE-005 can stamp a single number in the envelope.
4. Add the golden-triple and extrema fixtures; wire the property test.
5. Leave a `precision` hook so FR-CORE-006 can swap in a higher-order EoT if the boundary-case count demands it.

## §7 - Dependencies

Depends on FR-CORE-001 (reuses apparent longitude, obliquity, and the delta-T / JDE plumbing). Blocks FR-CORE-003 (the hour pillar assigns its branch from `gio_that`, so it cannot be correct until true solar time is) and FR-CORE-005 (the `chan_thai_duong` sub-object of the calendar output). This is why the catalog's CORE-003 dependency is widened to include CORE-002 (see FR-CORE-003 §7).

## §8 - Example payloads

```json
{
  "chan_thai_duong": {
    "ap_dung": true,
    "hieu_chinh_kinh_do_phut": 6.8,
    "phuong_trinh_thoi_gian_phut": -3.5,
    "hieu_chinh_phut": 3.3,
    "gio_that": "2004-01-01T10:33:18+07:00"
  }
}
```

With `use_true_solar_time: false` the same input yields `{ "ap_dung": false, "gio_that": "2004-01-01T10:30:00+07:00", "hieu_chinh_phut": 0.0 }`.

## §9 - Open questions

- Do we default `longitude` from a place lookup (geocode) or require the caller to pass it? Decision for MVP: the caller (API-001) resolves place -> longitude and passes decimal degrees; CORE never geocodes. Revisit if a place database lands.
- Is the low-order EoT enough at the hour boundary, or do the rare within-a-minute-of-boundary cases need the higher-order sun? Deferred to FR-CORE-006: the oracle harness counts boundary cases and decides whether a `precision` bump is ever needed.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| EoT sign flip | apparent-vs-mean convention confused | golden triple and extrema cross-table fail; do not ship |
| Longitude correction sign | east/west of meridian confused | Ha Noi / HCMC unit test fails (must be positive east of 105) |
| Standard meridian hardcoded | non-VN offset passed | assertion: standard meridian == utc_offset_hours * 15 |
| Correction applied after hour-branching | ordering bug in FR-CORE-003 wiring | boundary probe assigns wrong gio; caught by FR-CORE-003 test |
| Flag not stamped | `use_true_solar_time` omitted from `co_lich_phap` | reproduction test in FR-CORE-005 diverges |

## §11 - Notes

Keep the EoT anchored to FR-CORE-001's sun rather than a standalone day-of-year series: one source of truth for the sun's position is worth more than a few lines saved. The single stamped number `hieu_chinh_phut` (longitude + E) is what a reader needs to see how far the chart's hour was shifted; the two components are kept alongside for audit. Same crate `cyberos-lichphap` as FR-CORE-001 - this FR adds `truesolar.rs` and `eot.rs`, it does not create a new crate.
