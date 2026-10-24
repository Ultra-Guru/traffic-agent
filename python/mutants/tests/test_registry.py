import pytest

from traffic_agent.tools.registry import BridgeError, ToolRegistry


def test_register_and_dispatch():
    reg = ToolRegistry()
    reg.register("add", lambda a, b: a + b)
    assert reg.dispatch("add", a=1, b=2) == 3
    assert reg.has("add")
    assert reg.names() == ["add"]


def test_unknown_tool_raises():
    reg = ToolRegistry()
    with pytest.raises(BridgeError) as exc:
        reg.dispatch("nope")
    assert exc.value.code == "unknown_tool"


def test_bad_params_raise_bridge_error():
    reg = ToolRegistry()
    reg.register("add", lambda a, b: a + b)
    with pytest.raises(BridgeError) as exc:
        reg.dispatch("add", a=1)
    assert exc.value.code == "bad_params"


def test_duplicate_registration_rejected():
    reg = ToolRegistry()
    reg.register("x", lambda: 1)
    with pytest.raises(BridgeError) as exc:
        reg.register("x", lambda: 2)
    assert exc.value.code == "duplicate_tool"


def test_empty_name_rejected():
    reg = ToolRegistry()
    with pytest.raises(BridgeError) as exc:
        reg.register("", lambda: 1)
    assert exc.value.code == "invalid_tool"


def test_unregister():
    reg = ToolRegistry()
    reg.register("x", lambda: 1, doc="one")
    assert reg.unregister("x") is True
    assert reg.unregister("x") is False
    assert not reg.has("x")


def test_docs():
    reg = ToolRegistry()
    reg.register("x", lambda: 1, doc="does x")
    assert reg.doc("x") == "does x"
    assert reg.doc("missing") == ""


def test_dispatch_returns_callables_result_verbatim():
    reg = ToolRegistry()
    reg.register("data", lambda: {"k": [1, 2, 3]})
    assert reg.dispatch("data") == {"k": [1, 2, 3]}
