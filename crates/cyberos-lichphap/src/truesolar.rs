//! True solar time (EoT + longitude). FR-CORE-002.

use crate::eot::equation_of_time_minutes;
use crate::solar::julian_day_utc;

/// Standard meridian (degrees east) implied by a UTC offset hours.
/// e.g. +07:00 → 105°E.
pub fn standard_meridian_from_utc_offset_hours(offset_hours: f64) -> f64 {
    offset_hours * 15.0
}

/// Longitude correction in minutes: 4 min per degree east of the standard meridian.
pub fn longitude_correction_minutes(longitude_east: f64, standard_meridian_east: f64) -> f64 {
    4.0 * (longitude_east - standard_meridian_east)
}

#[derive(Debug, Clone, PartialEq)]
pub struct TrueSolarResult {
    /// Local civil clock components (for convenience).
    pub year: i32,
    pub month: u32,
    pub day: u32,
    pub hour: u32,
    pub minute: u32,
    pub second: u32,
    pub tz_offset_hours: f64,
    pub longitude_east: f64,
    pub longitude_correction_min: f64,
    pub eot_min: f64,
    pub use_true_solar_time: bool,
    pub ap_dung: bool,
    /// True solar local time (or clock if flag false).
    pub gio_that_hour: u32,
    pub gio_that_minute: u32,
    pub gio_that_second: u32,
    pub correction_total_min: f64,
}

/// Convert clock local time + longitude into true solar time.
/// `tz_offset_hours` is e.g. 7.0 for +07:00.
#[allow(clippy::too_many_arguments)]
pub fn true_solar_time(
    year: i32,
    month: u32,
    day: u32,
    hour: u32,
    minute: u32,
    second: u32,
    tz_offset_hours: f64,
    longitude_east: f64,
    use_true_solar_time: bool,
) -> TrueSolarResult {
    let standard = standard_meridian_from_utc_offset_hours(tz_offset_hours);
    let lon_corr = longitude_correction_minutes(longitude_east, standard);

    // JD of the UTC instant of this civil local clock
    let local_day_frac =
        (hour as f64 + minute as f64 / 60.0 + second as f64 / 3600.0) / 24.0;
    let jd_utc = julian_day_utc(year, month, day as f64 + local_day_frac) - tz_offset_hours / 24.0;
    let eot = equation_of_time_minutes(jd_utc);

    let (ap_dung, total) = if use_true_solar_time {
        (true, lon_corr + eot)
    } else {
        (false, 0.0)
    };

    let (th, tm, ts) = if use_true_solar_time {
        add_minutes(hour, minute, second, total)
    } else {
        (hour, minute, second)
    };

    TrueSolarResult {
        year,
        month,
        day,
        hour,
        minute,
        second,
        tz_offset_hours,
        longitude_east,
        longitude_correction_min: lon_corr,
        eot_min: eot,
        use_true_solar_time,
        ap_dung,
        gio_that_hour: th,
        gio_that_minute: tm,
        gio_that_second: ts,
        correction_total_min: total,
    }
}

fn add_minutes(h: u32, m: u32, s: u32, delta_min: f64) -> (u32, u32, u32) {
    let total_sec = h as f64 * 3600.0 + m as f64 * 60.0 + s as f64 + delta_min * 60.0;
    // wrap within day for unit tests (date rollover not required for golden)
    let mut sec = total_sec.rem_euclid(86400.0);
    let nh = (sec / 3600.0).floor() as u32;
    sec -= nh as f64 * 3600.0;
    let nm = (sec / 60.0).floor() as u32;
    sec -= nm as f64 * 60.0;
    let ns = sec.round() as u32;
    if ns == 60 {
        return (nh, nm + 1, 0);
    }
    (nh, nm, ns)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn meridians_from_offset() {
        assert!((standard_meridian_from_utc_offset_hours(7.0) - 105.0).abs() < 1e-9);
    }

    #[test]
    fn ha_noi_hcmc_lon_corr() {
        let std = 105.0;
        // Ha Noi ~105.85 → +3.4 min
        let hn = longitude_correction_minutes(105.85, std);
        assert!((hn - 3.4).abs() < 0.05, "hn={hn}");
        // HCMC 106.7 → +6.8
        let hcm = longitude_correction_minutes(106.7, std);
        assert!((hcm - 6.8).abs() < 0.05, "hcm={hcm}");
    }

    #[test]
    fn flag_false_passthrough() {
        let r = true_solar_time(2004, 1, 1, 10, 30, 0, 7.0, 106.7, false);
        assert!(!r.ap_dung);
        assert_eq!((r.gio_that_hour, r.gio_that_minute, r.gio_that_second), (10, 30, 0));
    }
}
