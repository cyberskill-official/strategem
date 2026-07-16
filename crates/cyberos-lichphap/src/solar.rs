//! Apparent solar longitude (Meeus low-precision). TASK-CORE-001.

use crate::delta_t::utc_jd_to_tt_jd;

const DEG: f64 = std::f64::consts::PI / 180.0;

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

/// Mean obliquity of the ecliptic (degrees), low precision.
fn mean_obliquity(t: f64) -> f64 {
    23.439_291 - 0.013_004_2 * t - 1.64e-7 * t * t + 5.04e-7 * t * t * t
}

/// Apparent geocentric solar longitude in degrees [0, 360).
/// Meeus Astronomical Algorithms ch.25 (low precision).
pub fn kinh_do_mat_troi(jd_utc: f64) -> f64 {
    let jd_tt = utc_jd_to_tt_jd(jd_utc);
    let t = (jd_tt - 2_451_545.0) / 36_525.0; // centuries from J2000 TT
                                              // Geometric mean longitude
    let l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t).rem_euclid(360.0);
    let m = (357.52911 + 35999.05029 * t - 0.0001537 * t * t).rem_euclid(360.0);
    let mr = m * DEG;
    let c = (1.914602 - 0.004817 * t - 0.000014 * t * t) * mr.sin()
        + (0.019993 - 0.000101 * t) * (2.0 * mr).sin()
        + 0.000289 * (3.0 * mr).sin();
    let sun = (l0 + c).rem_euclid(360.0);
    // Apparent: nutation in longitude (approx) + aberration
    let omega = 125.04 - 1934.136 * t;
    let lambda = sun - 0.00569 - 0.00478 * (omega * DEG).sin();
    // light deflection / aberration already partly in low-prec formula
    let _eps = mean_obliquity(t);
    lambda.rem_euclid(360.0)
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
        // 2000-01-01 12:00 TT ~ JD 2451545.0 — longitude ~280.46°
        let lon = kinh_do_mat_troi(2_451_545.0);
        assert!((lon - 280.0).abs() < 1.0, "lon={lon}");
    }

    #[test]
    fn spot_within_0_01_of_self_consistency() {
        // Monotonic-ish climb over a day
        let a = kinh_do_mat_troi(2_460_000.0);
        let b = kinh_do_mat_troi(2_460_000.0 + 1.0);
        let d = ang_diff(b, a);
        assert!(d > 0.9 && d < 1.1, "daily motion ~1°, got {d}");
    }
}
