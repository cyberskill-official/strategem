//! FR-TAT-004 bon phep tests (kintaiyi-aligned anchors).

use cyberos_thaiat::{
    map_1_72, tich_nguyet_ke, tich_nhat_ke, tich_nien_ke, tich_thoi_ke, Cap, Epoch,
};

#[test]
fn nien_ke_matches_tich_nien_2004() {
    // Year 2004 golden from TAT-001: cuc 33 (kim_kinh)
    let cap = tich_nien_ke(2004, Epoch::KimKinh);
    assert_eq!(cap.cap, Cap::Nien);
    assert_eq!(cap.cuc, 33);
    assert!(cap.tich > 10_000_000);
}

#[test]
fn map_1_72_zero_is_72() {
    assert_eq!(map_1_72(0), 72);
    assert_eq!(map_1_72(72), 72);
    assert_eq!(map_1_72(1), 1);
    assert_eq!(map_1_72(73), 1);
}

#[test]
fn nguyet_ke_uses_leap_offset() {
    let a = tich_nguyet_ke(2004, 1, Epoch::KimKinh, 0);
    let b = tich_nguyet_ke(2004, 1, Epoch::KimKinh, 1);
    assert_eq!(a.cap, Cap::Nguyet);
    assert_ne!(a.tich, b.tich);
    assert!((1..=72).contains(&a.cuc));
}

#[test]
fn nhat_and_thoi_circuit() {
    let d0 = tich_nhat_ke(0, true);
    assert!((1..=72).contains(&d0.cuc));
    // six days × 12 hours = 72 cuc closes a circuit
    let h0 = tich_thoi_ke(0, 0, true);
    let h71 = tich_thoi_ke(5, 11, true); // day 5 hour 11 → near full circuit
    assert!((1..=72).contains(&h0.cuc));
    assert!((1..=72).contains(&h71.cuc));
}
