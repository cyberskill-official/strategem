//! Ngu hanh of can/chi, sinh/khac, and dia chi relations (TASK-CORE-007).

use crate::ganzhi::{Can, Chi, NguHanh};

pub fn ngu_hanh_of_can(c: Can) -> NguHanh {
    match c {
        Can::Giap | Can::At => NguHanh::Moc,
        Can::Binh | Can::Dinh => NguHanh::Hoa,
        Can::Mau | Can::Ky => NguHanh::Tho,
        Can::Canh | Can::Tan => NguHanh::Kim,
        Can::Nham | Can::Quy => NguHanh::Thuy,
    }
}

pub fn ngu_hanh_of_chi(z: Chi) -> NguHanh {
    match z {
        Chi::Dan | Chi::Mao => NguHanh::Moc,
        Chi::Ty2 | Chi::Ngo => NguHanh::Hoa,
        Chi::Thin | Chi::Tuat | Chi::Suu | Chi::Mui => NguHanh::Tho,
        Chi::Than | Chi::Dau => NguHanh::Kim,
        Chi::Ty | Chi::Hoi => NguHanh::Thuy,
    }
}

/// 木 -> 火 -> 土 -> 金 -> 水 -> 木
pub fn sinh(a: NguHanh, b: NguHanh) -> bool {
    matches!(
        (a, b),
        (NguHanh::Moc, NguHanh::Hoa)
            | (NguHanh::Hoa, NguHanh::Tho)
            | (NguHanh::Tho, NguHanh::Kim)
            | (NguHanh::Kim, NguHanh::Thuy)
            | (NguHanh::Thuy, NguHanh::Moc)
    )
}

/// 木 -> 土 -> 水 -> 火 -> 金 -> 木
pub fn khac(a: NguHanh, b: NguHanh) -> bool {
    matches!(
        (a, b),
        (NguHanh::Moc, NguHanh::Tho)
            | (NguHanh::Tho, NguHanh::Thuy)
            | (NguHanh::Thuy, NguHanh::Hoa)
            | (NguHanh::Hoa, NguHanh::Kim)
            | (NguHanh::Kim, NguHanh::Moc)
    )
}

pub fn duoc_sinh(a: NguHanh, b: NguHanh) -> bool {
    sinh(b, a)
}

