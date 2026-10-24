"""Scriptlet engine: on_request / on_response hooks (Python layer)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..sandbox.executor import SandboxExecutor, SandboxResult


@dataclass
class ScriptletContext:
    """Values handed to the user script; mutations are visible to the caller."""

    values: Dict[str, Any] = field(default_factory=dict)


class Scriptlet:
    def __init__(self, name: str, source: str, namespace: Dict[str, Any]):
        self.name = name
        self.source = source
        self._namespace = namespace

    @property
    def has_on_request(self) -> bool:
        return callable(self._namespace.get("on_request"))

    @property
    def has_on_response(self) -> bool:
        return callable(self._namespace.get("on_response"))

    def on_request(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_request")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def on_response(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_response")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)


class ScriptletEngine:
    """Loads, validates and runs scriptlets inside the sandbox executor."""

    def __init__(self, executor: Optional[SandboxExecutor] = None):
        self.executor = executor or SandboxExecutor()
        self._scriptlets: Dict[str, Scriptlet] = {}

    def load(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def get(self, name: str) -> Optional[Scriptlet]:
        return self._scriptlets.get(name)

    def names(self) -> list:
        return sorted(self._scriptlets)

    def unload(self, name: str) -> bool:
        return self._scriptlets.pop(name, None) is not None

    def apply_on_request(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_request(ctx)

    def apply_on_response(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_response(ctx)
