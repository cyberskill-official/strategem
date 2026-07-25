use cyberos_thaiat::{cast_thai_at, Cap, CastInput, DemToan, Epoch, TatFlags};
use std::fs;
use std::path::PathBuf;

fn main() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/taiyi_cert_v1.csv");
    let text = fs::read_to_string(&path).expect("csv");
    let mut out =
        String::from("id,datetime,nam_ce,year_chi_idx,epoch,cache_key,oracle_source,flags_doc\n");
    for line in text.lines().skip(1).filter(|l| !l.trim().is_empty()) {
        let cols: Vec<&str> = line.split(',').collect();
        let nam_ce: i32 = cols[2].parse().unwrap();
        let year_chi_idx: u8 = cols[3].parse().unwrap();
        let epoch = match cols[4] {
            "co_dien" => Epoch::CoDien,
            _ => Epoch::KimKinh,
        };
        let input = CastInput {
            nam_ce,
            year_chi_idx,
            datetime: cols[1].into(),
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
        let oracle = cols.get(6).copied().unwrap_or("engine_golden_v1+cast_cli");
        let flags_doc = cols.get(7).copied().unwrap_or("");
        out.push_str(&format!(
            "{},{},{},{},{},{},{},{}\n",
            cols[0], cols[1], cols[2], cols[3], cols[4], r.cache_key, oracle, flags_doc
        ));
    }
    fs::write(&path, out).expect("write");
    eprintln!("regenerated {}", path.display());
}
