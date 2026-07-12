//! cast-cli — stdin JSON → la so envelope JSON on stdout.
//!
//! Input:
//! ```json
//! { "system": "qimen"|"liuren"|"taiyi", "lich_phap": { ... } }
//! ```
//!
//! Optional argv: `cast` (default). Exit 0 on success; non-zero + stderr on error.

use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{cast_luc_nham, QuyNhanVariant};
use cyberos_qimen::{cast_qimen, DingjuMethod, PanMethod, QiMenFlags, YinYangPan, ZhongGongKy};
use cyberos_thaiat::{cast_thai_at, Cap, DemToan, Epoch, TatFlags};
use serde::Deserialize;
use serde_json::{json, Value};
use std::io::{self, Read};
use std::process::ExitCode;

#[derive(Debug, Deserialize)]
struct CastRequest {
    system: String,
    #[serde(default)]
    lich_phap: Value,
}

fn main() -> ExitCode {
    let mut buf = String::new();
    if let Err(e) = io::stdin().read_to_string(&mut buf) {
        eprintln!("read stdin: {e}");
        return ExitCode::from(2);
    }
    let req: CastRequest = match serde_json::from_str(&buf) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("invalid json: {e}");
            return ExitCode::from(2);
        }
    };
    match cast_envelope(&req.system, &req.lich_phap) {
        Ok(env) => {
            println!("{}", env);
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("cast failed: {e}");
            ExitCode::from(1)
        }
    }
}

fn f64_field(v: &Value, keys: &[&str], default: f64) -> f64 {
    for k in keys {
        if let Some(n) = v.get(*k).and_then(|x| x.as_f64()) {
            return n;
        }
    }
    default
}

fn str_field(v: &Value, keys: &[&str], default: &str) -> String {
    for k in keys {
        if let Some(s) = v.get(*k).and_then(|x| x.as_str()) {
            return s.to_string();
        }
    }
    default.to_string()
}

fn u8_field(v: &Value, keys: &[&str], default: u8) -> u8 {
    for k in keys {
        if let Some(n) = v.get(*k).and_then(|x| x.as_u64()) {
            return n as u8;
        }
    }
    default
}

fn cast_envelope(system: &str, lich: &Value) -> Result<Value, String> {
    let sys = system.to_ascii_lowercase();
    match sys.as_str() {
        "qimen" | "ky_mon" => cast_qimen_env(lich),
        "liuren" | "luc_nham" => cast_liuren_env(lich),
        "taiyi" | "thai_at" => cast_taiyi_env(lich),
        other => Err(format!("unknown system: {other}")),
    }
}

fn cast_qimen_env(lich: &Value) -> Result<Value, String> {
    let datetime = str_field(lich, &["datetime", "dt"], "2004-01-01T10:30:00");
    let tz = str_field(lich, &["tz"], "+07:00");
    let kinh_do = f64_field(lich, &["kinh_do", "longitude"], 106.7);
    let term_index = u8_field(lich, &["term_index"], 0) % 24;
    let branch_index = u8_field(lich, &["branch_index"], 0) % 12;
    let hour_can = u8_field(lich, &["hour_can"], 0) % 10;
    let hour_chi = u8_field(lich, &["hour_chi"], 0) % 12;
    let hour_stem_palace = u8_field(lich, &["hour_stem_palace"], 1).clamp(1, 9);

    let flags_obj = lich.get("co_truong_phai").cloned().unwrap_or(json!({}));
    let dingju = match flags_obj
        .get("dingju_method")
        .or_else(|| flags_obj.get("ky_mon.dingju_method"))
        .and_then(|x| x.as_str())
        .unwrap_or("chaibu")
    {
        "zhirun" | "zhirunzhuo" => DingjuMethod::Zhirun,
        "maoshan" => DingjuMethod::Maoshan,
        _ => DingjuMethod::Chaibu,
    };
    let pan = match flags_obj
        .get("pan_method")
        .or_else(|| flags_obj.get("ky_mon.pan_method"))
        .and_then(|x| x.as_str())
        .unwrap_or("zhuan")
    {
        "fei" => PanMethod::Fei,
        _ => PanMethod::Zhuan,
    };
    let yin_yang = match flags_obj
        .get("yin_yang_pan")
        .or_else(|| flags_obj.get("ky_mon.yin_yang_pan"))
        .and_then(|x| x.as_str())
        .unwrap_or("duong")
    {
        "am" => YinYangPan::Am,
        _ => YinYangPan::Duong,
    };

    let input = cyberos_qimen::QimenCastInput {
        datetime,
        tz,
        kinh_do,
        term_index,
        branch_index,
        hour_can,
        hour_chi,
        hour_stem_palace,
        flags: QiMenFlags {
            dingju_method: dingju,
            pan_method: pan,
            yin_yang_pan: yin_yang,
            zhong_gong_ky: ZhongGongKy::Khon2,
            chan_thai_duong_thoi: true,
        },
    };
    let res = cast_qimen(&input)?;
    Ok(res.envelope)
}

