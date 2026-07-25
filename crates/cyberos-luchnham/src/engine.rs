//! LiuRen engine assembly — TASK-LN-006.

use crate::ban::{BanLucNham, ThienDiaBan};
use crate::khoathe::recognize_khoa_the;
use crate::tamtruyen::lap_tam_truyen;
use crate::thiendiaban::{dia_ban, quay_thien_ban};
use crate::thientuong::{lap_thien_tuong, QuyNhanVariant};
use crate::tukhoa::lap_tu_khoa;
use chrono::Utc;
use cyberos_lichphap::{tuan_khong, Can, Chi};
use laso_envelope::{
    attach_cache_key, CachCuc, DauVao, He, LaSo, Polarity, Provenance, ENVELOPE_VERSION,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
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

    let khoa_hits = recognize_khoa_the(&tam_truyen);
    let khoa_the: Vec<String> = khoa_hits.iter().map(|h| h.name.clone()).collect();
    let (kv1, kv2) = tuan_khong(input.can_ngay, input.chi_ngay);
    let khong_vong = [kv1, kv2];
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
    flags.insert("truong_sinh_phai".into(), "ngu_hanh".into());
    flags.insert("truong_sinh".into(), "stamped".into());
    flags.insert("school".into(), "luc_nham".into());

    let dau_vao = DauVao {
        datetime: input.datetime.clone(),
        tz: input.tz.clone(),
        kinh_do: input.kinh_do,
        loai_cau_hoi: None,
    };

    let lich_phap = serde_json::json!({
        "nguyet_tuong": input.nguyet_tuong.glyph(),
        "gio_chiem": input.gio_chiem.glyph(),
        "co_lich_phap": {
            "tz": input.tz,
            "longitude": input.kinh_do,
            "can_ngay": input.can_ngay.glyph(),
            "chi_ngay": input.chi_ngay.glyph(),
            "nguyet_tuong": input.nguyet_tuong.glyph(),
            "gio_chiem": input.gio_chiem.glyph(),
            "stamped": true,
        },
    });

    let ban_value = serde_json::json!({
        "nguyet_tuong": input.nguyet_tuong.glyph(),
        "gio_chiem": input.gio_chiem.glyph(),
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
    });

    // Map khoa hits to envelope CachCuc (drop `layer` — not in envelope schema)
    let cach_cuc_typed: Vec<CachCuc> = khoa_hits
        .iter()
        .map(|h| CachCuc {
            id: h.id.clone(),
            name: h.name.clone(),
            cung: None,
            polarity: match h.polarity.as_str() {
                "cat" => Polarity::Cat,
                "hung" => Polarity::Hung,
                _ => Polarity::Trung,
            },
            score: None,
            citations: vec![],
        })
        .collect();

    let mut la = LaSo {
        envelope_version: ENVELOPE_VERSION,
        he: He::LucNham,
        dau_vao,
        lich_phap,
        ban: ban_value,
        cach_cuc: cach_cuc_typed,
        co_truong_phai: flags,
        provenance: Provenance {
            engine: "ln".into(),
            engine_version: "0.1.0".into(),
            cast_at: Utc::now(),
            cache_key: None,
            engine_source: None,
        },
    };
    attach_cache_key(&mut la);
    let key = la.provenance.cache_key.clone().unwrap();
    let envelope = serde_json::to_value(&la).expect("LaSo always serializes");

    CastResult {
        ban,
        envelope,
        cache_key: key,
    }
}
