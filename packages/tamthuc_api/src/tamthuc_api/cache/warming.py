"""Cache warming for common casts — TASK-PLAT-006."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any

from tamthuc_api.cache.chart_cache import ChartCache


def warm_common(
    now: datetime,
    *,
    cache: ChartCache,
    casts: Iterable[tuple[str, Callable[[], dict[str, Any]]]],
) -> int:
    """Pre-cast and cache common charts. Returns number of entries warmed."""
    _ = now  # period-aware warming can use this later
    n = 0
    for key, cast_fn in casts:
        cache.get_or_cast(key, cast_fn)
        n += 1
    return n
