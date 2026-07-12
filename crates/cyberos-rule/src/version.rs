use crate::pattern::Pattern;

/// Bump version for curation workflow (FR-KB-004); refuses zero.
pub fn bump(p: &Pattern) -> Pattern {
    let mut next = p.clone();
    next.version = p.version.saturating_add(1).max(1);
    next
}

pub fn stamp_key(id: &str, version: u32) -> String {
    format!("{id}@{version}")
}
