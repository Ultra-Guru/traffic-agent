import json

from traffic_agent.tools.registry import ToolRegistry
from traffic_agent.tools.capture_tools import register_capture_tools
from traffic_agent.tools.transform_tools import register_transform_tools


def make_registry(store):
    reg = ToolRegistry()
    register_capture_tools(reg, store)
    register_transform_tools(reg, store)
    return reg


def test_list_requests_returns_dicts(store):
    reg = make_registry(store)
    out = reg.dispatch("list_requests", limit=2)
    assert len(out) == 2
    assert out[0]["host"] == "api.example.com"
    assert out[0]["method"] == "GET"


def test_list_requests_offset(store):
    reg = make_registry(store)
    out = reg.dispatch("list_requests", limit=2, offset=2)
    assert len(out) == 1
    assert out[0]["path"] == "/v1/login"


def test_read_request(store):
    reg = make_registry(store)
    target = store.list()[0]
    out = reg.dispatch("read_request", request_id=target.id)
    assert out["id"] == target.id
    assert out["status"] == 200
    assert out["request_headers"]["Accept"] == "application/json"


def test_filter_requests_by_host(store):
    reg = make_registry(store)
    out = reg.dispatch("filter_requests", host_regex=r"api\.example\.com")
    assert len(out) == 2


def test_filter_requests_by_method(store):
    reg = make_registry(store)
    out = reg.dispatch("filter_requests", method="POST")
    assert len(out) == 1
    assert out[0]["status"] == 403


def test_stats_summary_tool(store):
    reg = make_registry(store)
    out = reg.dispatch("stats_summary")
    assert out["count"] == 3
    assert out["hosts"]["api.example.com"] == 2
    assert out["methods"] == {"GET": 2, "POST": 1}


def test_modify_header_tool(store):
    reg = make_registry(store)
    target = store.list()[0]
    out = reg.dispatch("modify_header", request_id=target.id, name="Authorization", value="Bearer t")
    assert out["id"] == target.id
    assert out["headers"]["Authorization"] == "Bearer t"


def test_remove_header_tool(store):
    reg = make_registry(store)
    target = store.list()[0]
    out = reg.dispatch("remove_header", request_id=target.id, name="x-api")
    assert out["headers"] == {"Accept": "application/json"}


def test_rewrite_url_tool(store):
    reg = make_registry(store)
    target = store.list()[0]
    out = reg.dispatch("rewrite_url", request_id=target.id, host="proxy.example.net")
    assert out["host"] == "proxy.example.net"
    assert out["path"] == "/v1/users"


def test_modify_body_tool_bounds_replacements(store):
    reg = make_registry(store)
    target = store.list()[2]  # body {"user":"u"}
    out = reg.dispatch(
        "modify_body", request_id=target.id, pattern="u", replacement="x", max_replacements=1
    )
    assert out["replacements"] == 1
    assert store.get(target.id).body == '{"xser":"u"}'


def test_modify_body_tool_no_match(store):
    reg = make_registry(store)
    target = store.list()[2]
    out = reg.dispatch("modify_body", request_id=target.id, pattern="zzz", replacement="x")
    assert out["replacements"] == 0


def test_set_breakpoint_tool(store):
    reg = make_registry(store)
    target = store.list()[0]
    out = reg.dispatch("set_breakpoint", request_id=target.id, phase="response")
    assert out["phase"] == "response"
    pending = reg.dispatch("pending_breakpoints")
    assert pending[str(target.id)] == "response"


def test_json_serializable_payloads(store):
    reg = make_registry(store)
    payload = reg.dispatch("list_requests")
    text = json.dumps(payload)
    assert "api.example.com" in text
