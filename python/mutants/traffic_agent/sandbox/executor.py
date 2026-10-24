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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁSandboxViolationǁ__init____mutmut: MutantDict = {}  # type: ignore


class SandboxViolation(Exception):
    @_mutmut_mutated(mutants_xǁSandboxViolationǁ__init____mutmut)
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason
    def xǁSandboxViolationǁ__init____mutmut_orig(self, reason: str):
        super().__init__(reason)
        self.reason = reason
    def xǁSandboxViolationǁ__init____mutmut_1(self, reason: str):
        super().__init__(None)
        self.reason = reason
    def xǁSandboxViolationǁ__init____mutmut_2(self, reason: str):
        super().__init__(reason)
        self.reason = None

mutants_xǁSandboxViolationǁ__init____mutmut['_mutmut_orig'] = SandboxViolation.xǁSandboxViolationǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁSandboxViolationǁ__init____mutmut['xǁSandboxViolationǁ__init____mutmut_1'] = SandboxViolation.xǁSandboxViolationǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁSandboxViolationǁ__init____mutmut['xǁSandboxViolationǁ__init____mutmut_2'] = SandboxViolation.xǁSandboxViolationǁ__init____mutmut_2 # type: ignore # mutmut generated


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
mutants_x__safe_import__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__safe_import__mutmut)
def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(".")[0]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_orig(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(".")[0]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_1(name, globals=None, locals=None, fromlist=(), level=1):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(".")[0]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_2(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = None
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_3(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(None)[0]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_4(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split("XX.XX")[0]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_5(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(".")[1]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_6(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(".")[0]
    if root not in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_7(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(".")[0]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(None)
    import importlib
    return importlib.import_module(name)


def x__safe_import__mutmut_8(name, globals=None, locals=None, fromlist=(), level=0):
    """__import__ replacement enforcing the forbidden-module list at runtime."""
    root = name.split(".")[0]
    if root in FORBIDDEN_IMPORTS:
        raise SandboxViolation(f"import forbidden: {name}")
    import importlib
    return importlib.import_module(None)

mutants_x__safe_import__mutmut['_mutmut_orig'] = x__safe_import__mutmut_orig # type: ignore # mutmut generated
mutants_x__safe_import__mutmut['x__safe_import__mutmut_1'] = x__safe_import__mutmut_1 # type: ignore # mutmut generated
mutants_x__safe_import__mutmut['x__safe_import__mutmut_2'] = x__safe_import__mutmut_2 # type: ignore # mutmut generated
mutants_x__safe_import__mutmut['x__safe_import__mutmut_3'] = x__safe_import__mutmut_3 # type: ignore # mutmut generated
mutants_x__safe_import__mutmut['x__safe_import__mutmut_4'] = x__safe_import__mutmut_4 # type: ignore # mutmut generated
mutants_x__safe_import__mutmut['x__safe_import__mutmut_5'] = x__safe_import__mutmut_5 # type: ignore # mutmut generated
mutants_x__safe_import__mutmut['x__safe_import__mutmut_6'] = x__safe_import__mutmut_6 # type: ignore # mutmut generated
mutants_x__safe_import__mutmut['x__safe_import__mutmut_7'] = x__safe_import__mutmut_7 # type: ignore # mutmut generated
mutants_x__safe_import__mutmut['x__safe_import__mutmut_8'] = x__safe_import__mutmut_8 # type: ignore # mutmut generated
mutants_xǁ_CapturePrintǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁ_CapturePrintǁ__call____mutmut: MutantDict = {}  # type: ignore


class _CapturePrint:
    @_mutmut_mutated(mutants_xǁ_CapturePrintǁ__init____mutmut)
    def __init__(self) -> None:
        self.parts: list[str] = []
    def xǁ_CapturePrintǁ__init____mutmut_orig(self) -> None:
        self.parts: list[str] = []
    def xǁ_CapturePrintǁ__init____mutmut_1(self) -> None:
        self.parts: list[str] = None

    @_mutmut_mutated(mutants_xǁ_CapturePrintǁ__call____mutmut)
    def __call__(self, *args, **kwargs) -> None:
        self.parts.append(" ".join(str(a) for a in args))

    def xǁ_CapturePrintǁ__call____mutmut_orig(self, *args, **kwargs) -> None:
        self.parts.append(" ".join(str(a) for a in args))

    def xǁ_CapturePrintǁ__call____mutmut_1(self, *args, **kwargs) -> None:
        self.parts.append(None)

    def xǁ_CapturePrintǁ__call____mutmut_2(self, *args, **kwargs) -> None:
        self.parts.append(" ".join(None))

    def xǁ_CapturePrintǁ__call____mutmut_3(self, *args, **kwargs) -> None:
        self.parts.append("XX XX".join(str(a) for a in args))

    def xǁ_CapturePrintǁ__call____mutmut_4(self, *args, **kwargs) -> None:
        self.parts.append(" ".join(str(None) for a in args))

mutants_xǁ_CapturePrintǁ__init____mutmut['_mutmut_orig'] = _CapturePrint.xǁ_CapturePrintǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁ_CapturePrintǁ__init____mutmut['xǁ_CapturePrintǁ__init____mutmut_1'] = _CapturePrint.xǁ_CapturePrintǁ__init____mutmut_1 # type: ignore # mutmut generated

mutants_xǁ_CapturePrintǁ__call____mutmut['_mutmut_orig'] = _CapturePrint.xǁ_CapturePrintǁ__call____mutmut_orig # type: ignore # mutmut generated
mutants_xǁ_CapturePrintǁ__call____mutmut['xǁ_CapturePrintǁ__call____mutmut_1'] = _CapturePrint.xǁ_CapturePrintǁ__call____mutmut_1 # type: ignore # mutmut generated
mutants_xǁ_CapturePrintǁ__call____mutmut['xǁ_CapturePrintǁ__call____mutmut_2'] = _CapturePrint.xǁ_CapturePrintǁ__call____mutmut_2 # type: ignore # mutmut generated
mutants_xǁ_CapturePrintǁ__call____mutmut['xǁ_CapturePrintǁ__call____mutmut_3'] = _CapturePrint.xǁ_CapturePrintǁ__call____mutmut_3 # type: ignore # mutmut generated
mutants_xǁ_CapturePrintǁ__call____mutmut['xǁ_CapturePrintǁ__call____mutmut_4'] = _CapturePrint.xǁ_CapturePrintǁ__call____mutmut_4 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__check_ast__mutmut)
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


def x__check_ast__mutmut_orig(tree: ast.AST) -> None:
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


def x__check_ast__mutmut_1(tree: ast.AST) -> None:
    for node in ast.walk(None):
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


def x__check_ast__mutmut_2(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = None
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_3(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(None)[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_4(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split("XX.XX")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_5(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[1]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_6(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_7(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(None)
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_8(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = None
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_9(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(None)[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_10(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module and "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_11(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "XXXX").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_12(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split("XX.XX")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_13(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[1]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_14(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in FORBIDDEN_IMPORTS:
                raise SandboxViolation(f"import from forbidden: {node.module}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_15(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    raise SandboxViolation(f"import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                raise SandboxViolation(None)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_16(tree: ast.AST) -> None:
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
        elif isinstance(node, ast.Name) or isinstance(node.ctx, ast.Store):
            if node.id in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_17(tree: ast.AST) -> None:
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
            if node.id not in ("__builtins__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_18(tree: ast.AST) -> None:
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
            if node.id in ("XX__builtins__XX", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_19(tree: ast.AST) -> None:
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
            if node.id in ("__BUILTINS__", "__import__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_20(tree: ast.AST) -> None:
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
            if node.id in ("__builtins__", "XX__import__XX"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_21(tree: ast.AST) -> None:
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
            if node.id in ("__builtins__", "__IMPORT__"):
                raise SandboxViolation(f"assignment to reserved name: {node.id}")


def x__check_ast__mutmut_22(tree: ast.AST) -> None:
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
                raise SandboxViolation(None)

mutants_x__check_ast__mutmut['_mutmut_orig'] = x__check_ast__mutmut_orig # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_1'] = x__check_ast__mutmut_1 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_2'] = x__check_ast__mutmut_2 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_3'] = x__check_ast__mutmut_3 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_4'] = x__check_ast__mutmut_4 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_5'] = x__check_ast__mutmut_5 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_6'] = x__check_ast__mutmut_6 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_7'] = x__check_ast__mutmut_7 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_8'] = x__check_ast__mutmut_8 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_9'] = x__check_ast__mutmut_9 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_10'] = x__check_ast__mutmut_10 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_11'] = x__check_ast__mutmut_11 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_12'] = x__check_ast__mutmut_12 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_13'] = x__check_ast__mutmut_13 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_14'] = x__check_ast__mutmut_14 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_15'] = x__check_ast__mutmut_15 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_16'] = x__check_ast__mutmut_16 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_17'] = x__check_ast__mutmut_17 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_18'] = x__check_ast__mutmut_18 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_19'] = x__check_ast__mutmut_19 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_20'] = x__check_ast__mutmut_20 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_21'] = x__check_ast__mutmut_21 # type: ignore # mutmut generated
mutants_x__check_ast__mutmut['x__check_ast__mutmut_22'] = x__check_ast__mutmut_22 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁSandboxExecutorǁrun__mutmut: MutantDict = {}  # type: ignore


class SandboxExecutor:
    @_mutmut_mutated(mutants_xǁSandboxExecutorǁ__init____mutmut)
    def __init__(self, timeout_ms: int = 1000):
        self.timeout_ms = timeout_ms
    def xǁSandboxExecutorǁ__init____mutmut_orig(self, timeout_ms: int = 1000):
        self.timeout_ms = timeout_ms
    def xǁSandboxExecutorǁ__init____mutmut_1(self, timeout_ms: int = 1001):
        self.timeout_ms = timeout_ms
    def xǁSandboxExecutorǁ__init____mutmut_2(self, timeout_ms: int = 1000):
        self.timeout_ms = None

    @_mutmut_mutated(mutants_xǁSandboxExecutorǁrun__mutmut)
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

    def xǁSandboxExecutorǁrun__mutmut_orig(
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

    def xǁSandboxExecutorǁrun__mutmut_1(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = None
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

    def xǁSandboxExecutorǁrun__mutmut_2(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if (timeout_ms is not None) and False else self.timeout_ms
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

    def xǁSandboxExecutorǁrun__mutmut_3(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if (timeout_ms is not None) or True else self.timeout_ms
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

    def xǁSandboxExecutorǁrun__mutmut_4(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is None else self.timeout_ms
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

    def xǁSandboxExecutorǁrun__mutmut_5(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = None
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

    def xǁSandboxExecutorǁrun__mutmut_6(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(None, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_7(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, None, "exec", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_8(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", None, ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_9(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", None)
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

    def xǁSandboxExecutorǁrun__mutmut_10(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile("<scriptlet>", "exec", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_11(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "exec", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_12(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_13(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", )
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

    def xǁSandboxExecutorǁrun__mutmut_14(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "XX<scriptlet>XX", "exec", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_15(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<SCRIPTLET>", "exec", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_16(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "XXexecXX", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_17(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "EXEC", ast.PyCF_ONLY_AST)
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

    def xǁSandboxExecutorǁrun__mutmut_18(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
        except SyntaxError as exc:
            return SandboxResult(None, {}, f"syntax error: {exc.msg}")
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

    def xǁSandboxExecutorǁrun__mutmut_19(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
        except SyntaxError as exc:
            return SandboxResult(False, None, f"syntax error: {exc.msg}")
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

    def xǁSandboxExecutorǁrun__mutmut_20(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
        except SyntaxError as exc:
            return SandboxResult(False, {}, None)
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

    def xǁSandboxExecutorǁrun__mutmut_21(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
        except SyntaxError as exc:
            return SandboxResult({}, f"syntax error: {exc.msg}")
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

    def xǁSandboxExecutorǁrun__mutmut_22(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
        except SyntaxError as exc:
            return SandboxResult(False, f"syntax error: {exc.msg}")
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

    def xǁSandboxExecutorǁrun__mutmut_23(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
        except SyntaxError as exc:
            return SandboxResult(False, {}, )
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

    def xǁSandboxExecutorǁrun__mutmut_24(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> SandboxResult:
        effective_timeout = timeout_ms if timeout_ms is not None else self.timeout_ms
        try:
            tree = compile(source, "<scriptlet>", "exec", ast.PyCF_ONLY_AST)
        except SyntaxError as exc:
            return SandboxResult(True, {}, f"syntax error: {exc.msg}")
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

    def xǁSandboxExecutorǁrun__mutmut_25(
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
        _check_ast(None)

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

    def xǁSandboxExecutorǁrun__mutmut_26(
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

        sink = None
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

    def xǁSandboxExecutorǁrun__mutmut_27(
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
        safe_builtins = None
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

    def xǁSandboxExecutorǁrun__mutmut_28(
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
            name: getattr(None, name)
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

    def xǁSandboxExecutorǁrun__mutmut_29(
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
            name: getattr(_builtins_module, None)
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

    def xǁSandboxExecutorǁrun__mutmut_30(
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
            name: getattr(name)
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

    def xǁSandboxExecutorǁrun__mutmut_31(
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
            name: getattr(_builtins_module, )
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

    def xǁSandboxExecutorǁrun__mutmut_32(
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
            if name not in ("True", "False", "None") or hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_33(
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
            if name in ("True", "False", "None") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_34(
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
            if name not in ("XXTrueXX", "False", "None") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_35(
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
            if name not in ("true", "False", "None") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_36(
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
            if name not in ("TRUE", "False", "None") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_37(
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
            if name not in ("True", "XXFalseXX", "None") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_38(
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
            if name not in ("True", "false", "None") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_39(
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
            if name not in ("True", "FALSE", "None") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_40(
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
            if name not in ("True", "False", "XXNoneXX") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_41(
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
            if name not in ("True", "False", "none") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_42(
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
            if name not in ("True", "False", "NONE") and hasattr(_builtins_module, name)
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

    def xǁSandboxExecutorǁrun__mutmut_43(
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
            if name not in ("True", "False", "None") and hasattr(None, name)
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

    def xǁSandboxExecutorǁrun__mutmut_44(
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
            if name not in ("True", "False", "None") and hasattr(_builtins_module, None)
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

    def xǁSandboxExecutorǁrun__mutmut_45(
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
            if name not in ("True", "False", "None") and hasattr(name)
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

    def xǁSandboxExecutorǁrun__mutmut_46(
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
            if name not in ("True", "False", "None") and hasattr(_builtins_module, )
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

    def xǁSandboxExecutorǁrun__mutmut_47(
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
        safe_builtins["__import__"] = None
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

    def xǁSandboxExecutorǁrun__mutmut_48(
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
        safe_builtins["XX__import__XX"] = _safe_import
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

    def xǁSandboxExecutorǁrun__mutmut_49(
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
        safe_builtins["__IMPORT__"] = _safe_import
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

    def xǁSandboxExecutorǁrun__mutmut_50(
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
        namespace: Dict[str, Any] = None
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

    def xǁSandboxExecutorǁrun__mutmut_51(
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
        namespace: Dict[str, Any] = {"XX__builtins__XX": safe_builtins}
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

    def xǁSandboxExecutorǁrun__mutmut_52(
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
        namespace: Dict[str, Any] = {"__BUILTINS__": safe_builtins}
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

    def xǁSandboxExecutorǁrun__mutmut_53(
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
        namespace["print"] = None
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

    def xǁSandboxExecutorǁrun__mutmut_54(
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
        namespace["XXprintXX"] = sink
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

    def xǁSandboxExecutorǁrun__mutmut_55(
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
        namespace["PRINT"] = sink
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

    def xǁSandboxExecutorǁrun__mutmut_56(
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
        for k, v in (context and {}).items():
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

    def xǁSandboxExecutorǁrun__mutmut_57(
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
            namespace[k] = None

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

    def xǁSandboxExecutorǁrun__mutmut_58(
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

        if effective_timeout >= 0:
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

    def xǁSandboxExecutorǁrun__mutmut_59(
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

        if effective_timeout > 1:
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

    def xǁSandboxExecutorǁrun__mutmut_60(
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
            previous = None
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

    def xǁSandboxExecutorǁrun__mutmut_61(
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
            previous = signal.signal(None, self._alarm_handler)
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

    def xǁSandboxExecutorǁrun__mutmut_62(
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
            previous = signal.signal(signal.SIGALRM, None)
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

    def xǁSandboxExecutorǁrun__mutmut_63(
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
            previous = signal.signal(self._alarm_handler)
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

    def xǁSandboxExecutorǁrun__mutmut_64(
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
            previous = signal.signal(signal.SIGALRM, )
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

    def xǁSandboxExecutorǁrun__mutmut_65(
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
            signal.setitimer(None, effective_timeout / 1000.0)
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

    def xǁSandboxExecutorǁrun__mutmut_66(
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
            signal.setitimer(signal.ITIMER_REAL, None)
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

    def xǁSandboxExecutorǁrun__mutmut_67(
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
            signal.setitimer(effective_timeout / 1000.0)
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

    def xǁSandboxExecutorǁrun__mutmut_68(
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
            signal.setitimer(signal.ITIMER_REAL, )
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

    def xǁSandboxExecutorǁrun__mutmut_69(
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
            signal.setitimer(signal.ITIMER_REAL, effective_timeout * 1000.0)
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

    def xǁSandboxExecutorǁrun__mutmut_70(
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
            signal.setitimer(signal.ITIMER_REAL, effective_timeout / 1001.0)
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

    def xǁSandboxExecutorǁrun__mutmut_71(
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
            exec(None, namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_72(
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
            exec(compile(source, "<scriptlet>", "exec"), None)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_73(
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
            exec(namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_74(
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
            exec(compile(source, "<scriptlet>", "exec"), )  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_75(
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
            exec(compile(None, "<scriptlet>", "exec"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_76(
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
            exec(compile(source, None, "exec"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_77(
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
            exec(compile(source, "<scriptlet>", None), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_78(
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
            exec(compile("<scriptlet>", "exec"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_79(
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
            exec(compile(source, "exec"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_80(
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
            exec(compile(source, "<scriptlet>", ), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_81(
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
            exec(compile(source, "XX<scriptlet>XX", "exec"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_82(
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
            exec(compile(source, "<SCRIPTLET>", "exec"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_83(
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
            exec(compile(source, "<scriptlet>", "XXexecXX"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_84(
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
            exec(compile(source, "<scriptlet>", "EXEC"), namespace)  # noqa: S102 - sandboxed
        except SandboxTimeout:
            return SandboxResult(False, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_85(
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
            return SandboxResult(None, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_86(
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
            return SandboxResult(False, None, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_87(
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
            return SandboxResult(False, {}, None, "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_88(
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
            return SandboxResult(False, {}, "timeout", None)
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_89(
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
            return SandboxResult({}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_90(
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
            return SandboxResult(False, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_91(
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
            return SandboxResult(False, {}, "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_92(
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
            return SandboxResult(False, {}, "timeout", )
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_93(
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
            return SandboxResult(True, {}, "timeout", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_94(
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
            return SandboxResult(False, {}, "XXtimeoutXX", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_95(
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
            return SandboxResult(False, {}, "TIMEOUT", "\n".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_96(
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
            return SandboxResult(False, {}, "timeout", "\n".join(None))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_97(
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
            return SandboxResult(False, {}, "timeout", "XX\nXX".join(sink.parts))
        except BaseException as exc:  # user scripts may raise anything
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_98(
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
            return SandboxResult(None, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_99(
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
            return SandboxResult(False, None, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_100(
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
            return SandboxResult(False, {}, None, "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_101(
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
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", None)
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_102(
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
            return SandboxResult({}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_103(
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
            return SandboxResult(False, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_104(
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
            return SandboxResult(False, {}, "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_105(
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
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", )
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_106(
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
            return SandboxResult(True, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_107(
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
            return SandboxResult(False, {}, f"error: {type(None).__name__}: {exc}", "\n".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_108(
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
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "\n".join(None))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_109(
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
            return SandboxResult(False, {}, f"error: {type(exc).__name__}: {exc}", "XX\nXX".join(sink.parts))
        finally:
            if effective_timeout > 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_110(
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
            if effective_timeout >= 0:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_111(
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
            if effective_timeout > 1:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_112(
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
                signal.setitimer(None, 0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_113(
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
                signal.setitimer(signal.ITIMER_REAL, None)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_114(
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
                signal.setitimer(0)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_115(
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
                signal.setitimer(signal.ITIMER_REAL, )
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_116(
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
                signal.setitimer(signal.ITIMER_REAL, 1)
                signal.signal(signal.SIGALRM, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_117(
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
                signal.signal(None, previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_118(
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
                signal.signal(signal.SIGALRM, None)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_119(
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
                signal.signal(previous)
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_120(
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
                signal.signal(signal.SIGALRM, )
        return SandboxResult(True, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_121(
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
        return SandboxResult(None, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_122(
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
        return SandboxResult(True, None, None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_123(
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
        return SandboxResult(True, dict(namespace), None, None)

    def xǁSandboxExecutorǁrun__mutmut_124(
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
        return SandboxResult(dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_125(
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
        return SandboxResult(True, None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_126(
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
        return SandboxResult(True, dict(namespace), "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_127(
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
        return SandboxResult(True, dict(namespace), None, )

    def xǁSandboxExecutorǁrun__mutmut_128(
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
        return SandboxResult(False, dict(namespace), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_129(
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
        return SandboxResult(True, dict(None), None, "\n".join(sink.parts))

    def xǁSandboxExecutorǁrun__mutmut_130(
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
        return SandboxResult(True, dict(namespace), None, "\n".join(None))

    def xǁSandboxExecutorǁrun__mutmut_131(
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
        return SandboxResult(True, dict(namespace), None, "XX\nXX".join(sink.parts))

    @staticmethod
    def _alarm_handler(signum: int, frame) -> None:
        raise SandboxTimeout()

mutants_xǁSandboxExecutorǁ__init____mutmut['_mutmut_orig'] = SandboxExecutor.xǁSandboxExecutorǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁ__init____mutmut['xǁSandboxExecutorǁ__init____mutmut_1'] = SandboxExecutor.xǁSandboxExecutorǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁ__init____mutmut['xǁSandboxExecutorǁ__init____mutmut_2'] = SandboxExecutor.xǁSandboxExecutorǁ__init____mutmut_2 # type: ignore # mutmut generated

mutants_xǁSandboxExecutorǁrun__mutmut['_mutmut_orig'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_orig # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_1'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_1 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_2'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_2 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_3'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_3 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_4'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_4 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_5'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_5 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_6'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_6 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_7'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_7 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_8'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_8 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_9'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_9 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_10'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_10 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_11'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_11 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_12'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_12 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_13'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_13 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_14'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_14 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_15'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_15 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_16'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_16 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_17'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_17 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_18'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_18 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_19'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_19 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_20'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_20 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_21'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_21 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_22'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_22 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_23'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_23 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_24'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_24 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_25'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_25 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_26'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_26 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_27'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_27 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_28'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_28 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_29'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_29 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_30'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_30 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_31'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_31 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_32'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_32 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_33'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_33 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_34'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_34 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_35'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_35 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_36'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_36 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_37'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_37 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_38'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_38 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_39'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_39 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_40'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_40 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_41'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_41 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_42'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_42 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_43'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_43 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_44'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_44 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_45'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_45 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_46'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_46 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_47'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_47 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_48'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_48 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_49'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_49 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_50'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_50 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_51'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_51 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_52'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_52 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_53'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_53 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_54'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_54 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_55'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_55 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_56'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_56 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_57'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_57 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_58'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_58 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_59'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_59 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_60'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_60 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_61'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_61 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_62'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_62 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_63'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_63 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_64'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_64 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_65'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_65 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_66'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_66 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_67'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_67 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_68'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_68 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_69'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_69 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_70'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_70 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_71'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_71 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_72'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_72 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_73'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_73 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_74'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_74 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_75'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_75 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_76'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_76 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_77'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_77 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_78'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_78 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_79'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_79 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_80'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_80 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_81'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_81 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_82'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_82 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_83'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_83 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_84'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_84 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_85'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_85 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_86'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_86 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_87'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_87 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_88'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_88 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_89'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_89 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_90'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_90 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_91'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_91 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_92'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_92 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_93'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_93 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_94'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_94 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_95'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_95 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_96'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_96 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_97'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_97 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_98'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_98 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_99'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_99 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_100'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_100 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_101'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_101 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_102'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_102 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_103'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_103 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_104'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_104 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_105'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_105 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_106'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_106 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_107'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_107 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_108'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_108 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_109'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_109 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_110'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_110 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_111'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_111 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_112'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_112 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_113'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_113 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_114'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_114 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_115'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_115 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_116'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_116 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_117'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_117 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_118'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_118 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_119'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_119 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_120'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_120 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_121'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_121 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_122'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_122 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_123'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_123 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_124'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_124 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_125'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_125 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_126'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_126 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_127'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_127 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_128'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_128 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_129'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_129 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_130'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_130 # type: ignore # mutmut generated
mutants_xǁSandboxExecutorǁrun__mutmut['xǁSandboxExecutorǁrun__mutmut_131'] = SandboxExecutor.xǁSandboxExecutorǁrun__mutmut_131 # type: ignore # mutmut generated
