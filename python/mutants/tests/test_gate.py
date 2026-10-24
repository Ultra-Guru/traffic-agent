from traffic_agent.risk.gate import RiskGate, RiskLevel, RiskPolicy, TOOL_RISK


def test_risk_levels_are_ordered():
    assert RiskLevel.SAFE < RiskLevel.CAUTION < RiskLevel.DANGEROUS < RiskLevel.CRITICAL


def test_every_tool_has_a_risk():
    assert len(TOOL_RISK) >= 15
    assert set(TOOL_RISK.values()) <= set(RiskLevel)
    assert TOOL_RISK["list_requests"] == RiskLevel.SAFE
    assert TOOL_RISK["install_cert"] == RiskLevel.CRITICAL


def test_unknown_tool_is_denied():
    decision = RiskGate().evaluate("explode_device")
    assert decision.allowed is False
    assert decision.risk is None
    assert "unknown tool" in decision.reason


def test_safe_tools_pass_default_policy():
    gate = RiskGate()
    assert gate.evaluate("list_requests").allowed
    assert gate.evaluate("read_request").allowed


def test_caution_tools_pass_default_policy():
    assert RiskGate().evaluate("modify_header").allowed
    assert RiskGate().evaluate("set_breakpoint").allowed


def test_dangerous_tools_blocked_by_default_policy():
    decision = RiskGate().evaluate("replay_request")
    assert decision.allowed is False
    assert decision.risk == RiskLevel.DANGEROUS
    assert "exceeds policy" in decision.reason


def test_dangerous_allowed_when_policy_permits():
    policy = RiskPolicy(max_level=RiskLevel.DANGEROUS, require_approval_from=RiskLevel.CRITICAL)
    assert RiskGate(policy).evaluate("block_host").allowed


def test_critical_requires_approval():
    policy = RiskPolicy(max_level=RiskLevel.CRITICAL, require_approval_from=RiskLevel.CRITICAL)
    gate = RiskGate(policy)
    first = gate.evaluate("install_cert")
    assert first.allowed is False
    assert first.requires_approval is True
    assert first.risk == RiskLevel.CRITICAL
    second = gate.evaluate("install_cert", approved=True)
    assert second.allowed is True


def test_read_only_policy_blocks_caution():
    gate = RiskGate(RiskPolicy(max_level=RiskLevel.SAFE, require_approval_from=RiskLevel.CRITICAL))
    decision = gate.evaluate("modify_header")
    assert decision.allowed is False
    assert decision.risk == RiskLevel.CAUTION


def test_risk_of_helper():
    gate = RiskGate()
    assert gate.risk_of("modify_body") == RiskLevel.DANGEROUS
    assert gate.risk_of("missing") is None
