import pytest

from traffic_agent.sandbox.executor import (
    ALLOWED_BUILTINS,
    FORBIDDEN_IMPORTS,
    SandboxExecutor,
    SandboxTimeout,
    SandboxViolation,
)


def test_simple_script_runs():
    result = SandboxExecutor().run("x = 1 + 2\ny = x * 2")
    assert result.ok is True
    assert result.namespace["y"] == 6


def test_return_value_visible_in_namespace():
    result = SandboxExecutor().run("value = 'hello'.upper()")
    assert result.namespace["value"] == "HELLO"


def test_syntax_error_reported():
    result = SandboxExecutor().run("def broken(:")
    assert result.ok is False
    assert "syntax error" in result.error


def test_forbidden_os_import_rejected():
    with pytest.raises(SandboxViolation) as exc:
        SandboxExecutor().run("import os")
    assert "os" in exc.value.reason


def test_forbidden_subprocess_rejected():
    with pytest.raises(SandboxViolation):
        SandboxExecutor().run("import subprocess\nsubprocess.run(['ls'])")


def test_forbidden_import_from_rejected():
    with pytest.raises(SandboxViolation) as exc:
        SandboxExecutor().run("from socket import socket")
    assert "socket" in exc.value.reason


def test_allowed_import_passes():
    # re / json are not on the forbidden list
    result = SandboxExecutor().run("import json\nv = json.dumps({'a': 1})")
    assert result.ok is True
    assert result.namespace["v"] == '{"a": 1}'


def test_open_is_not_available():
    result = SandboxExecutor().run("f = open('/etc/passwd')")
    assert result.ok is False
    assert "error" in result.error


def test_eval_is_not_available():
    result = SandboxExecutor().run("v = eval('1+1')")
    assert result.ok is False


def test_timeout_kills_infinite_loop():
    result = SandboxExecutor().run("while True:\n    pass", timeout_ms=150)
    assert result.ok is False
    assert result.error == "timeout"


def test_print_is_captured():
    result = SandboxExecutor().run("print('hi'); print('there')")
    assert result.ok is True
    assert result.stdout == "hi\nthere"


def test_context_values_visible():
    result = SandboxExecutor().run("doubled = n * 2", context={"n": 21})
    assert result.namespace["doubled"] == 42


def test_runtime_exception_reported_not_raised():
    result = SandboxExecutor().run("raise ValueError('boom')")
    assert result.ok is False
    assert "ValueError" in result.error
    assert "boom" in result.error


def test_allowed_builtins_cover_common_cases():
    for name in ("len", "sorted", "range", "str", "int", "max"):
        assert name in ALLOWED_BUILTINS


def test_forbidden_set_covers_os_and_network():
    for name in ("os", "sys", "subprocess", "socket"):
        assert name in FORBIDDEN_IMPORTS
