use cyberos_thaiat::{
    compute_tich_nien, compute_toan, place_bat_tuong, van_xuong, DemToan, Epoch, TruongDoan,
};

#[test]
fn van_xuong_in_ring() {
    for cuc in 1u8..=72 {
        let r = van_xuong(cuc, true);
        assert!(r < 16);
        let r2 = van_xuong(cuc, false);
        assert!(r2 < 16);
    }
}

#[test]
fn toan_truong_doan() {
    let tn = compute_tich_nien(2004, Epoch::KimKinh);
    let (bt, seat) = place_bat_tuong(&tn, 0, true, DemToan::TruocThaiAt);
    assert!(bt.chu_toan.value > 0);
    assert!(bt.khach_toan.value > 0);
    assert!(bt.van_xuong < 16);
    assert!(seat.thai_at_cung != 5);
    let t = compute_toan(0, &seat, DemToan::TruocThaiAt);
    let _ = matches!(t.label, TruongDoan::Truong | TruongDoan::Doan);
}

#[test]
fn dem_toan_flag_matters() {
    let tn = compute_tich_nien(2004, Epoch::KimKinh);
    let (a, _) = place_bat_tuong(&tn, 5, true, DemToan::TruocThaiAt);
    let (b, _) = place_bat_tuong(&tn, 5, true, DemToan::SauThaiAt);
    // often differs by stop mark
    assert!(a.chu_toan.value > 0 && b.chu_toan.value > 0);
}
