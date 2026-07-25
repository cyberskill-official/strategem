//! LiuRen engine assembly — TASK-LN-006.

use crate::ban::{BanLucNham, ThienDiaBan};
use crate::khoathe::recognize_khoa_the_full;
use crate::tamtruyen::lap_tam_truyen;
use crate::thiendiaban::{dia_ban, quay_thien_ban};
use crate::thientuong::{lap_thien_tuong, QuyNhanVariant};
use crate::tukhoa::lap_tu_khoa;
use cyberos_lichphap::{tuan_khong, Can, Chi};
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

    // Không vong = tuần không from day pillar (TASK-CORE-004), not a hardcoded pair.
    let (kv1, kv2) = tuan_khong(input.can_ngay, input.chi_ngay);
    let khong_vong = [kv1, kv2];

    // COV-005: emit recognized khoa_the names (not Debug strings); L2 uses generals.
    let khoa_hits = recognize_khoa_the_full(&tam_truyen, Some(&tu_khoa), Some(&thien_tuong));
    let khoa_the: Vec<String> = khoa_hits.iter().map(|h| h.name.clone()).collect();
    let ban = BanLucNham {
        thien_dia_ban: thien_dia,
        tu_khoa,
        tam_truyen,
        thien_tuong,
        khoa_the: khoa_the.clone(),
        khong_vong,
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
    // COV-005: stamp truong_sinh / school flags used
    flags.insert("truong_sinh_phai".into(), "ngu_hanh".into());
    flags.insert("truong_sinh".into(), "stamped".into());
    flags.insert("school".into(), "luc_nham".into());

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
            // COV-002: full calendar flag stamp (never silent)
            "co_lich_phap": {
                "tz": input.tz,
                "longitude": input.kinh_do,
                "can_ngay": input.can_ngay.glyph(),
                "chi_ngay": input.chi_ngay.glyph(),
                "nguyet_tuong": input.nguyet_tuong.glyph(),
                "gio_chiem": input.gio_chiem.glyph(),
                "stamped": true,
            },
        },
        "ban": {
            "nguyet_tuong": input.nguyet_tuong.glyph(),
            "gio_chiem": input.gio_chiem.glyph(),
            // Full heaven–earth plates for TASK-CHART-002 (was missing; UI fell back to raw CHI12)
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
                "khoa_the": format!("{:?}", ban.tam_truyen.khoa_the),
            },
            "thien_tuong": ban.thien_tuong.generals.iter().map(|g| format!("{g:?}")).collect::<Vec<_>>(),
            "khoa_the": khoa_the,
            "khong_vong": [
                ban.khong_vong[0].glyph(),
                ban.khong_vong[1].glyph(),
            ],
        },
        "cach_cuc": khoa_hits.iter().map(|h| json!({
            "id": h.id,
            "name": h.name,
            "polarity": h.polarity,
            "layer": h.layer,
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
