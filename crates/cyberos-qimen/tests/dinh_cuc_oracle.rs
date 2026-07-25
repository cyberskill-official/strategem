use cyberos_qimen::{
    dinh_cuc, luoshu_governed_terms, luoshu_outer, phu_dau_nguyen, table_duong_don, table_so_cuc,
    DingjuMethod,
};

#[test]
fn table_72_cells() {
    for t in 0u8..24 {
        for n in 0u8..3 {
            let s = table_so_cuc(t, n);
            assert!((1..=9).contains(&s), "term={t} nguyen={n} so_cuc={s}");
        }
    }
}

#[test]
fn classical_pins_dong_chi_ha_chi() {
    // TASK-QMDG-001 AC example: Đông Chí thượng → 1 dương; Hạ Chí thượng → 9 âm
    assert_eq!(table_so_cuc(21, 0), 1);
    assert!(table_duong_don(21));
    assert_eq!(table_so_cuc(9, 0), 9);
    assert!(!table_duong_don(9));
    let dong = dinh_cuc(21, 0, DingjuMethod::Chaibu, false).unwrap();
    assert_eq!(dong.so_cuc, 1);
    assert!(dong.duong_don);
    let ha = dinh_cuc(9, 0, DingjuMethod::Chaibu, false).unwrap();
    assert_eq!(ha.so_cuc, 9);
    assert!(!ha.duong_don);
}

#[test]
fn luoshu_structural_invariant() {
    let outer = luoshu_outer();
    let terms = luoshu_governed_terms();
    assert_eq!(outer.len(), 8);
    for (i, &palace) in outer.iter().enumerate() {
        let term = terms[i];
        let cuc = table_so_cuc(term, 0);
        assert_eq!(
            cuc, palace,
            "palace {palace} must equal thuong nguyen of term {term}, got {cuc}"
        );
    }
}

#[test]
fn phu_dau_classical_branches() {
    // Tý/Ngọ/Mão/Dậu → thượng
    for b in [0u8, 3, 6, 9] {
        assert_eq!(phu_dau_nguyen(b), 1, "branch {b}");
    }
    // Dần/Thân/Tỵ/Hợi → trung
    for b in [2u8, 5, 8, 11] {
        assert_eq!(phu_dau_nguyen(b), 2, "branch {b}");
    }
    // Thìn/Tuất/Sửu/Mùi → hạ
    for b in [1u8, 4, 7, 10] {
        assert_eq!(phu_dau_nguyen(b), 3, "branch {b}");
    }
}

#[test]
fn methods_differ_on_boundary() {
    let a = dinh_cuc(8, 0, DingjuMethod::Chaibu, false).unwrap();
    let b = dinh_cuc(8, 0, DingjuMethod::Maoshan, false).unwrap();
    // Maoshan shifts nguyen; so_cuc may differ
    assert_ne!(a.nguyen, b.nguyen);
    assert!(dinh_cuc(8, 0, DingjuMethod::Zhirun, true).is_ok());
    assert!(dinh_cuc(0, 0, DingjuMethod::Zhirun, true).is_err());
    assert!(dinh_cuc(8, 0, DingjuMethod::Chaibu, true).is_err());
}

#[test]
fn fixture_sample_matches_table() {
    // Classical: Lập Xuân thượng = 8 dương
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    assert_eq!(d.so_cuc, 8);
    assert_eq!(d.so_cuc, table_so_cuc(0, 0));
    assert!(d.duong_don);
    assert_eq!(d.duong_don, table_duong_don(0));
}

#[test]
fn duong_am_halves() {
    for t in 0u8..=8 {
        assert!(table_duong_don(t), "term {t} should be dương");
    }
    for t in 9u8..=20 {
        assert!(!table_duong_don(t), "term {t} should be âm");
    }
    for t in 21u8..=23 {
        assert!(table_duong_don(t), "term {t} should be dương");
    }
}
