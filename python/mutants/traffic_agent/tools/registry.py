"""Agent tool registry with dispatch and error mapping."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁBridgeErrorǁ__init____mutmut: MutantDict = {}  # type: ignore


class BridgeError(Exception):
    @_mutmut_mutated(mutants_xǁBridgeErrorǁ__init____mutmut)
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message
    def xǁBridgeErrorǁ__init____mutmut_orig(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message
    def xǁBridgeErrorǁ__init____mutmut_1(self, code: str, message: str):
        super().__init__(None)
        self.code = code
        self.message = message
    def xǁBridgeErrorǁ__init____mutmut_2(self, code: str, message: str):
        super().__init__(message)
        self.code = None
        self.message = message
    def xǁBridgeErrorǁ__init____mutmut_3(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = None

mutants_xǁBridgeErrorǁ__init____mutmut['_mutmut_orig'] = BridgeError.xǁBridgeErrorǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁBridgeErrorǁ__init____mutmut['xǁBridgeErrorǁ__init____mutmut_1'] = BridgeError.xǁBridgeErrorǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁBridgeErrorǁ__init____mutmut['xǁBridgeErrorǁ__init____mutmut_2'] = BridgeError.xǁBridgeErrorǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁBridgeErrorǁ__init____mutmut['xǁBridgeErrorǁ__init____mutmut_3'] = BridgeError.xǁBridgeErrorǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁToolRegistryǁregister__mutmut: MutantDict = {}  # type: ignore
mutants_xǁToolRegistryǁunregister__mutmut: MutantDict = {}  # type: ignore
mutants_xǁToolRegistryǁnames__mutmut: MutantDict = {}  # type: ignore
mutants_xǁToolRegistryǁdoc__mutmut: MutantDict = {}  # type: ignore
mutants_xǁToolRegistryǁhas__mutmut: MutantDict = {}  # type: ignore
mutants_xǁToolRegistryǁdispatch__mutmut: MutantDict = {}  # type: ignore


class ToolRegistry:
    """Maps tool names to callables; tools receive keyword params only."""

    @_mutmut_mutated(mutants_xǁToolRegistryǁ__init____mutmut)
    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., object]] = {}
        self._docs: Dict[str, str] = {}

    def xǁToolRegistryǁ__init____mutmut_orig(self) -> None:
        self._tools: Dict[str, Callable[..., object]] = {}
        self._docs: Dict[str, str] = {}

    def xǁToolRegistryǁ__init____mutmut_1(self) -> None:
        self._tools: Dict[str, Callable[..., object]] = None
        self._docs: Dict[str, str] = {}

    def xǁToolRegistryǁ__init____mutmut_2(self) -> None:
        self._tools: Dict[str, Callable[..., object]] = {}
        self._docs: Dict[str, str] = None

    @_mutmut_mutated(mutants_xǁToolRegistryǁregister__mutmut)
    def register(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_orig(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_1(self, name: str, fn: Callable[..., object], doc: str = "XXXX") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_2(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_3(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError(None, "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_4(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", None)
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_5(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_6(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", )
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_7(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("XXinvalid_toolXX", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_8(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("INVALID_TOOL", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_9(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "XXtool name must not be emptyXX")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_10(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "TOOL NAME MUST NOT BE EMPTY")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_11(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name not in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_12(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError(None, f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_13(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", None)
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_14(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError(f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_15(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", )
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_16(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("XXduplicate_toolXX", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_17(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("DUPLICATE_TOOL", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_18(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = None
        self._docs[name] = doc

    def xǁToolRegistryǁregister__mutmut_19(self, name: str, fn: Callable[..., object], doc: str = "") -> None:
        if not name:
            raise BridgeError("invalid_tool", "tool name must not be empty")
        if name in self._tools:
            raise BridgeError("duplicate_tool", f"tool already registered: {name}")
        self._tools[name] = fn
        self._docs[name] = None

    @_mutmut_mutated(mutants_xǁToolRegistryǁunregister__mutmut)
    def unregister(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(name, None)
        self._docs.pop(name, None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_orig(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(name, None)
        self._docs.pop(name, None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_1(self, name: str) -> bool:
        existed = None
        self._tools.pop(name, None)
        self._docs.pop(name, None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_2(self, name: str) -> bool:
        existed = name not in self._tools
        self._tools.pop(name, None)
        self._docs.pop(name, None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_3(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(None, None)
        self._docs.pop(name, None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_4(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(None)
        self._docs.pop(name, None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_5(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(name, )
        self._docs.pop(name, None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_6(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(name, None)
        self._docs.pop(None, None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_7(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(name, None)
        self._docs.pop(None)
        return existed

    def xǁToolRegistryǁunregister__mutmut_8(self, name: str) -> bool:
        existed = name in self._tools
        self._tools.pop(name, None)
        self._docs.pop(name, )
        return existed

    @_mutmut_mutated(mutants_xǁToolRegistryǁnames__mutmut)
    def names(self) -> List[str]:
        return sorted(self._tools)

    def xǁToolRegistryǁnames__mutmut_orig(self) -> List[str]:
        return sorted(self._tools)

    def xǁToolRegistryǁnames__mutmut_1(self) -> List[str]:
        return sorted(None)

    @_mutmut_mutated(mutants_xǁToolRegistryǁdoc__mutmut)
    def doc(self, name: str) -> str:
        return self._docs.get(name, "")

    def xǁToolRegistryǁdoc__mutmut_orig(self, name: str) -> str:
        return self._docs.get(name, "")

    def xǁToolRegistryǁdoc__mutmut_1(self, name: str) -> str:
        return self._docs.get(None, "")

    def xǁToolRegistryǁdoc__mutmut_2(self, name: str) -> str:
        return self._docs.get(name, None)

    def xǁToolRegistryǁdoc__mutmut_3(self, name: str) -> str:
        return self._docs.get("")

    def xǁToolRegistryǁdoc__mutmut_4(self, name: str) -> str:
        return self._docs.get(name, )

    def xǁToolRegistryǁdoc__mutmut_5(self, name: str) -> str:
        return self._docs.get(name, "XXXX")

    @_mutmut_mutated(mutants_xǁToolRegistryǁhas__mutmut)
    def has(self, name: str) -> bool:
        return name in self._tools

    def xǁToolRegistryǁhas__mutmut_orig(self, name: str) -> bool:
        return name in self._tools

    def xǁToolRegistryǁhas__mutmut_1(self, name: str) -> bool:
        return name not in self._tools

    @_mutmut_mutated(mutants_xǁToolRegistryǁdispatch__mutmut)
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

    def xǁToolRegistryǁdispatch__mutmut_orig(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_1(self, tool: str, **params) -> object:
        fn = None
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_2(self, tool: str, **params) -> object:
        fn = self._tools.get(None)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_3(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is not None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_4(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError(None, f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_5(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", None)
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_6(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError(f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_7(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", )
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_8(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("XXunknown_toolXX", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_9(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("UNKNOWN_TOOL", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_10(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError(None, f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_11(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", None) from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_12(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError(f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_13(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", ) from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_14(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("XXbad_paramsXX", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_15(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("BAD_PARAMS", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_16(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError(None, f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_17(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", None) from exc

    def xǁToolRegistryǁdispatch__mutmut_18(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError(f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_19(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("bad_params", ) from exc

    def xǁToolRegistryǁdispatch__mutmut_20(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("XXbad_paramsXX", f"invalid parameter values for {tool}: {exc}") from exc

    def xǁToolRegistryǁdispatch__mutmut_21(self, tool: str, **params) -> object:
        fn = self._tools.get(tool)
        if fn is None:
            raise BridgeError("unknown_tool", f"no such tool: {tool}")
        try:
            return fn(**params)
        except TypeError as exc:
            raise BridgeError("bad_params", f"invalid parameters for {tool}: {exc}") from exc
        except ValueError as exc:
            raise BridgeError("BAD_PARAMS", f"invalid parameter values for {tool}: {exc}") from exc

mutants_xǁToolRegistryǁ__init____mutmut['_mutmut_orig'] = ToolRegistry.xǁToolRegistryǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁToolRegistryǁ__init____mutmut['xǁToolRegistryǁ__init____mutmut_1'] = ToolRegistry.xǁToolRegistryǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁ__init____mutmut['xǁToolRegistryǁ__init____mutmut_2'] = ToolRegistry.xǁToolRegistryǁ__init____mutmut_2 # type: ignore # mutmut generated

mutants_xǁToolRegistryǁregister__mutmut['_mutmut_orig'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_orig # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_1'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_1 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_2'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_2 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_3'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_3 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_4'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_4 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_5'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_5 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_6'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_6 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_7'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_7 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_8'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_8 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_9'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_9 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_10'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_10 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_11'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_11 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_12'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_12 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_13'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_13 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_14'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_14 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_15'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_15 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_16'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_16 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_17'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_17 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_18'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_18 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁregister__mutmut['xǁToolRegistryǁregister__mutmut_19'] = ToolRegistry.xǁToolRegistryǁregister__mutmut_19 # type: ignore # mutmut generated

mutants_xǁToolRegistryǁunregister__mutmut['_mutmut_orig'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_orig # type: ignore # mutmut generated
mutants_xǁToolRegistryǁunregister__mutmut['xǁToolRegistryǁunregister__mutmut_1'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_1 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁunregister__mutmut['xǁToolRegistryǁunregister__mutmut_2'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_2 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁunregister__mutmut['xǁToolRegistryǁunregister__mutmut_3'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_3 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁunregister__mutmut['xǁToolRegistryǁunregister__mutmut_4'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_4 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁunregister__mutmut['xǁToolRegistryǁunregister__mutmut_5'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_5 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁunregister__mutmut['xǁToolRegistryǁunregister__mutmut_6'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_6 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁunregister__mutmut['xǁToolRegistryǁunregister__mutmut_7'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_7 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁunregister__mutmut['xǁToolRegistryǁunregister__mutmut_8'] = ToolRegistry.xǁToolRegistryǁunregister__mutmut_8 # type: ignore # mutmut generated

mutants_xǁToolRegistryǁnames__mutmut['_mutmut_orig'] = ToolRegistry.xǁToolRegistryǁnames__mutmut_orig # type: ignore # mutmut generated
mutants_xǁToolRegistryǁnames__mutmut['xǁToolRegistryǁnames__mutmut_1'] = ToolRegistry.xǁToolRegistryǁnames__mutmut_1 # type: ignore # mutmut generated

mutants_xǁToolRegistryǁdoc__mutmut['_mutmut_orig'] = ToolRegistry.xǁToolRegistryǁdoc__mutmut_orig # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdoc__mutmut['xǁToolRegistryǁdoc__mutmut_1'] = ToolRegistry.xǁToolRegistryǁdoc__mutmut_1 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdoc__mutmut['xǁToolRegistryǁdoc__mutmut_2'] = ToolRegistry.xǁToolRegistryǁdoc__mutmut_2 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdoc__mutmut['xǁToolRegistryǁdoc__mutmut_3'] = ToolRegistry.xǁToolRegistryǁdoc__mutmut_3 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdoc__mutmut['xǁToolRegistryǁdoc__mutmut_4'] = ToolRegistry.xǁToolRegistryǁdoc__mutmut_4 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdoc__mutmut['xǁToolRegistryǁdoc__mutmut_5'] = ToolRegistry.xǁToolRegistryǁdoc__mutmut_5 # type: ignore # mutmut generated

mutants_xǁToolRegistryǁhas__mutmut['_mutmut_orig'] = ToolRegistry.xǁToolRegistryǁhas__mutmut_orig # type: ignore # mutmut generated
mutants_xǁToolRegistryǁhas__mutmut['xǁToolRegistryǁhas__mutmut_1'] = ToolRegistry.xǁToolRegistryǁhas__mutmut_1 # type: ignore # mutmut generated

mutants_xǁToolRegistryǁdispatch__mutmut['_mutmut_orig'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_orig # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_1'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_1 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_2'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_2 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_3'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_3 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_4'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_4 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_5'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_5 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_6'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_6 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_7'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_7 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_8'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_8 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_9'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_9 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_10'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_10 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_11'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_11 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_12'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_12 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_13'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_13 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_14'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_14 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_15'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_15 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_16'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_16 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_17'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_17 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_18'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_18 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_19'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_19 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_20'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_20 # type: ignore # mutmut generated
mutants_xǁToolRegistryǁdispatch__mutmut['xǁToolRegistryǁdispatch__mutmut_21'] = ToolRegistry.xǁToolRegistryǁdispatch__mutmut_21 # type: ignore # mutmut generated
