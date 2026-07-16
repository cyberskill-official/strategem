//! Cach cuc detection — TASK-QMDG-005 + COV-004 pattern-as-data catalog.

use crate::dia_ban::{DiaBan, Stem};
use crate::sao_mon_than::{BatMon, SaoMonThan, YinYangPan};
use crate::truc_phu_su::TrucPhuSu;
use serde::{Deserialize, Serialize};
use std::sync::OnceLock;

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
pub fn thap_can_khac_ung(sky: Stem, earth: Stem) -> &'static str {
    if sky == earth {
        "phuc"
    } else {
        "khac_ung"
    }
}

pub fn all_visible_stems() -> [Stem; 9] {
    Stem::SEQ
}

fn parse_polarity(s: &str) -> Polarity {
    match s.to_ascii_lowercase().as_str() {
        "cat" | "ji" => Polarity::Cat,
        "hung" | "xiong" => Polarity::Hung,
        _ => Polarity::Trung,
    }
}

/// Full catalog from `patterns/qimen_cach_cuc.json` (COV-004 ≥40 rows).
pub fn pattern_catalog() -> &'static [PatternRow] {
    static CAT: OnceLock<Vec<PatternRow>> = OnceLock::new();
    CAT.get_or_init(|| {
        load_patterns_json(include_str!("../patterns/qimen_cach_cuc.json"))
            .expect("qimen_cach_cuc.json must parse")
    })
    .as_slice()
}

fn match_ordered(sky: &str, earth: &str) -> Option<CachCucHit> {
    for row in pattern_catalog() {
        if row.sky == sky && row.earth == earth {
            return Some(CachCucHit {
                id: row.id.clone(),
                name: row.name.clone(),
                cung: None,
                polarity: parse_polarity(&row.polarity),
                score: Some(row.score),
                citations: row.citations.clone(),
            });
        }
    }
    None
}

/// Detect cat/hung cach from sky-over-earth stems + special states.
/// Polarity is never invented without a catalog/rule match (COV-004 §1.3).
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
        // mon bach: door present and "pressed" — hung doors only as special rule
        if let Some(door) = ban.bat_mon[(p - 1) as usize] {
            if !door.is_cat() && matches!(door, BatMon::Tu | BatMon::Thuong | BatMon::Kinh) {
                hits.push(CachCucHit {
                    id: format!("qimen_mon_bach_{p}"),
                    name: "門迫".into(),
                    cung: Some(p),
                    polarity: Polarity::Hung,
                    score: Some(0.5),
                    citations: vec!["Yên Ba Điếu Tẩu Ca".into()],
                });
            }
        }
    }
    // phuc/phan ngam whole-chart via xoay
    if tps.xoay == 0 {
        hits.push(CachCucHit {
            id: "qimen_phuc_ngam".into(),
            name: "伏吟".into(),
            cung: None,
            polarity: Polarity::Trung,
            score: Some(0.6),
            citations: vec!["Yên Ba Điếu Tẩu Ca".into()],
        });
    } else if tps.xoay.abs() == 4 {
        hits.push(CachCucHit {
            id: "qimen_phan_ngam".into(),
            name: "反吟".into(),
            cung: None,
            polarity: Polarity::Hung,
            score: Some(0.6),
            citations: vec!["Yên Ba Điếu Tẩu Ca".into()],
        });
    }
    hits
}

/// Load JSON patterns from string (catalog seed + tests).
pub fn load_patterns_json(s: &str) -> Result<Vec<PatternRow>, serde_json::Error> {
    serde_json::from_str(s)
}
