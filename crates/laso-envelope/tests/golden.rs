//! Golden fixture tests for the la so envelope contract (PLAT-002).
//!
//! - Loads one fixture per `he`.
//! - Round-trips through serde (simulates Rust <-> wire <-> Rust).
//! - Asserts version enforcement.
//! - Asserts cache_key stability and determinism.
//! - The Python side will run equivalent tests on the same fixture files.
//!
//! This is the cross-language contract test anchor.

use std::fs;
use std::path::Path;

use laso_envelope::{cache_key, require_supported_version, EnvelopeError, LaSo, ENVELOPE_VERSION};

fn load_fixture(name: &str) -> LaSo {
    let path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures")
        .join(name);
    let s = fs::read_to_string(&path).expect("fixture must exist");
    serde_json::from_str(&s).expect("fixture must parse to LaSo")
}

#[test]
fn ky_mon_golden_roundtrip_and_key() {
    let mut la = load_fixture("ky_mon.json");
    assert_eq!(la.envelope_version, ENVELOPE_VERSION);
    require_supported_version(&la).expect("v1 must be supported");

    let original_key = {
        let k = cache_key(&la);
        la.provenance.cache_key = Some(k.clone());
        k
    };

    // serialize -> deserialize
    let json = serde_json::to_string_pretty(&la).unwrap();
    let la2: LaSo = serde_json::from_str(&json).unwrap();
    assert_eq!(la, la2);

    let key2 = cache_key(&la2);
    assert_eq!(original_key, key2, "cache key must survive roundtrip");
}

#[test]
fn luc_nham_golden_roundtrip() {
    let mut la = load_fixture("luc_nham.json");
    require_supported_version(&la).unwrap();
    let _ = cache_key(&la);
    let json = serde_json::to_string(&la).unwrap();
    let la2: LaSo = serde_json::from_str(&json).unwrap();
    assert_eq!(format!("{:?}", la.he).to_lowercase(), "lucnham"); // enum debug form (we only care it roundtripped)
    assert_eq!(la, la2);
}

#[test]
fn thai_at_golden_roundtrip() {
    let mut la = load_fixture("thai_at.json");
    require_supported_version(&la).unwrap();
    let _ = cache_key(&la);
    let json = serde_json::to_string(&la).unwrap();
    let la2: LaSo = serde_json::from_str(&json).unwrap();
    assert_eq!(la, la2);
}

#[test]
fn rejects_unsupported_version() {
    let mut la = load_fixture("ky_mon.json");
    la.envelope_version = 99;
    match require_supported_version(&la) {
        Err(EnvelopeError::UnsupportedVersion(99, _)) => {}
        other => panic!("expected UnsupportedVersion, got {:?}", other),
    }
}

#[test]
fn cache_keys_identical_for_identical_inputs() {
    let la1 = load_fixture("ky_mon.json");
    let la2 = load_fixture("ky_mon.json");
    assert_eq!(cache_key(&la1), cache_key(&la2));
}
