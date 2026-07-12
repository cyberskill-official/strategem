use cyberos_rule::{load_seed, validate_pattern, Pattern, Status};
use serde_json::json;
use std::path::PathBuf;

fn sample() -> serde_json::Value {
    let p =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/patterns_seed_sample.json");
    serde_json::from_str(&std::fs::read_to_string(p).unwrap()).unwrap()
}

#[test]
fn valid_sample_ok() {
    let p = validate_pattern(&sample()).unwrap();
    assert_eq!(p.stamp(), ("qimen_sample_ok".into(), 1));
}

#[test]
fn reject_unknown_field() {
    let mut v = sample();
    v.as_object_mut().unwrap().insert("nope".into(), json!(1));
    assert!(validate_pattern(&v).is_err());
}

#[test]
fn reject_bad_system_confidence_version() {
    let mut v = sample();
    v["system"] = json!("nope");
    assert!(validate_pattern(&v).is_err());
    let mut v = sample();
    v["confidence"] = json!(1.5);
    let err = validate_pattern(&v).unwrap_err();
    assert!(err.iter().any(|e| e.field == "confidence"));
    let mut v = sample();
    v["version"] = json!(0);
    let err = validate_pattern(&v).unwrap_err();
    assert!(err.iter().any(|e| e.field == "version"));
}

#[test]
fn active_requires_citations() {
    let mut v = sample();
    v["citations"] = json!([]);
    v["status"] = json!("active");
    let err = validate_pattern(&v).unwrap_err();
    assert!(err.iter().any(|e| e.field == "citations"));
}

#[test]
fn conditions_shallow_check() {
    for bad in [json!([]), json!("x"), json!({}), json!({"foo": 1})] {
        let mut v = sample();
        v["conditions"] = bad;
        assert!(validate_pattern(&v).is_err());
    }
}

#[test]
fn load_seed_qimen_ok() {
    let dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("seed");
    let patterns = load_seed(&dir).unwrap();
    assert!(patterns.len() >= 2);
    assert!(patterns.iter().any(|p| p.id == "qimen_thanh_long_hoi_dau"));
}

#[test]
fn load_seed_fails_on_malformed() {
    let tmp = tempfile_dir();
    std::fs::write(
        tmp.join("bad.json"),
        r#"[{"id":"broken","system":"qimen","name":"x","conditions":{},"polarity":"cat","meaning_classical":"a","meaning_modern":"b","version":1,"confidence":0.5,"status":"active","citations":["c"]}]"#,
    )
    .unwrap();
    let err = load_seed(&tmp).unwrap_err();
    let msg = err.to_string();
    assert!(
        msg.contains("broken") || msg.contains("conditions"),
        "{msg}"
    );
}

#[test]
fn round_trip_stable() {
    let p: Pattern = serde_json::from_value(sample()).unwrap();
    let j = serde_json::to_value(&p).unwrap();
    let p2: Pattern = serde_json::from_value(j).unwrap();
    assert_eq!(p, p2);
    assert_eq!(p.status, Status::Active);
}

fn tempfile_dir() -> PathBuf {
    let dir = std::env::temp_dir().join(format!("cyberos-rule-seed-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}
