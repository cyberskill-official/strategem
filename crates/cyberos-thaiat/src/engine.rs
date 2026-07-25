//! Thai At engine assembly — TASK-TAT-006.

use crate::ban::{Cap, TatFlags, ThaiAtBan};
use crate::battuong::place_bat_tuong;
use crate::cachcuc::{map_to_envelope_cach_cuc, nhan_dien_cach_cuc};
use crate::flags::Epoch;
use crate::thaplucthan::THAP_LUC_THAN;
use crate::tichnien::compute_tich_nien;
use crate::toan::DemToan;
use chrono::Utc;
use laso_envelope::{
    attach_cache_key, CachCuc, DauVao, He, LaSo, Polarity, Provenance, ENVELOPE_VERSION,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CastInput {
    pub nam_ce: i32,
    pub year_chi_idx: u8,
    pub datetime: String,
    pub tz: String,
    pub kinh_do: f64,
    pub flags: TatFlags,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CastResult {
    pub ban: ThaiAtBan,
    pub envelope: Value,
    pub cache_key: String,
}

fn flag_map(f: &TatFlags) -> BTreeMap<String, String> {
    let mut m = BTreeMap::new();
    m.insert(
        "epoch".into(),
        match f.epoch {
            Epoch::KimKinh => "kim_kinh".into(),
            Epoch::CoDien => "co_dien".into(),
        },
    );
    m.insert(
        "dem_toan".into(),
        match f.dem_toan {
            DemToan::TruocThaiAt => "truoc_thai_at".into(),
            DemToan::SauThaiAt => "sau_thai_at".into(),
        },
    );
    m.insert(
        "cap".into(),
        match f.cap {
            Cap::Nien => "nien".into(),
            Cap::Nguyet => "nguyet".into(),
            Cap::Nhat => "nhat".into(),
            Cap::Thoi => "thoi".into(),
        },
    );
    m.insert("duong_don".into(), f.duong_don.to_string());
    m
}

/// Pipeline: tich nien → seat Thai At → bat tuong + toan → envelope.
pub fn cast_thai_at(input: &CastInput) -> CastResult {
    let f = &input.flags;
    let tich = compute_tich_nien(input.nam_ce, f.epoch);
    let (bt, seat) = place_bat_tuong(&tich, input.year_chi_idx, f.duong_don, f.dem_toan);
    let ban = ThaiAtBan {
        tich,
        seat,
        bat_tuong: bt,
    };
    let flags = flag_map(f);

    let detected = nhan_dien_cach_cuc(&ban.bat_tuong, ban.seat.thai_at_ring);
    let _raw_cach_cuc = map_to_envelope_cach_cuc(&detected);

    // dau_vao: only contract fields (no nam_ce, no cap)
    let dau_vao = DauVao {
        datetime: input.datetime.clone(),
        tz: input.tz.clone(),
        kinh_do: input.kinh_do,
        loai_cau_hoi: None,
    };

    let lich_phap = json!({
        "nam_ce": input.nam_ce,
        "duong_don": f.duong_don,
        "co_lich_phap": {
            "tz": input.tz,
            "longitude": input.kinh_do,
            "nam_ce": input.nam_ce,
            "year_chi_idx": input.year_chi_idx,
            "duong_don": f.duong_don,
            "stamped": true,
        },
    });

    let ban_value = json!({
        "tich": {
            "tich_nien": ban.tich.tich_nien,
            "nhap_cuc": ban.tich.nhap_cuc,
            "nhap_ky_nguyen": ban.tich.nhap_ky_nguyen,
            "can_chi": ban.tich.can_chi,
        },
        "thai_at_cung": ban.seat.thai_at_cung,
        "thai_at_ring": ban.seat.thai_at_ring,
        "thap_luc_than": THAP_LUC_THAN.iter().map(|t| json!({
            "ring": t.ring,
            "chi": t.chi,
            "han": t.han,
            "loai": t.loai,
        })).collect::<Vec<_>>(),
        "bat_tuong": {
            "van_xuong": ban.bat_tuong.van_xuong,
            "thuy_kich": ban.bat_tuong.thuy_kich,
            "ke_than": ban.bat_tuong.ke_than,
            "chu_dai_tuong": ban.bat_tuong.chu_dai_tuong,
            "khach_dai_tuong": ban.bat_tuong.khach_dai_tuong,
            "chu_tham_tuong": ban.bat_tuong.chu_tham_tuong,
            "khach_tham_tuong": ban.bat_tuong.khach_tham_tuong,
        },
        "cac_toan": {
            "chu_toan": ban.bat_tuong.chu_toan.value,
            "khach_toan": ban.bat_tuong.khach_toan.value,
            "chu_truong_doan": ban.bat_tuong.chu_toan.label,
            "khach_truong_doan": ban.bat_tuong.khach_toan.label,
        },
        "chu_khach": {
            "chu_toan": ban.bat_tuong.chu_toan.value,
            "khach_toan": ban.bat_tuong.khach_toan.value,
            "chu_truong_doan": ban.bat_tuong.chu_toan.label,
            "khach_truong_doan": ban.bat_tuong.khach_toan.label,
            "note": "positional counts only — not a victory verdict",
        },
    });

    // Map to typed CachCuc (drop tuong/bien_the — not in envelope schema)
    let cach_cuc_typed: Vec<CachCuc> = detected
        .iter()
        .map(|c| CachCuc {
            id: c.cach.id().into(),
            name: c.han.clone(),
            cung: Some(c.cung),
            polarity: Polarity::Trung,
            score: None,
            citations: vec!["kim_kinh_thuc_kinh".into(), "thong_tong_bao_giam".into()],
        })
        .collect();

    let mut la = LaSo {
        envelope_version: ENVELOPE_VERSION,
        he: He::ThaiAt,
        dau_vao,
        lich_phap,
        ban: ban_value,
        cach_cuc: cach_cuc_typed,
        co_truong_phai: flags,
        provenance: Provenance {
            engine: "tat".into(),
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
