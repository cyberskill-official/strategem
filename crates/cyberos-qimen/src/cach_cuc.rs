//! Cach cuc detection — FR-QMDG-005.

use crate::dia_ban::{DiaBan, Stem};
use crate::sao_mon_than::{BatMon, SaoMonThan, YinYangPan};
use crate::truc_phu_su::TrucPhuSu;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Polarity {
    Cat,
    Hung,
    Trung,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CachCucHit {
    pub id: String,
    pub name: String,
    pub cung: Option<u8>,
    pub polarity: Polarity,
    pub score: Option<f32>,
    pub citations: Vec<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PatternRow {
    pub id: String,
    pub name: String,
    pub polarity: String,
    pub score: f32,
    pub sky: String,
    pub earth: String,
    pub citations: Vec<String>,
}

fn stem_glyph(s: Stem) -> &'static str {
    s.glyph()
}

/// 9×9 thap can khac ung base: sky stem glyph × earth stem glyph.
/// Giap never appears. Returns a simple relation tag.
pub fn thap_can_khac_ung(sky: Stem, earth: Stem) -> &'static str {
    if sky == earth {
        "phuc"
    } else {
        // coarse relation marker for tests / downstream
        "khac_ung"
    }
}

pub fn all_visible_stems() -> [Stem; 9] {
    Stem::SEQ
}

const BUILTIN_PATTERNS: &[(&str, &str, &str, &str, f32, Polarity)] = &[
    (
        "qimen_thanh_long_hoi_dau",
        "青龍返首",
        "戊",
        "丙",
        0.9,
        Polarity::Cat,
    ),
    (
        "qimen_phi_dieu_diet_huyet",
        "飛鳥跌穴",
        "丙",
        "戊",
        0.9,
        Polarity::Cat,
    ),
    (
        "qimen_thanh_long_tron",
        "青龍逃走",
        "乙",
        "辛",
        0.85,
        Polarity::Hung,
    ),
    (
        "qimen_bach_ho_xuong_cuong",
        "白虎猖狂",
        "辛",
        "乙",
        0.85,
        Polarity::Hung,
    ),
    (
        "qimen_chu_tuoc_dau_giang",
        "朱雀投江",
        "丁",
        "癸",
        0.8,
        Polarity::Hung,
    ),
    (
        "qimen_dang_xa_yeu_kieu",
        "螣蛇夭矯",
        "癸",
        "丁",
        0.8,
        Polarity::Hung,
    ),
    (
        "qimen_thai_bach_nhap_huynh",
        "太白入熒",
        "庚",
        "丙",
        0.85,
        Polarity::Hung,
    ),
    (
        "qimen_huynh_nhap_thai_bach",
        "熒入太白",
        "丙",
        "庚",
        0.85,
        Polarity::Hung,
    ),
    ("qimen_dai_cach", "大格", "庚", "癸", 0.9, Polarity::Hung),
];

fn match_ordered(sky: &str, earth: &str) -> Option<CachCucHit> {
    for (id, name, s, e, score, pol) in BUILTIN_PATTERNS {
        if *s == sky && *e == earth {
            return Some(CachCucHit {
                id: (*id).into(),
                name: (*name).into(),
                cung: None,
                polarity: *pol,
                score: Some(*score),
                citations: vec!["Yên Ba Điếu Tẩu Ca".into()],
            });
        }
    }
    None
}

/// Detect cat/hung cach from sky-over-earth stems + special states.
pub fn detect_cach_cuc(ban: &SaoMonThan, dia: &DiaBan, tps: &TrucPhuSu) -> Vec<CachCucHit> {
    let mut hits = Vec::new();
    if ban.yin_yang_pan == YinYangPan::Am {
        // am lineage is light on cach cuc
        return hits;
    }
    for p in 1u8..=9 {
        let earth = dia.at_palace(p);
        let sky = tps.thien_ban[(p - 1) as usize];
        if let Some(mut h) = match_ordered(stem_glyph(sky), stem_glyph(earth)) {
            h.cung = Some(p);
            hits.push(h);
        }
        // mon bach: door present and "pressed" — stub: hung doors only as special
        if let Some(door) = ban.bat_mon[(p - 1) as usize] {
            if !door.is_cat() && matches!(door, BatMon::Tu | BatMon::Thuong | BatMon::Kinh) {
                hits.push(CachCucHit {
                    id: format!("qimen_mon_bach_{p}"),
                    name: "門迫".into(),
                    cung: Some(p),
                    polarity: Polarity::Hung,
                    score: Some(0.5),
                    citations: vec![],
                });
            }
        }
    }
    // phuc/phan ngam whole-chart stubs via xoay
    if tps.xoay == 0 {
        hits.push(CachCucHit {
            id: "qimen_phuc_ngam".into(),
            name: "伏吟".into(),
            cung: None,
            polarity: Polarity::Trung,
            score: Some(0.6),
            citations: vec![],
        });
    } else if tps.xoay.abs() == 4 {
        hits.push(CachCucHit {
            id: "qimen_phan_ngam".into(),
            name: "反吟".into(),
            cung: None,
            polarity: Polarity::Hung,
            score: Some(0.6),
            citations: vec![],
        });
    }
    hits
}

/// Load JSON patterns from file (optional; builtins always active).
pub fn load_patterns_json(s: &str) -> Result<Vec<PatternRow>, serde_json::Error> {
    serde_json::from_str(s)
}
