//! QiMen dung than by question type — FR-QMDG-007.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LoaiCauHoi {
    CauTai,
    SuNghiepCongDanh,
    HonNhan,
    KienTung,
    XuatHanh,
    BenhTat,
    CanhTranhChuKhach,
    HopTac,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DungThanRole {
    SelfRole,
    Wealth,
    Profit,
    Superior,
    Matchmaker,
    Opponent,
    Office,
    TravelGate,
    IllnessStar,
    MedicineStar,
    Host,
    Guest,
    Partner,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DungThanSymbol {
    pub role: DungThanRole,
    pub symbol: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct LocatedDungThan {
    pub role: DungThanRole,
    pub symbol: String,
    /// Palace 1..=9 when resolvable from ban; None if not found.
    pub cung: Option<u8>,
}

/// s7.3 table as data.
pub fn selection_table(loai: LoaiCauHoi) -> Vec<DungThanSymbol> {
    use DungThanRole::*;
    match loai {
        LoaiCauHoi::CauTai => vec![
            DungThanSymbol {
                role: SelfRole,
                symbol: "nhat_can".into(),
            },
            DungThanSymbol {
                role: Wealth,
                symbol: "thoi_can".into(),
            },
            DungThanSymbol {
                role: Profit,
                symbol: "Sinh".into(),
            },
            DungThanSymbol {
                role: Superior,
                symbol: "truc_phu".into(),
            },
            DungThanSymbol {
                role: Matchmaker,
                symbol: "LucHop".into(),
            },
            DungThanSymbol {
                role: Office,
                symbol: "Khai".into(),
            },
        ],
        LoaiCauHoi::SuNghiepCongDanh => vec![
            DungThanSymbol {
                role: Office,
                symbol: "Khai".into(),
            },
            DungThanSymbol {
                role: Superior,
                symbol: "truc_phu".into(),
            },
        ],
        LoaiCauHoi::HonNhan => vec![
            DungThanSymbol {
                role: SelfRole,
                symbol: "At".into(),
            },
            DungThanSymbol {
                role: Partner,
                symbol: "Canh".into(),
            },
            DungThanSymbol {
                role: Matchmaker,
                symbol: "LucHop".into(),
            },
        ],
        LoaiCauHoi::KienTung => vec![
            DungThanSymbol {
                role: Office,
                symbol: "Khai".into(),
            },
            DungThanSymbol {
                role: Superior,
                symbol: "truc_phu".into(),
            },
            DungThanSymbol {
                role: Opponent,
                symbol: "Canh".into(),
            },
            DungThanSymbol {
                role: SelfRole,
                symbol: "nhat_can".into(),
            },
        ],
        LoaiCauHoi::XuatHanh => vec![
            DungThanSymbol {
                role: TravelGate,
                symbol: "Khai".into(),
            },
            DungThanSymbol {
                role: TravelGate,
                symbol: "Huu".into(),
            },
            DungThanSymbol {
                role: TravelGate,
                symbol: "Sinh".into(),
            },
        ],
        LoaiCauHoi::BenhTat => vec![
            DungThanSymbol {
                role: IllnessStar,
                symbol: "ThienNhue".into(),
            },
            DungThanSymbol {
                role: MedicineStar,
                symbol: "ThienTam".into(),
            },
        ],
        LoaiCauHoi::CanhTranhChuKhach => vec![
            DungThanSymbol {
                role: Host,
                symbol: "nhat_can".into(),
            },
            DungThanSymbol {
                role: Guest,
                symbol: "thoi_can".into(),
            },
        ],
        LoaiCauHoi::HopTac => vec![DungThanSymbol {
            role: Partner,
            symbol: "LucHop".into(),
        }],
    }
}

/// Locate symbols on ban: bat_mon / cuu_tinh names as Debug strings in engine envelope.
pub fn locate_on_ban(
    symbols: &[DungThanSymbol],
    bat_mon: &[Option<String>],
    cuu_tinh: &[String],
) -> Vec<LocatedDungThan> {
    symbols
        .iter()
        .map(|s| {
            let mut cung = None;
            for (i, m) in bat_mon.iter().enumerate() {
                if let Some(name) = m {
                    if name.contains(&s.symbol) {
                        cung = Some((i as u8) + 1);
                        break;
                    }
                }
            }
            if cung.is_none() {
                for (i, name) in cuu_tinh.iter().enumerate() {
                    if name.contains(&s.symbol) {
                        cung = Some((i as u8) + 1);
                        break;
                    }
                }
            }
            LocatedDungThan {
                role: s.role,
                symbol: s.symbol.clone(),
                cung,
            }
        })
        .collect()
}

pub fn dung_than(
    loai: LoaiCauHoi,
    bat_mon: &[Option<String>],
    cuu_tinh: &[String],
) -> Vec<LocatedDungThan> {
    let sel = selection_table(loai);
    locate_on_ban(&sel, bat_mon, cuu_tinh)
}
