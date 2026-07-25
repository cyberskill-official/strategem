//! W4 external oracle certification — QiMen / kinqimen.
//!
//! - `sample/` rows always run (classical textbook pins; harness proof).
//! - `full/` kinqimen dump gates at 100% when present; otherwise SKIP (honest).

use cyberos_oracle_cert::{
    csv_rows, dataset_path, load_csv, require_sample, DatasetKind, LoadOutcome,
};
use cyberos_qimen::{dinh_cuc, DingjuMethod};

fn parse_method(s: &str) -> DingjuMethod {
    match s {
        "zhirun" => DingjuMethod::Zhirun,
        "maoshan" => DingjuMethod::Maoshan,
        _ => DingjuMethod::Chaibu,
    }
}

fn assert_dinh_cuc_rows(text: &str, label: &str) {
    let rows = csv_rows(text);
    assert!(!rows.is_empty(), "{label}: expected at least one data row");
    for (line_no, cols) in rows {
        assert!(
            cols.len() >= 7,
            "{label} line {line_no}: need ≥7 cols, got {}",
            cols.len()
        );
        let term: u8 = cols[0]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: term_index"));
        let branch: u8 = cols[1]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: branch_index"));
        let method = parse_method(cols[2]);
        let tri: u8 = cols[3]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: tri_nhuan"));
        let exp_so: u8 = cols[4]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: so_cuc"));
        let exp_duong: u8 = cols[5]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: duong_don"));
        let exp_nguyen: u8 = cols[6]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: nguyen"));

        let got = dinh_cuc(term, branch, method, tri != 0).unwrap_or_else(|e| {
            panic!("{label} line {line_no}: dinh_cuc failed: {e}");
        });
        assert_eq!(
            got.so_cuc, exp_so,
            "{label} line {line_no}: so_cuc mismatch"
        );
        assert_eq!(
            got.duong_don,
            exp_duong != 0,
            "{label} line {line_no}: duong_don mismatch"
        );
        assert_eq!(
            got.nguyen, exp_nguyen,
            "{label} line {line_no}: nguyen mismatch"
        );
    }
}

#[test]
fn kinqimen_sample_harness_matches_classical_pins() {
    let (_path, text) = require_sample("kinqimen", "dinh_cuc.csv");
    assert_dinh_cuc_rows(&text, "kinqimen sample");
}

#[test]
fn kinqimen_full_dump_gates_or_skips_honestly() {
    let path = dataset_path("kinqimen", DatasetKind::Full, "dinh_cuc.csv");
    match load_csv(&path, "kinqimen full") {
        LoadOutcome::Absent { message, .. } => {
            eprintln!("{message}");
        }
        LoadOutcome::Ready {
            text, row_count, ..
        } => {
            assert_dinh_cuc_rows(&text, "kinqimen full");
            eprintln!("kinqimen full certification: {row_count} rows matched 100%");
        }
    }
}
