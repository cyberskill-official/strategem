use cyberos_lichphap::{
    eot_at_date, equation_of_time_minutes, julian_day_utc, longitude_correction_minutes,
    standard_meridian_from_utc_offset_hours, true_solar_time,
};

#[test]
fn golden_triple_2004_hcmc() {
    // clock 2004-01-01T10:30:00 +07:00, lon 106.7 → corr +6.8, E~-3.5, gio_that 10:33:18
    let r = true_solar_time(2004, 1, 1, 10, 30, 0, 7.0, 106.7, true);
    assert!((r.longitude_correction_min - 6.8).abs() < 0.05);
    assert!(
        (r.eot_min + 3.5).abs() < 0.8,
        "EoT expected ~-3.5 min, got {}",
        r.eot_min
    );
    assert_eq!(r.gio_that_hour, 10);
    // total correction ≈ lon(+6.8) + EoT(~-3.5) ≈ +3.3 min → ~10:33:xx
    assert_eq!(r.gio_that_minute, 33);
    assert!(
        (r.correction_total_min - 3.3).abs() < 1.0,
        "total corr {}",
        r.correction_total_min
    );
    assert!(r.ap_dung);
    // total ≈ lon + E
    assert!((r.correction_total_min - (r.longitude_correction_min + r.eot_min)).abs() < 1e-9);
}

#[test]
fn standard_meridian_not_hardcoded_path() {
    let m = standard_meridian_from_utc_offset_hours(8.0);
    assert!((m - 120.0).abs() < 1e-9);
    let corr = longitude_correction_minutes(121.0, m);
    assert!((corr - 4.0).abs() < 1e-9);
}

#[test]
fn eot_extrema_within_band() {
    // annual extrema magnitudes (not exact published seconds in this low-prec model)
    let feb = eot_at_date(2000, 2, 11.0);
    let nov = eot_at_date(2000, 11, 3.0);
    assert!(feb < -12.0 && feb > -16.0, "feb={feb}");
    assert!(nov > 12.0 && nov < 18.0, "nov={nov}");
}

#[test]
fn sign_east_negative_e_makes_later() {
    let r = true_solar_time(2004, 1, 1, 10, 0, 0, 7.0, 106.7, true);
    // lon corr positive, EoT Jan negative but smaller magnitude → net positive
    assert!(r.correction_total_min > 0.0);
    let clock_sec = 10 * 3600;
    let true_sec =
        r.gio_that_hour as i32 * 3600 + r.gio_that_minute as i32 * 60 + r.gio_that_second as i32;
    assert!(true_sec > clock_sec);
}

#[test]
fn eot_spot_finite() {
    for y in [1900, 1950, 2000, 2050, 2099] {
        let jd = julian_day_utc(y, 6, 21.0);
        let e = equation_of_time_minutes(jd);
        assert!(e.abs() < 20.0, "y={y} e={e}");
    }
}
