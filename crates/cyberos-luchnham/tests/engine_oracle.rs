use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{cast_luc_nham, CastInput, QuyNhanVariant};
use laso_envelope::LaSo;

#[test]
fn worked_example_pipeline() {
    let input = CastInput {
        datetime: "2004-01-01T10:30:00".into(),
        tz: "+07:00".into(),
        kinh_do: 106.7,
        can_ngay: Can::Giap,
        chi_ngay: Chi::Ty,
        nguyet_tuong: Chi::Hoi,
        gio_chiem: Chi::Ty,
        quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
    };
    let r = cast_luc_nham(&input);
    assert_eq!(r.envelope["he"], "luc_nham");
    assert_eq!(r.envelope["envelope_version"], 1);
    assert!(r.envelope["ban"]["tu_khoa"].is_array());
    assert!(r.envelope["ban"]["tam_truyen"]["so"].is_string());
    assert!(r.envelope["co_truong_phai"]["quy_nhan_variant"] == "giap_mau_canh");
    assert!(!r.cache_key.is_empty());
    // khoa 1 of worked example: Suu over Dan
    let k0 = &r.envelope["ban"]["tu_khoa"][0];
    assert_eq!(k0[0], "丑");
    assert_eq!(k0[1], "寅");
}

#[test]
fn cache_key_stable() {
    let input = CastInput {
        datetime: "t".into(),
        tz: "+07:00".into(),
        kinh_do: 105.0,
        can_ngay: Can::Mau,
        chi_ngay: Chi::Ngo,
        nguyet_tuong: Chi::Ty,
        gio_chiem: Chi::Ngo,
        quy_nhan_variant: QuyNhanVariant::TachGiap,
    };
    let a = cast_luc_nham(&input);
    let b = cast_luc_nham(&input);
    assert_eq!(a.cache_key, b.cache_key);
    assert_eq!(a.envelope["ban"], b.envelope["ban"]);
}

#[test]
fn flag_variants_differ() {
    let base = CastInput {
        datetime: "t".into(),
        tz: "+07:00".into(),
        kinh_do: 105.0,
        can_ngay: Can::Giap,
        chi_ngay: Chi::Ty,
        nguyet_tuong: Chi::Hoi,
        gio_chiem: Chi::Ngo,
        quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
    };
    let mut other = base.clone();
    other.quy_nhan_variant = QuyNhanVariant::TachGiap;
    let a = cast_luc_nham(&base);
    let b = cast_luc_nham(&other);
    assert_ne!(
        a.envelope["ban"]["thien_tuong"],
        b.envelope["ban"]["thien_tuong"]
    );
}

#[test]
fn envelope_deserializes_as_laso_and_key_64() {
    let input = CastInput {
        datetime: "2004-01-01T10:30:00".into(),
        tz: "+07:00".into(),
        kinh_do: 106.7,
        can_ngay: Can::Giap,
        chi_ngay: Chi::Ty,
        nguyet_tuong: Chi::Hoi,
        gio_chiem: Chi::Ty,
        quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
    };
    let r = cast_luc_nham(&input);
    let la: LaSo = serde_json::from_value(r.envelope).expect("envelope must be valid LaSo");
    assert_eq!(la.provenance.engine, "ln");
    assert!(la.provenance.cast_at.timestamp() > 0);
    let key = la.provenance.cache_key.unwrap();
    assert_eq!(key.len(), 64, "cache_key must be 64 hex chars (SHA-256)");
    assert!(key.chars().all(|c| c.is_ascii_hexdigit()));
}
