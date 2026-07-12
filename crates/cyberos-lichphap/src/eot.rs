//! Equation of time (minutes). Meeus low-precision. FR-CORE-002.

use crate::delta_t::utc_jd_to_tt_jd;
use crate::solar::julian_day_utc;

const DEG: f64 = std::f64::consts::PI / 180.0;

/// Equation of time in minutes (true solar − mean solar).
/// Positive: sundial is ahead of the clock.
pub fn equation_of_time_minutes(jd_utc: f64) -> f64 {
    let jd_tt = utc_jd_to_tt_jd(jd_utc);
    let t = (jd_tt - 2_451_545.0) / 36_525.0;
    let l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) * DEG;
    let m = (357.52911 + 35999.05029 * t - 0.0001537 * t * t) * DEG;
    let e = 0.016_708_634 - 0.000_042_037 * t - 0.000_000_126_7 * t * t;
    let eps = (23.439_291 - 0.013_004_2 * t) * DEG;
    let y = (eps / 2.0).tan().powi(2);
    // E in radians
    let e_rad = y * (2.0 * l0).sin() - 2.0 * e * m.sin() + 4.0 * e * y * m.sin() * (2.0 * l0).cos()
        - 0.5 * y * y * (4.0 * l0).sin()
        - 1.25 * e * e * (2.0 * m).sin();
    // to minutes of time
    e_rad * (4.0 * 180.0 / std::f64::consts::PI)
}

/// Spot-check helpers for extrema months (Feb / Nov).
pub fn eot_at_date(year: i32, month: u32, day: f64) -> f64 {
    equation_of_time_minutes(julian_day_utc(year, month, day))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn extrema_signs() {
        let feb = eot_at_date(2020, 2, 11.0);
        let nov = eot_at_date(2020, 11, 4.0);
        assert!(feb < -10.0, "Feb min ~ -14m, got {feb}");
        assert!(nov > 10.0, "Nov max ~ +16m, got {nov}");
    }
}
