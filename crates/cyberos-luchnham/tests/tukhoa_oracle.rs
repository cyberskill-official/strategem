use cyberos_lichphap::{khac, ngu_hanh_of_can, ngu_hanh_of_chi};
use cyberos_lichphap::{Can, Chi, NguHanh};
use cyberos_luchnham::{
    census_khac_tac, ky_cung, lap_tu_khoa, quan_he_khoa, quay_thien_ban, KhacTac,
};

#[test]
fn worked_example_giap_ty_hoi() {
    // Nguyet tuong Hoi, gio Ty, day Giap Ty
    let (thien, _) = quay_thien_ban(Chi::Hoi, Chi::Ty);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    // pairs (thuong, ha palace)
    assert_eq!(tk.khoa[0].thuong_than, Chi::Suu);
    assert_eq!(tk.khoa[0].ha_than, Chi::Dan); // Giap ky cung
    assert!(tk.khoa[0].la_can_khoa);
    assert_eq!(tk.khoa[1].thuong_than, Chi::Ty);
    assert_eq!(tk.khoa[1].ha_than, Chi::Suu);
    assert_eq!(tk.khoa[2].thuong_than, Chi::Hoi);
    assert_eq!(tk.khoa[2].ha_than, Chi::Ty);
    assert_eq!(tk.khoa[3].thuong_than, Chi::Tuat);
    assert_eq!(tk.khoa[3].ha_than, Chi::Hoi);

    assert_eq!(tk.khoa[0].quan_he, Some(KhacTac::TacHaThuong));
    assert_eq!(tk.khoa[1].quan_he, Some(KhacTac::TacHaThuong));
    assert_eq!(tk.khoa[2].quan_he, None);
    assert_eq!(tk.khoa[3].quan_he, Some(KhacTac::KhacThuongHa));

    let census = census_khac_tac(&tk);
    assert_eq!(
        census,
        vec![
            (0, KhacTac::TacHaThuong),
            (1, KhacTac::TacHaThuong),
            (3, KhacTac::KhacThuongHa),
        ]
    );
}

#[test]
fn chained_construction() {
    for nt in Chi::ALL {
        for gio in Chi::ALL {
            let (thien, _) = quay_thien_ban(nt, gio);
            for can in Can::ALL {
                for chi in Chi::ALL {
                    let tk = lap_tu_khoa(&thien, can, chi);
                    assert_eq!(tk.khoa[1].ha_than, tk.khoa[0].thuong_than);
                    assert_eq!(tk.khoa[3].ha_than, tk.khoa[2].thuong_than);
                }
            }
        }
    }
}

#[test]
fn quan_he_all_25_pairs() {
    let all = [
        NguHanh::Moc,
        NguHanh::Hoa,
        NguHanh::Tho,
        NguHanh::Kim,
        NguHanh::Thuy,
    ];
    for &t in &all {
        for &h in &all {
            let q = quan_he_khoa(t, h);
            if khac(t, h) {
                assert_eq!(q, Some(KhacTac::KhacThuongHa));
            } else if khac(h, t) {
                assert_eq!(q, Some(KhacTac::TacHaThuong));
            } else {
                assert_eq!(q, None);
            }
        }
    }
}

#[test]
fn mau_day_uses_stem_element() {
    // Mau 戊 = Tho; ky cung Ti 巳 = Hoa — diverge
    assert_eq!(ngu_hanh_of_can(Can::Mau), NguHanh::Tho);
    assert_eq!(ngu_hanh_of_chi(ky_cung(Can::Mau)), NguHanh::Hoa);

    // Offset 3 so thien over Ty2 is Than (Kim): stem Tho vs Kim = none;
    // branch Hoa vs Kim = upper controls lower (Hoa khac Kim).
    let (thien, _) = quay_thien_ban(Chi::Mao, Chi::Ty);
    let tk = lap_tu_khoa(&thien, Can::Mau, Chi::Ty);
    let thuong = tk.khoa[0].thuong_than;
    assert_eq!(thuong, Chi::Than);
    let via_stem = quan_he_khoa(ngu_hanh_of_chi(thuong), NguHanh::Tho);
    let via_branch = quan_he_khoa(ngu_hanh_of_chi(thuong), NguHanh::Hoa);
    assert_ne!(via_stem, via_branch);
    assert_eq!(via_stem, None);
    // Hoa (branch) controls Kim (upper) → tac
    assert_eq!(via_branch, Some(KhacTac::TacHaThuong));
    assert_eq!(tk.khoa[0].quan_he, via_stem);
}
