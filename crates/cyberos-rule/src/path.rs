//! JSON path lookup into a chart object. FR-RULE-002.

use serde_json::Value;

/// Resolve dotted path like `ban.stars.0.name` or `he`.
pub fn get_path<'a>(root: &'a Value, path: &str) -> Option<&'a Value> {
    let mut cur = root;
    for part in path.split('.').filter(|p| !p.is_empty()) {
        cur = if let Ok(idx) = part.parse::<usize>() {
            cur.as_array()?.get(idx)?
        } else {
            cur.as_object()?.get(part)?
        };
    }
    Some(cur)
}
