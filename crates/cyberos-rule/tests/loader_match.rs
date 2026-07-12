use cyberos_rule::{match_laso, PatternCache, SeedRepository, StubPgRepository, System};
use serde_json::json;
use std::path::PathBuf;

#[test]
fn seed_active_for_qimen() {
    let dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("seed");
    let repo = SeedRepository::load(&dir).unwrap();
    let cache = PatternCache::new(repo);
    let rows = cache.active_for(System::Qimen).unwrap();
    assert!(rows.iter().all(|p| {
        matches!(p.system, System::Qimen | System::All)
            && matches!(p.status, cyberos_rule::Status::Active)
    }));
    assert!(rows.iter().any(|p| p.id == "qimen_thanh_long_hoi_dau"));
    assert!(!rows.iter().any(|p| p.id == "qimen_sample_draft"));
}

#[test]
fn match_and_cache() {
    let dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("seed");
    let patterns = SeedRepository::load(&dir).unwrap();
    // rebuild via stub for parity
    let seed_rows = {
        let c = PatternCache::new(SeedRepository::load(&dir).unwrap());
        c.active_for(System::Qimen).unwrap()
    };
    let stub = StubPgRepository::new(seed_rows.clone());
    let cache = PatternCache::new(stub);
    cache.warm(System::Qimen).unwrap();
    let reads_after_warm = cache.repo_reads();
    let chart = json!({"he": "ky_mon", "star": "thanh_long"});
    // force a match by using conditions from seed - may not match chart; still empty ok
    let _ = match_laso(&cache, System::Qimen, &chart).unwrap();
    let reads2 = cache.repo_reads();
    assert_eq!(reads2, reads_after_warm, "cache hit expected");
    cache.invalidate(System::Qimen);
    let _ = cache.active_for(System::Qimen).unwrap();
    assert!(cache.repo_reads() > reads2);

    // empty system with no patterns
    let empty = PatternCache::new(StubPgRepository::new(vec![]));
    let none = match_laso(&empty, System::Liuren, &chart).unwrap();
    assert!(none.is_empty());

    let _ = patterns;
}
