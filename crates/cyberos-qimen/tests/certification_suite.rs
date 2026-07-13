//! COV-001 — QiMen oracle certification suite (≥30 golden cases).
//! Fixtures: `tests/fixtures/qimen_cert_v1.csv` (engine golden via cast-cli).

use cyberos_qimen::{
    cast_qimen, DingjuMethod, PanMethod, QiMenFlags, QimenCastInput, YinYangPan, ZhongGongKy,
};
use std::fs;
use std::path::PathBuf;

fn fixture_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/qimen_cert_v1.csv")
}

fn parse_dingju(s: &str) -> DingjuMethod {
    match s {
        "zhirun" => DingjuMethod::Zhirun,
        "maoshan" => DingjuMethod::Maoshan,
        _ => DingjuMethod::Chaibu,
    }
}

fn parse_pan(s: &str) -> PanMethod {
    match s {
        "fei" => PanMethod::Fei,
        _ => PanMethod::Zhuan,
    }
}

#[test]
fn qimen_cert_v1_min_30_and_cache_keys_match() {
    let text = fs::read_to_string(fixture_path()).expect("qimen_cert_v1.csv");
    let mut rows = 0usize;
    for line in text.lines().skip(1).filter(|l| !l.trim().is_empty()) {
        let cols: Vec<&str> = line.split(',').collect();
        assert!(
            cols.len() >= 10,
            "row needs ≥10 cols, got {}: {line}",
            cols.len()
        );
        let id = cols[0];
        let datetime = cols[1];
        let term_index: u8 = cols[2].parse().unwrap();
        let branch_index: u8 = cols[3].parse().unwrap();
        let hour_can: u8 = cols[4].parse().unwrap();
        let hour_chi: u8 = cols[5].parse().unwrap();
        let hour_stem_palace: u8 = cols[6].parse().unwrap();
        let dingju = parse_dingju(cols[7]);
        let pan = parse_pan(cols[8]);
        let expected_key = cols[9];

        let input = QimenCastInput {
            datetime: datetime.into(),
            tz: "+07:00".into(),
            kinh_do: 106.7,
            term_index,
            branch_index,
            hour_can,
            hour_chi,
            hour_stem_palace,
            flags: QiMenFlags {
                dingju_method: dingju,
                pan_method: pan,
                yin_yang_pan: YinYangPan::Duong,
                zhong_gong_ky: ZhongGongKy::Khon2,
                chan_thai_duong_thoi: true,
            },
        };
        let r = cast_qimen(&input).unwrap_or_else(|e| panic!("{id}: cast failed: {e}"));
        assert_eq!(r.envelope["he"], "ky_mon", "{id}");
        assert!(r.envelope["ban"]["dia_ban"].is_array(), "{id} dia_ban");
        assert_eq!(
            r.cache_key, expected_key,
            "{id}: cache_key mismatch (flag drift or engine regression)"
        );
        // double-cast determinism
        let r2 = cast_qimen(&input).unwrap();
        assert_eq!(r.cache_key, r2.cache_key, "{id} nondeterministic");
        rows += 1;
    }
    assert!(
        rows >= 30,
        "COV-001 requires ≥30 QiMen golden cases, got {rows}"
    );
}
