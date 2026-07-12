//! Pattern-as-data (FR-RULE-001) + condition DSL (FR-RULE-002).

pub mod dsl;
pub mod eval;
pub mod path;
pub mod pattern;
pub mod score;
pub mod seed;
pub mod validate;
pub mod version;

pub use dsl::{Cond, DslError, Op};
pub use eval::evaluate;
pub use path::get_path;
pub use pattern::{Pattern, Polarity, Status, System};
pub use score::{score_match, CachCuc};
pub use seed::{load_seed, SeedError};
pub use validate::{validate_pattern, ValidationError};
