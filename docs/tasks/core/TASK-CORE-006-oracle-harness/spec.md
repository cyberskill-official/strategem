---
id: TASK-CORE-006
title: "Oracle cross-check harness - 24 tiet khi vs sxwnl <60s over decades, four pillars vs tyme4py incl. Lap Xuan / midnight / zi-hour boundaries, true-solar and derived-state checks, CI gate (RISK-1)"
module: CORE
priority: MUST
status: done
phase: P0
slice: 1
lang: rust
effort_h: 14
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy RISK-1, strategy RISK-6, Claude-05 s6.2, Claude-06 s5.2]
related_frs: [TASK-CORE-001, TASK-CORE-002, TASK-CORE-003, TASK-CORE-004, TASK-CORE-005]
depends_on: [TASK-CORE-005]
blocks: [TASK-QMDG-006, TASK-LN-006, TASK-TAT-006]
new_paths:
  - crates/cyberos-lichphap/tests/oracle_harness.rs
  - crates/cyberos-lichphap/scripts/gen_oracle_fixtures.py
  - crates/cyberos-lichphap/tests/fixtures/pillars_tyme4py_1900_2100.csv
  - crates/cyberos-lichphap/tests/fixtures/truesolar_handcalc.csv
  - crates/cyberos-lichphap/tests/fixtures/derived_manual.csv
  - .github/workflows/core-oracle.yml
---

## §1 - Description (BCP-14 normative)

This task is the cross-check test harness that is the RISK-1 gate for the whole platform. Because all three engines stand on the calendar core, a single error here shifts QiMen dinh cuc, LiuRen nguyet tuong, and TaiYi thoi ke at once (Claude-05 s1.2, strategy RISK-1). So the calendar core carries the highest test density in the project, and this task is where that density lives: it cross-checks every calendar output against at least two independent reference libraries over decades, including the boundary cases where errors hide.

The harness SHALL cross-check the 24 tiet khi instants against sxwnl to within 60 seconds across a multi-decade span. It SHALL cross-check the four pillars against tyme4py over a long day span that explicitly includes boundary cases: dates around Lap Xuan (the year-pillar turn) and dates around midnight and 23:00 (the zi-hour) for both `zi_hour_day_rollover` and `late_zi_handling` values. It SHALL cross-check true solar time against hand-computed values at the equation-of-time extrema. It SHALL cross-check tuan khong, vuong-suy, and truong sinh against manual tables per school. It SHALL run in CI as a required gate; a tiet khi off by more than 60 seconds, or any pillar mismatch, is a stop-ship.

The reference libraries (sxwnl, tyme4py) SHALL be used as CI test oracles that generate committed fixtures, NOT embedded as runtime dependencies (strategy RISK-6). This harness SHALL be structured so that each engine's assembly task (QMDG-006, LN-006, TAT-006) reuses it as the calendar half of its own oracle gate.

## §2 - Why this design (rationale for humans)

The engines must match reference oracles to the digit (strategy 1, 4.4), and the calendar is where that discipline is cheapest to enforce and most expensive to skip. Two independent libraries are used, not one, because a single library can carry a shared rounding bug: sxwnl (Thọ Tinh Thiên Văn Lịch, using a reduced VSOP87) is the de facto standard for tiet khi, and tyme4py is an independent lineage for the pillars (Claude-05 s1.3). Agreement across both is strong evidence; a divergence between them and our code is a signal to investigate rather than to trust either blindly.

Boundary cases are called out explicitly because that is where a sub-minute error becomes a whole-day error (Claude-05 s6.2). A tiet khi instant seconds from midnight, mis-corrected for delta-T, lands on the wrong calendar day and turns the year or month pillar. A moment at 23:30 under the wrong zi convention lands on the wrong day pillar. These are precisely the inputs a naive test set omits, so the harness generates them on purpose - every Lap Xuan for a century, every midnight and 23:00 crossing for both flags. Keeping the oracles as CI references rather than embedded deps also sidesteps the license risk of vendoring third-party calendar code into a commercial product (strategy RISK-6).

