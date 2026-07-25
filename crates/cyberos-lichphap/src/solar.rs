//! Apparent solar longitude — VSOP87D Earth L + Meeus apparent reduction.
//! TASK-CORE-001 / W3.
//!
//! Honest accuracy note:
//! - Heliocentric Earth longitude comes from the `vsop87` crate's **VSOP87D**
//!   solution (full series as published in that crate).
//! - Conversion to **apparent** geocentric solar longitude uses Meeus-class
//!   aberration + IAU-1980-leading nutation — not a second independent ephemeris.
//! - This is **not** an sxwnl certification path and does **not** by itself
//!   claim "VSOP-certified jieqi". The tập-5 **&lt;1 minute** audit gates against
//!   published equinox/solstice UTC fixtures; multi-decade sxwnl dumps:
//!   `oracle/sxwnl/full/` (W4 harness).

use crate::delta_t::utc_jd_to_tt_jd;
use vsop87::vsop87d;

const DEG: f64 = std::f64::consts::PI / 180.0;
const ARCSEC: f64 = DEG / 3600.0;

/// Julian Day from UTC Gregorian (Meeus).
pub fn julian_day_utc(year: i32, month: u32, day: f64) -> f64 {
    let mut y = year;
    let mut m = month as i32;
    if m <= 2 {
        y -= 1;
        m += 12;
    }
    let a = (y as f64 / 100.0).floor();
    let b = 2.0 - a + (a / 4.0).floor();
    ((365.25 * (y as f64 + 4716.0)).floor()) + ((30.6001 * (m as f64 + 1.0)).floor()) + day + b
        - 1524.5
}

/// Mean obliquity of the ecliptic (degrees).
fn mean_obliquity(t: f64) -> f64 {
    23.439_291_111 - 0.013_004_166 * t - 1.64e-7 * t * t + 5.04e-7 * t * t * t
}

/// Nutation in longitude (degrees), IAU 1980 leading terms (Meeus ch.22 style).
fn nutation_longitude_deg(t: f64) -> f64 {
    let omega = (125.044_52 - 1_934.136_261 * t) * DEG;
    let l = (280.4665 + 36_000.769_8 * t) * DEG;
    let lp = (218.3165 + 481_267.881_3 * t) * DEG;
    (-17.20 * omega.sin() - 1.32 * (2.0 * l).sin()
        + 0.23 * (2.0 * lp).sin()
        + 0.21 * (2.0 * omega).sin())
        * ARCSEC
        / DEG
}

/// Apparent geocentric solar longitude in degrees [0, 360).
pub fn kinh_do_mat_troi(jd_utc: f64) -> f64 {
    let jd_tt = utc_jd_to_tt_jd(jd_utc);
    let t = (jd_tt - 2_451_545.0) / 36_525.0;

    // VSOP87D Earth heliocentric ecliptic longitude (radians, equinox of date).
    let earth = vsop87d::earth(jd_tt);
    // Geocentric Sun = Earth + 180°
    let mut sun = (earth.longitude() + std::f64::consts::PI)
        .rem_euclid(std::f64::consts::TAU)
        .to_degrees();

    // Aberration (Meeus): ~20.4898″; use constant form adequate for <1 min jieqi.
    sun -= 20.489_8 / 3600.0;

    // Nutation in longitude → apparent
    sun += nutation_longitude_deg(t);

    let _eps = mean_obliquity(t);
    sun.rem_euclid(360.0)
}

/// Normalize angle difference to [-180, 180].
pub fn ang_diff(a: f64, b: f64) -> f64 {
    let mut d = (a - b).rem_euclid(360.0);
    if d > 180.0 {
        d -= 360.0;
    }
    d
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn j2000_near_280() {
        let lon = kinh_do_mat_troi(2_451_545.0);
        assert!((lon - 280.0).abs() < 1.5, "lon={lon}");
    }

    #[test]
    fn spot_daily_motion() {
        let a = kinh_do_mat_troi(2_460_000.0);
        let b = kinh_do_mat_troi(2_460_000.0 + 1.0);
        let d = ang_diff(b, a);
        assert!(d > 0.9 && d < 1.1, "daily motion ~1°, got {d}");
    }

    #[test]
    fn honesty_contract_finite() {
        let lon = kinh_do_mat_troi(julian_day_utc(2020, 3, 20.16));
        assert!((0.0..360.0).contains(&lon));
    }
}
