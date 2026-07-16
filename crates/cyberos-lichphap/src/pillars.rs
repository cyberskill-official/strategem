//! Four pillars (tứ trụ). TASK-CORE-003.

use crate::don_tables::{advance_can, ngu_ho_don_first_month_can, ngu_thu_don_zi_can};
use crate::ganzhi::{can_chi_of, giap_ty_from_can_chi, Can, Chi, GiapTy};
use crate::solar::julian_day_utc;
use crate::tietkhi::{solve_term_instant, target_longitude};
use crate::truesolar::true_solar_time;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Pillar {
    pub can: Can,
    pub chi: Chi,
}

impl Pillar {
    pub fn glyph(self) -> String {
        format!("{}{}", self.can.glyph(), self.chi.glyph())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LateZiHandling {
    /// 23:00–00:59 uses next calendar day's day pillar.
    NextDay,
    /// Keep old day pillar; hour stem from next-day rule (da_zi).
    DaZi,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FourPillars {
    pub year: Pillar,
    pub month: Pillar,
    pub day: Pillar,
    pub hour: Pillar,
    pub zi_hour_day_rollover: String,
    pub late_zi_handling: LateZiHandling,
}

/// Sexagenary day index: JD at local noon, anchored so 1949-10-01 -> 甲子 (and thus 2000-01-01 -> 戊午).
pub fn day_pillar(year: i32, month: u32, day: u32) -> Pillar {
    let jd = julian_day_utc(year, month, day as f64 + 0.5);
    let jd_jiazi = julian_day_utc(1949, 10, 1.5); // 甲子
    let idx = ((jd - jd_jiazi).round() as i64).rem_euclid(60) as u8;
    let g = GiapTy::new(idx).unwrap();
    let (c, z) = can_chi_of(g);
    Pillar { can: c, chi: z }
}

/// Year pillar at Lap Xuan (315°), not Jan 1.
pub fn year_pillar(year: i32, month: u32, day: u32) -> Pillar {
    // Lap Xuan of `year` (index 0)
    let lap = solve_term_instant(target_longitude(0), julian_day_utc(year, 2, 4.0));
    let jd = julian_day_utc(year, month, day as f64 + 0.5);
    let sexagenary_year = if jd < lap { year - 1 } else { year };
    // 1984 is 甲子
    let idx = (sexagenary_year - 1984).rem_euclid(60) as u8;
    let g = GiapTy::new(idx).unwrap();
    let (c, z) = can_chi_of(g);
    Pillar { can: c, chi: z }
}

/// Month pillar: jie boundary, Ngu Ho Don.
pub fn month_pillar(year: i32, month: u32, day: u32) -> Pillar {
    let yp = year_pillar(year, month, day);
    // Month branch: 寅=1 after Lap Xuan ... find which jie interval
    let jd = julian_day_utc(year, month, day as f64 + 0.5);
    // jie indices even: 0 Lap xuan, 2 kinh trap, ... map to month branch starting at Dan=寅
    let mut month_index: i32 = 0; // 0 = 寅
    for i in 0u8..12 {
        let jie_idx = i * 2; // even term indices for jie
        let y = if jie_idx == 0 {
            // Lap xuan of current year pillar year
            if jd < solve_term_instant(target_longitude(0), julian_day_utc(year, 2, 4.0)) {
                year - 1
            } else {
                year
            }
        } else {
            year
        };
        let inst = solve_term_instant(
            target_longitude(jie_idx),
            julian_day_utc(y, 2, 4.0) + (jie_idx as f64) * (365.2422 / 24.0),
        );
        if jd >= inst {
            month_index = i as i32;
        }
    }
    // Chi: 寅 + month_index
    let chi = Chi::from_index(((Chi::Dan.index() as i32 + month_index) % 12) as u8).unwrap();
    let first = ngu_ho_don_first_month_can(yp.can);
    let can = advance_can(first, month_index);
    Pillar { can, chi }
}

/// Hour pillar from true solar hour chi + Ngu Thu Don.
pub fn hour_pillar(
    day: Pillar,
    true_hour: u32,
    late_zi: LateZiHandling,
) -> (Pillar, Pillar /*effective day*/) {
    // chi from double-hour: 23-01=子, 01-03=丑, ...
    let chi_index = ((true_hour + 1) % 24) / 2;
    let chi = Chi::from_index(chi_index as u8).unwrap();
    let mut effective_day = day;
    if chi == Chi::Ty && true_hour >= 23 {
        match late_zi {
            LateZiHandling::NextDay => {
                // next day pillar: advance giap ty by 1
                let g = giap_ty_from_can_chi(day.can, day.chi).unwrap();
                let next = GiapTy::new((g.index() + 1) % 60).unwrap();
                let (c, z) = can_chi_of(next);
                effective_day = Pillar { can: c, chi: z };
            }
            LateZiHandling::DaZi => {
                // keep day; hour stem uses next day for table base
                let g = giap_ty_from_can_chi(day.can, day.chi).unwrap();
                let next = GiapTy::new((g.index() + 1) % 60).unwrap();
                let (c, _) = can_chi_of(next);
                let zi_can = ngu_thu_don_zi_can(c);
                let hour_can = advance_can(zi_can, chi_index as i32);
                return (Pillar { can: hour_can, chi }, day);
            }
        }
    }
    let zi_can = ngu_thu_don_zi_can(effective_day.can);
    let hour_can = advance_can(zi_can, chi_index as i32);
    (Pillar { can: hour_can, chi }, effective_day)
}

#[allow(clippy::too_many_arguments)]
pub fn compute_pillars(
    year: i32,
    month: u32,
    day: u32,
    hour: u32,
    minute: u32,
    second: u32,
    tz_offset_hours: f64,
    longitude_east: f64,
    use_true_solar: bool,
    late_zi: LateZiHandling,
) -> FourPillars {
    let ts = true_solar_time(
        year,
        month,
        day,
        hour,
        minute,
        second,
        tz_offset_hours,
        longitude_east,
        use_true_solar,
    );
    let y = year_pillar(year, month, day);
    let m = month_pillar(year, month, day);
    let d0 = day_pillar(year, month, day);
    let (h, d) = hour_pillar(d0, ts.gio_that_hour, late_zi);
    FourPillars {
        year: y,
        month: m,
        day: d,
        hour: h,
        zi_hour_day_rollover: "23:00".into(),
        late_zi_handling: late_zi,
    }
}
