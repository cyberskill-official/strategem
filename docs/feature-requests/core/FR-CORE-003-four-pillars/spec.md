---
id: FR-CORE-003
title: "Four pillars (bon tru can chi / tu tru) - year at Lap Xuan 315deg, month via Ngu Ho Don, day via Julian-day mod 60, hour via Ngu Thu Don, zi_hour_day_rollover + late_zi_handling flags"
module: CORE
priority: MUST
status: reviewing
phase: P0
slice: 1
lang: rust
effort_h: 16
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, strategy RISK-1, Claude-05 s4, Claude-05 s4.1, Claude-05 s4.2, Claude-05 s4.3, Claude-05 s4.4]
related_frs: [FR-CORE-001, FR-CORE-002, FR-CORE-004, FR-CORE-005, FR-CORE-007]
depends_on: [FR-CORE-001, FR-CORE-002]
blocks: [FR-CORE-004, FR-CORE-005]
new_paths:
  - crates/cyberos-lichphap/src/pillars.rs
  - crates/cyberos-lichphap/src/don_tables.rs
  - crates/cyberos-lichphap/tests/pillars_oracle.rs
---

## §1 - Description (BCP-14 normative)

This FR builds bon tru can chi (四柱干支, tu tru) - the year, month, day, and hour pillars, each a thien can paired with a dia chi - the calendar bedrock every engine reads. Each pillar follows a different rule with its own boundary and its own lookup table, and this is the most error-prone part of the calendar core (Claude-05 s4), so each is specified separately and pinned to a test vector.

The module SHALL compute the year pillar with its boundary at Lap Xuan (sun at 315 degrees), NOT at lunar new year and NOT at the Gregorian 1 January. The month pillar chi SHALL be fixed by the twelve jie (from FR-CORE-001), and its can SHALL be derived from the year can by Ngu Ho Don (五虎遁). The day pillar SHALL be a continuous sexagenary count from the Julian day number, unbroken since antiquity. The hour pillar chi SHALL be assigned from the true solar hour (FR-CORE-002), and its can derived from the day can by Ngu Thu Don (五鼠遁).

Two flags that change the result SHALL be honoured and stamped into `co_lich_phap`: `zi_hour_day_rollover` (`23:00` | `00:00`, default `23:00`) fixing when the day pillar advances, and `late_zi_handling` (`tao_zi` | `da_zi`, default `tao_zi`) fixing how the 23:00-24:00 late-Ty hour is treated. The gio Ty spans 23:00-01:00 across midnight, so these two flags MUST be resolved before the day and hour pillars are emitted.

## §2 - Why this design (rationale for humans)

Each pillar answers to a different clock (Claude-05 s4). The year turns on a solar term, so a birth on 2 February is often still in the previous sexagenary year - the single most common lay error is to turn the year at Tet or at 1 January. The month rides the twelve jie, not the mid-terms, so month boundaries land on Lap Xuan, Kinh Trap, and the rest. The day ignores solar terms entirely and simply counts a sixty-cycle that has run without a break for millennia, which is why it is anchored to a Julian day rather than reconstructed from a calendar. The hour is set by the real sun and then its stem is deduced from the day stem.

The zi-hour is the subtle trap. Classical practice starts the new day at 23:00 (Ty so), so 23:30 already belongs to the next day's day pillar; but Bat Tu schools split - the tao Ty school rolls the day at 23:00, while the da Ty school keeps the old day yet takes the hour stem from the next day (Claude-05 s4.4). Half of users reject a chart cast under the other convention (strategy RISK-2), so the platform refuses to hardcode: it exposes both flags and stamps whichever was used, making the chart reproducible and auditable. Getting the boundary right here is load-bearing for every engine that casts by the hour.

## §3 - Contract (algorithm)

### Year pillar (Claude-05 s4.1)

Boundary at Lap Xuan (sun 315 deg), from FR-CORE-001. For a civil year `y`:

```
can_index = (y - 4) mod 10        // 0 = 甲, ... 9 = 癸
chi_index = (y - 4) mod 12        // 0 = 子, ... 11 = 亥
// anchor: 1984 = 甲子 (Giap Ty).  If the instant is before Lap Xuan(y), use (y - 1).
```

### Month pillar (Claude-05 s4.2) - Ngu Ho Don (五虎遁)

The chi is fixed by jie: thang Dan (giêng) begins at Lap Xuan, thang Mao at Kinh Trap, and so on through the twelve jie (thang Dan 寅, Mao 卯, Thin 辰, Ty 巳, Ngo 午, Mui 未, Than 申, Dau 酉, Tuat 戌, Hoi 亥, Ty 子, Suu 丑). Month boundaries follow the jie, never the trung khi. The month can is deduced from the year can by Ngu Ho Don, named because thang Dan holds the tiger.

