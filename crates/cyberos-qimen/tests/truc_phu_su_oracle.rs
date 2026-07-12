use cyberos_qimen::{
    bo_dia_ban_raw, palace_of_stem, rotate_zhuan, truc_phu_truc_su, tuan_thu_from_hour, PanMethod,
    Stem, ZhongGongKy,
};

#[test]
fn six_tuan_hidden_nghi() {
    // (can, chi) pairs on each tuan head (Giap + head chi)
    let cases = [
        (0u8, 0u8, Stem::Mau), // 甲子
        (0, 10, Stem::Ky),     // 甲戌
        (0, 8, Stem::Canh),    // 甲申
        (0, 6, Stem::Tan),     // 甲午
        (0, 4, Stem::Nham),    // 甲辰
        (0, 2, Stem::Quy),     // 甲寅
    ];
    for (c, z, n) in cases {
        let (head, nghi) = tuan_thu_from_hour(c, z);
        assert_eq!(head, z);
        assert_eq!(nghi, n);
    }
}

#[test]
fn sixty_hours_map_to_valid_tuan() {
    for can in 0u8..10 {
        for chi in 0u8..12 {
            if (can % 2) != (chi % 2) {
                continue; // invalid parity
            }
            let (head, nghi) = tuan_thu_from_hour(can, chi);
            assert!(matches!(head, 0 | 2 | 4 | 6 | 8 | 10));
            let _ = nghi;
        }
    }
}

#[test]
fn tuan_thu_palace_matches_dia_ban() {
    let dia = bo_dia_ban_raw(1, true);
    let nghi = Stem::Mau;
    assert_eq!(palace_of_stem(&dia, nghi), 1);
    let r = truc_phu_truc_su(&dia, 0, 0, 3, PanMethod::Zhuan, ZhongGongKy::Khon2);
    assert_eq!(r.nghi_an, Stem::Mau);
    assert_eq!(r.cung_tuan_thu, 1);
}

#[test]
fn zhuan_rigid_rotation() {
    let dia = bo_dia_ban_raw(1, true);
    let (sky, xoay) = rotate_zhuan(&dia, 1, 3);
    assert_eq!(xoay, 2);
    // stem that was at 1 (Mau) now at 3
    assert_eq!(sky[2], Stem::Mau);
}

#[test]
fn zhuan_fei_diverge() {
    let dia = bo_dia_ban_raw(1, true);
    let a = truc_phu_truc_su(&dia, 0, 0, 7, PanMethod::Zhuan, ZhongGongKy::Khon2);
    let b = truc_phu_truc_su(&dia, 0, 0, 7, PanMethod::Fei, ZhongGongKy::Khon2);
    assert_ne!(a.thien_ban, b.thien_ban);
}

#[test]
fn center_lodging_khon2() {
    let dia = bo_dia_ban_raw(5, true);
    let r = truc_phu_truc_su(&dia, 0, 0, 5, PanMethod::Zhuan, ZhongGongKy::Khon2);
    assert_eq!(r.cung_gio, 2); // 5 lodges to 2
    let r2 = truc_phu_truc_su(&dia, 0, 0, 5, PanMethod::Zhuan, ZhongGongKy::GiuNguyen);
    assert_eq!(r2.cung_gio, 5);
}
