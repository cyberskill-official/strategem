//! Cach cuc recognition between Thai At and tuong — FR-TAT-005.
//! Emits positional facts only; no victory verdict.

use crate::battuong::BatTuong;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Cach {
    Yem,
    Bach,
    Quan,
    Tu,
    Kich,
    Cach,
    Doi,
}

impl Cach {
    pub fn han(self) -> &'static str {
        match self {
            Cach::Yem => "掩",
            Cach::Bach => "迫",
            Cach::Quan => "關",
            Cach::Tu => "囚",
            Cach::Kich => "擊",
            Cach::Cach => "格",
            Cach::Doi => "對",
        }
    }

    pub fn id(self) -> &'static str {
        match self {
            Cach::Yem => "tat_yem",
            Cach::Bach => "tat_bach",
            Cach::Quan => "tat_quan",
            Cach::Tu => "tat_tu",
            Cach::Kich => "tat_kich",
            Cach::Cach => "tat_cach",
            Cach::Doi => "tat_doi",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BienTheKich {
    NoiKich,
    NgoaiKich,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CachCucTat {
    pub cach: Cach,
    pub han: String,
    pub tuong: String,
    pub cung: u8,
    pub bien_the: Option<BienTheKich>,
}

fn adj(a: u8, b: u8) -> bool {
    let d = (a as i16 - b as i16).abs();
    d == 1 || d == 15
}

fn opposed(a: u8, b: u8) -> bool {
    (a as u16 + 8) % 16 == b as u16
}

/// Recognize cach from relative positions of Thai At and the tuong.
pub fn nhan_dien_cach_cuc(bat: &BatTuong, thai_at_ring: u8) -> Vec<CachCucTat> {
    let mut out = Vec::new();
    let ta = thai_at_ring;

    // Yem: khach muc/tuong same palace as Thai At
    for (name, ring) in [
        ("khach_dai_tuong", bat.khach_dai_tuong),
        ("khach_tham_tuong", bat.khach_tham_tuong),
        ("thuy_kich", bat.thuy_kich),
    ] {
        if ring == ta {
            out.push(CachCucTat {
                cach: Cach::Yem,
                han: Cach::Yem.han().into(),
                tuong: name.into(),
                cung: ring,
                bien_the: None,
            });
        }
    }

    // Quan: chu muc/tuong same as Thai At
    for (name, ring) in [
        ("chu_dai_tuong", bat.chu_dai_tuong),
        ("chu_tham_tuong", bat.chu_tham_tuong),
        ("van_xuong", bat.van_xuong),
    ] {
        if ring == ta {
            out.push(CachCucTat {
                cach: Cach::Quan,
                han: Cach::Quan.han().into(),
                tuong: name.into(),
                cung: ring,
                bien_the: None,
            });
        }
    }

    // Tu: dai tuong same palace
    for (name, ring) in [
        ("chu_dai_tuong", bat.chu_dai_tuong),
        ("khach_dai_tuong", bat.khach_dai_tuong),
    ] {
        if ring == ta {
            out.push(CachCucTat {
                cach: Cach::Tu,
                han: Cach::Tu.han().into(),
                tuong: name.into(),
                cung: ring,
                bien_the: None,
            });
        }
    }

    // Bach: tuong immediately before/after Thai At
    for (name, ring) in [
        ("van_xuong", bat.van_xuong),
        ("thuy_kich", bat.thuy_kich),
        ("chu_dai_tuong", bat.chu_dai_tuong),
        ("khach_dai_tuong", bat.khach_dai_tuong),
    ] {
        if adj(ring, ta) {
            out.push(CachCucTat {
                cach: Cach::Bach,
                han: Cach::Bach.han().into(),
                tuong: name.into(),
                cung: ring,
                bien_the: None,
            });
        }
    }

    // Kich: Thuy Kich adjacent — after = noi, before = ngoai
    if adj(bat.thuy_kich, ta) {
        let after = (ta + 1) % 16;
        let before = if ta == 0 { 15 } else { ta - 1 };
        let bien = if bat.thuy_kich == after {
            BienTheKich::NoiKich
        } else if bat.thuy_kich == before {
            BienTheKich::NgoaiKich
        } else {
            BienTheKich::NoiKich
        };
        out.push(CachCucTat {
            cach: Cach::Kich,
            han: Cach::Kich.han().into(),
            tuong: "thuy_kich".into(),
            cung: bat.thuy_kich,
            bien_the: Some(bien),
        });
    }

    // Cach / Doi: opposed palace
    for (name, ring) in [
        ("van_xuong", bat.van_xuong),
        ("thuy_kich", bat.thuy_kich),
        ("chu_dai_tuong", bat.chu_dai_tuong),
        ("khach_dai_tuong", bat.khach_dai_tuong),
    ] {
        if opposed(ring, ta) {
            out.push(CachCucTat {
                cach: Cach::Cach,
                han: Cach::Cach.han().into(),
                tuong: name.into(),
                cung: ring,
                bien_the: None,
            });
            out.push(CachCucTat {
                cach: Cach::Doi,
                han: Cach::Doi.han().into(),
                tuong: name.into(),
                cung: ring,
                bien_the: None,
            });
        }
    }

    out
}

/// Map to FR-PLAT-002 envelope cach_cuc entries (facts + citations, no verdict).
pub fn map_to_envelope_cach_cuc(cach: &[CachCucTat]) -> Vec<serde_json::Value> {
    cach.iter()
        .map(|c| {
            serde_json::json!({
                "id": c.cach.id(),
                "name": c.han,
                "cung": c.cung,
                "polarity": "trung",
                "citations": ["kim_kinh_thuc_kinh", "thong_tong_bao_giam"],
                "tuong": c.tuong,
                "bien_the": c.bien_the,
            })
        })
        .collect()
}
