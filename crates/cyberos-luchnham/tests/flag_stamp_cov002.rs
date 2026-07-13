//! COV-002 — full co_truong_phai + co_lich_phap stamps on every LiuRen cast.

use cyberos_lichphap::{Can, Chi};
use cyberos_luchnham::{cast_luc_nham, CastInput, QuyNhanVariant};

#[test]
fn liuren_envelope_stamps_full_flags() {
    let r = cast_luc_nham(&CastInput {
        datetime: "2004-01-01T10:30:00".into(),
        tz: "+07:00".into(),
        kinh_do: 106.7,
        can_ngay: Can::Giap,
        chi_ngay: Chi::Ty,
        nguyet_tuong: Chi::Hoi,
        gio_chiem: Chi::Ty,
        quy_nhan_variant: QuyNhanVariant::GiapMauCanh,
    });
    let env = &r.envelope;
    assert_eq!(env["he"], "luc_nham");
    let ctp = env["co_truong_phai"].as_object().expect("co_truong_phai");
    assert!(ctp.contains_key("quy_nhan_variant"));
    let clp = env["lich_phap"]["co_lich_phap"]
        .as_object()
        .expect("co_lich_phap");
    assert_eq!(clp.get("stamped").and_then(|v| v.as_bool()), Some(true));
    assert!(clp.contains_key("can_ngay"));
    assert!(clp.contains_key("gio_chiem"));
}
