//! Placeholder engine binary for Docker multi-stage path (FR-PLAT-004).
//! Real engine service binary lands with assembly FRs.

use smoke::add;

fn main() {
    let _ = add(2, 2);
    println!("engine-image-ok");
}
