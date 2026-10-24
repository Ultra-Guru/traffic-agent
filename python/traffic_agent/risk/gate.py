"""Risk gate for agent tool calls (SPEC v2.1 L4).

Every tool carries a risk level; the gate decides whether a call may run
under the active policy, and whether it requires explicit approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class RiskLevel(IntEnum):
    SAFE = 0
    CAUTION = 1
    DANGEROUS = 2
    CRITICAL = 3


TOOL_RISK = {
    # read-only
    "list_requests": RiskLevel.SAFE,
    "read_request": RiskLevel.SAFE,
    "filter_requests": RiskLevel.SAFE,
    "stats_summary": RiskLevel.SAFE,
    "audit_tail": RiskLevel.SAFE,
    "pending_breakpoints": RiskLevel.SAFE,
    # local rewrites
    "modify_header": RiskLevel.CAUTION,
    "remove_header": RiskLevel.CAUTION,
    "rewrite_url": RiskLevel.CAUTION,
    "set_breakpoint": RiskLevel.CAUTION,
    # behaviour-changing
    "modify_body": RiskLevel.DANGEROUS,
    "replay_request": RiskLevel.DANGEROUS,
    "block_host": RiskLevel.DANGEROUS,
    # device-level
    "install_cert": RiskLevel.CRITICAL,
    "clear_rules": RiskLevel.CRITICAL,
}


@dataclass
class GateDecision:
    tool: str
    allowed: bool
    risk: Optional[RiskLevel]
    reason: Optional[str] = None
    requires_approval: bool = False


@dataclass
class RiskPolicy:
    max_level: RiskLevel = RiskLevel.CAUTION
    require_approval_from: RiskLevel = RiskLevel.CRITICAL


class RiskGate:
    def __init__(self, policy: Optional[RiskPolicy] = None):
        self.policy = policy or RiskPolicy()

    def risk_of(self, tool: str) -> Optional[RiskLevel]:
        return TOOL_RISK.get(tool)

    def evaluate(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)
