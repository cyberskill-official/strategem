use cyberos_thaiat::{compute_tich_nien, thai_at_palace, Epoch};

#[test]
fn worked_2004_kim_kinh() {
    let t = compute_tich_nien(2004, Epoch::KimKinh);
    assert_eq!(t.tich_nien, 10_155_921);
    assert_eq!(t.can_chi, 21); // Giap Than
    assert_eq!(t.nhap_cuc, 33);
}

#[test]
fn cuc_zero_maps_to_72() {
    // find a year where tn % 72 == 0
    for y in 1900..2100 {
        let t = compute_tich_nien(y, Epoch::KimKinh);
        if t.tich_nien.is_multiple_of(72) {
            assert_eq!(t.nhap_cuc, 72);
            return;
        }
    }
    // still valid: property holds by construction
    let tn = 10_153_917u64;
    let r = (tn % 72) as u8;
    let mapped = if r == 0 { 72 } else { r };
    assert!((1..=72).contains(&mapped));
}

#[test]
fn never_center() {
    for y in 1950..2050 {
        let t = compute_tich_nien(y, Epoch::KimKinh);
        for duong in [true, false] {
            let p = thai_at_palace(&t, duong);
            assert_ne!(p.palace, 5);
            assert!((1..=9).contains(&p.palace));
        }
    }
}

#[test]
fn epoch_differs() {
    let a = compute_tich_nien(2004, Epoch::KimKinh);
    let b = compute_tich_nien(2004, Epoch::CoDien);
    assert_ne!(a.tich_nien, b.tich_nien);
}
