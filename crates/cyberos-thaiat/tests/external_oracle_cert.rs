//! W4 external oracle certification — TaiYi / kintaiyi.
//!
//! - `sample/` rows always run (Claude-04 §4.1 Văn Xương pins; harness proof).
//! - `full/` kintaiyi dump gates at 100% when present; otherwise SKIP (honest).

use cyberos_oracle_cert::{
    csv_rows, dataset_path, load_csv, require_sample, DatasetKind, LoadOutcome,
};
use cyberos_thaiat::van_xuong;

fn assert_van_xuong_rows(text: &str, label: &str) {
    let rows = csv_rows(text);
    assert!(!rows.is_empty(), "{label}: expected at least one data row");
    for (line_no, cols) in rows {
        assert!(
            cols.len() >= 3,
            "{label} line {line_no}: need ≥3 cols, got {}",
            cols.len()
        );
        let cuc: u8 = cols[0]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: nhap_cuc"));
        let duong: u8 = cols[1]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: duong_don"));
        let exp_ring: u8 = cols[2]
            .parse()
            .unwrap_or_else(|_| panic!("{label} line {line_no}: expected_ring"));
        let got = van_xuong(cuc, duong != 0);
        assert_eq!(
            got,
            exp_ring,
            "{label} line {line_no}: van_xuong(cuc={cuc}, duong={}) got {got} want {exp_ring}",
            duong != 0
        );
    }
}

#[test]
fn kintaiyi_sample_harness_matches_classical_pins() {
    let (_path, text) = require_sample("kintaiyi", "van_xuong.csv");
    assert_van_xuong_rows(&text, "kintaiyi sample");
}

#[test]
fn kintaiyi_full_dump_gates_or_skips_honestly() {
    let path = dataset_path("kintaiyi", DatasetKind::Full, "van_xuong.csv");
    match load_csv(&path, "kintaiyi full") {
        LoadOutcome::Absent { message, .. } => {
            eprintln!("{message}");
        }
        LoadOutcome::Ready {
            text, row_count, ..
        } => {
            assert_van_xuong_rows(&text, "kintaiyi full");
            eprintln!("kintaiyi full certification: {row_count} rows matched 100%");
        }
    }
}
