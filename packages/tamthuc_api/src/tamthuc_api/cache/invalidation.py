"""Pattern-update invalidation — TASK-PLAT-006."""

from __future__ import annotations

import logging

from tamthuc_api.cache.redis_cache import RedisCache

log = logging.getLogger("tamthuc_api.cache.invalidation")


def on_pattern_update(pattern_key: str, redis: RedisCache) -> int:
    """Drop rag_interp entries and any chart entries tagged with the pattern id.

    Chart keys do not embed pattern ids; we scan rag:interp:* and optionally
    chart keys that were stored with a sidecar tag `pattern:{id}` when present.
    """
    deleted = 0
    try:
        for key in redis.scan("rag:interp:*"):
            redis.delete(key)
            deleted += 1
        # optional pattern-scoped tags
        for key in redis.scan(f"pattern:{pattern_key}:*"):
            redis.delete(key)
            deleted += 1
        for key in redis.scan(f"chart:pat:{pattern_key}:*"):
            redis.delete(key)
            deleted += 1
    except Exception:
        log.warning("invalidation.fail_open", extra={"pattern": pattern_key})
        return deleted
    log.info(
        "invalidation.pattern_update",
        extra={"pattern": pattern_key, "deleted": deleted},
    )
    return deleted
