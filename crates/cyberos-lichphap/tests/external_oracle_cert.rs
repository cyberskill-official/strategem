//! W4 external oracle certification — lichpháp / sxwnl.
//!
//! - `sample/` rows always run (published USNO/almanac equinox–solstice pins).
//! - `full/` multi-decade sxwnl 24×N dump gates when present; otherwise SKIP.

use cyberos_lichphap::{ang_diff, kinh_do_mat_troi, solve_term_instant, term_def};
use cyberos_oracle_cert::{
    csv_rows, dataset_path, load_csv, require_sample, DatasetKind, LoadOutcome,
};

const MAX_ERR_SEC: f64 = 60.0;

fn assert_tietkhi_rows(text: &str, label: &str) {
    let rows = csv_rows(text);
    assert!(!rows.is_empty(), "{label}: expected at least one data row");
    let mut max_err = 0.0f64;
    for (line_no, cols) in rows {
        assert!(
            cols.len() >= 3,
            "{label} line {line_no}: need ≥3 cols, got {}",
            cols.len()
        );
        let _year: i32 = cols[0]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: year"));
        let idx: u8 = cols[1]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: term_index"));
        let ref_jd: f64 = cols[2]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: jd_utc"));
        let target = term_def(idx).target_longitude;
        let got = solve_term_instant(target, ref_jd);
        let err_sec = (got - ref_jd).abs() * 86400.0;
        assert!(
            err_sec < MAX_ERR_SEC,
            "{label} line {line_no}: err={err_sec:.2}s exceeds {MAX_ERR_SEC}s"
        );
        let lon = kinh_do_mat_troi(got);
        assert!(
            ang_diff(lon, target).abs() < 0.01,
            "{label} line {line_no}: longitude residual too large"
        );
        if err_sec > max_err {
            max_err = err_sec;
        }
    }
    eprintln!("{label}: max_err_s={max_err:.3} (gate <{MAX_ERR_SEC}s)");
}

#[test]
fn sxwnl_sample_harness_matches_published_almanac() {
    let (_path, text) = require_sample("sxwnl", "tietkhi.csv");
    assert_tietkhi_rows(&text, "sxwnl sample");
}

#[test]
fn sxwnl_full_dump_gates_or_skips_honestly() {
    let path = dataset_path("sxwnl", DatasetKind::Full, "tietkhi.csv");
    match load_csv(&path, "sxwnl full") {
        LoadOutcome::Absent { message, .. } => {
            eprintln!("{message}");
        }
        LoadOutcome::Ready {
            text, row_count, ..
        } => {
            assert_tietkhi_rows(&text, "sxwnl full");
            eprintln!("sxwnl full certification: {row_count} rows matched 100%");
        }
    }
}
