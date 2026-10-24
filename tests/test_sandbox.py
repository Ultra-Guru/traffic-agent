from __future__ import annotations

import pytest

from traffic_agent.transform.sandbox import (
    SANDBOX_APIS,
    SandboxViolation,
    ScriptSandbox,
    validate_script,
)


class TestValidateScript:
    def test_ok_script(self):
        validate_script("r = getRequest()\nr['k'] = 1\nsetRequest(r)\nlog('done')")

    def test_import_forbidden(self):
        with pytest.raises(SandboxViolation, match="imports"):
            validate_script("import os")

    def test_from_import_forbidden(self):
        with pytest.raises(SandboxViolation, match="imports"):
            validate_script("from os import path")

    def test_dunder_name_forbidden(self):
        with pytest.raises(SandboxViolation, match="dunder"):
            validate_script("x = __name__")

    def test_dunder_attribute_forbidden(self):
        with pytest.raises(SandboxViolation, match="dunder"):
            validate_script("x = y.__class__")

    def test_method_call_forbidden(self):
        with pytest.raises(SandboxViolation, match="method"):
            validate_script("x = 'abc'.upper()")

    def test_non_whitelist_function_forbidden(self):
        with pytest.raises(SandboxViolation, match="not available"):
            validate_script("x = len([1, 2])")

    def test_eval_forbidden(self):
        with pytest.raises(SandboxViolation, match="not available"):
            validate_script("x = eval('1')")

    def test_global_forbidden(self):
        with pytest.raises(SandboxViolation, match="global"):
            validate_script("global x")

    def test_nonlocal_forbidden(self):
        with pytest.raises(SandboxViolation, match="nonlocal"):
            validate_script("def f():\n    nonlocal x")

    def test_too_large_raises(self):
        with pytest.raises(SandboxViolation, match="too large"):
            validate_script("x = 1\n" * 30000)  # ~120KB

    def test_syntax_error_propagates(self):
        with pytest.raises(SyntaxError):
            validate_script("def broken(:")

    def test_lambda_with_whitelisted_call_ok(self):
        validate_script("f = lambda: log('x')")


class TestSandboxRun:
    def test_read_modify_write_request(self):
        sandbox = ScriptSandbox()
        result = sandbox.run(
            "r = getRequest()\nr['vip'] = True\nsetRequest(r)\nlog('vip flipped')",
            request={"vip": False, "expire": 2025},
        )
        assert result.mutated is True
        assert result.request == {"vip": True, "expire": 2025}
        assert result.logs == ["vip flipped"]
        assert result.source_lines == 4

    def test_read_only_does_not_flag_mutated(self):
        sandbox = ScriptSandbox()
        result = sandbox.run("r = getRequest()\nlog(r)", request={"a": 1})
        assert result.mutated is False
        assert result.request == {"a": 1}

    def test_get_request_returns_deep_copy(self):
        sandbox = ScriptSandbox()
        source = "r = getRequest()\nr['inner'] = 'changed'"
        result = sandbox.run(source, request={"inner": "original"})
        assert result.request == {"inner": "original"}

    def test_response_roundtrip(self):
        sandbox = ScriptSandbox()
        source = "s = getResponse()\ns['status'] = 'ok'\nsetResponse(s)"
        result = sandbox.run(source, response={"status": "error"})
        assert result.mutated is True
        assert result.response == {"status": "ok"}

    def test_logs_multiple_args_and_types(self):
        result = ScriptSandbox().run("log('a', 1, True)")
        assert result.logs == ["a 1 true"]

    def test_runtime_error_wrapped(self):
        with pytest.raises(SandboxViolation, match="script failed"):
            ScriptSandbox().run("x = getRequest()['missing-key']", request={})

    def test_static_violation_before_exec(self):
        with pytest.raises(SandboxViolation, match="imports"):
            ScriptSandbox().run("import os\nsetRequest({})")

    def test_empty_script_ok(self):
        result = ScriptSandbox().run("")
        assert result.mutated is False
        assert result.logs == []
        assert result.source_lines == 0

    def test_sandbox_apis_order(self):
        assert SANDBOX_APIS == ("getRequest", "setRequest", "getResponse", "setResponse", "log")

    def test_no_builtins_available(self):
        # bool/int 转换、dict/list 访问可用，但 builtins（如 len）静态校验即拒绝
        with pytest.raises(SandboxViolation, match="not available"):
            ScriptSandbox().run("n = len([1])")

    def test_arithmetic_and_string_concat_work(self):
        result = ScriptSandbox().run("x = 1 + 2\ns = 'a' + 'b'\nlog(x, s)")
        assert result.logs == ["3 ab"]
