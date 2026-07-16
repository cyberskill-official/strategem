# CORE - calendar and ganzhi core

The shared lich phap (calendar and astronomy) core that all three Tam Thuc engines stand on: 24 tiet khi from solar longitude, true solar time, the four pillars, the derived states, one JSON output, and the oracle harness that gates the lot. 7 tasks, ~90 engineering-hours, all P0. Source of rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (sections 4.3, 4.4, RISK-1) and `../../Claude/Markdown/Tam-Thuc-05-Nen-tang-dung-chung.md`.

## task list

| task | Pri | Phase | h | Title |
|---|---|---|--:|---|
| [CORE-001](TASK-CORE-001-solar-longitude-tiet-khi/spec.md) | MUST | P0 | 20 | Solar longitude + 24 tiet khi (Meeus, inverse solve, delta-T) |
| [CORE-002](TASK-CORE-002-true-solar-time/spec.md) | MUST | P0 | 12 | True solar time (equation of time + longitude correction + flags) |
| [CORE-003](TASK-CORE-003-four-pillars/spec.md) | MUST | P0 | 16 | Four pillars (Ngu Ho / Ngu Thu don, Julian-day, zi-hour flags) |
| [CORE-004](TASK-CORE-004-derived-states/spec.md) | MUST | P0 | 10 | Derived states (tuan khong, vuong-suy, truong sinh, school flag) |
| [CORE-005](TASK-CORE-005-calendar-module-api/spec.md) | MUST | P0 | 10 | Calendar module API + JSON output + flag set + stamp |
| [CORE-006](TASK-CORE-006-oracle-harness/spec.md) | MUST | P0 | 14 | Oracle cross-check harness (sxwnl + tyme4py, decades, boundary, CI gate) |
| [CORE-007](TASK-CORE-007-ganzhi-primitives/spec.md) | MUST | P0 | 8 | Ganzhi primitives + relations (ngu hanh sinh/khac, chi hinh/xung/pha/hai/hop) |

## Internal build order

```
PLAT-001 -> CORE-001 -> CORE-002 -> CORE-003 -> CORE-004 -> CORE-005 -> CORE-006
PLAT-001 -> CORE-007 (parallel; joined at CORE-003 integration)
```

CORE-001 is the astronomy root and owns the crate's birth; CORE-002/003/004 add modules to it; CORE-005 assembles them into the public `lich_phap` object; CORE-006 is the cross-check gate over the whole thing. CORE-007 is dependency-light and can be built alongside the astronomy chain, then wired in where the pillars and derived states need `Can`/`Chi` and the phase relations.

## Cross-module dependencies

- Depends on: TASK-PLAT-001 (the cargo + uv + Next.js workspace). CORE-001 and CORE-007 root here; everything else in the module chains off CORE-001.
- Fills a contract slot: TASK-CORE-005's output IS the `lich_phap` sub-object of the la so JSON envelope (TASK-PLAT-002). The two are one contract seen from two sides - PLAT-002 fixes the slot and the version / stamp / cache-key rules, CORE-005 fills it and owns the `LichFlags` set. Keep their `lich_phap` fixtures byte-identical.
- Blocks every engine: TASK-QMDG-001, TASK-LN-001, TASK-TAT-001 each read the calendar object as their first input (via CORE-005), and TASK-QMDG-006 / TASK-LN-006 / TASK-TAT-006 reuse the CORE-006 oracle harness as the calendar half of their own oracle gate. TASK-API-001 resolves the calendar context here. The relation-consuming engine slices (QMDG-005, LN-002, TAT-003) build on CORE-007.

## Module notes

- The crate is `cyberos-lichphap`. All seven tasks live in and extend this one crate - CORE-002..007 add modules (`truesolar.rs`, `pillars.rs`, `derived.rs`, `api.rs`, `ganzhi.rs`, ...) rather than spawning new crates, so the calendar core is a single testable unit.
- All school and precision differences are flags, never hardcoded: `use_true_solar_time`, `longitude`, `zi_hour_day_rollover`, `late_zi_handling`, `truong_sinh_phai`, `delta_t_model`. Every one is stamped into `lich_phap.co_lich_phap` on every cast, so a chart's calendar layer is fully reproducible from `dau_vao` plus the stamp alone (strategy 4.4, RISK-2).
- The oracle libraries sxwnl and tyme4py are CI test references, not embedded runtime dependencies (strategy RISK-6). They generate committed fixtures via a documented, human-run script; they never enter the build or the shipped artifact.
- This is the highest-test-density module in the project. Because all three engines stand on it, one error here propagates to all three at once (strategy RISK-1), so CORE-006 is a non-negotiable, required CI gate: a tiet khi off by more than 60 seconds, or any pillar mismatch, is a stop-ship.
- One catalog reconciliation to note: CORE-003 depends on both CORE-001 (jie boundaries) and CORE-002 (true-solar hour for the hour pillar); the master catalog currently lists CORE-001 only. CORE-007's soft edges into QMDG-005 / LN-002 / TAT-003 are likewise real but not yet hard-wired in the catalog. See each task's §7.
