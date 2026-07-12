use cyberos_lichphap::Can;
use cyberos_lichphap::Chi;
use cyberos_luchnham::{
    dia_ban, ky_cung, nguyet_tuong_tai, quay_thien_ban, thien_over, TrangThaiBan,
};

#[test]
fn rotation_all_pairs_bijection() {
    for nt in Chi::ALL {
        for gio in Chi::ALL {
            let (thien, _) = quay_thien_ban(nt, gio);
            let mut seen = [false; 12];
            for c in thien {
                assert!(!seen[c.index() as usize]);
                seen[c.index() as usize] = true;
            }
            let offset = (nt.index() as i32 - gio.index() as i32).rem_euclid(12) as u8;
            let dia = dia_ban();
            for i in 0..12 {
                assert_eq!(thien[i], dia[((i as u8 + offset) % 12) as usize]);
            }
        }
    }
}

#[test]
fn phuc_phan_ngam() {
    let (t, s) = quay_thien_ban(Chi::Ty, Chi::Ty);
    assert_eq!(s, TrangThaiBan::PhucNgam);
    assert_eq!(t, dia_ban());
    let (t2, s2) = quay_thien_ban(Chi::Ty, Chi::Ngo);
    assert_eq!(s2, TrangThaiBan::PhanNgam);
    let dia = dia_ban();
    for i in 0..12 {
        assert_eq!(t2[i], dia[(i + 6) % 12]);
    }
}

#[test]
fn worked_example_hoi_ty() {
    // nguyet tuong Hoi, gio Ty → offset 11
    let (thien, _) = quay_thien_ban(Chi::Hoi, Chi::Ty);
    let dia = dia_ban();
    // Suu over Dan, Ty over Suu, Hoi over Ty, Tuat over Hoi
    assert_eq!(thien_over(&dia, &thien, Chi::Dan), Chi::Suu);
    assert_eq!(thien_over(&dia, &thien, Chi::Suu), Chi::Ty);
    assert_eq!(thien_over(&dia, &thien, Chi::Ty), Chi::Hoi);
    assert_eq!(thien_over(&dia, &thien, Chi::Hoi), Chi::Tuat);
}

#[test]
fn ky_cung_never_cardinal() {
    let banned = [Chi::Ty, Chi::Ngo, Chi::Mao, Chi::Dau];
    for c in Can::ALL {
        let k = ky_cung(c);
        assert!(!banned.contains(&k), "{:?} -> {:?}", c, k);
    }
}

#[test]
fn nguyet_tuong_trung_only() {
    assert_eq!(nguyet_tuong_tai(21), Chi::Ty);
}
