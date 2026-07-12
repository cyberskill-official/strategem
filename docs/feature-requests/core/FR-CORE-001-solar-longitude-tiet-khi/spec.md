---
id: FR-CORE-001
title: "Solar longitude + 24 tiet khi - Meeus apparent longitude, Newton inverse-solve for jieqi instants, delta-T correction, jie vs trung khi split"
module: CORE
priority: MUST
status: reviewing
phase: P0
slice: 1
lang: rust
effort_h: 20
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, strategy RISK-1, Claude-05 s2, Claude-05 s1.3]
related_frs: [FR-CORE-002, FR-CORE-003, FR-CORE-005, FR-CORE-006]
depends_on: [FR-PLAT-001]
blocks: [FR-CORE-002, FR-CORE-003, FR-CORE-005, FR-QMDG-001]
new_paths:
  - crates/cyberos-lichphap/Cargo.toml
  - crates/cyberos-lichphap/src/lib.rs
  - crates/cyberos-lichphap/src/solar.rs
  - crates/cyberos-lichphap/src/tietkhi.rs
  - crates/cyberos-lichphap/src/delta_t.rs
  - crates/cyberos-lichphap/tests/tietkhi_oracle.rs
  - crates/cyberos-lichphap/tests/fixtures/tietkhi_sxwnl_1900_2100.csv
---

## §1 - Description (BCP-14 normative)

This FR implements the astronomy layer (L1) of the shared calendar core: the apparent solar longitude function and the 24 solar terms (tiet khi) derived from it. It is the foundation of the entire platform - an error here propagates to all three engines at once (strategy RISK-1), so it carries the highest test density in the project.

The module SHALL compute apparent solar longitude for any instant using the Jean Meeus low-order method (Astronomical Algorithms, ch. 25/27) to an accuracy of seconds-to-one-minute. It SHALL solve the inverse problem - given a target longitude (a multiple of 15 degrees), find the instant at which apparent solar longitude equals it - by Newton/secant iteration seeded from the Meeus equinox/solstice polynomial, converging to under one second. It SHALL apply the delta-T correction (Espenak-Meeus polynomial) to convert between Terrestrial Time and civil (UT) time; failing to do so can shift a term by minutes, enough to push it across a day boundary in edge cases.

The module SHALL distinguish the two interleaved kinds of term: the twelve jie (節, odd 15-degree marks) that govern month-pillar boundaries (consumed by FR-CORE-003), and the twelve trung khi (中氣, even marks) that govern nguyet tuong changes in LiuRen (consumed by FR-LN-001). Every returned term SHALL carry its kind, its exact instant in UTC, and the current tam nguyen (thuong/trung/ha) marker where applicable.

School and precision differences are flags, not hardcoded choices: `delta_t_model` (default `espenak_meeus`) and a `precision` selector (default `meeus_low`, with a `vsop87` slot reserved for FR-CORE-006 follow-up).

## §2 - Why this design (rationale for humans)

Solar terms are equal divisions of the sun's apparent ecliptic longitude (15 degrees each), not equal divisions of the calendar (Claude-05 s2.1). Because the sun moves unevenly on the ecliptic, the day-gap between terms varies, so terms MUST be computed from longitude, never counted in days. Get this wrong and QiMen dinh cuc, LiuRen nguyet tuong, and TaiYi all shift together.

Meeus low-order is chosen because it is accurate to well under a minute - more than enough for chart casting - and is cheap and auditable. VSOP87 (sub-arcsecond) is reserved behind a flag for the rare boundary case where a term instant sits within seconds of midnight; the oracle harness (FR-CORE-006) decides whether we ever need it. Delta-T is called out explicitly because it is the most common silent bug: Meeus runs in Terrestrial Time, civil clocks run in UT, and the offset (about 67s in 2010, 93s in 2050) is exactly the size that flips a boundary case.

## §3 - Contract (algorithm)

### Apparent solar longitude (Claude-05 s2.2, verbatim algorithm)

```
# jde = Julian Ephemeris Day (Terrestrial Time)
fn kinh_do_mat_troi(jde: f64) -> f64 {           // returns apparent longitude, degrees [0,360)
    let t  = (jde - 2451545.0) / 36525.0;
    let l0 = (280.46646 + 36000.76983*t + 0.0003032*t*t).rem_euclid(360.0);   // mean longitude
    let m  = 357.52911 + 35999.05029*t - 0.0001537*t*t;                       // mean anomaly
    let mr = m.to_radians();
    let c  = (1.914602 - 0.004817*t - 0.000014*t*t)*mr.sin()
           + (0.019993 - 0.000101*t)*(2.0*mr).sin()
           + 0.000289*(3.0*mr).sin();                                          // equation of center
    let theta = l0 + c;
    let omega = (125.04 - 1934.136*t).to_radians();
    let lam = theta - 0.00569 - 0.00478*omega.sin();                          // apparent longitude
    lam.rem_euclid(360.0)
}
```

### Inverse solve (find the instant of a target longitude)

```
fn thoi_diem_tiet_khi(target_deg: f64, year: i32) -> DateTime<Utc> {
    // 1. seed from Meeus ch.27 equinox/solstice polynomial for a close jde0
    // 2. iterate: jde_{n+1} = jde_n + (target - kinh_do_mat_troi(jde_n))_wrapped * (365.25/360)
    //    handle the 0/360 wrap; 3-5 iterations converge to < 1 second
    // 3. convert jde (TT) -> UTC by subtracting delta_t(year)
}
```

