//! match(la_so) -> Vec<CachCuc>. TASK-RULE-003.

use crate::cache::PatternCache;
use crate::pattern::{Polarity, System};
use crate::repo::PatternRepository;
use crate::score::{score_match, CachCuc};
use serde_json::Value;

fn polarity_rank(p: &str) -> i32 {
    match p {
        "cat" => 0,
        "trung" => 1,
        "hung" => 2,
        _ => 3,
    }
}

pub fn match_laso<R: PatternRepository>(
    cache: &PatternCache<R>,
    system: System,
    chart: &Value,
) -> Result<Vec<CachCuc>, crate::repo::RepoError> {
    let patterns = cache.active_for(system)?;
    let mut out: Vec<CachCuc> = patterns
        .iter()
        .filter_map(|p| score_match(p, chart))
        .collect();
    // de-dupe by id keeping first after sort prep
    out.sort_by(|a, b| {
        polarity_rank(&a.polarity)
            .cmp(&polarity_rank(&b.polarity))
            .then_with(|| {
                b.score
                    .partial_cmp(&a.score)
                    .unwrap_or(std::cmp::Ordering::Equal)
            })
            .then_with(|| a.id.cmp(&b.id))
    });
    out.dedup_by(|a, b| a.id == b.id);
    let _ = Polarity::Cat; // keep import used if needed
    Ok(out)
}
