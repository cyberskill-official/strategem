//! Pattern-as-data (FR-RULE-001) + condition DSL (FR-RULE-002) + cross-system (FR-RULE-004).

pub mod cache;
pub mod cross;
pub mod dsl;
pub mod eval;
pub mod matcher;
pub mod path;
pub mod pattern;
pub mod repo;
pub mod score;
pub mod score_set;
pub mod seed;
pub mod validate;
pub mod version;

pub use cache::PatternCache;
pub use cross::{evaluate_set, resolve_in_set, ChartSet};
pub use dsl::{Cond, DslError, Op};
pub use eval::evaluate;
pub use matcher::match_laso;
pub use path::get_path;
pub use pattern::{Pattern, Polarity, Status, System};
pub use repo::{PatternRepository, RepoError, SeedRepository, StubPgRepository};
pub use score::{score_match, CachCuc};
pub use score_set::score_set;
pub use seed::{load_seed, SeedError};
pub use validate::{validate_pattern, ValidationError};
