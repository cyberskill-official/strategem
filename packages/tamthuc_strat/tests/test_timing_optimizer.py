from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from tamthuc_strat.models import TimingRequest
from tamthuc_strat.scoring import score_envelope
from tamthuc_strat.timing_optimizer import TimingError, optimize_timing


def stub_engine(when: datetime, req: TimingRequest) -> dict:
    # better mid-range
    hour = when.hour
    if 8 <= hour < 12:
        cach = [{"id": "c1", "name": "青龍返首", "polarity": "cat", "score": 0.9, "citations": ["x"]}]
    else:
        cach = [{"id": "h1", "name": "大格", "polarity": "hung", "score": 0.8, "citations": ["y"]}]
    return {
        "he": "ky_mon",
        "ban": {"stub": True},
        "cach_cuc": cach,
        "provenance": {"cache_key": f"k-{when.isoformat()}"},
    }


def test_top_n_ranking() -> None:
    start = datetime(2004, 1, 1, 0, 0)
    end = datetime(2004, 1, 1, 22, 0)
    req = TimingRequest(start=start, end=end, granularity="gio", top_n=3)
    calls: list[datetime] = []

    def eng(when: datetime, r: TimingRequest) -> dict:
        calls.append(when)
        return stub_engine(when, r)

    res = optimize_timing(req, eng)
    assert len(res.windows) == 3
    assert res.windows[0].score >= res.windows[1].score
    assert all(w.cast_ref for w in res.windows)
    assert calls  # engine called, no local plate math


def test_score_pure() -> None:
    env = {
        "cach_cuc": [
            {"polarity": "cat", "score": 0.9, "id": "a", "name": "A", "citations": []},
            {"polarity": "hung", "score": 0.4, "id": "b", "name": "B", "citations": []},
        ]
    }
    s, cat, hung = score_envelope(env)
    assert s == pytest.approx(0.5)
    assert len(cat) == 1 and len(hung) == 1
    # explainability: score = sum cat - sum hung
    assert s == pytest.approx(sum(c["score"] for c in cat) - sum(h["score"] for h in hung))


def test_inverted_range() -> None:
    req = TimingRequest(
        start=datetime(2004, 1, 2),
        end=datetime(2004, 1, 1),
    )
    with pytest.raises(TimingError):
        optimize_timing(req, stub_engine)


def test_start_eq_end() -> None:
    t = datetime(2004, 1, 1, 10, 0)
    req = TimingRequest(start=t, end=t, top_n=5)
    res = optimize_timing(req, stub_engine)
    assert len(res.windows) == 1


def test_deterministic() -> None:
    start = datetime(2004, 1, 1, 8)
    end = start + timedelta(hours=6)
    req = TimingRequest(start=start, end=end, granularity="gio", top_n=2)
    a = optimize_timing(req, stub_engine)
    b = optimize_timing(req, stub_engine)
    assert a.model_dump() == b.model_dump()


def test_monotonic_cat_helps() -> None:
    base = {"cach_cuc": [{"polarity": "hung", "score": 0.5, "id": "h", "name": "H"}]}
    better = {
        "cach_cuc": [
            {"polarity": "hung", "score": 0.5, "id": "h", "name": "H"},
            {"polarity": "cat", "score": 0.8, "id": "c", "name": "C"},
        ]
    }
    assert score_envelope(better)[0] > score_envelope(base)[0]
