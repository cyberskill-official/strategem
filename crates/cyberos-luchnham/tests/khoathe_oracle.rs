use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{
    dung_than_kind, khoa_the_from_method, lap_tam_truyen, lap_tu_khoa, luc_than_of, pick_dung_than,
    quay_thien_ban, recognize_khoa_the, recognize_khoa_the_full, thiep_hai_depth, KhoaThe, LucThan,
    Phap,
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

#[test]
fn thiep_hai_depth_counts_khac_toward_home() {
    // Spirit at Dần (Mộc) over Tý (Thủy): walk Tý→Sửu→Dần; Mộc khắc Thổ at Sửu → ≥1
    let d = thiep_hai_depth(Chi::Dan, Chi::Ty);
    assert!(d >= 1, "expected at least one khac on path, got {d}");
    // Home on self: only counts ha palace itself
    let home = thiep_hai_depth(Chi::Ngo, Chi::Ngo);
    assert!(home <= 1);
}

#[test]
fn thiep_hai_path_uses_depth_not_first_stub() {
    let (thien, state) = quay_thien_ban(Chi::Hoi, Chi::Ty);
    let tk = lap_tu_khoa(&thien, Can::Giap, Chi::Ty);
    let tt = lap_tam_truyen(&tk, &thien, state, Can::Giap);
    if matches!(tt.phap, Phap::ThiepHai) {
        let hits = recognize_khoa_the(&tt);
        assert!(hits.iter().any(|h| h.name == "涉害" || h.name == "涉害課"));
    }
}

#[test]
fn l2_with_generals_context() {
    use cyberos_luchnham::{cast_luc_nham, CastInput, QuyNhanVariant};
    let input = CastInput {
        datetime: "2020-06-01T12:00:00".into(),
        tz: "+07:00".into(),
        kinh_do: 105.0,
        can_ngay: Can::Giap,
        chi_ngay: Chi::Ngo, // 甲午旬 → trống Thìn/Tỵ, not the old hardcoded Tuất/Hợi
        nguyet_tuong: Chi::Hoi,
        gio_chiem: Chi::Ty,
        quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
    };
    let r = cast_luc_nham(&input);
    assert_eq!(r.ban.khong_vong, [Chi::Thin, Chi::Ty2]);
    assert_ne!(
        r.ban.khong_vong,
        [Chi::Tuat, Chi::Hoi],
        "khong_vong must come from day pillar tuan_khong, not a hardcoded pair"
    );
    let kv = r.envelope["ban"]["khong_vong"].as_array().unwrap();
    assert_eq!(kv.len(), 2);
    let _ = recognize_khoa_the_full(
        &r.ban.tam_truyen,
        Some(&r.ban.tu_khoa),
        Some(&r.ban.thien_tuong),
    );
}
