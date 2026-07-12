//! Sixteen than ring — FR-TAT-002.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LoaiThan {
    ChinhCung,
    GianThan,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Than {
    pub ring: u8,
    pub chi: &'static str,
    pub han: &'static str,
    pub ten: &'static str,
    pub loai: LoaiThan,
}

pub const THAP_LUC_THAN: [Than; 16] = [
    Than {
        ring: 0,
        chi: "子",
        han: "地主",
        ten: "Dia chu",
        loai: LoaiThan::ChinhCung,
    },
    Than {
        ring: 1,
        chi: "丑",
        han: "陽德",
        ten: "Duong duc",
        loai: LoaiThan::GianThan,
    },
    Than {
        ring: 2,
        chi: "艮",
        han: "和德",
        ten: "Hoa duc",
        loai: LoaiThan::ChinhCung,
    },
    Than {
        ring: 3,
        chi: "寅",
        han: "呂申",
        ten: "Lu than",
        loai: LoaiThan::GianThan,
    },
    Than {
        ring: 4,
        chi: "卯",
        han: "高叢",
        ten: "Cao tung",
        loai: LoaiThan::ChinhCung,
    },
    Than {
        ring: 5,
        chi: "辰",
        han: "太陽",
        ten: "Thai duong",
        loai: LoaiThan::GianThan,
    },
    Than {
        ring: 6,
        chi: "巽",
        han: "大炅",
        ten: "Dai quynh",
        loai: LoaiThan::ChinhCung,
    },
    Than {
        ring: 7,
        chi: "巳",
        han: "大神",
        ten: "Dai than",
        loai: LoaiThan::GianThan,
    },
    Than {
        ring: 8,
        chi: "午",
        han: "大威",
        ten: "Dai uy",
        loai: LoaiThan::ChinhCung,
    },
    Than {
        ring: 9,
        chi: "未",
        han: "天道",
        ten: "Thien dao",
        loai: LoaiThan::GianThan,
    },
    Than {
        ring: 10,
        chi: "坤",
        han: "大武",
        ten: "Dai vu",
        loai: LoaiThan::ChinhCung,
    },
    Than {
        ring: 11,
        chi: "申",
        han: "武德",
        ten: "Vu duc",
        loai: LoaiThan::GianThan,
    },
    Than {
        ring: 12,
        chi: "酉",
        han: "太簇",
        ten: "Thai thoc",
        loai: LoaiThan::ChinhCung,
    },
    Than {
        ring: 13,
        chi: "戌",
        han: "陰主",
        ten: "Am chu",
        loai: LoaiThan::GianThan,
    },
    Than {
        ring: 14,
        chi: "乾",
        han: "陰德",
        ten: "Am duc",
        loai: LoaiThan::ChinhCung,
    },
    Than {
        ring: 15,
        chi: "亥",
        han: "大義",
        ten: "Dai nghia",
        loai: LoaiThan::GianThan,
    },
];

pub fn is_chinh_cung(ring: u8) -> bool {
    THAP_LUC_THAN
        .get(ring as usize)
        .map(|t| t.loai == LoaiThan::ChinhCung)
        .unwrap_or(false)
}
