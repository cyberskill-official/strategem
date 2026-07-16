//! ΔT ≈ TT − UT1 (seconds). TASK-CORE-001 uses this for TT↔UTC direction.

/// Polynomial approximation (Espenak/Meeus-style) for years 1900–2100.
/// Returns ΔT in seconds. Positive: TT is ahead of UT.
pub fn delta_t_seconds(year: f64) -> f64 {
    // Simplified Espenak table fit for modern era (adequate for <60s term gate).
    let t = (year - 2000.0) / 100.0;
    if (1900.0..1920.0).contains(&year) {
        let u = year - 1900.0;
        return -2.79 + 1.494_119 * u - 0.059_893_9 * u.powi(2) + 0.006_196_6 * u.powi(3)
            - 0.000_197 * u.powi(4);
    }
    if (1920.0..1941.0).contains(&year) {
        let u = year - 1920.0;
        return 21.20 + 0.84493 * u - 0.076_100 * u.powi(2) + 0.002_093_6 * u.powi(3);
    }
    if (1941.0..1961.0).contains(&year) {
        let u = year - 1950.0;
        return 29.07 + 0.407 * u - u.powi(2) / 233.0 + u.powi(3) / 2547.0;
    }
    if (1961.0..1986.0).contains(&year) {
        let u = year - 1975.0;
        return 45.45 + 1.067 * u - u.powi(2) / 260.0 - u.powi(3) / 718.0;
    }
    if (1986.0..2005.0).contains(&year) {
        let u = year - 2000.0;
        return 63.86 + 0.3345 * u - 0.060_374 * u.powi(2)
            + 0.001_727_5 * u.powi(3)
            + 0.000_651_814 * u.powi(4)
            + 0.000_023_735_99 * u.powi(5);
    }
    // 2005–2100
    62.92 + 0.32217 * t * 100.0 + 0.005589 * (t * 100.0).powi(2)
}

/// Convert Terrestrial Time JD to approximate UTC JD by subtracting ΔT.
pub fn tt_jd_to_utc_jd(jd_tt: f64) -> f64 {
    let year = jd_to_year(jd_tt);
    let dt = delta_t_seconds(year);
    jd_tt - dt / 86400.0
}

/// Convert UTC JD to TT JD by adding ΔT.
pub fn utc_jd_to_tt_jd(jd_utc: f64) -> f64 {
    let year = jd_to_year(jd_utc);
    let dt = delta_t_seconds(year);
    jd_utc + dt / 86400.0
}

fn jd_to_year(jd: f64) -> f64 {
    // Approximate Gregorian year from JD
    let a = jd + 0.5;
    let z = a.floor();
    let f = a - z;
    let alpha = ((z - 1_867_216.25) / 36_524.25).floor();
    let a2 = z + 1.0 + alpha - (alpha / 4.0).floor();
    let b = a2 + 1524.0;
    let c = ((b - 122.1) / 365.25).floor();
    let d = (365.25 * c).floor();
    let e = ((b - d) / 30.6001).floor();
    let day = b - d - (30.6001 * e).floor() + f;
    let month = if e < 14.0 { e - 1.0 } else { e - 13.0 };
    let year = if month > 2.0 { c - 4716.0 } else { c - 4715.0 };
    year + (month - 1.0) / 12.0 + day / 365.25
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn delta_t_positive_modern() {
        let dt = delta_t_seconds(2020.0);
        assert!(dt > 60.0 && dt < 120.0, "ΔT 2020 ~70s, got {dt}");
    }

    #[test]
    fn tt_utc_round_direction() {
        let jd_utc = 2_459_945.5; // ~2022-11-27
        let jd_tt = utc_jd_to_tt_jd(jd_utc);
        assert!(jd_tt > jd_utc, "TT must be ahead of UTC");
        let back = tt_jd_to_utc_jd(jd_tt);
        assert!((back - jd_utc).abs() < 1e-9);
    }
}
