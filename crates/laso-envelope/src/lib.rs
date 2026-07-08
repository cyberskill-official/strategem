//! La So JSON Envelope (PLAT-002)
//!
//! Single source of truth shape for all Tam Thuc engine outputs.
//! - Engines (Rust) write `ban`, `cach_cuc`, stamp `co_truong_phai` + `lich_phap` flags.
//! - Interpretation (Python etc) reads; MUST NOT write ban/cach_cuc/lich_phap/co_truong_phai.
//! - Versioned; unknown versions -> typed error.
//! - `ban` is opaque Value here; engine crates provide typed views.
//! - `co_truong_phai` uses BTreeMap for stable ordering (cache keys, reproducibility).
//!
//! See docs/contracts/laso-envelope.schema.json and strategy 4.3/4.4.

use std::collections::BTreeMap;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use thiserror::Error;

/// Current envelope contract version.
pub const ENVELOPE_VERSION: u16 = 1;

/// Supported envelope versions (for consumer checks).
pub const SUPPORTED_VERSIONS: &[u16] = &[1];

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum He {
    LucNham,
    KyMon,
    ThaiAt,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Polarity {
    Cat,
    Hung,
    Trung,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub struct CachCuc {
    pub id: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cung: Option<u8>,
    pub polarity: Polarity,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub score: Option<f32>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub citations: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct DauVao {
    pub datetime: String,
    pub tz: String,
    pub kinh_do: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub loai_cau_hoi: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Provenance {
    pub engine: String,
    pub engine_version: String,
    pub cast_at: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cache_key: Option<String>,
}

/// The root envelope. Matches docs/contracts/laso-envelope.schema.json exactly.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct LaSo {
    pub envelope_version: u16,
    pub he: He,
    pub dau_vao: DauVao,
    /// CORE calendar output + all flags used. See FR-CORE-005 for the detailed shape.
    /// Engines stamp every flag that affected the result here (under co_lich_phap or top level).
    pub lich_phap: Value,
    /// Engine-specific plates. Opaque at this boundary.
    /// Engine crates define e.g. KyMonBan and serialize into this Value slot.
    pub ban: Value,
    #[serde(default)]
    pub cach_cuc: Vec<CachCuc>,
    /// Every school flag / variant actually used for this cast.
    /// BTreeMap guarantees sorted keys -> stable serialization and cache keys.
    pub co_truong_phai: BTreeMap<String, String>,
    pub provenance: Provenance,
}

#[derive(Debug, Error)]
pub enum EnvelopeError {
    #[error("unsupported envelope version: {0} (supported: {1:?})")]
    UnsupportedVersion(u16, Vec<u16>),
    #[error("invalid json: {0}")]
    InvalidJson(#[from] serde_json::Error),
    #[error("schema violation: {0}")]
    SchemaViolation(String),
}

/// Require that this envelope's version is supported. Call on receipt.
pub fn require_supported_version(la: &LaSo) -> Result<(), EnvelopeError> {
    if SUPPORTED_VERSIONS.contains(&la.envelope_version) {
        Ok(())
    } else {
        Err(EnvelopeError::UnsupportedVersion(
            la.envelope_version,
            SUPPORTED_VERSIONS.to_vec(),
        ))
    }
}

/// Compute a stable cache key for a LaSo.
/// Rule (per FR): hash of (he, dau_vao rounded to casting granularity, co_truong_phai sorted, lich_phap.co_lich_phap sorted).
/// We use canonical JSON (BTreeMap already sorted) + sha256 for cross-lang stability.
pub fn cache_key(la: &LaSo) -> String {
    // Build a deterministic sub-object for hashing.
    // Use only the parts that affect determinism per the FR.
    let mut canon = serde_json::Map::new();
    canon.insert("he".to_string(), serde_json::to_value(&la.he).unwrap());

    // dau_vao as-is (consumer of envelope controls rounding if needed at cast time)
    canon.insert(
        "dau_vao".to_string(),
        serde_json::to_value(&la.dau_vao).unwrap(),
    );

    // co_truong_phai is already BTreeMap -> sorted
    canon.insert(
        "co_truong_phai".to_string(),
        serde_json::to_value(&la.co_truong_phai).unwrap(),
    );

    // For lich_phap we take the whole (CORE-005 will keep co_lich_phap inside); engines guarantee stamp.
    // To keep keys stable we serialize the Value as-is (producer must have sorted any maps inside).
    canon.insert("lich_phap".to_string(), la.lich_phap.clone());

    let json = serde_json::to_string(&canon).expect("canon map is always serializable");
    let mut hasher = Sha256::new();
    hasher.update(json.as_bytes());
    let digest = hasher.finalize();
    format!("{:x}", digest)
}

/// Helper: attach a freshly computed cache_key into provenance (mutates).
pub fn attach_cache_key(la: &mut LaSo) {
    let key = cache_key(la);
    la.provenance.cache_key = Some(key);
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn minimal_ky_mon() -> LaSo {
        let mut co = BTreeMap::new();
        co.insert("dingju_method".into(), "chaibu".into());
        co.insert("pan_method".into(), "zhuan".into());
        co.insert("yin_yang_pan".into(), "duong".into());

        LaSo {
            envelope_version: ENVELOPE_VERSION,
            he: He::KyMon,
            dau_vao: DauVao {
                datetime: "2004-01-01T10:30:00".into(),
                tz: "+07:00".into(),
                kinh_do: 106.7,
                loai_cau_hoi: Some("trach_thoi".into()),
            },
            lich_phap: json!({
                "tu_tru": {"nam":"癸未","thang":"甲子","ngay":"戊午","gio":"丁巳"},
                "tiet_khi": {"hien_hanh":"冬至","bat_dau":"2003-12-22T08:04:00Z","tam_nguyen":"thuong"},
                "chan_thai_duong": {"ap_dung":true,"gio_that":"2004-01-01T10:33:18","hieu_chinh_phut":3.3},
                "phai_sinh": {"tuan_khong":["申","酉"],"vuong_suy":{},"truong_sinh":{}},
                "co_lich_phap": {
                    "use_true_solar_time": true,
                    "longitude": 106.7,
                    "zi_hour_day_rollover": "23:00",
                    "late_zi_handling": "tao_zi",
                    "truong_sinh_phai": "ngu_hanh",
                    "delta_t_model": "espenak_meeus"
                }
            }),
            ban: json!({ "cuu_cung": [], "note": "placeholder for QMDG-00x" }),
            cach_cuc: vec![CachCuc {
                id: "qimen_thanh_long_hoi_dau".into(),
                name: "青龍返首".into(),
                cung: Some(1),
                polarity: Polarity::Cat,
                score: Some(0.9),
                citations: vec!["Yen Ba Dieu Tau Ca".into()],
            }],
            co_truong_phai: co,
            provenance: Provenance {
                engine: "qmdg".into(),
                engine_version: "0.1.0".into(),
                cast_at: Utc::now(),
                cache_key: None,
            },
        }
    }

    #[test]
    fn roundtrip_and_cache_key_stable() {
        let mut la = minimal_ky_mon();
        attach_cache_key(&mut la); // needs mut for attach

        let s = serde_json::to_string(&la).unwrap();
        let la2: LaSo = serde_json::from_str(&s).unwrap();
        assert_eq!(la, la2);

        // cache key must be identical after roundtrip
        let k1 = la.provenance.cache_key.clone().unwrap();
        let k2 = cache_key(&la2);
        assert_eq!(k1, k2);
        assert!(!k1.is_empty());
    }

    #[test]
    fn version_check_rejects_unknown() {
        let mut la = minimal_ky_mon();
        la.envelope_version = 99; // mutate to simulate bad version
        let err = require_supported_version(&la).unwrap_err();
        match err {
            EnvelopeError::UnsupportedVersion(v, _) => assert_eq!(v, 99),
            _ => panic!("wrong error"),
        }
    }

    #[test]
    fn deny_unknown_fields() {
        let mut la = minimal_ky_mon();
        let mut v = serde_json::to_value(&la).unwrap();
        if let Value::Object(ref mut m) = v {
            m.insert("unexpected_field".into(), json!("boom"));
        }
        let res: Result<LaSo, _> = serde_json::from_value(v);
        assert!(res.is_err(), "must reject unknown field at envelope root");
    }

    #[test]
    fn co_truong_phai_ordering_is_stable() {
        let mut la = minimal_ky_mon();
        // insert in "wrong" alpha order; BTreeMap will sort
        la.co_truong_phai.insert("aaa".into(), "1".into());
        la.co_truong_phai.insert("zzz".into(), "9".into());
        let j = serde_json::to_string(&la.co_truong_phai).unwrap();
        // keys must appear sorted
        assert!(j.find("aaa").unwrap() < j.find("dingju_method").unwrap());
        assert!(j.find("dingju_method").unwrap() < j.find("zzz").unwrap());
    }
}