Ca quyet: Giáp Kỷ chi niên Bính tác thủ, Ất Canh chi tuế Mậu vi đầu, Bính Tân tất định tầm Canh khởi, Đinh Nhâm Nhâm vị thuận hành lưu, Mậu Quý hà phương phát, Giáp Dần chi thượng hảo truy cầu.

| Can nam | Can thang Dan (giêng) |
|---|---|
| 甲 hoac 己 | 丙寅 Bính Dần |
| 乙 hoac 庚 | 戊寅 Mậu Dần |
| 丙 hoac 辛 | 庚寅 Canh Dần |
| 丁 hoac 壬 | 壬寅 Nhâm Dần |
| 戊 hoac 癸 | 甲寅 Giáp Dần |

From the thang Dan stem, later months advance the can by one per jie (thuan hanh) around the sixty cycle.

### Day pillar (Claude-05 s4.3) - continuous Julian-day mod 60

No solar-term boundary; a continuous sixty count. Anchor: Julian day 2451545 (noon 2000-01-01 TT) = 戊午 Mau Ngo. Practical form:

```
index = (JDN - 10) mod 60          // 0 = 甲子 Giap Ty
can_index = index mod 10
chi_index = index mod 12
```

Verification anchors (both MUST pass): 2000-01-01 -> 戊午 (index 55); 1949-10-01 -> 甲子 (index 0). `JDN` is the integer Julian day number of the civil date after the `zi_hour_day_rollover` decision has been applied.

### Hour pillar (Claude-05 s4.4) - Ngu Thu Don (五鼠遁)

Chi from the true solar hour: gio Ty 23:00-01:00, Suu 01:00-03:00, Dan 03:00-05:00, ... Tuat 19:00-21:00, Hoi 21:00-23:00 (twelve two-hour branches; Ty straddles midnight). The hour can is deduced from the day can by Ngu Thu Don, named because gio Ty holds the rat.

Ca quyet: Giáp Kỷ hoàn gia Giáp, Ất Canh Bính tác sơ, Bính Tân tòng Mậu khởi, Đinh Nhâm Canh Tý cư, Mậu Quý hà phương phát, Nhâm Tý thị chân đồ.

| Can ngay | Can gio Ty |
|---|---|
| 甲 hoac 己 | 甲子 Giáp Tý |
| 乙 hoac 庚 | 丙子 Bính Tý |
| 丙 hoac 辛 | 戊子 Mậu Tý |
| 丁 hoac 壬 | 庚子 Canh Tý |
| 戊 hoac 癸 | 壬子 Nhâm Tý |

From the gio Ty stem, later gio advance the can by one per branch (thuan hanh).

### Zi-hour flags (Claude-05 s4.4)

- `zi_hour_day_rollover = 23:00` (default): a moment in 23:00-24:00 already belongs to the next day; the day pillar advances at 23:00 (Ty so). `= 00:00`: the day pillar advances at midnight.
- `late_zi_handling` resolves the 23:00-24:00 late-Ty (da Ty): `tao_zi` (default) rolls the day at 23:00 (so day pillar is the next day, hour stem from that next day). `da_zi` keeps the OLD day's day pillar but takes the hour stem from the next day.

### Public types

```rust
pub struct TruCanChi { pub can: Can, pub chi: Chi }          // Can/Chi from FR-CORE-007
pub struct BonTru { pub nam: TruCanChi, pub thang: TruCanChi, pub ngay: TruCanChi, pub gio: TruCanChi }
pub fn bon_tru(true_solar: DateTime<FixedOffset>, flags: &LichFlags) -> BonTru;
```

## §4 - Acceptance criteria

1. Year pillar turns at Lap Xuan: a probe on 1984-02-03 (before Lap Xuan) is 癸亥 (the prior year), and on 1984-02-05 (after) is 甲子; 1 January and Tet are NOT boundaries.
2. Ngu Ho Don is correct for all five year-can classes; the month can advances by one per jie; the boundary is the jie, not the trung khi.
3. Day pillar passes both anchors: 2000-01-01 -> 戊午 and 1949-10-01 -> 甲子; the count is continuous across month and year ends.
4. Ngu Thu Don is correct for all five day-can classes; the hour chi is taken from `gio_that` (FR-CORE-002), not clock time.
5. Zi-hour: with `zi_hour_day_rollover = 23:00`, a 23:30 probe uses the next day's day pillar; with `da_zi`, the day pillar stays on the old day while the hour stem comes from the next day. Both flag values are exercised and stamped.
6. All can/chi are returned as `FR-CORE-007` `Can`/`Chi` values, serialized to their Han glyph in the envelope (e.g. 甲子).

