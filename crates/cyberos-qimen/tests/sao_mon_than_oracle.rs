use cyberos_qimen::{
    bo_dia_ban_raw, dinh_cuc, sao_mon_than, truc_phu_truc_su, BatMon, CuuTinh, DingjuMethod,
    PanMethod, YinYangPan, ZhongGongKy,
};

#[test]
fn resting_stars() {
    assert_eq!(CuuTinh::REST[0], CuuTinh::ThienBong);
    assert_eq!(CuuTinh::REST[4], CuuTinh::ThienCam);
    assert_eq!(CuuTinh::REST[8], CuuTinh::ThienAnh);
}

#[test]
fn resting_doors_and_cat() {
    assert_eq!(BatMon::REST[0], Some(BatMon::Huu));
    assert_eq!(BatMon::REST[4], None);
    assert_eq!(BatMon::REST[5], Some(BatMon::Khai));
    for m in [
        BatMon::Huu,
        BatMon::Sinh,
        BatMon::Thuong,
        BatMon::Do,
        BatMon::Canh,
        BatMon::Tu,
        BatMon::Kinh,
        BatMon::Khai,
    ] {
        assert_eq!(m.is_cat(), matches!(m, BatMon::Khai | BatMon::Huu | BatMon::Sinh));
    }
}

#[test]
fn placement_rings() {
    let dia = bo_dia_ban_raw(1, true);
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    let tps = truc_phu_truc_su(&dia, 0, 0, 3, PanMethod::Zhuan, ZhongGongKy::Khon2);
    let sm = sao_mon_than(&tps, &d, YinYangPan::Duong);
    assert_eq!(sm.bat_mon[4], None);
    assert!(sm.bat_than.iter().filter(|g| g.is_some()).count() == 8);
}

#[test]
fn god_direction_differs_by_don() {
    let dia = bo_dia_ban_raw(1, true);
    let mut d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    d.duong_don = true;
    let tps = truc_phu_truc_su(&dia, 0, 0, 3, PanMethod::Zhuan, ZhongGongKy::Khon2);
    let a = sao_mon_than(&tps, &d, YinYangPan::Duong);
    d.duong_don = false;
    let b = sao_mon_than(&tps, &d, YinYangPan::Duong);
    assert_ne!(a.bat_than, b.bat_than);
}

#[test]
fn am_duong_god_swap() {
    let dia = bo_dia_ban_raw(1, true);
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    let tps = truc_phu_truc_su(&dia, 0, 0, 3, PanMethod::Zhuan, ZhongGongKy::Khon2);
    let duong = sao_mon_than(&tps, &d, YinYangPan::Duong);
    let am = sao_mon_than(&tps, &d, YinYangPan::Am);
    assert_ne!(duong.bat_than, am.bat_than);
}