## §3 - Contract (checks and fixtures)

### Check 1 - tiet khi vs sxwnl

For every year in the span (default 1900-2100, CI subset 1950-2050), for all 24 terms: assert `|our_instant - sxwnl_instant| <= 60s`. Fixture: `fixtures/tietkhi_sxwnl_1900_2100.csv` (shared with TASK-CORE-001), columns `year, term_index, sxwnl_utc`.

### Check 2 - four pillars vs tyme4py (with boundary cases)

Over a long day span plus targeted boundary sets, assert each of nam/thang/ngay/gio matches tyme4py. Boundary sets:

```
- Lap Xuan turn:   for each year 1950-2050, probe at LapXuan-2h, LapXuan, LapXuan+2h
- Midnight cross:  for a sample of days, probe at 23:30, 23:59, 00:01, 00:30
- Zi flags:        run the midnight set under {23:00, 00:00} x {tao_zi, da_zi}
```

Fixture: `fixtures/pillars_tyme4py_1900_2100.csv`, columns `utc, tz, longitude, zi_rollover, late_zi, nam, thang, ngay, gio`.

### Check 3 - true solar time vs hand-calc at EoT extrema

At the two annual extrema (~Feb 11, ~Nov 4) and the reference input, assert `gio_that` matches a hand-computed value within a few seconds. Fixture: `fixtures/truesolar_handcalc.csv`, columns `clock, tz, longitude, expected_gio_that, expected_hieu_chinh_phut`.

### Check 4 - derived states vs manual tables, per school

Assert tuan khong, vuong-suy, and truong sinh (both `am_duong` and `ngu_hanh`) match a hand-computed fixture. Fixture: `fixtures/derived_manual.csv`, columns `can, chi, season, truong_sinh_phai, tuan_khong, vuong_suy, truong_sinh`.

### Fixture generation and CI

```
scripts/gen_oracle_fixtures.py    # documented, run once by a human, NOT run in CI
  - emits the four CSVs from sxwnl + tyme4py + hand tables; pins library versions in a header comment
.github/workflows/core-oracle.yml # runs `cargo test -p cyberos-lichphap --test oracle_harness` as a required check
```

The generation script is committed and documented but never runs in CI (CI only reads the committed CSVs), so the third-party libraries never enter the build or the shipped artifact.

### Reuse hook

```rust
pub mod oracle {                          // exported for engine harnesses
    pub fn assert_calendar_matches_oracles(span: Span, flags: &LichFlags) -> OracleReport;
    pub struct OracleReport { pub tietkhi_max_delta_s: f64, pub pillar_mismatches: usize,
                              pub boundary_cases_seen: usize }
}
```

QMDG-006 / LN-006 / TAT-006 call `assert_calendar_matches_oracles` as the calendar half of their own gate and add their engine-specific oracle (kinqimen / kinliuren / kintaiyi) on top.

## §4 - Acceptance criteria

1. All 24 tiet khi match sxwnl within 60 seconds for every year in the CI span; the harness reports the max delta and fails above 60s.
2. Four pillars match tyme4py across the day span and all boundary sets; zero mismatches under every `{zi_rollover} x {late_zi}` combination.
3. True solar time matches the hand-calc fixture at both EoT extrema and the reference input within tolerance.
4. Tuan khong, vuong-suy, and both truong sinh schools match the manual fixture exactly.
5. `OracleReport.boundary_cases_seen` is greater than zero and includes at least the Lap Xuan and 23:00 crossings (proves the boundary sets are actually exercised, not skipped).
6. The CI workflow runs the harness as a required check; the oracle libraries appear only in `gen_oracle_fixtures.py`, never in `Cargo.toml`.

## §5 - Verification

