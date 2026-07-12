"""Timing Optimizer — FR-STRAT-001. Calls engine; never re-casts plates."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from tamthuc_strat.models import ScoredWindow, TimingRequest, TimingResult
from tamthuc_strat.scoring import score_envelope


class TimingError(ValueError):
    pass


EngineFn = Callable[[datetime, TimingRequest], dict[str, Any]]


def _step(granularity: str) -> timedelta:
    g = granularity.lower()
    if g in ("gio", "2h", "pt2h"):
        return timedelta(hours=2)
    if g in ("ngay", "day", "p1d"):
        return timedelta(days=1)
    if g in ("hour", "1h", "pt1h"):
        return timedelta(hours=1)
    return timedelta(hours=2)


def _enumerate(start: datetime, end: datetime, step: timedelta) -> list[tuple[datetime, datetime]]:
    out: list[tuple[datetime, datetime]] = []
    cur = start
    while cur <= end:
        window_end = min(cur + step, end + step)
        out.append((cur, window_end))
        if cur == end:
            break
        nxt = cur + step
        if nxt > end and cur < end:
            # last partial already covered when start==end handled
            break
        cur = nxt
        if cur > end:
            break
    return out


def optimize_timing(req: TimingRequest, engine: EngineFn) -> TimingResult:
    if req.end < req.start:
        raise TimingError("end must be >= start")
    step = _step(req.granularity)
    candidates = _enumerate(req.start, req.end, step)
    if req.start == req.end:
        candidates = [(req.start, req.end)]

    scored: list[ScoredWindow] = []
    for s, e in candidates:
        env = engine(s, req)
        # STRAT never mutates ban / plates
        total, cat, hung = score_envelope(env)
        cast_ref = str(
            (env.get("provenance") or {}).get("cache_key")
            or env.get("cache_key")
            or f"cast:{s.isoformat()}"
        )
        scored.append(
            ScoredWindow(
                start=s,
                end=e,
                score=total,
                cat=cat,
                hung=hung,
                cast_ref=cast_ref,
            )
        )
    scored.sort(key=lambda w: (-w.score, w.start))
    return TimingResult(windows=scored[: req.top_n], request_echo=req)
