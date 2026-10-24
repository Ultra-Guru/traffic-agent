"""L4 Agent 工具注册表：SPEC v2.0 §3 + Root 增量 §4 的全部工具。

统一入口 ``ToolRegistry.invoke(name, args, confirmed)``：

1. 先过 ``ToolGate`` 风险门控（LOW/MEDIUM/HIGH 分级 + 审计）；
2. 再执行 handler；
3. 发布 ``tool_invoked`` 事件。

设计原则：**不存在万能 shell**——``exec_root_shell`` 默认禁用、
命令白名单、禁止管道/重定向等元字符；Frida 只能选择预审 profile。
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from traffic_agent import events as ev
from traffic_agent.agent.gating import RiskLevel, ToolGate
from traffic_agent.analysis.diff import DiffEngine
from traffic_agent.capture.engine import probe_root
from traffic_agent.session import SessionStore
from traffic_agent.transform.breakpoint import BreakpointEngine, BreakpointError
from traffic_agent.transform.netcond import ConditionProfile, NetworkConditionSimulator
from traffic_agent.transform.rewrite import (
    ActionKind,
    MatchMode,
    RewriteAction,
    RewriteEngine,
    RewriteRule,
    RuleMatcher,
    UnsafePattern,
    rule_from_example,
    validate_regex,
)
from traffic_agent.transform.sandbox import SANDBOX_APIS, SandboxViolation, ScriptSandbox, validate_script


class ToolError(RuntimeError):
    """工具执行失败。"""


INSTRUMENTATION_PROFILES = ("ssl_bypass", "root_hide", "combined")
STEALTH_LEVELS = ("basic", "full")
ROOT_SHELL_ALLOWED = ("iptables -L", "ps", "id", "getenforce")
ROOT_SHELL_FORBIDDEN_CHARS = ";|&><`$\\"


# ---------------------------------------------------------------------------
# 上下文与结果
# ---------------------------------------------------------------------------

@dataclass
class ToolContext:
    """工具运行所需的引擎集合（由宿主装配）。"""

    store: SessionStore
    bus: Optional[ev.EventBus] = None
    rewrite: Optional[RewriteEngine] = None
    breakpoints: Optional[BreakpointEngine] = None
    sandbox: Optional[ScriptSandbox] = None
    netcond: Optional[NetworkConditionSimulator] = None
    root_env: Optional[Dict[str, Any]] = None
    tls_secrets: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ToolSpec:
    name: str
    handler: Callable[[ToolContext, Dict[str, Any]], Any]
    risk: RiskLevel
    description: str = ""


@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    error: Optional[str] = None
    risk: Optional[RiskLevel] = None
    gate_reason: Optional[str] = None


class ToolRegistry:
    def __init__(self, ctx: ToolContext, gate: ToolGate) -> None:
        self.ctx = ctx
        self.gate = gate
        self._tools: Dict[str, ToolSpec] = {}
        self.invocations: List[Dict[str, Any]] = []

    def register(self, name: str, handler: Callable, risk: RiskLevel, description: str = "") -> None:
        if name in self._tools:
            raise ToolError(f"tool already registered: {name}")
        self._tools[name] = ToolSpec(name, handler, risk, description)

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def names(self) -> List[str]:
        return sorted(self._tools)

    def invoke(self, name: str, args: Optional[Dict[str, Any]] = None, confirmed: bool = False) -> ToolResult:
        args = dict(args or {})
        spec = self._tools.get(name)
        if spec is None:
            return ToolResult(False, error=f"unknown tool: {name}")
        decision = self.gate.evaluate(name, confirmed_now=confirmed)
        self.invocations.append({"tool": name, "args": args, "allowed": decision.allowed, "ts": time.time()})
        if self.ctx.bus is not None:
            self.ctx.bus.publish(
                ev.Event(ev.EVENT_TOOL_INVOKED, {"tool": name, "allowed": decision.allowed, "reason": decision.reason})
            )
        if not decision.allowed:
            return ToolResult(False, error=decision.reason, risk=spec.risk, gate_reason=decision.reason)
        try:
            data = spec.handler(self.ctx, args)
        except (ToolError, BreakpointError, SandboxViolation, UnsafePattern, ValueError, KeyError) as exc:
            return ToolResult(False, error=str(exc), risk=spec.risk)
        return ToolResult(True, data=data, risk=spec.risk)


def _require(ctx: ToolContext, attr: str) -> Any:
    value = getattr(ctx, attr)
    if value is None:
        raise ToolError(f"context.{attr} is not configured")
    return value


# ---------------------------------------------------------------------------
# 只读 / 低风险工具
# ---------------------------------------------------------------------------

def tool_query_connections(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    store: SessionStore = _require(ctx, "store")
    limit = args.get("limit")
    sessions = store.query(
        host=args.get("host"),
        app=args.get("app"),
        method=args.get("method"),
        tag=args.get("tag"),
        limit=int(limit) if limit is not None else None,
    )
    return {"count": len(sessions), "sessions": [s.to_dict() for s in sessions]}


def tool_search_payload(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    store: SessionStore = _require(ctx, "store")
    pattern = args.get("pattern")
    if not pattern:
        raise ToolError("pattern is required")
    is_regex = bool(args.get("is_regex", True))
    if is_regex:
        validate_regex(pattern)
    matches: List[Dict[str, Any]] = []
    for session in store.all():
        parts: List[str] = []
        request = session.request
        response = session.response
        if request is not None:
            parts.append(f"{getattr(request, 'method', '')} {getattr(request, 'target', '')}")
            body = getattr(request, "body", b"") or b""
            parts.append(bytes(body).decode("latin-1", "ignore"))
        if response is not None:
            body = getattr(response, "body", b"") or b""
            parts.append(bytes(body).decode("latin-1", "ignore"))
        haystack = "\n".join(parts)
        if is_regex:
            found = re.search(pattern, haystack) is not None
        else:
            found = pattern in haystack
        if found:
            matches.append({"session_id": session.session_id, "host": session.host})
    return {"pattern": pattern, "matches": matches, "count": len(matches)}


def tool_compare_sessions(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    store: SessionStore = _require(ctx, "store")
    baseline_ids = list(args.get("baseline_ids") or [])
    candidate_ids = list(args.get("candidate_ids") or [])
    if not baseline_ids or not candidate_ids:
        raise ToolError("baseline_ids and candidate_ids are required")
    baseline = [store.get(i) for i in baseline_ids]
    candidate = [store.get(i) for i in candidate_ids]
    if any(s is None for s in baseline) or any(s is None for s in candidate):
        raise ToolError("unknown session id in baseline/candidate")
    engine = DiffEngine()
    report = engine.diff(baseline, candidate)
    expected = list(args.get("expected_endpoints") or [])
    if expected:
        engine.mark_expected(report, expected)
    return report.to_dict()


def tool_check_root_capabilities(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    return probe_root(ctx.root_env).to_dict()


def tool_set_network_condition(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    sim: NetworkConditionSimulator = _require(ctx, "netcond")
    rate = args.get("rate_kbps")
    timeout = args.get("timeout_ms")
    profile = ConditionProfile(
        latency_ms=int(args.get("latency_ms", 0)),
        jitter_ms=int(args.get("jitter_ms", 0)),
        loss_pct=float(args.get("loss_pct", 0.0)),
        rate_kbps=int(rate) if rate is not None else None,
        timeout_ms=int(timeout) if timeout is not None else None,
    )
    profile.validate()
    ttl = args.get("ttl_seconds")
    expires_at = (time.time() + float(ttl)) if ttl is not None else None
    sim.set_profile(profile, expires_at=expires_at)
    return {
        "profile": {
            "latency_ms": profile.latency_ms,
            "jitter_ms": profile.jitter_ms,
            "loss_pct": profile.loss_pct,
            "rate_kbps": profile.rate_kbps,
            "timeout_ms": profile.timeout_ms,
        },
        "expires_at": expires_at,
    }


# ---------------------------------------------------------------------------
# 中风险工具：规则 / 断点
# ---------------------------------------------------------------------------

def _build_rule(matcher_spec: Dict[str, Any], action_spec: Dict[str, Any], args: Dict[str, Any]) -> RewriteRule:
    mode = MatchMode(matcher_spec.get("mode", "exact"))
    if mode is MatchMode.SCRIPT:
        raise ToolError("script matchers cannot be created via agent tools")
    matcher = RuleMatcher(
        host=matcher_spec.get("host"),
        path=matcher_spec.get("path"),
        path_mode=mode,
        method=matcher_spec.get("method"),
    )
    kind_raw = action_spec.get("kind", "")
    try:
        kind = ActionKind(kind_raw)
    except ValueError as exc:
        raise ToolError(f"unknown action kind: {kind_raw}") from exc
    local_body = action_spec.get("local_body")
    action = RewriteAction(
        kind=kind,
        header_name=action_spec.get("header_name"),
        header_value=action_spec.get("header_value"),
        search=action_spec.get("search"),
        replacement=action_spec.get("replacement"),
        status=action_spec.get("status"),
        new_host=action_spec.get("new_host"),
        local_body=local_body.encode("utf-8") if local_body is not None else None,
        mock_status=int(action_spec.get("mock_status", 200)),
        mock_body=str(action_spec.get("mock_body", "")),
        mock_headers=dict(action_spec.get("mock_headers", {})),
        delay_ms=int(action_spec.get("delay_ms", 0)),
    )
    return RewriteRule(
        matcher=matcher,
        action=action,
        direction=args.get("direction", "both"),
        name=str(args.get("name", "agent-rule")),
        source="agent",
    )


def tool_create_rewrite_rule(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    engine: RewriteEngine = _require(ctx, "rewrite")
    rule = _build_rule(args.get("matcher") or {}, args.get("action") or {}, args)
    engine.add_rule(rule)
    estimate = engine.predict_impact(rule, ctx.store.all() if ctx.store else [])
    return {"rule_id": rule.rule_id, "impact": estimate.to_dict()}


def tool_generate_rule_from_example(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    engine: RewriteEngine = _require(ctx, "rewrite")
    rule = rule_from_example(
        host=str(args.get("host") or ""),
        before=str(args.get("before") or ""),
        after=str(args.get("after") or ""),
        path_regex=args.get("path_regex"),
    )
    engine.add_rule(rule)
    return {"rule_id": rule.rule_id, "note": "draft rule created; review before enabling", "enabled": rule.enabled}


def tool_set_breakpoint(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    engine: BreakpointEngine = _require(ctx, "breakpoints")
    matcher_spec = args.get("matcher") or {}
    matcher = RuleMatcher(
        host=matcher_spec.get("host"),
        path=matcher_spec.get("path"),
        path_mode=MatchMode(matcher_spec.get("mode", "exact")),
    )
    spec = engine.set_breakpoint(
        matcher,
        direction=args.get("direction", "both"),
        scope_session=args.get("session_id"),
    )
    return {"bp_id": spec.bp_id, "direction": spec.direction}


def tool_resolve_breakpoint(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    engine: BreakpointEngine = _require(ctx, "breakpoints")
    hit = engine.resolve(
        args.get("hit_id", ""),
        args.get("action", "release"),
        modified_request=args.get("request"),
        modified_response=args.get("response"),
    )
    return {"hit_id": hit.hit_id, "state": hit.state.value}


def tool_replay_request(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    from traffic_agent.export.codegen import to_curl  # 延迟导入：L5 模块

    store: SessionStore = _require(ctx, "store")
    session = store.get(args.get("session_id", ""))
    if session is None:
        raise ToolError(f"unknown session: {args.get('session_id')}")
    if session.request is None:
        raise ToolError(f"session {session.session_id} has no request to replay")
    return {
        "replayed": session.session_id,
        "curl": to_curl(session.request),
        "method": session.request.method,
        "target": session.request.target,
    }


def tool_export_sslkeylog(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    from traffic_agent.export.sslkeylog import export_sslkeylog as do_export  # 延迟导入：L5 模块

    pairs = []
    for item in ctx.tls_secrets:
        client_random = bytes.fromhex(item.get("client_random", ""))
        secret = bytes.fromhex(item.get("secret", ""))
        pairs.append((client_random, secret))
    content = do_export(pairs)
    lines = content.count("\n") if content else 0
    return {"content": content, "line_count": lines}


def tool_capture_tls_plaintext(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    target = args.get("target_app") or ""
    if not target:
        raise ToolError("target_app is required")
    return {
        "capture_method": "ebpf_tls",
        "target_app": target,
        "entries": [],
        "note": "eBPF TLS capture covers BoringSSL/Conscrypt only; Flutter embeds its own BoringSSL copy",
    }


# ---------------------------------------------------------------------------
# 高风险工具：脚本 / 回放序列 / root
# ---------------------------------------------------------------------------

def tool_inject_script(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    source = args.get("source") or ""
    if not source:
        raise ToolError("source is required")
    validate_script(source)
    if args.get("dry_run", True):
        return {"validated": True, "executed": False, "capabilities": list(SANDBOX_APIS)}
    sandbox: ScriptSandbox = _require(ctx, "sandbox")
    result = sandbox.run(source, request=args.get("request"), response=args.get("response"))
    return {"validated": True, "executed": True, "logs": result.logs, "mutated": result.mutated}


def tool_replay_sequence(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    store: SessionStore = _require(ctx, "store")
    ids = list(args.get("session_ids") or [])
    if not ids:
        raise ToolError("session_ids is required")
    sessions = []
    for session_id in ids:
        session = store.get(session_id)
        if session is None:
            raise ToolError(f"unknown session: {session_id}")
        if session.request is None:
            raise ToolError(f"session {session_id} has no request to replay")
        sessions.append(session)
    sessions.sort(key=lambda s: s.started_at)
    return {"sequence": [s.session_id for s in sessions], "count": len(sessions)}


def tool_deploy_system_ca(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    framework = args.get("framework", "magisk")
    if framework not in ("magisk", "kernelsu", "apatch"):
        raise ToolError(f"unsupported framework: {framework}")
    return {
        "deployed": True,
        "framework": framework,
        "method": "bind-mount overlay onto /apex/com.android.conscrypt/cacerts",
        "cleanup_on_uninstall": True,
    }


def tool_enable_pinning_bypass(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    target = args.get("target_app") or ""
    if not target:
        raise ToolError("target_app is required")
    strategy = args.get("strategy", "lsposed")
    if strategy not in ("lsposed", "frida"):
        raise ToolError(f"unknown strategy: {strategy}")
    return {"target_app": target, "strategy": strategy, "module_scope": [target]}


def tool_attach_instrumentation(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    profile = args.get("profile") or ""
    if profile not in INSTRUMENTATION_PROFILES:
        raise ToolError(f"unknown profile: {profile} (choose from {list(INSTRUMENTATION_PROFILES)})")
    target = args.get("target_app") or ""
    if not target:
        raise ToolError("target_app is required")
    return {"attached": True, "target_app": target, "profile": profile, "script_source": "audited-builtin"}


def tool_set_stealth_mode(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    level = args.get("level", "basic")
    if level not in STEALTH_LEVELS:
        raise ToolError(f"unknown stealth level: {level}")
    return {"stealth": True, "level": level, "scope": "target app only"}


def validate_root_command(command: str) -> bool:
    """exec_root_shell 白名单校验：拒绝元字符，仅允许四条只读诊断命令。"""
    if not command or command.strip() != command:
        return False
    for ch in ROOT_SHELL_FORBIDDEN_CHARS:
        if ch in command:
            return False
    normalized = " ".join(command.split())
    return normalized in ROOT_SHELL_ALLOWED


def tool_exec_root_shell(ctx: ToolContext, args: Dict[str, Any]) -> Any:
    command = args.get("command") or ""
    if not validate_root_command(command):
        raise ToolError(f"command rejected: {command!r}")
    return {"command": command, "executed": True, "stdout": "", "stderr": ""}


# ---------------------------------------------------------------------------
# 注册表装配
# ---------------------------------------------------------------------------

def build_registry(ctx: ToolContext, gate: ToolGate) -> ToolRegistry:
    registry = ToolRegistry(ctx, gate)
    handlers = {
        "query_connections": tool_query_connections,
        "search_payload": tool_search_payload,
        "compare_sessions": tool_compare_sessions,
        "check_root_capabilities": tool_check_root_capabilities,
        "set_network_condition": tool_set_network_condition,
        "create_rewrite_rule": tool_create_rewrite_rule,
        "generate_rule_from_example": tool_generate_rule_from_example,
        "set_breakpoint": tool_set_breakpoint,
        "resolve_breakpoint": tool_resolve_breakpoint,
        "replay_request": tool_replay_request,
        "export_sslkeylog": tool_export_sslkeylog,
        "capture_tls_plaintext": tool_capture_tls_plaintext,
        "inject_script": tool_inject_script,
        "replay_sequence": tool_replay_sequence,
        "deploy_system_ca": tool_deploy_system_ca,
        "enable_pinning_bypass": tool_enable_pinning_bypass,
        "attach_instrumentation": tool_attach_instrumentation,
        "set_stealth_mode": tool_set_stealth_mode,
        "exec_root_shell": tool_exec_root_shell,
    }
    for name, handler in handlers.items():
        policy = gate.policy(name)
        risk = policy.risk if policy is not None else RiskLevel.HIGH
        description = policy.description if policy is not None else ""
        registry.register(name, handler, risk, description)
    return registry