- `tests/oracle_harness.rs` implements the four checks against the committed CSVs and asserts the thresholds; it is the RISK-1 gate and MUST be a required CI check.
- A meta-test asserts the fixtures cover the boundary sets (e.g. at least 100 Lap Xuan probes and 4 zi-flag combinations present), so a thinned fixture fails rather than silently weakening the gate.
- License note in `gen_oracle_fixtures.py` header records the sxwnl and tyme4py versions and licenses used to generate the CSVs (strategy RISK-6 evidence).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-lichphap -- -D warnings`, `cargo test -p cyberos-lichphap` (includes the oracle harness).

## §6 - Implementation skeleton

1. `scripts/gen_oracle_fixtures.py`: pull sxwnl tiet khi and tyme4py pillars over the span and the boundary sets, hand-encode the true-solar and derived fixtures, write the four CSVs with a version/license header. Run once locally; commit the CSVs.
2. `tests/oracle_harness.rs`: load each CSV, run Checks 1-4 against `tinh_lich_phap` (TASK-CORE-005), assert thresholds, build `OracleReport`.
3. Export the `oracle` module with `assert_calendar_matches_oracles` for engine reuse.
4. `.github/workflows/core-oracle.yml`: run the harness on every PR touching `crates/cyberos-lichphap/**` as a required status check.
5. Add the meta-test that guards fixture coverage.

## §7 - Dependencies

Depends on TASK-CORE-005 (the harness runs against the assembled calendar API). Transitively exercises TASK-CORE-001..004. Blocks TASK-QMDG-006, TASK-LN-006, TASK-TAT-006 - each engine's assembly reuses `assert_calendar_matches_oracles` as its calendar-oracle half before layering its own kin* oracle. Relates to TASK-PLAT-004 (CI/CD) for wiring the required check.

## §8 - Example payloads

```
OracleReport { tietkhi_max_delta_s: 41.7, pillar_mismatches: 0, boundary_cases_seen: 312 }
```

A failing run prints the offending row, e.g. `tiet khi mismatch: 2011 term=3 (清明) ours=2011-04-05T03:12:41Z sxwnl=2011-04-05T03:11:20Z delta=81s > 60s`.

## §9 - Open questions

- Is 60 seconds the right tiet khi tolerance, or should boundary-adjacent terms use a tighter bound? Decision: 60s is the ship gate (Claude-05 accuracy target); the harness additionally reports any term within 5 minutes of a day boundary so we can watch whether a tighter bound or the VSOP87 precision path is ever needed (feeds TASK-CORE-001 §9).
- Do we pin exact sxwnl / tyme4py versions in the fixture header, or re-generate per release? Decision: pin versions in the header and re-generate only deliberately; a fixture change is a reviewed event, since it moves the gate.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Shared library bug | sxwnl and our code share a Meeus rounding | tyme4py (independent lineage) diverges -> investigate, do not auto-trust |
| Boundary set thinned | fixture regenerated without boundaries | coverage meta-test fails; `boundary_cases_seen` too low |
| Oracle vendored as dep | sxwnl/tyme4py added to Cargo.toml | license/dep review blocks; oracles are CI-only (RISK-6) |
| Delta-T sign regression | TASK-CORE-001 change flips sign | tiet khi deltas jump ~1-2 min; gate fails |
| Zi combo skipped | only default flags tested | pillar check misses da_zi; matrix over flags required |
| Gate made non-required | CI check downgraded to optional | branch protection MUST keep core-oracle required (RISK-1) |

## §11 - Notes

This is the non-negotiable gate of the project. Treat any red here as a stop-ship, not a flaky test to retry. The whole point of two independent oracles is to catch the case where one library and our code agree on a wrong answer - never resolve a divergence by picking the library that matches us. The harness is deliberately reusable so every engine inherits the calendar oracle rather than re-implementing it. Same crate `cyberos-lichphap` - this task adds the harness, the generation script, the fixtures, and the CI workflow.
