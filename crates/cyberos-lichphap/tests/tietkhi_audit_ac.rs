//! W3 / tập-5 AC — jieqi quantitative audit: |engine − published| < 1 minute.
//!
//! Fixture `tietkhi_audit_ac.csv` holds published equinox/solstice UTC instants
//! (USNO/almanac class), **independent** of this engine. This is the tập-5
//! acceptance band (&lt;1 minute). It is **not** an sxwnl dump and does **not**
//! certify full VSOP87; heliocentric L is VSOP87D via the `vsop87` crate with
//! Meeus-class apparent reduction (see `solar.rs` honesty note).

use cyberos_lichphap::{ang_diff, kinh_do_mat_troi, solve_term_instant, term_def};
use std::fs;
use std::path::PathBuf;

const MAX_ERR_SEC: f64 = 60.0;

fn fixture_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/tietkhi_audit_ac.csv")
}

#[test]
fn jieqi_under_one_minute_vs_published_almanac() {
    let text = fs::read_to_string(fixture_path()).expect("tietkhi_audit_ac.csv");
    let mut rows = 0usize;
    let mut max_err = 0.0f64;
    for line in text
        .lines()
        .filter(|l| !l.starts_with('#') && !l.trim().is_empty())
    {
        let mut parts = line.split(',');
        let year: i32 = parts.next().unwrap().parse().unwrap();
        let idx: u8 = parts.next().unwrap().parse().unwrap();
        let ref_jd: f64 = parts.next().unwrap().parse().unwrap();
        let target = term_def(idx).target_longitude;
        let got = solve_term_instant(target, ref_jd);
        let err_sec = (got - ref_jd).abs() * 86400.0;
        assert!(
            err_sec < MAX_ERR_SEC,
            "tập-5 AC fail: year={year} term={idx}: err={err_sec:.2}s exceeds {MAX_ERR_SEC}s vs published"
        );
        let lon = kinh_do_mat_troi(got);
        assert!(
            ang_diff(lon, target).abs() < 0.01,
            "year={year} term={idx}: longitude residual too large"
        );
        if err_sec > max_err {
            max_err = err_sec;
        }
        rows += 1;
    }
    assert!(
        rows >= 16,
        "audit fixture should cover ≥16 equinox/solstice samples, got {rows}"
    );
    eprintln!("tietkhi_audit_ac rows={rows} max_err_s={max_err:.3} (gate <{MAX_ERR_SEC}s)");
}

#[test]
fn audit_fixture_exists() {
    let n = fs::read_to_string(fixture_path())
        .unwrap()
        .lines()
        .filter(|l| !l.starts_with('#') && !l.trim().is_empty())
        .count();
    assert!(n >= 16);
}