fn cast_liuren_env(lich: &Value) -> Result<Value, String> {
    let datetime = str_field(lich, &["datetime", "dt"], "2004-01-01T10:30:00");
    let tz = str_field(lich, &["tz"], "+07:00");
    let kinh_do = f64_field(lich, &["kinh_do", "longitude"], 106.7);
    let can_i = u8_field(lich, &["can_ngay", "day_can"], 0) % 10;
    let chi_i = u8_field(lich, &["chi_ngay", "day_chi"], 0) % 12;
    let nt = u8_field(lich, &["nguyet_tuong"], chi_i) % 12;
    let gio = u8_field(lich, &["gio_chiem", "hour_chi"], 0) % 12;
    let can = Can::from_index(can_i).ok_or("bad can")?;
    let chi = Chi::from_index(chi_i).ok_or("bad chi")?;
    let nguyet = Chi::from_index(nt).ok_or("bad nguyet")?;
    let gio_chiem = Chi::from_index(gio).ok_or("bad gio")?;

    let input = cyberos_luchnham::CastInput {
        datetime,
        tz,
        kinh_do,
        can_ngay: can,
        chi_ngay: chi,
        nguyet_tuong: nguyet,
        gio_chiem,
        quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
    };
    let res = cast_luc_nham(&input);
    Ok(res.envelope)
}

fn cast_taiyi_env(lich: &Value) -> Result<Value, String> {
    let datetime = str_field(lich, &["datetime", "dt"], "2004-01-01T10:30:00");
    let tz = str_field(lich, &["tz"], "+07:00");
    let kinh_do = f64_field(lich, &["kinh_do", "longitude"], 106.7);
    let nam_ce = lich
        .get("nam_ce")
        .and_then(|x| x.as_i64())
        .map(|n| n as i32)
        .unwrap_or_else(|| {
            datetime
                .get(0..4)
                .and_then(|s| s.parse().ok())
                .unwrap_or(2004)
        });
    let year_chi = u8_field(lich, &["year_chi_idx"], (nam_ce.rem_euclid(12)) as u8) % 12;
    let flags_obj = lich.get("co_truong_phai").cloned().unwrap_or(json!({}));
    let epoch = match flags_obj
        .get("epoch")
        .or_else(|| flags_obj.get("thai_at.epoch"))
        .and_then(|x| x.as_str())
        .unwrap_or("kim_kinh")
    {
        "co_dien" => Epoch::CoDien,
        _ => Epoch::KimKinh,
    };
    let input = cyberos_thaiat::CastInput {
        nam_ce,
        year_chi_idx: year_chi,
        datetime,
        tz,
        kinh_do,
        flags: TatFlags {
            epoch,
            dem_toan: DemToan::TruocThaiAt,
            cap: Cap::Nien,
            duong_don: true,
        },
    };
    let res = cast_thai_at(&input);
    Ok(res.envelope)
}
