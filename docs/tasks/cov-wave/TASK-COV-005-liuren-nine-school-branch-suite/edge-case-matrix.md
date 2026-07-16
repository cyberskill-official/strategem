# edge-case-matrix@1 — COV-005

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | BRANCHES | All 9 Phap reachable | seen contains NINE_PHAP | all_nine_branches_reachable |
| E2 | EDGE | Phuc/Phan ngam | khoa_the PhucNgam/PhanNgam | branch_phuc_and_phan_ngam |
| E3 | EDGE | Single census | TacKhac + TrongTham/NguyenThu | branch_tac_khac_single_census |
| E4 | EDGE | Multi census | TyDung / ThiepHai | branch_ty_dung_and_thiep_hai |
| E5 | EDGE | Empty census | Bat/Dao/Biet/Mao family | branch_empty_census_bat_dao_biet_mao |
| E6 | UX | khoa_the array classical names | non-Debug 元首/伏吟… | envelope_khoa_the_and_flags |
| E7 | FLAGS | quy_nhan + truong_sinh stamped | co_truong_phai keys | envelope_khoa_the_and_flags |
| E8 | GOLDEN | ≥30 LN casts | tu_khoa×4 + tam_truyen fields | golden_30_with_tu_khoa_and_tam_truyen |
| E9 | WEB | LiurenChart shows khoa_the | testid liuren-khoa-the | liuren-khoa-the-cov005.test.mjs |
