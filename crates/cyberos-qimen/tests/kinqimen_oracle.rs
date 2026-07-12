use cyberos_qimen::{
    cast_qimen, DingjuMethod, PanMethod, QiMenFlags, QimenCastInput, YinYangPan, ZhongGongKy,
};

fn default_input(flags: QiMenFlags) -> QimenCastInput {
    QimenCastInput {
        datetime: "2004-01-01T10:30:00".into(),
        tz: "+07:00".into(),
        kinh_do: 106.7,
        term_index: 0,
        branch_index: 0,
        hour_can: 0,
        hour_chi: 0,
        hour_stem_palace: 3,
        flags,
    }
}

#[test]
fn default_cast_envelope() {
    let r = cast_qimen(&default_input(QiMenFlags::default())).unwrap();
    assert_eq!(r.envelope["he"], "ky_mon");
    assert_eq!(r.envelope["envelope_version"], 1);
    assert!(r.envelope["ban"]["dia_ban"].is_array());
    assert!(r.envelope["ban"]["thien_ban"].is_array());
    assert!(r.envelope["co_truong_phai"]["dingju_method"].is_string());
    assert!(!r.cache_key.is_empty());
}

#[test]
fn flag_matrix_all_combinations() {
    for dingju in [
        DingjuMethod::Chaibu,
        DingjuMethod::Zhirun,
        DingjuMethod::Maoshan,
    ] {
        for pan in [PanMethod::Zhuan, PanMethod::Fei] {
            for yy in [YinYangPan::Duong, YinYangPan::Am] {
                for zg in [ZhongGongKy::Khon2, ZhongGongKy::GiuNguyen] {
                    for solar in [true, false] {
                        let flags = QiMenFlags {
                            dingju_method: dingju,
                            pan_method: pan,
                            yin_yang_pan: yy,
                            zhong_gong_ky: zg,
                            chan_thai_duong_thoi: solar,
                        };
                        let r = cast_qimen(&default_input(flags)).unwrap();
                        assert_eq!(r.envelope["he"], "ky_mon");
                        assert_eq!(r.ban.dia_ban.cung.len(), 9);
                    }
                }
            }
        }
    }
}

#[test]
fn reproducible_cache_key() {
    let f = QiMenFlags::default();
    let a = cast_qimen(&default_input(f)).unwrap();
    let b = cast_qimen(&default_input(f)).unwrap();
    assert_eq!(a.cache_key, b.cache_key);
    assert_eq!(a.envelope["ban"], b.envelope["ban"]);
}

#[test]
fn pan_method_diverges() {
    let mut a = QiMenFlags::default();
    a.pan_method = PanMethod::Zhuan;
    let mut b = QiMenFlags::default();
    b.pan_method = PanMethod::Fei;
    let ra = cast_qimen(&default_input(a)).unwrap();
    let rb = cast_qimen(&default_input(b)).unwrap();
    assert_ne!(ra.envelope["ban"]["thien_ban"], rb.envelope["ban"]["thien_ban"]);
}
