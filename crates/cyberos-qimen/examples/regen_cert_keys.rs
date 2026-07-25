//! Rewrite `cache_key` column in `qimen_cert_v1.csv` from live `cast_qimen`.
//!
//! Use after intentional laso-envelope / dinh-cuc changes that alter the SHA-256
//! digest (keys hash full `lich_phap`, including `so_cuc`). Do not invent keys.

use cyberos_qimen::{
    cast_qimen, DingjuMethod, PanMethod, QiMenFlags, QimenCastInput, YinYangPan, ZhongGongKy,
};
use std::fs;
use std::path::PathBuf;

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

fn main() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/qimen_cert_v1.csv");
    let text = fs::read_to_string(&path).expect("csv");
    let mut out = String::from(
        "id,datetime,term_index,branch_index,hour_can,hour_chi,hour_stem_palace,dingju,pan,cache_key,oracle_source,flags_doc\n",
    );
    for line in text.lines().skip(1).filter(|l| !l.trim().is_empty()) {
        let cols: Vec<&str> = line.split(',').collect();
        let input = QimenCastInput {
            datetime: cols[1].into(),
            tz: "+07:00".into(),
            kinh_do: 106.7,
            term_index: cols[2].parse().unwrap(),
            branch_index: cols[3].parse().unwrap(),
            hour_can: cols[4].parse().unwrap(),
            hour_chi: cols[5].parse().unwrap(),
            hour_stem_palace: cols[6].parse().unwrap(),
            flags: QiMenFlags {
                dingju_method: parse_dingju(cols[7]),
                pan_method: parse_pan(cols[8]),
                yin_yang_pan: YinYangPan::Duong,
                zhong_gong_ky: ZhongGongKy::Khon2,
                chan_thai_duong_thoi: true,
            },
        };
        let r = cast_qimen(&input).expect("cast");
        let oracle = cols.get(10).copied().unwrap_or("engine_golden_v1+cast_cli");
        let flags_doc = cols.get(11).copied().unwrap_or("");
        out.push_str(&format!(
            "{},{},{},{},{},{},{},{},{},{},{},{}\n",
            cols[0],
            cols[1],
            cols[2],
            cols[3],
            cols[4],
            cols[5],
            cols[6],
            cols[7],
            cols[8],
            r.cache_key,
            oracle,
            flags_doc
        ));
    }
    fs::write(&path, out).expect("write");
    eprintln!("regenerated {}", path.display());
}
