//! COV-001 — TaiYi oracle certification suite (≥20 golden cases).
//! Fixtures: `tests/fixtures/taiyi_cert_v1.csv` (engine golden via cast-cli).

use cyberos_thaiat::{cast_thai_at, Cap, CastInput, DemToan, Epoch, TatFlags};
use std::fs;
use std::path::PathBuf;

fn fixture_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/taiyi_cert_v1.csv")
}

#[test]
fn taiyi_cert_v1_min_20_and_cache_keys_match() {
    let text = fs::read_to_string(fixture_path()).expect("taiyi_cert_v1.csv");
    let mut rows = 0usize;
    for line in text.lines().skip(1).filter(|l| !l.trim().is_empty()) {
        let cols: Vec<&str> = line.split(',').collect();
        assert!(cols.len() >= 6, "row short: {line}");
        let id = cols[0];
        let datetime = cols[1];
        let nam_ce: i32 = cols[2].parse().unwrap();
        let year_chi_idx: u8 = cols[3].parse().unwrap();
        let epoch = match cols[4] {
            "co_dien" => Epoch::CoDien,
            _ => Epoch::KimKinh,
        };
        let expected_key = cols[5];

        let input = CastInput {
            nam_ce,
            year_chi_idx,
            datetime: datetime.into(),
            tz: "+07:00".into(),
            kinh_do: 106.7,
            flags: TatFlags {
                epoch,
                dem_toan: DemToan::TruocThaiAt,
                cap: Cap::Nien,
                duong_don: true,
            },
        };
        let r = cast_thai_at(&input);
        assert_eq!(r.envelope["he"], "thai_at", "{id}");
        assert!(
            r.envelope["ban"]["thap_luc_than"].as_array().unwrap().len() == 16,
            "{id}"
        );
        assert_eq!(r.cache_key, expected_key, "{id}: cache_key mismatch");
        let r2 = cast_thai_at(&input);
        assert_eq!(r.cache_key, r2.cache_key, "{id} nondeterministic");
        rows += 1;
    }
    assert!(
        rows >= 20,
        "COV-001 requires ≥20 TaiYi golden cases, got {rows}"
    );
}
