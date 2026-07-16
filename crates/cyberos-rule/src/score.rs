//! Pattern match → CachCuc. TASK-RULE-002.

use crate::dsl::Cond;
use crate::eval::evaluate;
use crate::pattern::Pattern;
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// Matches laso-envelope CachCuc shape (TASK-PLAT-002).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CachCuc {
    pub id: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cung: Option<i32>,
    pub polarity: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub score: Option<f32>,
    #[serde(default)]
    pub citations: Vec<String>,
}

pub fn score_match(pattern: &Pattern, chart: &Value) -> Option<CachCuc> {
    let cond = Cond::from_json(&pattern.conditions).ok()?;
    if !evaluate(&cond, chart) {
        return None;
    }
    Some(CachCuc {
        id: pattern.id.clone(),
        name: pattern.name.clone(),
        cung: None,
        polarity: match pattern.polarity {
            crate::pattern::Polarity::Cat => "cat".into(),
            crate::pattern::Polarity::Hung => "hung".into(),
            crate::pattern::Polarity::Trung => "trung".into(),
        },
        score: Some(pattern.confidence),
        citations: pattern.citations.clone(),
    })
}
