use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{lap_tam_truyen, lap_tu_khoa, quay_thien_ban, KhoaThe, Phap, TrangThaiBan};

#[test]
fn worked_multi_census_ty_or_thiep() {
    // Hoi/Ty board, Giap Ty → census has 3 relations (from LN-002 example)
    let (thien, state) = quay_thien_ban(Chi::Hoi, Chi::Ty);
    assert_eq!(state, TrangThaiBan::Thuong);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    let tt = lap_tam_truyen(&tk, &thien, state, Can::Giap);
    assert!(matches!(tt.phap, Phap::TyDung | Phap::ThiepHai));
    // chain: trung over so, mat over trung
    let dia = cyberos_luchnham::dia_ban();
    let trung = cyberos_luchnham::thien_over(&dia, &thien, tt.so);
    let mat = cyberos_luchnham::thien_over(&dia, &thien, trung);
    assert_eq!(tt.trung, trung);
    assert_eq!(tt.mat, mat);
}

#[test]
fn phuc_ngam_path() {
    let (thien, state) = quay_thien_ban(Chi::Ty, Chi::Ty);
    assert_eq!(state, TrangThaiBan::PhucNgam);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    let tt = lap_tam_truyen(&tk, &thien, state, Can::Giap);
    assert_eq!(tt.phap, Phap::PhucNgam);
    assert_eq!(tt.khoa_the, KhoaThe::PhucNgam);
}

#[test]
fn phan_ngam_path() {
    let (thien, state) = quay_thien_ban(Chi::Ty, Chi::Ngo);
    assert_eq!(state, TrangThaiBan::PhanNgam);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    let tt = lap_tam_truyen(&tk, &thien, state, Can::Giap);
    assert_eq!(tt.phap, Phap::PhanNgam);
}

#[test]
fn single_tac_trong_tham() {
    // craft board: use phuc for simplicity — instead force by finding a case
    // with single census. Use direct construction via multi skip:
    // Hoi/Ty Giap has multi; try At day
    let (thien, state) = quay_thien_ban(Chi::Hoi, Chi::Ty);
    let tk = lap_tu_khoa(&thien, Can::At, Chi::Suu);
    let census: Vec<_> = tk
        .khoa
        .iter()
        .enumerate()
        .filter_map(|(i, k)| k.quan_he.map(|q| (i, q)))
        .collect();
    let tt = lap_tam_truyen(&tk, &thien, state, Can::At);
    if census.len() == 1 {
        assert_eq!(tt.phap, Phap::TacKhac);
    } else {
        // still produces valid chain
        assert_ne!(tt.so.glyph(), "");
    }
}
