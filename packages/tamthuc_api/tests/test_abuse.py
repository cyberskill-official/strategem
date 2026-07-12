from __future__ import annotations

from tamthuc_api.abuse import AbuseDetector, AbuseSignal, RequestEvent


def test_credential_stuffing_lockout() -> None:
    d = AbuseDetector(stuffing_threshold=5)
    for _ in range(4):
        v = d.evaluate(None, "1.2.3.4", RequestEvent(path="/auth/login", failed_login=True))
        assert v.action in ("allow", "throttle")
    v = d.evaluate(None, "1.2.3.4", RequestEvent(path="/auth/login", failed_login=True))
    assert v.signal == AbuseSignal.credential_stuffing
    assert v.action == "lockout"


def test_velocity_throttle() -> None:
    d = AbuseDetector(velocity_threshold=3)
    for _ in range(3):
        assert (
            d.evaluate("p1", "9.9.9.9", RequestEvent(path="/api/v1/calculate/qimen")).action
            == "allow"
        )
    v = d.evaluate("p1", "9.9.9.9", RequestEvent(path="/api/v1/calculate/qimen"))
    assert v.signal == AbuseSignal.velocity_spike
    assert v.action == "throttle"


def test_probing_flag() -> None:
    d = AbuseDetector(probing_threshold=3)
    for _ in range(2):
        assert (
            d.evaluate(None, "8.8.8.8", RequestEvent(path="/x", malformed=True)).action == "allow"
        )
    v = d.evaluate(None, "8.8.8.8", RequestEvent(path="/x", malformed=True))
    assert v.signal == AbuseSignal.probing
    assert v.action == "flag"
