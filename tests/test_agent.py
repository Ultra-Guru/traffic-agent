from __future__ import annotations

import pytest

from tests.helpers import make_session
from traffic_agent import events as ev
from traffic_agent.agent.gating import RiskLevel, ToolGate, default_policies
from traffic_agent.agent.tools import (
    ToolContext,
    ToolRegistry,
    build_registry,
    validate_root_command,
)
from traffic_agent.session import SessionStore
from traffic_agent.transform.breakpoint import BreakpointEngine
from traffic_agent.transform.netcond import NetworkConditionSimulator
from traffic_agent.transform.rewrite import RewriteEngine
from traffic_agent.transform.sandbox import ScriptSandbox


def make_ctx(store=None, bus=None):
    return ToolContext(
        store=store or SessionStore(),
        bus=bus or ev.EventBus(),
        rewrite=RewriteEngine(bus=bus),
        breakpoints=BreakpointEngine(bus=bus),
        sandbox=ScriptSandbox(),
        netcond=NetworkConditionSimulator(),
        root_env={"root_available": True, "kernel_version": (5, 15)},
        tls_secrets=[
            {"client_random": "11" * 32, "secret": "22" * 48},
            {"client_random": "33" * 32, "secret": "44" * 48},
        ],
    )


def seeded_store():
    store = SessionStore()
    store.add(make_session(host="api.example.com", path="/login", method="POST", started_at=1.0))
    store.add(make_session(host="api.example.com", path="/data", started_at=2.0))
    store.add(make_session(host="cdn.example.net", path="/img", started_at=3.0))
    return store


class TestToolGate:
    def test_unknown_tool_denied(self):
        gate = ToolGate()
        decision = gate.evaluate("no-such-tool")
        assert decision.allowed is False
        assert decision.requires_confirmation is False
        assert decision.risk is None
        assert "unknown tool" in decision.reason

    def test_low_risk_auto_approved(self):
        gate = ToolGate()
        decision = gate.evaluate("query_connections")
        assert decision.allowed is True
        assert decision.requires_confirmation is False
        assert decision.risk is RiskLevel.LOW

    def test_medium_requires_confirmation_then_remembered(self):
        gate = ToolGate()
        decision = gate.evaluate("create_rewrite_rule")
        assert decision.allowed is False
        assert decision.requires_confirmation is True
        assert decision.risk is RiskLevel.MEDIUM
        assert gate.confirm("create_rewrite_rule") is True
        assert gate.evaluate("create_rewrite_rule").allowed is True
        assert "create_rewrite_rule" in gate.confirmed_tools()

    def test_medium_confirmed_now_remembered(self):
        gate = ToolGate()
        assert gate.evaluate("create_rewrite_rule", confirmed_now=True).allowed is True
        assert gate.evaluate("create_rewrite_rule").allowed is True

    def test_high_risk_needs_confirmation_every_time(self):
        gate = ToolGate()
        assert gate.evaluate("inject_script").requires_confirmation is True
        assert gate.evaluate("inject_script", confirmed_now=True).allowed is True
        # HIGH 不做会话记忆：下一次仍然要求确认
        again = gate.evaluate("inject_script")
        assert again.allowed is False
        assert again.requires_confirmation is True
        assert gate.confirm("inject_script") is False

    def test_default_disabled_tool(self):
        gate = ToolGate()
        decision = gate.evaluate("exec_root_shell")
        assert decision.allowed is False
        assert "disabled by default" in decision.reason
        gate.enable_tool("exec_root_shell")
        assert gate.evaluate("exec_root_shell", confirmed_now=True).allowed is True

    def test_enable_unknown_tool_raises(self):
        gate = ToolGate()
        with pytest.raises(KeyError):
            gate.enable_tool("nope")

    def test_audit_log_records(self):
        gate = ToolGate(clock=lambda: 42.0)
        gate.evaluate("query_connections")
        gate.evaluate("inject_script")
        assert len(gate.audit) == 2
        assert gate.audit[0].ts == 42.0
        assert gate.audit[1].allowed is False
        assert gate.audit[1].tool == "inject_script"

    def test_reset_clears(self):
        gate = ToolGate()
        gate.confirm("set_breakpoint")
        gate.evaluate("query_connections")
        gate.reset()
        assert gate.confirmed_tools() == set()
        assert gate.audit == []
        assert gate.evaluate("set_breakpoint").allowed is False

    def test_default_policies_complete(self):
        policies = default_policies()
        for name in (
            "query_connections", "search_payload", "compare_sessions", "check_root_capabilities",
            "set_network_condition", "create_rewrite_rule", "set_breakpoint", "resolve_breakpoint",
            "generate_rule_from_example", "replay_request", "export_sslkeylog", "capture_tls_plaintext",
            "inject_script", "replay_sequence", "deploy_system_ca", "enable_pinning_bypass",
            "attach_instrumentation", "set_stealth_mode", "exec_root_shell",
        ):
            assert name in policies, name
        assert policies["exec_root_shell"].default_disabled is True
        assert policies["exec_root_shell"].risk is RiskLevel.HIGH
        assert policies["compare_sessions"].risk is RiskLevel.LOW

    def test_risk_level_ordering(self):
        assert RiskLevel.LOW < RiskLevel.MEDIUM < RiskLevel.HIGH


