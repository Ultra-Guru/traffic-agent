"""Agent tool registry with dispatch and error mapping."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional


class BridgeError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class ToolRegistry:
    """Maps tool names to callables; tools receive keyword params only."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., object]] = {}
        self._docs: Dict[str, str] = {}

    def register(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def unregister(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(name, None)
        self._docs.pop(name, None)
        return existed

    def names(self) -> List[str]:
        return sorted(self._tools)

    def doc(self, name: str) -> str:
        return self._docs.get(name, "")

    def has(self, name: str) -> bool:
        return name in self._tools

    def dispatch(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc
