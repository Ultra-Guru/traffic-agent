"""L4 风险门控：LOW 自动放行 / MEDIUM 首次确认 / HIGH 每次确认。

对应 SPEC v2.0 §3「新增 Agent 工具」的风险分级与门控列，
以及 Root 增量 §4 的 root 专用工具（``exec_root_shell`` 默认禁用）。
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Dict, List, Optional, Set


class RiskLevel(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class ToolPolicy:
    name: str
    risk: RiskLevel
    default_disabled: bool = False
    description: str = ""


def default_policies() -> Dict[str, ToolPolicy]:
    """SPEC v2.0 §3 + Root 增量 §4 的完整工具风险表。"""
    specs = [
        # ---- LOW：无副作用 / 只读 ----
        ("query_connections", RiskLevel.LOW, False, "查询历史连接"),
        ("search_payload", RiskLevel.LOW, False, "正则/文本检索载荷"),
        ("compare_sessions", RiskLevel.LOW, False, "差分两次抓包"),
        ("check_root_capabilities", RiskLevel.LOW, False, "探测 root 能力（只读）"),
        ("set_network_condition", RiskLevel.LOW, False, "施加弱网/超时/限速（作用域受限 + 自动过期）"),
        # ---- MEDIUM：首次确认后本会话免确认 ----
        ("create_rewrite_rule", RiskLevel.MEDIUM, False, "创建重写/注入/屏蔽规则"),
        ("set_breakpoint", RiskLevel.MEDIUM, False, "设置请求/响应断点"),
        ("resolve_breakpoint", RiskLevel.MEDIUM, False, "放行/修改/丢弃断点"),
        ("generate_rule_from_example", RiskLevel.MEDIUM, False, "由示例生成规则草稿"),
        ("replay_request", RiskLevel.MEDIUM, False, "重发单个请求"),
        ("export_sslkeylog", RiskLevel.MEDIUM, False, "导出 SSLKEYLOGFILE"),
        ("capture_tls_plaintext", RiskLevel.MEDIUM, False, "eBPF TLS 明文捕获"),
        # ---- HIGH：每次调用都要显式确认 ----
        ("inject_script", RiskLevel.HIGH, False, "在沙箱中加载脚本"),
        ("replay_sequence", RiskLevel.HIGH, False, "按时间轴回放请求序列"),
        ("deploy_system_ca", RiskLevel.HIGH, False, "部署系统 CA overlay"),
        ("enable_pinning_bypass", RiskLevel.HIGH, False, "LSPosed pinning bypass"),
        ("attach_instrumentation", RiskLevel.HIGH, False, "Frida 预审 profile 插桩"),
        ("set_stealth_mode", RiskLevel.HIGH, False, "隐藏 root/VPN/Frida 痕迹"),
        ("exec_root_shell", RiskLevel.HIGH, True, "受限 root 诊断命令（默认禁用，白名单校验）"),
    ]
    return {name: ToolPolicy(name, risk, disabled, desc) for name, risk, disabled, desc in specs}


@dataclass
class GateDecision:
    allowed: bool
    requires_confirmation: bool
    risk: Optional[RiskLevel]
    reason: str


@dataclass
class GateAuditRecord:
    tool: str
    allowed: bool
    reason: str
    ts: float


class ToolGate:
    """工具门控器。

    - LOW：自动放行；
    - MEDIUM：本会话确认一次后放行（``confirm()`` 或 ``evaluate(confirmed_now=True)``）；
    - HIGH：每次调用必须 ``confirmed_now=True``，不做会话记忆；
    - ``default_disabled``（如 exec_root_shell）：必须先 ``enable_tool()`` 显式开启。
    所有决策写入审计日志。
    """

    def __init__(self, policies: Optional[Dict[str, ToolPolicy]] = None, clock: Optional[Callable[[], float]] = None) -> None:
        self.policies = policies if policies is not None else default_policies()
        self._clock = clock or time.time
        self._confirmed: Set[str] = set()
        self._enabled: Set[str] = set()
        self.audit: List[GateAuditRecord] = []

    def policy(self, tool: str) -> Optional[ToolPolicy]:
        return self.policies.get(tool)

    def enable_tool(self, tool: str) -> None:
        """显式开启默认禁用的工具（如 exec_root_shell）。"""
        if tool not in self.policies:
            raise KeyError(f"unknown tool: {tool}")
        self._enabled.add(tool)

    def confirm(self, tool: str) -> bool:
        """会话级确认；只有 MEDIUM 会被记忆，HIGH 返回 False（需每次确认）。"""
        policy = self.policies.get(tool)
        if policy is None:
            return False
        if policy.risk is RiskLevel.MEDIUM:
            self._confirmed.add(tool)
            return True
        return False

    def evaluate(self, tool: str, confirmed_now: bool = False) -> GateDecision:
        policy = self.policies.get(tool)
        if policy is None:
            decision = GateDecision(False, False, None, f"unknown tool: {tool}")
        elif policy.default_disabled and tool not in self._enabled:
            decision = GateDecision(False, False, policy.risk, f"tool disabled by default: {tool}")
        elif policy.risk is RiskLevel.LOW:
            decision = GateDecision(True, False, policy.risk, "low risk: auto-approved")
        elif policy.risk is RiskLevel.MEDIUM:
            if tool in self._confirmed:
                decision = GateDecision(True, False, policy.risk, "medium risk: confirmed this session")
            elif confirmed_now:
                self._confirmed.add(tool)
                decision = GateDecision(True, False, policy.risk, "medium risk: confirmed")
            else:
                decision = GateDecision(False, True, policy.risk, "medium risk: requires user confirmation")
        else:  # HIGH
            if confirmed_now:
                decision = GateDecision(True, False, policy.risk, "high risk: confirmed for this invocation")
            else:
                decision = GateDecision(False, True, policy.risk, "high risk: requires per-invocation confirmation")
        self.audit.append(GateAuditRecord(tool, decision.allowed, decision.reason, self._clock()))
        return decision

    def confirmed_tools(self) -> Set[str]:
        return set(self._confirmed)

    def reset(self) -> None:
        self._confirmed.clear()
        self.audit.clear()