### Delta-T (Espenak-Meeus, 2005-2050 band; full piecewise table for other bands)

```
fn delta_t_seconds(year: f64) -> f64 {           // model = espenak_meeus
    let t = year - 2000.0;
    62.92 + 0.32217*t + 0.005589*t*t             // valid ~2005-2050; other bands use the piecewise set
}
```

### The 24 terms and the jie/trung split

Term i (i in 0..24) is at longitude `i * 15` starting Xuan Phan = 0 deg. Odd-longitude marks (Lap Xuan 315, Kinh Trap 345, ...) are `Jie`; even marks (Xuan Phan 0, Dong Chi 270, ...) are `TrungKhi`. Public type:

```rust
pub struct TietKhi { pub name: &'static str, pub han: &'static str,
    pub longitude_deg: u16, pub kind: TermKind, pub instant: DateTime<Utc> }
pub enum TermKind { Jie, TrungKhi }
pub fn tiet_khi_in_year(year: i32, flags: &LichFlags) -> Vec<TietKhi>;      // 24 (or 25 with wrap) terms
pub fn tiet_khi_hien_hanh(at: DateTime<Utc>, flags: &LichFlags) -> TietKhi;  // the term in force at `at`
```

## §4 - Acceptance criteria

1. `kinh_do_mat_troi` matches a reference ephemeris within 0.01 degree over 1900-2100 spot checks.
2. Every one of the 24 term instants matches the sxwnl library within 60 seconds across 1900-2100 (the CI gate; fixture in `tests/fixtures/`).
3. Delta-T is applied in the correct direction (TT -> UTC), verified by a known term instant published to the second.
4. `kind` is correct for all 24 terms (12 Jie, 12 TrungKhi); a unit test enumerates them.
5. Boundary case: a term instant within 5 minutes of local midnight is returned with the correct calendar date after delta-T and does not drift under the `precision` flag.
6. `tiet_khi_hien_hanh` returns the correct in-force term for a set of dated probes, including one probe seconds before and after a term instant.

## §5 - Verification

- `tests/tietkhi_oracle.rs` loads `fixtures/tietkhi_sxwnl_1900_2100.csv` (generated once from sxwnl and committed) and asserts every computed instant is within 60s. This is the RISK-1 gate; it MUST run in CI.
- Property test: for 10,000 random instants, `kinh_do_mat_troi` is continuous and monotonic modulo wrap; the inverse solve round-trips (solve(long) then longitude(instant) == long within tolerance).
- A second independent cross-check against tyme4py term instants (a different implementation lineage) over one decade, to catch a shared-bug-in-one-library case.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-lichphap -- -D warnings`, `cargo test -p cyberos-lichphap`.

## §6 - Implementation skeleton

1. Create the `cyberos-lichphap` crate (this FR owns its birth; FR-CORE-002/003/004 add modules to it).
2. `solar.rs`: `kinh_do_mat_troi`, the Meeus mean-longitude/anomaly/center terms.
3. `delta_t.rs`: the piecewise Espenak-Meeus set with the 2005-2050 fast path.
4. `tietkhi.rs`: the inverse solver, the 24-term table with han names and kinds, `tiet_khi_in_year`, `tiet_khi_hien_hanh`.
5. Generate the sxwnl fixture once (script under `crates/cyberos-lichphap/scripts/gen_fixture.py`, documented, not run in CI) and commit the CSV.
6. Wire the oracle test and the property test.

## §7 - Dependencies

Depends on FR-PLAT-001 (cargo workspace). Blocks FR-CORE-002 (true solar time reuses the equation-of-center terms), FR-CORE-003 (month pillar needs jie boundaries), FR-CORE-005 (module output), and FR-QMDG-001 (dinh cuc keys off the current term + tam nguyen).

## §8 - Example payloads

```
tiet_khi_hien_hanh(2004-01-01T03:30:00Z, default_flags) ->
  { name: "Dong Chi", han: "冬至", longitude_deg: 270, kind: TrungKhi,
    instant: 2003-12-22T08:04:00Z }
```

## §9 - Open questions

- Do we ever need VSOP87 in production, or only as an oracle? Default: Meeus low-order in production, VSOP87 only in the FR-CORE-006 cross-check. Decide from the boundary-case count the oracle harness reports.
- Tam nguyen (thuong/trung/ha) assignment belongs partly here and partly in QMDG-001. Decision: this FR returns the raw term + instant; the thuong/trung/ha nguyen for QiMen dinh cuc is computed in QMDG-001 from the phu dau, since it is QiMen-specific. Cross-check this boundary when QMDG-001 lands.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Delta-T wrong sign | TT/UT confusion | oracle gate fails (instants off by ~1-2 min); do not ship |
| Inverse solve non-convergence | seed too far / wrap mishandled | cap iterations, assert residual < 1s, return typed error if not met |
| Wrong jie/trung kind | off-by-one in the 24-term table | enumerated unit test fails |
| Year boundary term | term near Jan 1 attributed to wrong year | explicit test at Tieu Han / Dai Han near year edge |
| Library shared bug | sxwnl and our code share a Meeus rounding | second oracle (tyme4py) diverges -> investigate |

## §11 - Notes

This is the highest-risk FR in the project (RISK-1). Treat the oracle gate as non-negotiable: a term off by more than 60 seconds is a stop-ship. The crate name `cyberos-lichphap` is shared with FR-CORE-002/003/004/005 - they extend this crate rather than create new ones, so the calendar core is one testable unit.
