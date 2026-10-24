"""Risk gate for agent tool calls (SPEC v2.1 L4).

Every tool carries a risk level; the gate decides whether a call may run
under the active policy, and whether it requires explicit approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


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
mutants_xǁRiskGateǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁRiskGateǁrisk_of__mutmut: MutantDict = {}  # type: ignore
mutants_xǁRiskGateǁevaluate__mutmut: MutantDict = {}  # type: ignore


class RiskGate:
    @_mutmut_mutated(mutants_xǁRiskGateǁ__init____mutmut)
    def __init__(self, policy: Optional[RiskPolicy] = None):
        self.policy = policy or RiskPolicy()
    def xǁRiskGateǁ__init____mutmut_orig(self, policy: Optional[RiskPolicy] = None):
        self.policy = policy or RiskPolicy()
    def xǁRiskGateǁ__init____mutmut_1(self, policy: Optional[RiskPolicy] = None):
        self.policy = None
    def xǁRiskGateǁ__init____mutmut_2(self, policy: Optional[RiskPolicy] = None):
        self.policy = policy and RiskPolicy()

    @_mutmut_mutated(mutants_xǁRiskGateǁrisk_of__mutmut)
    def risk_of(self, tool: str) -> Optional[RiskLevel]:
        return TOOL_RISK.get(tool)

    def xǁRiskGateǁrisk_of__mutmut_orig(self, tool: str) -> Optional[RiskLevel]:
        return TOOL_RISK.get(tool)

    def xǁRiskGateǁrisk_of__mutmut_1(self, tool: str) -> Optional[RiskLevel]:
        return TOOL_RISK.get(None)

    @_mutmut_mutated(mutants_xǁRiskGateǁevaluate__mutmut)
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

    def xǁRiskGateǁevaluate__mutmut_orig(self, tool: str, approved: bool = False) -> GateDecision:
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

    def xǁRiskGateǁevaluate__mutmut_1(self, tool: str, approved: bool = True) -> GateDecision:
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

    def xǁRiskGateǁevaluate__mutmut_2(self, tool: str, approved: bool = False) -> GateDecision:
        risk = None
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_3(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(None)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_4(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is not None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_5(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(None, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_6(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, None, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_7(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, None)
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_8(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_9(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_10(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_11(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, )
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_12(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, True, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_13(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from or not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_14(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk > self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_15(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_16(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                None, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_17(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, None, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_18(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, None, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_19(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, None, requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_20(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=None
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_21(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_22(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_23(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_24(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_25(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_26(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, True, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_27(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=False
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_28(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk >= self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_29(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(None, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_30(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, None, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_31(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, None, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_32(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, None)
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_33(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_34(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_35(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_36(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, )
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_37(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, True, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, risk)

    def xǁRiskGateǁevaluate__mutmut_38(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(None, True, risk)

    def xǁRiskGateǁevaluate__mutmut_39(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, None, risk)

    def xǁRiskGateǁevaluate__mutmut_40(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, None)

    def xǁRiskGateǁevaluate__mutmut_41(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(True, risk)

    def xǁRiskGateǁevaluate__mutmut_42(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, risk)

    def xǁRiskGateǁevaluate__mutmut_43(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, True, )

    def xǁRiskGateǁevaluate__mutmut_44(self, tool: str, approved: bool = False) -> GateDecision:
        risk = self.risk_of(tool)
        if risk is None:
            return GateDecision(tool, False, None, f"unknown tool: {tool}")
        if risk >= self.policy.require_approval_from and not approved:
            return GateDecision(
                tool, False, risk, f"{tool} is {risk.name} and needs approval", requires_approval=True
            )
        if risk > self.policy.max_level:
            return GateDecision(tool, False, risk, f"{tool} exceeds policy level {self.policy.max_level.name}")
        return GateDecision(tool, False, risk)

mutants_xǁRiskGateǁ__init____mutmut['_mutmut_orig'] = RiskGate.xǁRiskGateǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁRiskGateǁ__init____mutmut['xǁRiskGateǁ__init____mutmut_1'] = RiskGate.xǁRiskGateǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁRiskGateǁ__init____mutmut['xǁRiskGateǁ__init____mutmut_2'] = RiskGate.xǁRiskGateǁ__init____mutmut_2 # type: ignore # mutmut generated

mutants_xǁRiskGateǁrisk_of__mutmut['_mutmut_orig'] = RiskGate.xǁRiskGateǁrisk_of__mutmut_orig # type: ignore # mutmut generated
mutants_xǁRiskGateǁrisk_of__mutmut['xǁRiskGateǁrisk_of__mutmut_1'] = RiskGate.xǁRiskGateǁrisk_of__mutmut_1 # type: ignore # mutmut generated

mutants_xǁRiskGateǁevaluate__mutmut['_mutmut_orig'] = RiskGate.xǁRiskGateǁevaluate__mutmut_orig # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_1'] = RiskGate.xǁRiskGateǁevaluate__mutmut_1 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_2'] = RiskGate.xǁRiskGateǁevaluate__mutmut_2 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_3'] = RiskGate.xǁRiskGateǁevaluate__mutmut_3 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_4'] = RiskGate.xǁRiskGateǁevaluate__mutmut_4 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_5'] = RiskGate.xǁRiskGateǁevaluate__mutmut_5 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_6'] = RiskGate.xǁRiskGateǁevaluate__mutmut_6 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_7'] = RiskGate.xǁRiskGateǁevaluate__mutmut_7 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_8'] = RiskGate.xǁRiskGateǁevaluate__mutmut_8 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_9'] = RiskGate.xǁRiskGateǁevaluate__mutmut_9 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_10'] = RiskGate.xǁRiskGateǁevaluate__mutmut_10 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_11'] = RiskGate.xǁRiskGateǁevaluate__mutmut_11 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_12'] = RiskGate.xǁRiskGateǁevaluate__mutmut_12 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_13'] = RiskGate.xǁRiskGateǁevaluate__mutmut_13 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_14'] = RiskGate.xǁRiskGateǁevaluate__mutmut_14 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_15'] = RiskGate.xǁRiskGateǁevaluate__mutmut_15 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_16'] = RiskGate.xǁRiskGateǁevaluate__mutmut_16 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_17'] = RiskGate.xǁRiskGateǁevaluate__mutmut_17 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_18'] = RiskGate.xǁRiskGateǁevaluate__mutmut_18 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_19'] = RiskGate.xǁRiskGateǁevaluate__mutmut_19 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_20'] = RiskGate.xǁRiskGateǁevaluate__mutmut_20 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_21'] = RiskGate.xǁRiskGateǁevaluate__mutmut_21 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_22'] = RiskGate.xǁRiskGateǁevaluate__mutmut_22 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_23'] = RiskGate.xǁRiskGateǁevaluate__mutmut_23 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_24'] = RiskGate.xǁRiskGateǁevaluate__mutmut_24 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_25'] = RiskGate.xǁRiskGateǁevaluate__mutmut_25 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_26'] = RiskGate.xǁRiskGateǁevaluate__mutmut_26 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_27'] = RiskGate.xǁRiskGateǁevaluate__mutmut_27 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_28'] = RiskGate.xǁRiskGateǁevaluate__mutmut_28 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_29'] = RiskGate.xǁRiskGateǁevaluate__mutmut_29 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_30'] = RiskGate.xǁRiskGateǁevaluate__mutmut_30 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_31'] = RiskGate.xǁRiskGateǁevaluate__mutmut_31 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_32'] = RiskGate.xǁRiskGateǁevaluate__mutmut_32 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_33'] = RiskGate.xǁRiskGateǁevaluate__mutmut_33 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_34'] = RiskGate.xǁRiskGateǁevaluate__mutmut_34 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_35'] = RiskGate.xǁRiskGateǁevaluate__mutmut_35 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_36'] = RiskGate.xǁRiskGateǁevaluate__mutmut_36 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_37'] = RiskGate.xǁRiskGateǁevaluate__mutmut_37 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_38'] = RiskGate.xǁRiskGateǁevaluate__mutmut_38 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_39'] = RiskGate.xǁRiskGateǁevaluate__mutmut_39 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_40'] = RiskGate.xǁRiskGateǁevaluate__mutmut_40 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_41'] = RiskGate.xǁRiskGateǁevaluate__mutmut_41 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_42'] = RiskGate.xǁRiskGateǁevaluate__mutmut_42 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_43'] = RiskGate.xǁRiskGateǁevaluate__mutmut_43 # type: ignore # mutmut generated
mutants_xǁRiskGateǁevaluate__mutmut['xǁRiskGateǁevaluate__mutmut_44'] = RiskGate.xǁRiskGateǁevaluate__mutmut_44 # type: ignore # mutmut generated
