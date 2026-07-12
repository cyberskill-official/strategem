use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{
    is_thuan_bo, khoi_from_gio, lap_thien_tuong, quy_nhan_palace, KhoiQuyNhan, QuyNhanVariant,
    ThienTuong,
};

#[test]
fn day_night_window() {
    assert_eq!(khoi_from_gio(Chi::Mao), KhoiQuyNhan::TruQuy);
    assert_eq!(khoi_from_gio(Chi::Than), KhoiQuyNhan::TruQuy);
    assert_eq!(khoi_from_gio(Chi::Dau), KhoiQuyNhan::DaQuy);
    assert_eq!(khoi_from_gio(Chi::Dan), KhoiQuyNhan::DaQuy);
}

#[test]
fn quy_nhan_table() {
    assert_eq!(
        quy_nhan_palace(Can::Giap, KhoiQuyNhan::TruQuy, QuyNhanVariant::GiapMauCanh),
        Chi::Suu
    );
    assert_eq!(
        quy_nhan_palace(Can::Giap, KhoiQuyNhan::DaQuy, QuyNhanVariant::GiapMauCanh),
        Chi::Mui
    );
    assert_eq!(
        quy_nhan_palace(Can::Giap, KhoiQuyNhan::TruQuy, QuyNhanVariant::TachGiap),
        Chi::Mui
    );
}

#[test]
fn thuan_nghich_halves() {
    assert!(is_thuan_bo(Chi::Ty));
    assert!(is_thuan_bo(Chi::Hoi));
    assert!(!is_thuan_bo(Chi::Ngo));
    assert!(!is_thuan_bo(Chi::Ty2));
}

#[test]
fn arrangement_bijection() {
    let ban = lap_thien_tuong(Can::Giap, Chi::Ngo, QuyNhanVariant::GiapMauCanh);
    let mut seen = [false; 12];
    for g in ban.generals {
        let i = ThienTuong::SEQ.iter().position(|x| *x == g).unwrap();
        assert!(!seen[i]);
        seen[i] = true;
    }
    assert!(seen.iter().all(|x| *x));
    assert_eq!(
        ban.generals[ban.quy_nhan_palace.index() as usize],
        ThienTuong::QuyNhan
    );
}

#[test]
fn polarity_sets() {
    assert_eq!(ThienTuong::QuyNhan.polarity(), "cat");
    assert_eq!(ThienTuong::BachHo.polarity(), "hung");
    assert_eq!(ThienTuong::ThienKhong.polarity(), "trung");
}
