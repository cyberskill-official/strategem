"""Redis cache protocol + in-memory fail-open backend — FR-PLAT-006."""

from __future__ import annotations

import time
from typing import Protocol


class RedisCache(Protocol):
    def get(self, key: str) -> bytes | None: ...
    def set(self, key: str, value: bytes, ttl_s: int) -> None: ...
    def delete(self, *keys: str) -> None: ...
    def scan(self, match: str) -> list[str]: ...


class InMemoryRedis:
    """Deterministic stand-in for Redis used in tests and local dev."""

    def __init__(self, *, fail: bool = False) -> None:
        self._data: dict[str, tuple[bytes, float | None]] = {}
        self.fail = fail

    def _expired(self, key: str) -> bool:
        item = self._data.get(key)
        if item is None:
            return True
        _, exp = item
        if exp is not None and exp < time.time():
            del self._data[key]
            return True
        return False

    def get(self, key: str) -> bytes | None:
        if self.fail:
            raise ConnectionError("redis down")
        if self._expired(key):
            return None
        return self._data[key][0]

    def set(self, key: str, value: bytes, ttl_s: int) -> None:
        if self.fail:
            raise ConnectionError("redis down")
        exp = time.time() + ttl_s if ttl_s > 0 else None
        self._data[key] = (value, exp)

    def delete(self, *keys: str) -> None:
        if self.fail:
            raise ConnectionError("redis down")
        for k in keys:
            self._data.pop(k, None)

    def scan(self, match: str) -> list[str]:
        if self.fail:
            raise ConnectionError("redis down")
        # support trailing *
        prefix = match[:-1] if match.endswith("*") else match
        out: list[str] = []
        for k in list(self._data):
            if self._expired(k):
                continue
            if match.endswith("*") and k.startswith(prefix) or k == match:
                out.append(k)
        return out
