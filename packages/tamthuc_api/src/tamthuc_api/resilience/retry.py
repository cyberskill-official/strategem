from __future__ import annotations

import random
import time
from collections.abc import Callable


class TransientError(Exception):
    pass


class PermanentError(Exception):
    """4xx-class — do not retry."""


def retry_call[T](
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.01,
    deadline: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
) -> T:
    start = time.monotonic()
    attempt = 0
    last: Exception | None = None
    while attempt < max_attempts:
        if deadline is not None and time.monotonic() - start > deadline:
            break
        try:
            return fn()
        except PermanentError:
            raise
        except Exception as e:
            last = e
            attempt += 1
            if attempt >= max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1)) * (0.5 + rng())
            sleep(delay)
    assert last is not None
    raise last
