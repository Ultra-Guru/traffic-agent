from __future__ import annotations

import pytest

from traffic_agent.transform.netcond import (
    ConditionAction,
    ConditionProfile,
    ConditionResult,
    NetworkConditionSimulator,
)


class TestConditionProfile:
    def test_defaults_validate(self):
        profile = ConditionProfile()
        profile.validate()
        assert profile.latency_ms == 0
        assert profile.jitter_ms == 0
        assert profile.loss_pct == 0.0
        assert profile.rate_kbps is None
        assert profile.timeout_ms is None

    @pytest.mark.parametrize(
        "kwargs",
        [
            dict(latency_ms=-1),
            dict(jitter_ms=-2),
            dict(loss_pct=100.5),
            dict(loss_pct=-0.1),
            dict(rate_kbps=0),
            dict(timeout_ms=0),
        ],
    )
    def test_invalid_profiles(self, kwargs):
        with pytest.raises(ValueError):
            ConditionProfile(**kwargs).validate()


class TestNetworkConditionSimulator:
    def test_no_profile_sends(self):
        sim = NetworkConditionSimulator()
        result = sim.apply(b"data", now=100.0)
        assert result.action is ConditionAction.SEND
        assert result.send_at == 100.0
        assert result.reason == "no active profile"
        assert result.delivered is True

    def test_constructor_validates_profile(self):
        with pytest.raises(ValueError):
            NetworkConditionSimulator(profile=ConditionProfile(loss_pct=200))

    def test_latency_only(self):
        sim = NetworkConditionSimulator(profile=ConditionProfile(latency_ms=100))
        result = sim.apply(b"x", now=10.0)
        assert result.action is ConditionAction.DELAY
        assert result.send_at == pytest.approx(10.1)
        assert result.delivered is True

    def test_jitter_within_bounds(self):
        sim = NetworkConditionSimulator(profile=ConditionProfile(latency_ms=50, jitter_ms=100))
        for _ in range(20):
            result = sim.apply(b"x", now=0.0)
            assert result.action is ConditionAction.DELAY
            assert 0.050 <= result.send_at <= 0.1499

    def test_full_loss_always_drops(self):
        sim = NetworkConditionSimulator(profile=ConditionProfile(loss_pct=100))
        for _ in range(10):
            result = sim.apply(b"x", now=1.0)
            assert result.action is ConditionAction.DROP
            assert result.send_at is None
            assert result.delivered is False

    def test_zero_loss_never_drops(self):
        sim = NetworkConditionSimulator(profile=ConditionProfile(loss_pct=0, latency_ms=10))
        for _ in range(10):
            assert sim.apply(b"x", now=0.0).action is ConditionAction.DELAY

    def test_timeout_wins(self):
        sim = NetworkConditionSimulator(profile=ConditionProfile(timeout_ms=1000, latency_ms=100))
        result = sim.apply(b"x", now=0.0)
        assert result.action is ConditionAction.TIMEOUT
        assert result.send_at is None
        assert result.reason == "timeout profile: 1000ms"

    def test_rate_limiting_transfer_time(self):
        sim = NetworkConditionSimulator(profile=ConditionProfile(rate_kbps=8))
        result = sim.apply(b"\x00" * 1000, now=0.0)  # 8000 bits / 8000 bps = 1s
        assert result.action is ConditionAction.DELAY
        assert result.send_at == pytest.approx(1.0)

    def test_rate_limiting_empty_data_no_delay(self):
        sim = NetworkConditionSimulator(profile=ConditionProfile(rate_kbps=8))
        result = sim.apply(b"", now=5.0)
        assert result.action is ConditionAction.SEND
        assert result.send_at == 5.0

    def test_set_profile_with_expiry(self):
        sim = NetworkConditionSimulator()
        sim.set_profile(ConditionProfile(latency_ms=100), expires_at=50.0)
        assert sim.apply(b"x", now=49.999).action is ConditionAction.DELAY
        # 到期：画像自动撤销
        expired = sim.apply(b"x", now=50.0)
        assert expired.action is ConditionAction.SEND
        assert expired.reason == "no active profile"
        assert sim.profile is None

    def test_set_profile_validates(self):
        sim = NetworkConditionSimulator()
        with pytest.raises(ValueError):
            sim.set_profile(ConditionProfile(loss_pct=-1))

    def test_rule_linked_conditions(self):
        sim = NetworkConditionSimulator()
        profile = ConditionProfile(latency_ms=5000)
        sim.link_condition("rule-1", profile)
        assert sim.condition_for("rule-1") is profile
        assert sim.condition_for("rule-2") is None
        with pytest.raises(ValueError):
            sim.link_condition("rule-3", ConditionProfile(latency_ms=-1))

    def test_result_delivered_property(self):
        assert ConditionResult(ConditionAction.SEND, 1.0, "r").delivered is True
        assert ConditionResult(ConditionAction.DELAY, 2.0, "r").delivered is True
        assert ConditionResult(ConditionAction.DROP, None, "r").delivered is False
        assert ConditionResult(ConditionAction.TIMEOUT, None, "r").delivered is False

    def test_deterministic_with_seed(self):
        a = NetworkConditionSimulator(profile=ConditionProfile(loss_pct=50), seed=7)
        b = NetworkConditionSimulator(profile=ConditionProfile(loss_pct=50), seed=7)
        actions_a = [a.apply(b"x", now=0.0).action for _ in range(15)]
        actions_b = [b.apply(b"x", now=0.0).action for _ in range(15)]
        assert actions_a == actions_b
        # seed=7 的 50% 丢包应同时出现 DROP 与 SEND（无延迟 → 未丢包直接发送）
        assert ConditionAction.DROP in actions_a
        assert ConditionAction.SEND in actions_a
