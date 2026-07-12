//! LiuRen engine assembly — FR-LN-006.

use crate::ban::{BanLucNham, ThienDiaBan};
use crate::tamtruyen::lap_tam_truyen;
use crate::thiendiaban::{dia_ban, quay_thien_ban};
use crate::thientuong::{lap_thien_tuong, QuyNhanVariant};
use crate::tukhoa::lap_tu_khoa;
use cyberos_lichphap::{Can, Chi};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CastInput {
    pub datetime: String,
    pub tz: String,
    pub kinh_do: f64,
    pub can_ngay: Can,
    pub chi_ngay: Chi,
    pub nguyet_tuong: Chi,
    pub gio_chiem: Chi,
    pub quy_nhan_variant: QuyNhanVariant,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CastResult {
    pub ban: BanLucNham,
    pub envelope: Value,
    pub cache_key: String,
}

fn cache_key(he: &str, dau_vao: &Value, flags: &BTreeMap<String, String>) -> String {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    let mut h = DefaultHasher::new();
    he.hash(&mut h);
    dau_vao.to_string().hash(&mut h);
    for (k, v) in flags {
        k.hash(&mut h);
        v.hash(&mut h);
    }
    format!("{:016x}", h.finish())
}

/// Run LN pipeline: thien dia ban → tu khoa → tam truyen → thien tuong.
pub fn cast_luc_nham(input: &CastInput) -> CastResult {
    let (thien, state) = quay_thien_ban(input.nguyet_tuong, input.gio_chiem);
    let dia = dia_ban();
    let thien_dia = ThienDiaBan {
        dia,
        thien,
        nguyet_tuong: input.nguyet_tuong,
        gio_chiem: input.gio_chiem,
        state,
    };
    let tu_khoa = lap_tu_khoa(&thien, input.can_ngay, input.chi_ngay);
    let tam_truyen = lap_tam_truyen(&tu_khoa, &thien, state, input.can_ngay);
    let thien_tuong = lap_thien_tuong(input.can_ngay, input.gio_chiem, input.quy_nhan_variant);

    let khoa_the = vec![format!("{:?}", tam_truyen.khoa_the)];
    let ban = BanLucNham {
        thien_dia_ban: thien_dia,
        tu_khoa,
        tam_truyen,
        thien_tuong,
        khoa_the: khoa_the.clone(),
        khong_vong: [Chi::Tuat, Chi::Hoi], // filled by CORE in full stack
    };

    let mut flags = BTreeMap::new();
    flags.insert(
        "quy_nhan_variant".into(),
        match input.quy_nhan_variant {
            QuyNhanVariant::GiapMauCanh => "giap_mau_canh".into(),
            QuyNhanVariant::TachGiap => "tach_giap".into(),
        },
    );
    flags.insert(
        "khoi_quy_nhan".into(),
        format!("{:?}", ban.thien_tuong.khoi).to_ascii_lowercase(),
    );
    flags.insert("truong_sinh_phai".into(), "ngu_hanh".into());

    let dau_vao = json!({
        "datetime": input.datetime,
        "tz": input.tz,
        "kinh_do": input.kinh_do,
    });
    let key = cache_key("luc_nham", &dau_vao, &flags);

    let envelope = json!({
        "envelope_version": 1,
        "he": "luc_nham",
        "dau_vao": dau_vao,
        "lich_phap": {
            "nguyet_tuong": input.nguyet_tuong.glyph(),
            "gio_chiem": input.gio_chiem.glyph(),
        },
        "ban": {
            "nguyet_tuong": input.nguyet_tuong.glyph(),
            "gio_chiem": input.gio_chiem.glyph(),
            // Full heaven–earth plates for FR-CHART-002 (was missing; UI fell back to raw CHI12)
            "thien_dia_ban": {
                "dia": ban.thien_dia_ban.dia.iter().map(|c| c.glyph()).collect::<Vec<_>>(),
                "thien": ban.thien_dia_ban.thien.iter().map(|c| c.glyph()).collect::<Vec<_>>(),
                "nguyet_tuong": ban.thien_dia_ban.nguyet_tuong.glyph(),
                "gio_chiem": ban.thien_dia_ban.gio_chiem.glyph(),
                "state": format!("{:?}", ban.thien_dia_ban.state),
            },
            "tu_khoa": ban.tu_khoa.khoa.iter().map(|k| {
                [k.thuong_than.glyph(), k.ha_than.glyph()]
            }).collect::<Vec<_>>(),
            "tam_truyen": {
                "so": ban.tam_truyen.so.glyph(),
                "trung": ban.tam_truyen.trung.glyph(),
                "mat": ban.tam_truyen.mat.glyph(),
                "phap": format!("{:?}", ban.tam_truyen.phap),
            },
            "thien_tuong": ban.thien_tuong.generals.iter().map(|g| format!("{g:?}")).collect::<Vec<_>>(),
            "khoa_the": khoa_the,
        },
        "cach_cuc": ban.khoa_the.iter().map(|k| json!({
            "id": k,
            "name": k,
            "polarity": "trung",
        })).collect::<Vec<_>>(),
        "co_truong_phai": flags,
        "provenance": {
            "engine": "ln",
            "engine_version": "0.1.0",
            "cache_key": key,
        }
    });

    CastResult {
        ban,
        envelope,
        cache_key: key,
    }
}