pub fn bi_khac(a: NguHanh, b: NguHanh) -> bool {
    khac(b, a)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum ChiQuanHe {
    LucHop,
    TamHop,
    LucXung,
    LucHai,
    LucPha,
    Hinh,
    TuHinh,
}

fn pair_set(pairs: &[(Chi, Chi)], a: Chi, b: Chi) -> bool {
    pairs
        .iter()
        .any(|&(x, y)| (x == a && y == b) || (x == b && y == a))
}

const LUC_HOP: [(Chi, Chi); 6] = [
    (Chi::Ty, Chi::Suu),
    (Chi::Dan, Chi::Hoi),
    (Chi::Mao, Chi::Tuat),
    (Chi::Thin, Chi::Dau),
    (Chi::Ty2, Chi::Than),
    (Chi::Ngo, Chi::Mui),
];

const LUC_XUNG: [(Chi, Chi); 6] = [
    (Chi::Ty, Chi::Ngo),
    (Chi::Suu, Chi::Mui),
    (Chi::Dan, Chi::Than),
    (Chi::Mao, Chi::Dau),
    (Chi::Thin, Chi::Tuat),
    (Chi::Ty2, Chi::Hoi),
];

const LUC_HAI: [(Chi, Chi); 6] = [
    (Chi::Ty, Chi::Mui),
    (Chi::Suu, Chi::Ngo),
    (Chi::Dan, Chi::Ty2),
    (Chi::Mao, Chi::Thin),
    (Chi::Than, Chi::Hoi),
    (Chi::Dau, Chi::Tuat),
];

const LUC_PHA: [(Chi, Chi); 6] = [
    (Chi::Ty, Chi::Dau),
    (Chi::Ngo, Chi::Mao),
    (Chi::Than, Chi::Ty2),
    (Chi::Dan, Chi::Hoi),
    (Chi::Thin, Chi::Suu),
    (Chi::Tuat, Chi::Mui),
];

const HINH_TRIADS: [[Chi; 3]; 2] = [
    [Chi::Dan, Chi::Ty2, Chi::Than], // 寅巳申
    [Chi::Suu, Chi::Tuat, Chi::Mui], // 丑戌未
];

const HINH_PAIR: (Chi, Chi) = (Chi::Ty, Chi::Mao); // 子卯

const TU_HINH: [Chi; 4] = [Chi::Thin, Chi::Ngo, Chi::Dau, Chi::Hoi];

/// Tam hop trines: (members, formed phase)
const TAM_HOP: [([Chi; 3], NguHanh); 4] = [
    ([Chi::Than, Chi::Ty, Chi::Thin], NguHanh::Thuy), // 申子辰 水
    ([Chi::Hoi, Chi::Mao, Chi::Mui], NguHanh::Moc),   // 亥卯未 木
    ([Chi::Dan, Chi::Ngo, Chi::Tuat], NguHanh::Hoa),  // 寅午戌 火
    ([Chi::Ty2, Chi::Dau, Chi::Suu], NguHanh::Kim),   // 巳酉丑 金
];

pub fn quan_he(a: Chi, b: Chi) -> Vec<ChiQuanHe> {
    let mut out = Vec::new();
    if a == b {
        if TU_HINH.contains(&a) {
            out.push(ChiQuanHe::TuHinh);
            out.push(ChiQuanHe::Hinh);
        }
        return out;
    }
    if pair_set(&LUC_HOP, a, b) {
        out.push(ChiQuanHe::LucHop);
    }
    if tam_hop_pair(a, b) {
        out.push(ChiQuanHe::TamHop);
    }
    if pair_set(&LUC_XUNG, a, b) {
        out.push(ChiQuanHe::LucXung);
    }
    if pair_set(&LUC_HAI, a, b) {
        out.push(ChiQuanHe::LucHai);
    }
    if pair_set(&LUC_PHA, a, b) {
        out.push(ChiQuanHe::LucPha);
    }
    if is_hinh(a, b) {
        out.push(ChiQuanHe::Hinh);
    }
    out
}

fn tam_hop_pair(a: Chi, b: Chi) -> bool {
    TAM_HOP
        .iter()
        .any(|(members, _)| members.contains(&a) && members.contains(&b))
}

fn is_hinh(a: Chi, b: Chi) -> bool {
    if (a == HINH_PAIR.0 && b == HINH_PAIR.1) || (a == HINH_PAIR.1 && b == HINH_PAIR.0) {
        return true;
    }
    for triad in &HINH_TRIADS {
        if triad.contains(&a) && triad.contains(&b) {
            return true;
        }
    }
    false
}

/// Other two of z's trine + phase formed.
pub fn tam_hop_cua(z: Chi) -> (Chi, Chi, NguHanh) {
    for (members, phase) in &TAM_HOP {
        if let Some(pos) = members.iter().position(|&m| m == z) {
            let others: Vec<Chi> = members
                .iter()
                .enumerate()
                .filter(|(i, _)| *i != pos)
                .map(|(_, &c)| c)
                .collect();
            return (others[0], others[1], *phase);
        }
    }
    // Every chi is in exactly one trine in the classical set
    unreachable!("chi not in any tam hop: {:?}", z);
}

#[cfg(test)]
mod unit {
    use super::*;

    #[test]
    fn example_payloads() {
        assert_eq!(quan_he(Chi::Ty, Chi::Ngo), vec![ChiQuanHe::LucXung]);
        let q = quan_he(Chi::Dan, Chi::Hoi);
        assert!(q.contains(&ChiQuanHe::LucHop));
        assert!(q.contains(&ChiQuanHe::LucPha));
        let (a, b, p) = tam_hop_cua(Chi::Than);
        assert_eq!(p, NguHanh::Thuy);
        assert!(matches!(
            (a, b),
            (Chi::Ty, Chi::Thin) | (Chi::Thin, Chi::Ty)
        ));
        assert!(khac(NguHanh::Moc, NguHanh::Tho));
        assert!(sinh(NguHanh::Moc, NguHanh::Hoa));
    }
}
