//! FR-CORE-001 oracle-style tests. Fixture holds self-consistent reference
//! instants (generated from the same theory at high precision) — sxwnl external
//! cross-check is FR-CORE-006; here we enforce <60s stability and 0.01° longitude.

use cyberos_lichphap::{
    ang_diff, julian_day_utc, kinh_do_mat_troi, solve_term_instant, term_def, tiet_khi_hien_hanh,
    tiet_khi_year, TermKind,
};
use std::fs;
use std::path::PathBuf;

#[test]
fn longitude_spot_checks_1900_2100() {
    // Spot JD samples: ensure solar theory is finite and smooth
    for year in [1900, 1950, 2000, 2050, 2100] {
        let jd = julian_day_utc(year, 6, 21.5);
        let lon = kinh_do_mat_troi(jd);
        assert!((0.0..360.0).contains(&lon), "year={year} lon={lon}");
        // Near June solstice ~90°
        if year == 2000 {
            assert!(ang_diff(lon, 90.0).abs() < 1.5, "ha chi approx lon={lon}");
        }
    }
}

#[test]
fn terms_match_fixture_within_60s() {
    let path =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/tietkhi_ref_2020.csv");
    let text = fs::read_to_string(&path).expect("fixture");
    for line in text
        .lines()
        .filter(|l| !l.starts_with('#') && !l.trim().is_empty())
    {
        let mut parts = line.split(',');
        let idx: u8 = parts.next().unwrap().parse().unwrap();
        let ref_jd: f64 = parts.next().unwrap().parse().unwrap();
        let target = term_def(idx).target_longitude;
        let got = solve_term_instant(target, ref_jd);
        let err_sec = (got - ref_jd).abs() * 86400.0;
        assert!(
            err_sec < 60.0,
            "term {idx}: err={err_sec}s got={got} ref={ref_jd}"
        );
        let lon = kinh_do_mat_troi(got);
        assert!(ang_diff(lon, target).abs() < 0.01, "term {idx} lon err");
    }
}

#[test]
fn all_kinds_enumerated() {
    let mut jie = 0;
    let mut trung = 0;
    for i in 0u8..24 {
        match term_def(i).kind {
            TermKind::Jie => jie += 1,
            TermKind::TrungKhi => trung += 1,
        }
    }
    assert_eq!(jie, 12);
    assert_eq!(trung, 12);
}

#[test]
fn midnight_boundary_stable() {
    // Force a solve near a day boundary
    let guess = julian_day_utc(2020, 12, 21.0) + 0.001; // near midnight UTC
    let inst = solve_term_instant(270.0, guess);
    let lon1 = kinh_do_mat_troi(inst);
    let lon2 = kinh_do_mat_troi(inst + 1e-9);
    assert!(ang_diff(lon1, 270.0).abs() < 0.01);
    assert!(ang_diff(lon2, lon1).abs() < 1e-6);
}

#[test]
fn year_returns_24_monotonic() {
    let terms = tiet_khi_year(2020);
    assert_eq!(terms.len(), 24);
    for w in terms.windows(2) {
        assert!(w[1] > w[0], "terms must increase");
    }
    let mid = (terms[10] + terms[11]) / 2.0;
    let cur = tiet_khi_hien_hanh(mid);
    assert_eq!(cur.index, 10);
}

/// Generate reference CSV once (kept as committed fixture for CI).
#[test]
fn fixture_exists_and_has_24_rows() {
    let path =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/tietkhi_ref_2020.csv");
    let n = fs::read_to_string(path)
        .unwrap()
        .lines()
        .filter(|l| !l.starts_with('#') && !l.trim().is_empty())
        .count();
    assert_eq!(n, 24);
}
