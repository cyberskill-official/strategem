//! Can / Chi / GiapTy primitives (TASK-CORE-007).

use serde::{Deserialize, Deserializer, Serialize, Serializer};
use thiserror::Error;

/// 甲乙丙丁戊己庚辛壬癸 — index 0..10
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Can {
    Giap = 0, // 甲
    At = 1,   // 乙
    Binh = 2, // 丙
    Dinh = 3, // 丁
    Mau = 4,  // 戊
    Ky = 5,   // 己
    Canh = 6, // 庚
    Tan = 7,  // 辛
    Nham = 8, // 壬
    Quy = 9,  // 癸
}

/// 子丑寅卯辰巳午未申酉戌亥 — index 0..12
/// `Ty` = 子 (rat), `Ty2` = 巳 (snake) — never conflate.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Chi {
    Ty = 0,    // 子
    Suu = 1,   // 丑
    Dan = 2,   // 寅
    Mao = 3,   // 卯
    Thin = 4,  // 辰
    Ty2 = 5,   // 巳
    Ngo = 6,   // 午
    Mui = 7,   // 未
    Than = 8,  // 申
    Dau = 9,   // 酉
    Tuat = 10, // 戌
    Hoi = 11,  // 亥
}

/// 木火土金水
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum NguHanh {
    Moc,
    Hoa,
    Tho,
    Kim,
    Thuy,
}

/// Sexagenary cycle index 0..60 (0 = 甲子).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct GiapTy(pub u8);

#[derive(Debug, Error, PartialEq, Eq)]
pub enum GanzhiError {
    #[error("illegal can-chi pair")]
    IllegalPair,
    #[error("giap ty out of range")]
    OutOfRange,
    #[error("unknown glyph")]
    UnknownGlyph,
}

const CAN_GLYPHS: [&str; 10] = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
const CHI_GLYPHS: [&str; 12] = [
    "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥",
];

impl Can {
    pub const ALL: [Can; 10] = [
        Can::Giap,
        Can::At,
        Can::Binh,
        Can::Dinh,
        Can::Mau,
        Can::Ky,
        Can::Canh,
        Can::Tan,
        Can::Nham,
        Can::Quy,
    ];

    pub fn index(self) -> u8 {
        self as u8
    }

    pub fn from_index(i: u8) -> Option<Self> {
        Self::ALL.get(i as usize).copied()
    }

    pub fn glyph(self) -> &'static str {
        CAN_GLYPHS[self.index() as usize]
    }

    pub fn from_glyph(g: &str) -> Option<Self> {
        CAN_GLYPHS
            .iter()
            .position(|&x| x == g)
            .and_then(|i| Self::from_index(i as u8))
    }
}

impl Chi {
    pub const ALL: [Chi; 12] = [
        Chi::Ty,
        Chi::Suu,
        Chi::Dan,
        Chi::Mao,
        Chi::Thin,
        Chi::Ty2,
        Chi::Ngo,
        Chi::Mui,
        Chi::Than,
        Chi::Dau,
        Chi::Tuat,
        Chi::Hoi,
    ];

    pub fn index(self) -> u8 {
        self as u8
    }

    pub fn from_index(i: u8) -> Option<Self> {
        Self::ALL.get(i as usize).copied()
    }

    pub fn glyph(self) -> &'static str {
        CHI_GLYPHS[self.index() as usize]
    }

    pub fn from_glyph(g: &str) -> Option<Self> {
        CHI_GLYPHS
            .iter()
            .position(|&x| x == g)
            .and_then(|i| Self::from_index(i as u8))
    }
}

impl GiapTy {
    pub fn new(i: u8) -> Result<Self, GanzhiError> {
        if i >= 60 {
            return Err(GanzhiError::OutOfRange);
        }
        Ok(Self(i))
    }

    pub fn index(self) -> u8 {
        self.0
    }

    pub fn glyph(self) -> String {
        let (c, z) = can_chi_of(self);
        format!("{}{}", c.glyph(), z.glyph())
    }
}

/// Legal pair: (can_index - chi_index) % 2 == 0, and index = can + 10*k matching cycle.
/// Standard: stem cycles with branch; idx = (can_i + 10 * t) where chi_i = (can_i + even) mod 12
/// Actually: for n in 0..60, can = n % 10, chi = n % 12.
pub fn can_chi_of(g: GiapTy) -> (Can, Chi) {
    let n = g.0 as usize;
    (
        Can::from_index((n % 10) as u8).unwrap(),
        Chi::from_index((n % 12) as u8).unwrap(),
    )
}

pub fn giap_ty_from_can_chi(c: Can, z: Chi) -> Result<GiapTy, GanzhiError> {
    // Find unique n in 0..60 with n%10==can and n%12==chi
    for n in 0u8..60 {
        if n % 10 == c.index() && n % 12 == z.index() {
            return Ok(GiapTy(n));
        }
    }
    Err(GanzhiError::IllegalPair)
}

impl Serialize for Can {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(self.glyph())
    }
}

impl<'de> Deserialize<'de> for Can {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let g = String::deserialize(d)?;
        Self::from_glyph(&g).ok_or_else(|| serde::de::Error::custom("unknown can glyph"))
    }
}

impl Serialize for Chi {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(self.glyph())
    }
}

impl<'de> Deserialize<'de> for Chi {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let g = String::deserialize(d)?;
        Self::from_glyph(&g).ok_or_else(|| serde::de::Error::custom("unknown chi glyph"))
    }
}

impl Serialize for GiapTy {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(&self.glyph())
    }
}

impl<'de> Deserialize<'de> for GiapTy {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let g = String::deserialize(d)?;
        if g.chars().count() != 2 {
            return Err(serde::de::Error::custom("giap ty glyph must be 2 chars"));
        }
        let mut it = g.chars();
        let c = it.next().unwrap().to_string();
        let z = it.next().unwrap().to_string();
        let can = Can::from_glyph(&c).ok_or_else(|| serde::de::Error::custom("bad can"))?;
        let chi = Chi::from_glyph(&z).ok_or_else(|| serde::de::Error::custom("bad chi"))?;
        giap_ty_from_can_chi(can, chi).map_err(serde::de::Error::custom)
    }
}
