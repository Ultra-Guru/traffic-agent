"""Scriptlet engine: on_request / on_response hooks (Python layer)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..sandbox.executor import SandboxExecutor, SandboxResult


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass
class ScriptletContext:
    """Values handed to the user script; mutations are visible to the caller."""

    values: Dict[str, Any] = field(default_factory=dict)
mutants_xǁScriptletǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁScriptletǁon_request__mutmut: MutantDict = {}  # type: ignore
mutants_xǁScriptletǁon_response__mutmut: MutantDict = {}  # type: ignore


class Scriptlet:
    @_mutmut_mutated(mutants_xǁScriptletǁ__init____mutmut)
    def __init__(self, name: str, source: str, namespace: Dict[str, Any]):
        self.name = name
        self.source = source
        self._namespace = namespace
    def xǁScriptletǁ__init____mutmut_orig(self, name: str, source: str, namespace: Dict[str, Any]):
        self.name = name
        self.source = source
        self._namespace = namespace
    def xǁScriptletǁ__init____mutmut_1(self, name: str, source: str, namespace: Dict[str, Any]):
        self.name = None
        self.source = source
        self._namespace = namespace
    def xǁScriptletǁ__init____mutmut_2(self, name: str, source: str, namespace: Dict[str, Any]):
        self.name = name
        self.source = None
        self._namespace = namespace
    def xǁScriptletǁ__init____mutmut_3(self, name: str, source: str, namespace: Dict[str, Any]):
        self.name = name
        self.source = source
        self._namespace = None

    @property
    def has_on_request(self) -> bool:
        return callable(self._namespace.get("on_request"))

    @property
    def has_on_response(self) -> bool:
        return callable(self._namespace.get("on_response"))

    @_mutmut_mutated(mutants_xǁScriptletǁon_request__mutmut)
    def on_request(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_request")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_orig(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_request")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_1(self, ctx: ScriptletContext) -> Any:
        fn = None
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_2(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get(None)
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_3(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("XXon_requestXX")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_4(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("ON_REQUEST")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_5(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_request")
        if callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_6(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_request")
        if not callable(None):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_7(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_request")
        if not callable(fn):
            raise TypeError(None)
        return fn(ctx)

    def xǁScriptletǁon_request__mutmut_8(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_request")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_request hook")
        return fn(None)

    @_mutmut_mutated(mutants_xǁScriptletǁon_response__mutmut)
    def on_response(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_response")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_orig(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_response")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_1(self, ctx: ScriptletContext) -> Any:
        fn = None
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_2(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get(None)
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_3(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("XXon_responseXX")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_4(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("ON_RESPONSE")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_5(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_response")
        if callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_6(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_response")
        if not callable(None):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_7(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_response")
        if not callable(fn):
            raise TypeError(None)
        return fn(ctx)

    def xǁScriptletǁon_response__mutmut_8(self, ctx: ScriptletContext) -> Any:
        fn = self._namespace.get("on_response")
        if not callable(fn):
            raise TypeError(f"scriptlet {self.name} has no on_response hook")
        return fn(None)

mutants_xǁScriptletǁ__init____mutmut['_mutmut_orig'] = Scriptlet.xǁScriptletǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletǁ__init____mutmut['xǁScriptletǁ__init____mutmut_1'] = Scriptlet.xǁScriptletǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁScriptletǁ__init____mutmut['xǁScriptletǁ__init____mutmut_2'] = Scriptlet.xǁScriptletǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁScriptletǁ__init____mutmut['xǁScriptletǁ__init____mutmut_3'] = Scriptlet.xǁScriptletǁ__init____mutmut_3 # type: ignore # mutmut generated

mutants_xǁScriptletǁon_request__mutmut['_mutmut_orig'] = Scriptlet.xǁScriptletǁon_request__mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletǁon_request__mutmut['xǁScriptletǁon_request__mutmut_1'] = Scriptlet.xǁScriptletǁon_request__mutmut_1 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_request__mutmut['xǁScriptletǁon_request__mutmut_2'] = Scriptlet.xǁScriptletǁon_request__mutmut_2 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_request__mutmut['xǁScriptletǁon_request__mutmut_3'] = Scriptlet.xǁScriptletǁon_request__mutmut_3 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_request__mutmut['xǁScriptletǁon_request__mutmut_4'] = Scriptlet.xǁScriptletǁon_request__mutmut_4 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_request__mutmut['xǁScriptletǁon_request__mutmut_5'] = Scriptlet.xǁScriptletǁon_request__mutmut_5 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_request__mutmut['xǁScriptletǁon_request__mutmut_6'] = Scriptlet.xǁScriptletǁon_request__mutmut_6 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_request__mutmut['xǁScriptletǁon_request__mutmut_7'] = Scriptlet.xǁScriptletǁon_request__mutmut_7 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_request__mutmut['xǁScriptletǁon_request__mutmut_8'] = Scriptlet.xǁScriptletǁon_request__mutmut_8 # type: ignore # mutmut generated

mutants_xǁScriptletǁon_response__mutmut['_mutmut_orig'] = Scriptlet.xǁScriptletǁon_response__mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletǁon_response__mutmut['xǁScriptletǁon_response__mutmut_1'] = Scriptlet.xǁScriptletǁon_response__mutmut_1 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_response__mutmut['xǁScriptletǁon_response__mutmut_2'] = Scriptlet.xǁScriptletǁon_response__mutmut_2 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_response__mutmut['xǁScriptletǁon_response__mutmut_3'] = Scriptlet.xǁScriptletǁon_response__mutmut_3 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_response__mutmut['xǁScriptletǁon_response__mutmut_4'] = Scriptlet.xǁScriptletǁon_response__mutmut_4 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_response__mutmut['xǁScriptletǁon_response__mutmut_5'] = Scriptlet.xǁScriptletǁon_response__mutmut_5 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_response__mutmut['xǁScriptletǁon_response__mutmut_6'] = Scriptlet.xǁScriptletǁon_response__mutmut_6 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_response__mutmut['xǁScriptletǁon_response__mutmut_7'] = Scriptlet.xǁScriptletǁon_response__mutmut_7 # type: ignore # mutmut generated
mutants_xǁScriptletǁon_response__mutmut['xǁScriptletǁon_response__mutmut_8'] = Scriptlet.xǁScriptletǁon_response__mutmut_8 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁScriptletEngineǁload__mutmut: MutantDict = {}  # type: ignore
mutants_xǁScriptletEngineǁget__mutmut: MutantDict = {}  # type: ignore
mutants_xǁScriptletEngineǁnames__mutmut: MutantDict = {}  # type: ignore
mutants_xǁScriptletEngineǁunload__mutmut: MutantDict = {}  # type: ignore
mutants_xǁScriptletEngineǁapply_on_request__mutmut: MutantDict = {}  # type: ignore
mutants_xǁScriptletEngineǁapply_on_response__mutmut: MutantDict = {}  # type: ignore


class ScriptletEngine:
    """Loads, validates and runs scriptlets inside the sandbox executor."""

    @_mutmut_mutated(mutants_xǁScriptletEngineǁ__init____mutmut)
    def __init__(self, executor: Optional[SandboxExecutor] = None):
        self.executor = executor or SandboxExecutor()
        self._scriptlets: Dict[str, Scriptlet] = {}

    def xǁScriptletEngineǁ__init____mutmut_orig(self, executor: Optional[SandboxExecutor] = None):
        self.executor = executor or SandboxExecutor()
        self._scriptlets: Dict[str, Scriptlet] = {}

    def xǁScriptletEngineǁ__init____mutmut_1(self, executor: Optional[SandboxExecutor] = None):
        self.executor = None
        self._scriptlets: Dict[str, Scriptlet] = {}

    def xǁScriptletEngineǁ__init____mutmut_2(self, executor: Optional[SandboxExecutor] = None):
        self.executor = executor and SandboxExecutor()
        self._scriptlets: Dict[str, Scriptlet] = {}

    def xǁScriptletEngineǁ__init____mutmut_3(self, executor: Optional[SandboxExecutor] = None):
        self.executor = executor or SandboxExecutor()
        self._scriptlets: Dict[str, Scriptlet] = None

    @_mutmut_mutated(mutants_xǁScriptletEngineǁload__mutmut)
    def load(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_orig(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_1(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = None
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_2(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(None)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_3(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_4(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(None)
        scriptlet = Scriptlet(name, source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_5(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = None
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_6(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(None, source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_7(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, None, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_8(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, None)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_9(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(source, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_10(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, result.namespace)
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_11(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, )
        self._scriptlets[name] = scriptlet
        return scriptlet

    def xǁScriptletEngineǁload__mutmut_12(self, name: str, source: str) -> Scriptlet:
        result: SandboxResult = self.executor.run(source)
        if not result.ok:
            raise ValueError(f"scriptlet {name} failed to load: {result.error}")
        scriptlet = Scriptlet(name, source, result.namespace)
        self._scriptlets[name] = None
        return scriptlet

    @_mutmut_mutated(mutants_xǁScriptletEngineǁget__mutmut)
    def get(self, name: str) -> Optional[Scriptlet]:
        return self._scriptlets.get(name)

    def xǁScriptletEngineǁget__mutmut_orig(self, name: str) -> Optional[Scriptlet]:
        return self._scriptlets.get(name)

    def xǁScriptletEngineǁget__mutmut_1(self, name: str) -> Optional[Scriptlet]:
        return self._scriptlets.get(None)

    @_mutmut_mutated(mutants_xǁScriptletEngineǁnames__mutmut)
    def names(self) -> list:
        return sorted(self._scriptlets)

    def xǁScriptletEngineǁnames__mutmut_orig(self) -> list:
        return sorted(self._scriptlets)

    def xǁScriptletEngineǁnames__mutmut_1(self) -> list:
        return sorted(None)

    @_mutmut_mutated(mutants_xǁScriptletEngineǁunload__mutmut)
    def unload(self, name: str) -> bool:
        return self._scriptlets.pop(name, None) is not None

    def xǁScriptletEngineǁunload__mutmut_orig(self, name: str) -> bool:
        return self._scriptlets.pop(name, None) is not None

    def xǁScriptletEngineǁunload__mutmut_1(self, name: str) -> bool:
        return self._scriptlets.pop(None, None) is not None

    def xǁScriptletEngineǁunload__mutmut_2(self, name: str) -> bool:
        return self._scriptlets.pop(None) is not None

    def xǁScriptletEngineǁunload__mutmut_3(self, name: str) -> bool:
        return self._scriptlets.pop(name, ) is not None

    def xǁScriptletEngineǁunload__mutmut_4(self, name: str) -> bool:
        return self._scriptlets.pop(name, None) is None

    @_mutmut_mutated(mutants_xǁScriptletEngineǁapply_on_request__mutmut)
    def apply_on_request(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_request(ctx)

    def xǁScriptletEngineǁapply_on_request__mutmut_orig(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_request(ctx)

    def xǁScriptletEngineǁapply_on_request__mutmut_1(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = None
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_request(ctx)

    def xǁScriptletEngineǁapply_on_request__mutmut_2(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(None)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_request(ctx)

    def xǁScriptletEngineǁapply_on_request__mutmut_3(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is not None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_request(ctx)

    def xǁScriptletEngineǁapply_on_request__mutmut_4(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(None)
        return scriptlet.on_request(ctx)

    def xǁScriptletEngineǁapply_on_request__mutmut_5(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_request(None)

    @_mutmut_mutated(mutants_xǁScriptletEngineǁapply_on_response__mutmut)
    def apply_on_response(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_response(ctx)

    def xǁScriptletEngineǁapply_on_response__mutmut_orig(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_response(ctx)

    def xǁScriptletEngineǁapply_on_response__mutmut_1(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = None
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_response(ctx)

    def xǁScriptletEngineǁapply_on_response__mutmut_2(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(None)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_response(ctx)

    def xǁScriptletEngineǁapply_on_response__mutmut_3(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is not None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_response(ctx)

    def xǁScriptletEngineǁapply_on_response__mutmut_4(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(None)
        return scriptlet.on_response(ctx)

    def xǁScriptletEngineǁapply_on_response__mutmut_5(self, name: str, ctx: ScriptletContext) -> Any:
        scriptlet = self._scriptlets.get(name)
        if scriptlet is None:
            raise KeyError(f"unknown scriptlet: {name}")
        return scriptlet.on_response(None)

mutants_xǁScriptletEngineǁ__init____mutmut['_mutmut_orig'] = ScriptletEngine.xǁScriptletEngineǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁ__init____mutmut['xǁScriptletEngineǁ__init____mutmut_1'] = ScriptletEngine.xǁScriptletEngineǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁ__init____mutmut['xǁScriptletEngineǁ__init____mutmut_2'] = ScriptletEngine.xǁScriptletEngineǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁ__init____mutmut['xǁScriptletEngineǁ__init____mutmut_3'] = ScriptletEngine.xǁScriptletEngineǁ__init____mutmut_3 # type: ignore # mutmut generated

mutants_xǁScriptletEngineǁload__mutmut['_mutmut_orig'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_1'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_1 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_2'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_2 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_3'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_3 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_4'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_4 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_5'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_5 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_6'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_6 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_7'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_7 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_8'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_8 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_9'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_9 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_10'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_10 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_11'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_11 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁload__mutmut['xǁScriptletEngineǁload__mutmut_12'] = ScriptletEngine.xǁScriptletEngineǁload__mutmut_12 # type: ignore # mutmut generated

mutants_xǁScriptletEngineǁget__mutmut['_mutmut_orig'] = ScriptletEngine.xǁScriptletEngineǁget__mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁget__mutmut['xǁScriptletEngineǁget__mutmut_1'] = ScriptletEngine.xǁScriptletEngineǁget__mutmut_1 # type: ignore # mutmut generated

mutants_xǁScriptletEngineǁnames__mutmut['_mutmut_orig'] = ScriptletEngine.xǁScriptletEngineǁnames__mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁnames__mutmut['xǁScriptletEngineǁnames__mutmut_1'] = ScriptletEngine.xǁScriptletEngineǁnames__mutmut_1 # type: ignore # mutmut generated

mutants_xǁScriptletEngineǁunload__mutmut['_mutmut_orig'] = ScriptletEngine.xǁScriptletEngineǁunload__mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁunload__mutmut['xǁScriptletEngineǁunload__mutmut_1'] = ScriptletEngine.xǁScriptletEngineǁunload__mutmut_1 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁunload__mutmut['xǁScriptletEngineǁunload__mutmut_2'] = ScriptletEngine.xǁScriptletEngineǁunload__mutmut_2 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁunload__mutmut['xǁScriptletEngineǁunload__mutmut_3'] = ScriptletEngine.xǁScriptletEngineǁunload__mutmut_3 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁunload__mutmut['xǁScriptletEngineǁunload__mutmut_4'] = ScriptletEngine.xǁScriptletEngineǁunload__mutmut_4 # type: ignore # mutmut generated

mutants_xǁScriptletEngineǁapply_on_request__mutmut['_mutmut_orig'] = ScriptletEngine.xǁScriptletEngineǁapply_on_request__mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_request__mutmut['xǁScriptletEngineǁapply_on_request__mutmut_1'] = ScriptletEngine.xǁScriptletEngineǁapply_on_request__mutmut_1 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_request__mutmut['xǁScriptletEngineǁapply_on_request__mutmut_2'] = ScriptletEngine.xǁScriptletEngineǁapply_on_request__mutmut_2 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_request__mutmut['xǁScriptletEngineǁapply_on_request__mutmut_3'] = ScriptletEngine.xǁScriptletEngineǁapply_on_request__mutmut_3 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_request__mutmut['xǁScriptletEngineǁapply_on_request__mutmut_4'] = ScriptletEngine.xǁScriptletEngineǁapply_on_request__mutmut_4 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_request__mutmut['xǁScriptletEngineǁapply_on_request__mutmut_5'] = ScriptletEngine.xǁScriptletEngineǁapply_on_request__mutmut_5 # type: ignore # mutmut generated

mutants_xǁScriptletEngineǁapply_on_response__mutmut['_mutmut_orig'] = ScriptletEngine.xǁScriptletEngineǁapply_on_response__mutmut_orig # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_response__mutmut['xǁScriptletEngineǁapply_on_response__mutmut_1'] = ScriptletEngine.xǁScriptletEngineǁapply_on_response__mutmut_1 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_response__mutmut['xǁScriptletEngineǁapply_on_response__mutmut_2'] = ScriptletEngine.xǁScriptletEngineǁapply_on_response__mutmut_2 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_response__mutmut['xǁScriptletEngineǁapply_on_response__mutmut_3'] = ScriptletEngine.xǁScriptletEngineǁapply_on_response__mutmut_3 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_response__mutmut['xǁScriptletEngineǁapply_on_response__mutmut_4'] = ScriptletEngine.xǁScriptletEngineǁapply_on_response__mutmut_4 # type: ignore # mutmut generated
mutants_xǁScriptletEngineǁapply_on_response__mutmut['xǁScriptletEngineǁapply_on_response__mutmut_5'] = ScriptletEngine.xǁScriptletEngineǁapply_on_response__mutmut_5 # type: ignore # mutmut generated
