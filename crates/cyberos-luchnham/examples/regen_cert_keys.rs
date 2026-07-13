use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{cast_luc_nham, CastInput, QuyNhanVariant};
use std::fs;
use std::path::PathBuf;

fn main() {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/liuren_cert_v1.csv");
    let text = fs::read_to_string(&path).expect("csv");
    let mut out = String::from(
        "id,datetime,can_ngay,chi_ngay,nguyet_tuong,gio_chiem,quy_nhan_variant,cache_key,oracle_source,flags_doc\n",
    );
    for line in text.lines().skip(1).filter(|l| !l.trim().is_empty()) {
        let cols: Vec<&str> = line.split(',').collect();
        let input = CastInput {
            datetime: cols[1].into(),
            tz: "+07:00".into(),
            kinh_do: 105.0,
            can_ngay: Can::from_index(cols[2].parse().unwrap()).unwrap(),
            chi_ngay: Chi::from_index(cols[3].parse().unwrap()).unwrap(),
            nguyet_tuong: Chi::from_index(cols[4].parse().unwrap()).unwrap(),
            gio_chiem: Chi::from_index(cols[5].parse().unwrap()).unwrap(),
            quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
        };
        let r = cast_luc_nham(&input);
        let flags = cols.get(9).copied().unwrap_or("quy_nhan=giap_mau_canh");
        out.push_str(&format!(
            "{},{},{},{},{},{},{},{},engine_golden_v1+cast_cli,{}\n",
            cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6], r.cache_key, flags
        ));
    }
    fs::write(&path, out).expect("write");
    eprintln!("regenerated {}", path.display());
}
