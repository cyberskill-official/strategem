//! QiMen engine assembly — TASK-QMDG-006.

use crate::ban::{KyMonBan, QiMenFlags};
use crate::bo_dia_ban;
use crate::cach_cuc::{detect_cach_cuc, CachCucHit};
use crate::dinh_cuc::{dinh_cuc, DinhCuc};
use crate::sao_mon_than::sao_mon_than;
use crate::truc_phu_su::truc_phu_truc_su;
use chrono::Utc;
use laso_envelope::{
    attach_cache_key, CachCuc, DauVao, He, LaSo, Polarity as EnvPolarity, Provenance,
    ENVELOPE_VERSION,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CastInput {
    pub datetime: String,
    pub tz: String,
    pub kinh_do: f64,
    pub term_index: u8,
    pub branch_index: u8,
    pub hour_can: u8,
    pub hour_chi: u8,
    pub hour_stem_palace: u8,
    pub flags: QiMenFlags,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CastResult {
    pub ban: KyMonBan,
    pub cach_cuc: Vec<CachCucHit>,
    pub envelope: Value,
    pub cache_key: String,
}

fn flag_map(f: &QiMenFlags) -> BTreeMap<String, String> {
    let mut m = BTreeMap::new();
    m.insert(
        "dingju_method".into(),
        format!("{:?}", f.dingju_method).to_ascii_lowercase(),
    );
    m.insert(
        "pan_method".into(),
        format!("{:?}", f.pan_method).to_ascii_lowercase(),
    );
    m.insert(
        "yin_yang_pan".into(),
        format!("{:?}", f.yin_yang_pan).to_ascii_lowercase(),
    );
    m.insert(
        "zhong_gong_ky".into(),
        format!("{:?}", f.zhong_gong_ky).to_ascii_lowercase(),
    );
    m.insert(
        "chan_thai_duong_thoi".into(),
        f.chan_thai_duong_thoi.to_string(),
    );
    m
}

/// Full pipeline: dinh cuc → dia ban → truc phu/su → sao mon than → cach cuc.
pub fn cast_qimen(input: &CastInput) -> Result<CastResult, String> {
    let f = &input.flags;
    let dinh: DinhCuc = dinh_cuc(input.term_index, input.branch_index, f.dingju_method, false)?;
    let dia = bo_dia_ban(&dinh);
    let tps = truc_phu_truc_su(
        &dia,
        input.hour_can,
        input.hour_chi,
        input.hour_stem_palace,
        f.pan_method,
        f.zhong_gong_ky,
    );
    let smt = sao_mon_than(&tps, &dinh, f.yin_yang_pan);
    let hits = detect_cach_cuc(&smt, &dia, &tps);
    let ban = KyMonBan {
        dinh_cuc: dinh,
        dia_ban: dia,
        thien_ban: tps.thien_ban,
        cuu_tinh: smt.cuu_tinh,
        bat_mon: smt.bat_mon,
        bat_than: smt.bat_than,
        truc_phu: tps.truc_phu,
        truc_su: tps.truc_su,
        sao_mon_than: smt,
        tps,
    };
    let flags = flag_map(f);

    let dau_vao = DauVao {
        datetime: input.datetime.clone(),
        tz: input.tz.clone(),
        kinh_do: input.kinh_do,
        loai_cau_hoi: None,
    };

    let lich_phap = serde_json::json!({
        "term_index": input.term_index,
        "so_cuc": ban.dinh_cuc.so_cuc,
        "duong_don": ban.dinh_cuc.duong_don,
        "nguyen": ban.dinh_cuc.nguyen,
        "co_lich_phap": {
            "tz": input.tz,
            "longitude": input.kinh_do,
            "term_index": input.term_index,
            "branch_index": input.branch_index,
            "hour_can": input.hour_can,
            "hour_chi": input.hour_chi,
            "hour_stem_palace": input.hour_stem_palace,
            "use_true_solar_time": f.chan_thai_duong_thoi,
            "stamped": true,
        },
    });

    let ban_value = serde_json::json!({
        "dinh_cuc": {
            "so_cuc": ban.dinh_cuc.so_cuc,
            "duong_don": ban.dinh_cuc.duong_don,
            "nguyen": ban.dinh_cuc.nguyen,
        },
        "dia_ban": ban.dia_ban.cung.iter().map(|s| s.glyph()).collect::<Vec<_>>(),
        "thien_ban": ban.thien_ban.iter().map(|s| s.glyph()).collect::<Vec<_>>(),
        "truc_phu": ban.truc_phu,
        "truc_su": ban.truc_su,
        "cuu_tinh": ban.cuu_tinh.iter().map(|c| format!("{c:?}")).collect::<Vec<_>>(),
        "bat_mon": ban.bat_mon.iter().map(|m| m.map(|x| format!("{x:?}"))).collect::<Vec<_>>(),
        "bat_than": ban.bat_than.iter().map(|m| m.map(|x| format!("{x:?}"))).collect::<Vec<_>>(),
    });

    let cach_cuc_typed: Vec<CachCuc> = hits
        .iter()
        .map(|h| CachCuc {
            id: h.id.clone(),
            name: h.name.clone(),
            cung: h.cung,
            polarity: match h.polarity {
                crate::cach_cuc::Polarity::Cat => EnvPolarity::Cat,
                crate::cach_cuc::Polarity::Hung => EnvPolarity::Hung,
                crate::cach_cuc::Polarity::Trung => EnvPolarity::Trung,
            },
            score: h.score,
            citations: h.citations.clone(),
        })
        .collect();

    let mut la = LaSo {
        envelope_version: ENVELOPE_VERSION,
        he: He::KyMon,
        dau_vao,
        lich_phap,
        ban: ban_value,
        cach_cuc: cach_cuc_typed,
        co_truong_phai: flags,
        provenance: Provenance {
            engine: "qmdg".into(),
            engine_version: "0.1.0".into(),
            cast_at: Utc::now(),
            cache_key: None,
            engine_source: None,
        },
    };
    attach_cache_key(&mut la);
    let key = la.provenance.cache_key.clone().unwrap();
    let envelope = serde_json::to_value(&la).expect("LaSo always serializes");

    Ok(CastResult {
        ban,
        cach_cuc: hits,
        envelope,
        cache_key: key,
    })
}
