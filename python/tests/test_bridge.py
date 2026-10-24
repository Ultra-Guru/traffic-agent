import json
import io

from traffic_agent.bridge import Bridge
from traffic_agent.risk.gate import RiskGate, RiskPolicy, RiskLevel


def make_bridge(**kwargs):
    return Bridge(gate=RiskGate(RiskPolicy(max_level=RiskLevel.CAUTION)), **kwargs)


def decoded(line):
    from urllib.parse import parse_qsl
    return dict(parse_qsl(line, keep_blank_values=True))


def test_encode_escapes_values():
    out = Bridge.encode({"msg": "a b&c=d"})
    assert out == "msg=a%20b%26c%3Dd"


def test_decode_round_trip():
    line = Bridge.encode({"method": "read_request", "id": "5"})
    assert Bridge.decode(line) == {"method": "read_request", "id": "5"}


def test_successful_list_call(store):
    bridge = make_bridge(store=store)
    response = decoded(bridge.handle_line("method=list_requests&limit=2"))
    assert response["ok"] == "1"
    payload = json.loads(response["payload"])
    assert len(payload) == 2


def test_read_request_call(store):
    bridge = make_bridge(store=store)
    target = store.list()[0]
    response = decoded(bridge.handle_line(f"method=read_request&request_id={target.id}"))
    assert response["ok"] == "1"
    assert json.loads(response["payload"])["host"] == "api.example.com"


def test_unknown_method_reports_error(store):
    bridge = make_bridge(store=store)
    response = decoded(bridge.handle_line("method=does_not_exist"))
    assert response["ok"] == "0"
    assert response["error_code"] == "unknown_tool"


def test_missing_method_reports_error(store):
    bridge = make_bridge(store=store)
    response = decoded(bridge.handle_line("limit=5"))
    assert response["ok"] == "0"
    assert response["error_code"] == "missing_method"


def test_empty_line_reports_error(store):
    bridge = make_bridge(store=store)
    response = decoded(bridge.handle_line("   "))
    assert response["ok"] == "0"
    assert response["error_code"] == "empty_line"


def test_gated_tool_denied_by_default_policy(store):
    bridge = make_bridge(store=store)
    target = store.list()[0]
    response = decoded(bridge.handle_line(f"method=modify_body&request_id={target.id}&pattern=a&replacement=b"))
    assert response["ok"] == "0"
    assert response["error_code"] == "gate_denied"
    assert response["risk"] == "dangerous"


def test_caution_tool_allowed(store):
    bridge = make_bridge(store=store)
    target = store.list()[0]
    response = decoded(bridge.handle_line(f"method=modify_header&request_id={target.id}&name=X-A&value=1"))
    assert response["ok"] == "1"


def test_critical_requires_approval_flag(store):
    policy = RiskPolicy(max_level=RiskLevel.CRITICAL, require_approval_from=RiskLevel.CRITICAL)
    bridge = Bridge(gate=RiskGate(policy), store=store)
    denied = decoded(bridge.handle_line("method=install_cert"))
    assert denied["ok"] == "0"
    assert denied["error_code"] == "approval_required"
    approved = decoded(bridge.handle_line("method=install_cert&__approve=1"))
    # install_cert is registered nowhere yet, but the gate lets it through to
    # the registry which reports unknown_tool — proving the gate passed.
    assert approved["error_code"] == "unknown_tool"


def test_audit_trails_calls(store):
    bridge = make_bridge(store=store)
    target = store.list()[0]
    bridge.handle_line("method=list_requests")
    bridge.handle_line(f"method=modify_body&request_id={target.id}&pattern=a&replacement=b")
    entries = bridge.audit.tail(10)
    assert len(entries) == 2
    assert entries[0].decision == "allowed"
    assert entries[1].decision == "denied"


def test_serve_loop_over_stringio(store):
    bridge = make_bridge(store=store)
    stdin = io.StringIO("method=list_requests&limit=1\n\nmethod=stats_summary\n")
    stdout = io.StringIO()
    handled = bridge.serve(stdin=stdin, stdout=stdout)
    assert handled == 2
    lines = stdout.getvalue().strip().split("\n")
    assert all(line.startswith("ok=") for line in lines)
