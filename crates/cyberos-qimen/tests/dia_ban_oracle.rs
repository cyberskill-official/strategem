use cyberos_qimen::{bo_dia_ban, bo_dia_ban_raw, dinh_cuc, DingjuMethod, Stem};

#[test]
fn duong_don_cuc_1_worked_table() {
    // Claude-03 s4.2: start Kham 1 → Mau … Ly 9 → At
    let dia = bo_dia_ban_raw(1, true);
    let expected = [
        Stem::Mau,  // 1
        Stem::Ky,   // 2
        Stem::Canh, // 3
        Stem::Tan,  // 4
        Stem::Nham, // 5
        Stem::Quy,  // 6
        Stem::Dinh, // 7
        Stem::Binh, // 8
        Stem::At,   // 9
    ];
    assert_eq!(dia.cung, expected);
}

#[test]
fn all_cuc_duong_permutation() {
    for cuc in 1u8..=9 {
        let dia = bo_dia_ban_raw(cuc, true);
        let mut seen = [false; 9];
        for s in dia.cung {
            let i = Stem::SEQ.iter().position(|x| *x == s).unwrap();
            assert!(!seen[i], "duplicate {:?}", s);
            seen[i] = true;
        }
        assert!(seen.iter().all(|x| *x));
        assert_eq!(dia.at_palace(cuc), Stem::Mau);
    }
}

#[test]
fn am_don_steps_backward() {
    let dia = bo_dia_ban_raw(1, false);
    // start 1 Mau, then 9 At? wait: sequence Mau,Ky,... so next after 1 is nghich → 9
    assert_eq!(dia.at_palace(1), Stem::Mau);
    assert_eq!(dia.at_palace(9), Stem::Ky);
    assert_eq!(dia.at_palace(8), Stem::Canh);
    // all nine stems present
    let mut seen = [false; 9];
    for s in dia.cung {
        let i = Stem::SEQ.iter().position(|x| *x == s).unwrap();
        seen[i] = true;
    }
    assert!(seen.iter().all(|x| *x));
}

#[test]
fn no_giap_on_plate() {
    for cuc in 1u8..=9 {
        for duong in [true, false] {
            let dia = bo_dia_ban_raw(cuc, duong);
            for s in dia.cung {
                assert_ne!(s.glyph(), "甲");
            }
        }
    }
}

#[test]
fn from_dinh_cuc() {
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    let dia = bo_dia_ban(&d);
    assert_eq!(dia.at_palace(d.so_cuc), Stem::Mau);
}
