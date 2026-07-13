//! COV-002 — full co_truong_phai + co_lich_phap stamps on every QiMen cast.

use cyberos_qimen::{cast_qimen, QiMenFlags, QimenCastInput};

#[test]
fn qimen_envelope_stamps_full_flags() {
    let r = cast_qimen(&QimenCastInput {
        datetime: "2004-01-01T10:30:00".into(),
        tz: "+07:00".into(),
        kinh_do: 106.7,
        term_index: 0,
        branch_index: 0,
        hour_can: 0,
        hour_chi: 0,
        hour_stem_palace: 3,
        flags: QiMenFlags::default(),
    })
    .unwrap();
    let env = &r.envelope;
    assert_eq!(env["he"], "ky_mon");
    let ctp = env["co_truong_phai"].as_object().expect("co_truong_phai");
    for k in [
        "dingju_method",
        "pan_method",
        "yin_yang_pan",
        "zhong_gong_ky",
        "chan_thai_duong_thoi",
    ] {
        assert!(ctp.contains_key(k), "missing co_truong_phai.{k}");
    }
    let clp = env["lich_phap"]["co_lich_phap"]
        .as_object()
        .expect("co_lich_phap");
    assert_eq!(clp.get("stamped").and_then(|v| v.as_bool()), Some(true));
    assert!(clp.contains_key("tz"));
    assert!(clp.contains_key("longitude"));
    assert!(clp.contains_key("term_index"));
}
