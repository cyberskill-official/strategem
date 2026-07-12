use cyberos_qimen::{
    all_visible_stems, bo_dia_ban_raw, detect_cach_cuc, dinh_cuc, sao_mon_than, thap_can_khac_ung,
    truc_phu_truc_su, DingjuMethod, PanMethod, Polarity, Stem, YinYangPan, ZhongGongKy,
};
use std::collections::HashSet;

#[test]
fn eighty_one_cells_no_giap() {
    let stems = all_visible_stems();
    assert_eq!(stems.len(), 9);
    let mut n = 0;
    for &s in &stems {
        for &e in &stems {
            let _ = thap_can_khac_ung(s, e);
            n += 1;
            assert_ne!(s.glyph(), "甲");
            assert_ne!(e.glyph(), "甲");
        }
    }
    assert_eq!(n, 81);
}

#[test]
fn ordered_stem_pairs() {
    // 戊+丙 (thanh long) vs 丙+戊 (phi dieu) are distinct ordered pairs
    let dia = bo_dia_ban_raw(1, true);
    assert_eq!(dia.at_palace(1), Stem::Mau); // 戊 earth
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    let mut tps = truc_phu_truc_su(&dia, 0, 0, 1, PanMethod::Zhuan, ZhongGongKy::Khon2);
    // 丙 over 戊 → 飛鳥跌穴
    tps.thien_ban[0] = Stem::Binh;
    tps.xoay = 1; // avoid phuc ngam noise
    let ban = sao_mon_than(&tps, &d, YinYangPan::Duong);
    let hits = detect_cach_cuc(&ban, &dia, &tps);
    assert!(
        hits.iter()
            .any(|h| h.name == "飛鳥跌穴" && h.cung == Some(1)),
        "{hits:?}"
    );

    // Craft earth Binh at p=3 (cuc1 places Canh at 3 = 庚); use raw dia override via palace search
    // Put Mau on sky over a palace that has Binh on earth — find Binh palace on dia
    let binh_p = (1u8..=9).find(|p| dia.at_palace(*p) == Stem::Binh).unwrap();
    tps.thien_ban[(binh_p - 1) as usize] = Stem::Mau; // 戊 over 丙
    let hits2 = detect_cach_cuc(&ban, &dia, &tps);
    assert!(
        hits2
            .iter()
            .any(|h| h.name == "青龍返首" && h.cung == Some(binh_p)),
        "binh_p={binh_p} hits={hits2:?}"
    );
}

#[test]
fn am_lineage_light() {
    let dia = bo_dia_ban_raw(1, true);
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    let tps = truc_phu_truc_su(&dia, 0, 0, 3, PanMethod::Zhuan, ZhongGongKy::Khon2);
    let ban = sao_mon_than(&tps, &d, YinYangPan::Am);
    let hits = detect_cach_cuc(&ban, &dia, &tps);
    assert!(hits.is_empty());
}

#[test]
fn detect_on_duong_chart() {
    let dia = bo_dia_ban_raw(1, true);
    let d = dinh_cuc(0, 0, DingjuMethod::Chaibu, false).unwrap();
    let tps = truc_phu_truc_su(&dia, 0, 0, 3, PanMethod::Zhuan, ZhongGongKy::Khon2);
    let ban = sao_mon_than(&tps, &d, YinYangPan::Duong);
    let hits = detect_cach_cuc(&ban, &dia, &tps);
    let _ids: HashSet<_> = hits.iter().map(|h| h.id.as_str()).collect();
    let _ = Polarity::Cat;
}

#[test]
fn patterns_json_loads() {
    let raw = include_str!("../patterns/qimen_cach_cuc.json");
    let rows = cyberos_qimen::load_patterns_json(raw).unwrap();
    assert!(rows.len() >= 9);
}
