//! COV-001 — jieqi / tiet khi certification: ≥50 terms, |error| < 60s vs fixture.

use cyberos_lichphap::{solve_term_instant, term_def};
use std::fs;
use std::path::PathBuf;

#[test]
fn tietkhi_multiyear_cert_min_50_within_60s() {
    let path =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/tietkhi_cert_multiyear.csv");
    let text = fs::read_to_string(&path).expect("tietkhi_cert_multiyear.csv");
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
            err_sec < 60.0,
            "year={year} term={idx}: err={err_sec}s exceeds 60s gate"
        );
        if err_sec > max_err {
            max_err = err_sec;
        }
        rows += 1;
    }
    assert!(
        rows >= 50,
        "COV-001 requires ≥50 tiet-khi terms, got {rows}"
    );
    // touch max_err so report readers can log it if --nocapture
    eprintln!("tietkhi_cert rows={rows} max_err_s={max_err:.6}");
}