## §5 - Verification

- `tests/pillars_oracle.rs` cross-checks bon tru against tyme4py over a long day span, including boundary cases: dates around Lap Xuan (each year 1950-2050), dates around midnight and around 23:00 for both zi flags, and the two day-pillar anchors. This feeds the FR-CORE-006 gate.
- Table-driven unit tests enumerate Ngu Ho Don (5 rows) and Ngu Thu Don (5 rows) exhaustively against the tables above.
- Property test: over 100,000 consecutive days the day pillar advances by exactly one sexagenary step per day with no gaps or repeats.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-lichphap -- -D warnings`, `cargo test -p cyberos-lichphap`.

## §6 - Implementation skeleton

1. `don_tables.rs`: the Ngu Ho Don and Ngu Thu Don tables as `const` arrays keyed by year-can / day-can class, plus the sixty-cycle helpers (reuse FR-CORE-007 for can/chi indexing).
2. `pillars.rs`: `year_pillar` (with the Lap Xuan lookback via FR-CORE-001), `month_pillar` (jie index -> chi, Ngu Ho Don -> can), `day_pillar` ((JDN-10) mod 60), `hour_pillar` (gio branch from `gio_that`, Ngu Thu Don -> can).
3. Resolve the two zi flags in one place before day/hour emission; document the tao_zi vs da_zi branch inline with the Claude-05 s4.4 quote.
4. Add the tyme4py fixture (generated once by a documented script, committed as CSV) and the enumerated don-table tests.

## §7 - Dependencies

Depends on FR-CORE-001 (Lap Xuan / jie boundaries for year and month) and FR-CORE-002 (true solar hour for the hour-pillar branch). NOTE: the master catalog lists CORE-003 depends_on CORE-001 only; this FR widens it to include CORE-002 because the hour-pillar chi is assigned from `gio_that`, which does not exist until CORE-002 is done - propose updating the catalog row to match. Uses FR-CORE-007 for `Can`/`Chi` primitives (soft: the two can be built in parallel and joined at integration). Blocks FR-CORE-004 (derived states key off the pillars) and FR-CORE-005 (the `tu_tru` sub-object).

## §8 - Example payloads

```json
{
  "tu_tru": { "nam": "癸未", "thang": "甲子", "ngay": "戊午", "gio": "丁巳" }
}
```

Late-Ty illustration (da_zi): input 2004-01-01T23:30:00 +07:00 keeps 2004-01-01's day pillar for `ngay` but takes the gio Ty stem from 2004-01-02's day can; the same input under tao_zi advances `ngay` to 2004-01-02.

## §9 - Open questions

- Which JDN convention (astronomical noon vs civil midnight) do we lock for the day-pillar count? Decision: use the civil-date integer JDN after the zi rollover; the two anchors (2000-01-01, 1949-10-01) pin it, and the tyme4py cross-check guards it.
- Should `da_zi` also affect the year/month pillars in the rare 23:00-24:00 window at a year boundary? Decision: no - da_zi touches only the day pillar's stem-source and the hour stem; year and month still follow the solar longitude of the actual instant. Confirm against tyme4py boundary cases in FR-CORE-006.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Year turned at Tet / 1 Jan | boundary set to lunar new year or Gregorian | 1984-02-03 vs 02-05 probe fails; must turn at Lap Xuan |
| Month boundary at trung khi | jie/trung confusion | month pillar off by one near a mid-term; enumerated jie test fails |
| Day anchor off by an offset | wrong constant in (JDN - 10) | 2000-01-01 != 戊午 or 1949-10-01 != 甲子; do not ship |
| Hour chi from clock, not sun | FR-CORE-002 not applied first | boundary probe assigns wrong gio; ordering test fails |
| Zi flag ignored | 23:00-24:00 handled one fixed way | tao_zi vs da_zi probes identical -> flag not honoured; fails |
| Flags unstamped | zi flags missing from `co_lich_phap` | FR-CORE-005 reproduction test diverges |

## §11 - Notes

The two don tables and the two ca quyet verses are the classical source of truth - keep them verbatim in `don_tables.rs` comments so a reviewer can check them against a text. The zi-hour logic is the single most contested boundary in the calendar core; treat its tests as non-negotiable, on par with the tiet khi oracle. Same crate `cyberos-lichphap` - this FR adds `pillars.rs` and `don_tables.rs`.