class TestToolRegistry:
    def test_register_and_names(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        assert "query_connections" in registry.names()
        assert "exec_root_shell" in registry.names()

    def test_duplicate_registration_raises(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        with pytest.raises(Exception):
            registry.register("query_connections", lambda c, a: None, RiskLevel.LOW)

    def test_unknown_tool_invoke(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("nope")
        assert result.ok is False
        assert "unknown tool" in result.error

    def test_query_connections(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("query_connections", {"host": "api.example.com"})
        assert result.ok is True
        assert result.data["count"] == 2
        assert result.risk is RiskLevel.LOW

    def test_query_connections_with_limit(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("query_connections", {"limit": 1})
        assert result.data["count"] == 1

    def test_search_payload(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("search_payload", {"pattern": r"\{"})
        assert result.ok is True
        assert result.data["count"] == 3  # 请求/响应体均为 {}

    def test_search_payload_unsafe_regex_rejected(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("search_payload", {"pattern": "(a+)+"})
        assert result.ok is False

    def test_search_payload_literal(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("search_payload", {"pattern": "/login", "is_regex": False})
        assert result.ok is True
        assert result.data["count"] == 1

    def test_create_rewrite_rule_with_impact(self):
        store = seeded_store()
        ctx = make_ctx(store=store)
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "create_rewrite_rule",
            {
                "matcher": {"host": "api.example.com"},
                "action": {"kind": "replace_body", "search": "false", "replacement": "true"},
            },
            confirmed=True,
        )
        assert result.ok is True
        assert len(ctx.rewrite.rules) == 1
        impact = result.data["impact"]
        assert impact["total_sessions"] == 3
        assert len(impact["matched_sessions"]) == 2
        assert len(impact["sensitive_hits"]) == 1  # /login

    def test_create_rewrite_rule_gate_blocks_without_confirm(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("create_rewrite_rule", {"matcher": {}, "action": {"kind": "set_header", "header_name": "x", "header_value": "1"}})
        assert result.ok is False
        assert "confirmation" in result.error

    def test_create_rewrite_rule_invalid_action(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "create_rewrite_rule",
            {"matcher": {}, "action": {"kind": "set_header"}},  # 缺 header_name
            confirmed=True,
        )
        assert result.ok is False
        assert "header_name" in result.error

    def test_generate_rule_from_example(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "generate_rule_from_example",
            {"host": "api.example.com", "before": '"vip":false', "after": '"vip":true'},
            confirmed=True,
        )
        assert result.ok is True
        assert result.data["rule_id"]
        assert len(ctx.rewrite.rules) == 1
        assert ctx.rewrite.rules[0].source == "agent"

    def test_generate_rule_from_example_same_before_after(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "generate_rule_from_example",
            {"before": "x", "after": "x"},
            confirmed=True,
        )
        assert result.ok is False

    def test_set_and_resolve_breakpoint(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("set_breakpoint", {"matcher": {"host": "api.example.com"}}, confirmed=True)
        assert result.ok is True
        bp_id = result.data["bp_id"]
        from tests.helpers import build_request_bytes
        from traffic_agent.capture.parsers import parse_http1_request

        request = parse_http1_request(build_request_bytes("POST", "/pay", "api.example.com"))
        hit = ctx.breakpoints.intercept("up", request=request)
        assert hit is not None
        assert hit.bp_id == bp_id
        resolved = registry.invoke("resolve_breakpoint", {"hit_id": hit.hit_id, "action": "drop"}, confirmed=True)
        assert resolved.ok is True
        assert resolved.data["state"] == "dropped"

    def test_inject_script_dry_run(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "inject_script", {"source": "r = getRequest()\nsetRequest(r)"}, confirmed=True
        )
        assert result.ok is True
        assert result.data["validated"] is True
        assert result.data["executed"] is False
        assert result.data["capabilities"] == ["getRequest", "setRequest", "getResponse", "setResponse", "log"]

    def test_inject_script_executes_when_not_dry_run(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "inject_script",
            {"source": "r = getRequest()\nlog('seen')", "request": {"a": 1}, "dry_run": False},
            confirmed=True,
        )
        assert result.ok is True
        assert result.data["executed"] is True
        assert result.data["logs"] == ["seen"]

    def test_inject_script_unsafe_source_rejected(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("inject_script", {"source": "import os"}, confirmed=True)
        assert result.ok is False
        assert "imports" in result.error

    def test_set_network_condition(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "set_network_condition", {"latency_ms": 100, "jitter_ms": 20, "loss_pct": 10.0, "ttl_seconds": 5}
        )
        assert result.ok is True
        assert result.data["profile"]["latency_ms"] == 100
        assert result.data["profile"]["jitter_ms"] == 20
        assert ctx.netcond.profile.latency_ms == 100
        assert ctx.netcond.profile.loss_pct == 10.0

    def test_set_network_condition_invalid(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("set_network_condition", {"loss_pct": 150})
        assert result.ok is False

    def test_replay_request(self):
        store = seeded_store()
        ctx = make_ctx(store=store)
        registry = build_registry(ctx, ToolGate())
        session_id = store.all()[0].session_id
        result = registry.invoke("replay_request", {"session_id": session_id}, confirmed=True)
        assert result.ok is True
        assert result.data["replayed"] == session_id
        assert result.data["curl"].startswith("curl -X POST")

    def test_replay_request_unknown_session(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("replay_request", {"session_id": "nope"}, confirmed=True)
        assert result.ok is False
        assert "unknown session" in result.error

    def test_replay_sequence(self):
        store = seeded_store()
        ctx = make_ctx(store=store)
        registry = build_registry(ctx, ToolGate())
        ids = [s.session_id for s in store.all()][::-1]
        result = registry.invoke("replay_sequence", {"session_ids": ids}, confirmed=True)
        assert result.ok is True
        assert result.data["count"] == 3
        assert result.data["sequence"] == [s.session_id for s in store.all()]  # 按时间轴排序

    def test_replay_sequence_high_risk_needs_confirm(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("replay_sequence", {"session_ids": ["x"]})
        assert result.ok is False
        assert "high risk" in result.error

    def test_replay_sequence_empty(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("replay_sequence", {"session_ids": []}, confirmed=True)
        assert result.ok is False

    def test_compare_sessions(self):
        store = seeded_store()
        ctx = make_ctx(store=store)
        registry = build_registry(ctx, ToolGate())
        baseline_ids = [s.session_id for s in store.query(host="api.example.com")]
        candidate_ids = [s.session_id for s in store.all()]
        result = registry.invoke(
            "compare_sessions", {"baseline_ids": baseline_ids, "candidate_ids": candidate_ids}
        )
        assert result.ok is True
        assert result.data["baseline_count"] == 2
        assert result.data["candidate_count"] == 3
        assert result.data["counts"]["added"] == 1

    def test_compare_sessions_missing_ids(self):
        ctx = make_ctx(store=seeded_store())
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("compare_sessions", {"baseline_ids": [], "candidate_ids": ["x"]})
        assert result.ok is False

    def test_check_root_capabilities(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("check_root_capabilities")
        assert result.ok is True
        assert result.data["root_available"] is True
        assert result.data["ebpf_tls"] == "available"
        assert result.data["channels"] == ["af_packet", "nfqueue", "tproxy", "ebpf_socket"]

    def test_export_sslkeylog(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("export_sslkeylog", {}, confirmed=True)
        assert result.ok is True
        assert result.data["line_count"] == 2
        assert result.data["content"].startswith("CLIENT_RANDOM")

    def test_capture_tls_plaintext(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("capture_tls_plaintext", {"target_app": "com.demo"}, confirmed=True)
        assert result.ok is True
        assert result.data["capture_method"] == "ebpf_tls"

    def test_capture_tls_plaintext_requires_target(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("capture_tls_plaintext", {}, confirmed=True)
        assert result.ok is False

    def test_deploy_system_ca(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("deploy_system_ca", {"framework": "magisk"}, confirmed=True)
        assert result.ok is True
        assert result.data["deployed"] is True
        assert result.data["cleanup_on_uninstall"] is True

    def test_deploy_system_ca_bad_framework(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("deploy_system_ca", {"framework": "supersu"}, confirmed=True)
        assert result.ok is False

    def test_enable_pinning_bypass(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "enable_pinning_bypass", {"target_app": "com.demo", "strategy": "lsposed"}, confirmed=True
        )
        assert result.ok is True
        assert result.data["module_scope"] == ["com.demo"]

    def test_enable_pinning_bypass_requires_target(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("enable_pinning_bypass", {}, confirmed=True)
        assert result.ok is False

    def test_attach_instrumentation(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "attach_instrumentation", {"target_app": "com.demo", "profile": "ssl_bypass"}, confirmed=True
        )
        assert result.ok is True
        assert result.data["script_source"] == "audited-builtin"

    def test_attach_instrumentation_bad_profile(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke(
            "attach_instrumentation", {"target_app": "com.demo", "profile": "rm_rf"}, confirmed=True
        )
        assert result.ok is False
        assert "ssl_bypass" in result.error

    def test_set_stealth_mode(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        assert registry.invoke("set_stealth_mode", {"level": "full"}, confirmed=True).data["stealth"] is True
        assert registry.invoke("set_stealth_mode", {"level": "maximum"}, confirmed=True).ok is False

    def test_exec_root_shell_disabled_by_default(self):
        ctx = make_ctx()
        gate = ToolGate()
        registry = build_registry(ctx, gate)
        result = registry.invoke("exec_root_shell", {"command": "ps"}, confirmed=True)
        assert result.ok is False
        assert "disabled by default" in result.error

    def test_exec_root_shell_whitelist(self):
        ctx = make_ctx()
        gate = ToolGate()
        gate.enable_tool("exec_root_shell")
        registry = build_registry(ctx, gate)
        ok = registry.invoke("exec_root_shell", {"command": "iptables -L"}, confirmed=True)
        assert ok.ok is True
        assert ok.data["executed"] is True
        # 白名单内命令的多空格归一化
        assert registry.invoke("exec_root_shell", {"command": "iptables  -L"}, confirmed=True).ok is True
        for bad in ["ps -A", "ps;rm -rf /", "ps | cat", "ps > out", "ps `id`", "ps $HOME", "rm -rf /", "  ps", "ps ", "ps & bg", "ps \\x"]:
            rejected = registry.invoke("exec_root_shell", {"command": bad}, confirmed=True)
            assert rejected.ok is False, bad

    def test_validate_root_command_direct(self):
        assert validate_root_command("ps") is True
        assert validate_root_command("id") is True
        assert validate_root_command("getenforce") is True
        assert validate_root_command("") is False
        assert validate_root_command("ps -ef") is False
        assert validate_root_command("iptables -L;\nrm") is False

    def test_tool_invoked_event_published(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        registry.invoke("query_connections")
        events = ctx.bus.events(topic=ev.EVENT_TOOL_INVOKED)
        assert len(events) == 1
        assert events[0].payload["tool"] == "query_connections"
        assert events[0].payload["allowed"] is True
        assert len(registry.invocations) == 1

    def test_gate_denial_published_with_allowed_false(self):
        ctx = make_ctx()
        registry = build_registry(ctx, ToolGate())
        registry.invoke("inject_script", {"source": "log('x')"})
        events = ctx.bus.events(topic=ev.EVENT_TOOL_INVOKED)
        assert events[-1].payload["allowed"] is False

    def test_missing_context_engine(self):
        ctx = ToolContext(store=SessionStore())  # rewrite 未配置
        registry = build_registry(ctx, ToolGate())
        result = registry.invoke("create_rewrite_rule", {"matcher": {}, "action": {"kind": "set_header", "header_name": "x", "header_value": "1"}}, confirmed=True)
        assert result.ok is False
        assert "not configured" in result.error
