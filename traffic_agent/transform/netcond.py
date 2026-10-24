"""网络条件模拟器：延迟 / 抖动 / 丢包 / 限速 / 超时（对应 SPEC v2.0 §1.3 弱网）。

与重写规则联动的入口：``link_condition(rule_id, profile)``——
「命中 /pay 的请求施加 5s 延迟」。
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class ConditionAction(str, Enum):
    SEND = "send"
    DELAY = "delay"
    DROP = "drop"
    TIMEOUT = "timeout"


@dataclass
class ConditionProfile:
    """一份弱网画像。"""

    latency_ms: int = 0
    jitter_ms: int = 0
    loss_pct: float = 0.0
    rate_kbps: Optional[int] = None
    timeout_ms: Optional[int] = None

    def validate(self) -> None:
        if self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        if self.jitter_ms < 0:
            raise ValueError("jitter_ms must be non-negative")
        if not (0.0 <= self.loss_pct <= 100.0):
            raise ValueError("loss_pct must be within [0, 100]")
        if self.rate_kbps is not None and self.rate_kbps <= 0:
            raise ValueError("rate_kbps must be positive")
        if self.timeout_ms is not None and self.timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")


@dataclass
class ConditionResult:
    """一次施加弱网条件后的裁决。"""

    action: ConditionAction
    send_at: Optional[float]
    reason: str

    @property
    def delivered(self) -> bool:
        return self.action in (ConditionAction.SEND, ConditionAction.DELAY)


class NetworkConditionSimulator:
    """确定性弱网模拟：注入 seed 保证可测性；TTL 到期自动撤销（工具门控约束）。"""

    def __init__(self, profile: Optional[ConditionProfile] = None, seed: int = 1337) -> None:
        if profile is not None:
            profile.validate()
        self.profile = profile
        self._expires_at: Optional[float] = None
        self._rng = random.Random(seed)
        self._rule_profiles: Dict[str, ConditionProfile] = {}

    def set_profile(self, profile: Optional[ConditionProfile], expires_at: Optional[float] = None) -> None:
        if profile is not None:
            profile.validate()
        self.profile = profile
        self._expires_at = expires_at

    def apply(self, data: bytes, now: float) -> ConditionResult:
        """对一段数据施加当前画像，返回 SEND / DELAY / DROP / TIMEOUT 裁决。"""
        if (
            self.profile is not None
            and self._expires_at is not None
            and now >= self._expires_at
        ):
            self.profile = None
            self._expires_at = None
        profile = self.profile
        if profile is None:
            return ConditionResult(ConditionAction.SEND, now, "no active profile")
        if profile.timeout_ms is not None:
            return ConditionResult(ConditionAction.TIMEOUT, None, f"timeout profile: {profile.timeout_ms}ms")
        if profile.loss_pct > 0 and (self._rng.random() * 100.0) < profile.loss_pct:
            return ConditionResult(ConditionAction.DROP, None, "simulated packet loss")
        delay_ms = float(profile.latency_ms)
        if profile.jitter_ms > 0:
            delay_ms += int(self._rng.random() * profile.jitter_ms)
        if profile.rate_kbps is not None and len(data) > 0:
            transfer_ms = len(data) * 8 / (profile.rate_kbps * 1000) * 1000
            delay_ms += transfer_ms
        if delay_ms <= 0:
            return ConditionResult(ConditionAction.SEND, now, "no delay required")
        return ConditionResult(ConditionAction.DELAY, now + delay_ms / 1000.0, f"delayed by {round(delay_ms, 3)}ms")

    def link_condition(self, rule_id: str, profile: ConditionProfile) -> None:
        """重写规则联动：命中规则时自动施加的弱网画像。"""
        profile.validate()
        self._rule_profiles[rule_id] = profile

    def condition_for(self, rule_id: str) -> Optional[ConditionProfile]:
        return self._rule_profiles.get(rule_id)
