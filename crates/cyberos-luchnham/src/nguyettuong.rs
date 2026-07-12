//! Nguyet tuong keyed off trung khi. FR-LN-001.

use cyberos_lichphap::Chi;

/// Twelve trung khi (odd term indices 1,3,...,23) → nguyet tuong chi.
/// Classical mapping: after dong chi (index 21) → 子, etc. Simplified table.
pub fn nguyet_tuong_for_trung_khi_index(trung_idx: u8) -> Chi {
    // trung indices 1,3,5,...,23 map to months
    // Use (trung_idx / 2) as month offset from Ty after dong chi complexity simplified:
    // index 21 (dong chi) -> Ty, then +1 each trung
    let order = [
        Chi::Suu,  // 1 vu thuy ~ after lap xuan mid
        Chi::Dan,  // 3
        Chi::Mao,  // 5
        Chi::Thin, // 7
        Chi::Ty2,  // 9
        Chi::Ngo,  // 11
        Chi::Mui,  // 13
        Chi::Than, // 15
        Chi::Dau,  // 17
        Chi::Tuat, // 19
        Chi::Hoi,  // 21 dong chi often 子 — use Ty for 21 via special
        Chi::Ty,   // 23
    ];
    if trung_idx == 21 {
        return Chi::Ty;
    }
    let i = ((trung_idx.saturating_sub(1)) / 2) as usize % 12;
    order[i]
}

/// Active nguyet tuong for a term index (must be trung khi kind for change).
pub fn nguyet_tuong_tai(active_trung_khi_index: u8) -> Chi {
    assert!(active_trung_khi_index % 2 == 1, "trung khi only");
    nguyet_tuong_for_trung_khi_index(active_trung_khi_index)
}
