use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{
    dung_than_kind, khoa_the_from_method, lap_tam_truyen, lap_tu_khoa, luc_than_of, pick_dung_than,
    quay_thien_ban, recognize_khoa_the, KhoaThe, LucThan,
};

#[test]
fn layer_one_from_method() {
    let (thien, state) = quay_thien_ban(Chi::Hoi, Chi::Ty);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    let tt = lap_tam_truyen(&tk, &thien, state, Can::Giap);
    let hit = khoa_the_from_method(&tt);
    assert_eq!(hit.layer, 1);
    assert!(!hit.name.is_empty());
    let all = recognize_khoa_the(&tt);
    assert!(!all.is_empty());
}

#[test]
fn phuc_ngam_hits() {
    let (thien, state) = quay_thien_ban(Chi::Ty, Chi::Ty);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    let tt = lap_tam_truyen(&tk, &thien, state, Can::Giap);
    assert_eq!(tt.khoa_the, KhoaThe::PhucNgam);
    let hits = recognize_khoa_the(&tt);
    assert!(hits.iter().any(|h| h.name == "伏吟"));
    assert!(hits.iter().any(|h| h.layer == 2));
}

#[test]
fn luc_than_cycle() {
    // Giap = Moc
    // Thuy generates Moc → PhuMau
    assert_eq!(luc_than_of(Chi::Ty, Can::Giap), LucThan::PhuMau);
    // Moc generates Hoa (Ngo) → TuTon
    assert_eq!(luc_than_of(Chi::Ngo, Can::Giap), LucThan::TuTon);
    // Moc controls Tho (Suu) → TheTai
    assert_eq!(luc_than_of(Chi::Suu, Can::Giap), LucThan::TheTai);
    // same Moc (Dan) → HuynhDe
    assert_eq!(luc_than_of(Chi::Dan, Can::Giap), LucThan::HuynhDe);
    // Kim controls Moc → QuanQuy (Dau)
    assert_eq!(luc_than_of(Chi::Dau, Can::Giap), LucThan::QuanQuy);
}

#[test]
fn dung_than_mapping() {
    assert_eq!(dung_than_kind("tai_loc"), LucThan::TheTai);
    assert_eq!(dung_than_kind("cong_danh"), LucThan::QuanQuy);
    let cands = Chi::ALL;
    let d = pick_dung_than(Can::Giap, &cands, "tai_loc");
    assert!(d.is_some());
    assert_eq!(luc_than_of(d.unwrap(), Can::Giap), LucThan::TheTai);
}
