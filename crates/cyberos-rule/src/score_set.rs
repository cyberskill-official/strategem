//! Weighted cross-system scoring — TASK-RULE-004.

use crate::cross::{evaluate_set, ChartSet};
use crate::dsl::Cond;
use crate::pattern::Pattern;
use crate::score::CachCuc;
use serde_json::Value;

/// Node weight from condition JSON (default 1.0). Used as a scoring hint.
pub fn node_weight(cond_json: &Value) -> f32 {
    cond_json
        .get("weight")
        .and_then(|w| w.as_f64())
        .map(|f| f as f32)
        .unwrap_or(1.0)
}

/// Score a pattern over a chart set. Returns CachCuc when the condition matches.
pub fn score_set(pattern: &Pattern, set: &ChartSet) -> Option<CachCuc> {
    let cond = Cond::from_json(&pattern.conditions).ok()?;
    if !evaluate_set(&cond, set) {
        return None;
    }
    let w = node_weight(&pattern.conditions);
    Some(CachCuc {
        id: pattern.id.clone(),
        name: pattern.name.clone(),
        cung: None, // whole-set agreement patterns have no single palace
        polarity: match pattern.polarity {
            crate::pattern::Polarity::Cat => "cat".into(),
            crate::pattern::Polarity::Hung => "hung".into(),
            crate::pattern::Polarity::Trung => "trung".into(),
        },
        score: Some(pattern.confidence * w),
        citations: pattern.citations.clone(),
    })
}
