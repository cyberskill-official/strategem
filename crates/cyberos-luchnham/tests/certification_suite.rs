//! Self-oracle regression suite (COV-001 goldens) — NOT kinliuren certification.
//!
//! Fixtures: `tests/fixtures/liuren_cert_v1.csv` with
//! `oracle_source=engine_golden_v1+cast_cli`. External kinliuren dumps live under
//! `oracle/kinliuren/` and are gated by `external_oracle_cert.rs` (W4).

use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{cast_luc_nham, CastInput, QuyNhanVariant};
use std::fs;
use std::path::PathBuf;

fn fixture_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/liuren_cert_v1.csv")
}

#[test]
fn liuren_self_oracle_regression_min_30_and_cache_keys_match() {
    let text = fs::read_to_string(fixture_path()).expect("liuren_cert_v1.csv");
    let mut rows = 0usize;
    for line in text.lines().skip(1).filter(|l| !l.trim().is_empty()) {
        let cols: Vec<&str> = line.split(',').collect();
        assert!(cols.len() >= 8, "row short: {line}");
        let id = cols[0];
        let datetime = cols[1];
        let can_i: u8 = cols[2].parse().unwrap();
        let chi_i: u8 = cols[3].parse().unwrap();
        let nt: u8 = cols[4].parse().unwrap();
        let gio: u8 = cols[5].parse().unwrap();
        let expected_key = cols[7];

        let input = CastInput {
            datetime: datetime.into(),
            tz: "+07:00".into(),
            kinh_do: 105.0,
            can_ngay: Can::from_index(can_i).expect("can"),
            chi_ngay: Chi::from_index(chi_i).expect("chi"),
            nguyet_tuong: Chi::from_index(nt).expect("nt"),
            gio_chiem: Chi::from_index(gio).expect("gio"),
            // cast-cli currently stamps GiapMauCanh for all cases in this fixture set
            quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
        };
        let r = cast_luc_nham(&input);
        assert_eq!(r.envelope["he"], "luc_nham", "{id}");
        assert!(r.envelope["ban"]["tu_khoa"].is_array(), "{id}");
        assert_eq!(r.cache_key, expected_key, "{id}: cache_key mismatch");
        let r2 = cast_luc_nham(&input);
        assert_eq!(r.cache_key, r2.cache_key, "{id} nondeterministic");
        rows += 1;
    }
    assert!(
        rows >= 30,
        "self-oracle regression requires ≥30 LiuRen golden cases, got {rows}"
    );
}
