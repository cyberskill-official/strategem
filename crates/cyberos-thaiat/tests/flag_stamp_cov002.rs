//! COV-002 — full co_truong_phai + co_lich_phap stamps on every TaiYi cast.

use cyberos_thaiat::{cast_thai_at, CastInput, TatFlags};

#[test]
fn taiyi_envelope_stamps_full_flags() {
    let r = cast_thai_at(&CastInput {
        nam_ce: 2004,
        year_chi_idx: 0,
        datetime: "2004-01-01T00:00:00".into(),
        tz: "+07:00".into(),
        kinh_do: 106.7,
        flags: TatFlags::default(),
    });
    let env = &r.envelope;
    assert_eq!(env["he"], "thai_at");
    let ctp = env["co_truong_phai"].as_object().expect("co_truong_phai");
    for k in ["epoch", "cap", "dem_toan", "duong_don"] {
        assert!(ctp.contains_key(k), "missing co_truong_phai.{k}");
    }
    let clp = env["lich_phap"]["co_lich_phap"]
        .as_object()
        .expect("co_lich_phap");
    assert_eq!(clp.get("stamped").and_then(|v| v.as_bool()), Some(true));
    assert!(clp.contains_key("nam_ce"));
    assert!(clp.contains_key("year_chi_idx"));
}
