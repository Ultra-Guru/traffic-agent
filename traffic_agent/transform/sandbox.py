"""L1.5 脚本沙箱：白名单 API（对应 SPEC v2.0 §2.1 / §7 风险表第 1 条）。

脚本可调用的 API 严格限定为::

    getRequest() / setRequest() / getResponse() / setResponse() / log()

脚本**不能** import、不能访问任何 builtin、不能调用白名单以外的函数、
不能进行方法调用——脚本不能成为逃逸通道，也不能操控 Agent 工具。
"""

from __future__ import annotations

import ast
import copy
from dataclasses import dataclass
from typing import Any, Dict, List

SANDBOX_APIS = ("getRequest", "setRequest", "getResponse", "setResponse", "log")
MAX_SCRIPT_BYTES = 100_000
MAX_LOG_LINES = 500
MAX_LOG_LINE_CHARS = 2000


class SandboxViolation(RuntimeError):
    """脚本违反沙箱约束（静态校验或运行期失败）。"""


def validate_script(source: str) -> None:
    """AST 静态校验：违规直接抛 SandboxViolation。"""
    if len(source.encode("utf-8")) > MAX_SCRIPT_BYTES:
        raise SandboxViolation("script too large")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        raise
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise SandboxViolation("imports are forbidden")
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            raise SandboxViolation("global/nonlocal are forbidden")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise SandboxViolation(f"dunder name is forbidden: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise SandboxViolation(f"dunder attribute is forbidden: {node.attr}")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                raise SandboxViolation("method calls are forbidden in sandbox scripts")
            if isinstance(func, ast.Name) and func.id not in SANDBOX_APIS:
                raise SandboxViolation(f"function not available in sandbox: {func.id}")


def _to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return repr(value)


class SandboxContext:
    """脚本运行上下文：持有请求/响应快照，只暴露白名单方法。"""

    def __init__(self, request: Any = None, response: Any = None) -> None:
        self._request = request
        self._response = response
        self.logs: List[str] = []
        self.mutated = False

    def getRequest(self) -> Any:
        return copy.deepcopy(self._request)

    def getResponse(self) -> Any:
        return copy.deepcopy(self._response)

    def setRequest(self, value: Any) -> None:
        self._request = copy.deepcopy(value)
        self.mutated = True

    def setResponse(self, value: Any) -> None:
        self._response = copy.deepcopy(value)
        self.mutated = True

    def log(self, *args: Any) -> None:
        line = " ".join(_to_text(a) for a in args)
        if len(line) > MAX_LOG_LINE_CHARS:
            line = line[:MAX_LOG_LINE_CHARS] + "…"
        self.logs.append(line)
        if len(self.logs) > MAX_LOG_LINES:
            del self.logs[: len(self.logs) - MAX_LOG_LINES]


@dataclass
class SandboxResult:
    request: Any
    response: Any
    logs: List[str]
    mutated: bool
    source_lines: int = 0


class ScriptSandbox:
    """受限执行环境：先静态校验，再以空 builtins 执行。"""

    def run(self, source: str, request: Any = None, response: Any = None) -> SandboxResult:
        validate_script(source)
        ctx = SandboxContext(request, response)
        env: Dict[str, Any] = {"__builtins__": {}}
        for name in SANDBOX_APIS:
            env[name] = getattr(ctx, name)
        try:
            exec(compile(source, "<sandbox>", "exec"), env)  # noqa: S102 — 受限环境执行
        except SandboxViolation:
            raise
        except Exception as exc:  # noqa: BLE001 — 脚本错误统一包装
            raise SandboxViolation(f"script failed: {type(exc).__name__}: {exc}") from exc
        return SandboxResult(
            request=ctx._request,
            response=ctx._response,
            logs=list(ctx.logs),
            mutated=ctx.mutated,
            source_lines=len(source.splitlines()),
        )
