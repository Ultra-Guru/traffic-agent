"""Restricted scriptlet executor (SPEC v2.1 L1.5 script sandbox).

Executes small user scripts with:
  * an AST pass rejecting imports of forbidden modules,
  * a minimal builtin surface,
  * a wall-clock timeout.
The executor is deliberately conservative: it is a component of the layered
sandbox, not the only line of defence.
"""

from __future__ import annotations

import ast
import builtins as _builtins_module
import signal
from dataclasses import dataclass
from typing import Any, Dict, Optional


class SandboxViolation(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class SandboxTimeout(Exception):
    pass


FORBIDDEN_IMPORTS = frozenset(
    {
        "os",
        "sys",
        "subprocess",
        "socket",
        "shutil",
        "pathlib",
        "importlib",
        "ctypes",
        "builtins",
    }
)

ALLOWED_BUILTINS = frozenset(
    {
        "abs",
        "all",
        "any",
        "bool",
        "dict",
        "enumerate",
        "filter",
        "float",
        "int",
        "isinstance",
        "len",
        "list",
        "map",
        "max",
        "min",
        "print",
        "range",
        "reversed",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "zip",
        "True",
        "False",
        "None",
        # exceptions user scripts may legitimately raise or catch
        "Exception",
        "ValueError",
        "TypeError",
        "KeyError",
        "IndexError",
        "RuntimeError",
        "StopIteration",
        "ZeroDivisionError",
        "AttributeError",
        "NotImplementedError",
    }
)


@dataclass
class SandboxResult:
    ok: bool
    namespace: Dict[str, Any]
    error: Optional[str] = None
    stdout: str = ""


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(".")[0]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


class _CapturePrint:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def __call__(self, *args, **kwargs) -> None:
        self.parts.append(" ".join(str(a) for a in args))


def _check_ast(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


class SandboxExecutor:
    def __init__(self, timeout_ms: int = 1000):
        self.timeout_ms = timeout_ms

    def run(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
        except SyntaxError as exc:
            return SandboxResult(False, {}, f"syntax error: {exc.msg}")
        _check_ast(tree)

        sink = _CapturePrint()
        # True/False/None are language keywords and need no builtins entry.
        safe_builtins = {
            name: getattr(_builtins_module, name)
            for name in ALLOWED_BUILTINS
            if name not in ("True", "False", "None") and hasattr(_builtins_module, name)
        }
        safe_builtins["__import__"] = _safe_import
        namespace: Dict[str, Any] = {"__builtins__": safe_builtins}
        namespace["print"] = sink
        for k, v in (context or {}).items():
            namespace[k] = v

        if effective_timeout > 0:
            previous = signal.signal(signal.SIGALRM, self._alarm_handler)
            signal.setitimer(signal.ITIMER_REAL, effective_timeout / 1000.0)
        try:
            exec(compile(source, "<scriptlet>", "exec"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    @staticmethod
    def _alarm_handler(signum: int, frame) -> None:
        raise SandboxTimeout()
