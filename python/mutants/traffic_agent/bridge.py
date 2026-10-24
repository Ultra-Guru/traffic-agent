"""Line bridge between the Kotlin app and the Python agent layer.

Protocol (newline-delimited, query-string encoded, one command per line):
    request : method=list_requests&limit=10
    response: ok=1&count=2...
              ok=0&error_code=unknown_tool&error=no+such+tool%3A+X
Values are URL-encoded; the response is a flat key/value pair set plus the
JSON payload under the `payload` key when a tool returns structured data.
"""

from __future__ import annotations

import json
import sys
from typing import Optional, TextIO
from urllib.parse import quote, parse_qsl

from .risk.audit import AuditLog
from .risk.gate import RiskGate
from .store import CaptureStore
from .tools.capture_tools import register_capture_tools
from .tools.registry import BridgeError, ToolRegistry
from .tools.transform_tools import register_transform_tools


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁBridgeǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁBridgeǁencode__mutmut: MutantDict = {}  # type: ignore
mutants_xǁBridgeǁdecode__mutmut: MutantDict = {}  # type: ignore
mutants_xǁBridgeǁhandle_line__mutmut: MutantDict = {}  # type: ignore
mutants_xǁBridgeǁcall__mutmut: MutantDict = {}  # type: ignore
mutants_xǁBridgeǁserve__mutmut: MutantDict = {}  # type: ignore


class Bridge:
    """Wires registry + gate + audit together and answers single lines."""

    @_mutmut_mutated(mutants_xǁBridgeǁ__init____mutmut)
    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_orig(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_1(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = None
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_2(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store and CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_3(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = None
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_4(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry and ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_5(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = None
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_6(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate and RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_7(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = None
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_8(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit and AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_9(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(None, self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_10(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, None)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_11(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.store)
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_12(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, )
        register_transform_tools(self.registry, self.store)

    def xǁBridgeǁ__init____mutmut_13(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(None, self.store)

    def xǁBridgeǁ__init____mutmut_14(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, None)

    def xǁBridgeǁ__init____mutmut_15(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.store)

    def xǁBridgeǁ__init____mutmut_16(
        self,
        registry: Optional[ToolRegistry] = None,
        gate: Optional[RiskGate] = None,
        audit: Optional[AuditLog] = None,
        store: Optional[CaptureStore] = None,
    ):
        self.store = store or CaptureStore()
        self.registry = registry or ToolRegistry()
        self.gate = gate or RiskGate()
        self.audit = audit or AuditLog()
        register_capture_tools(self.registry, self.store)
        register_transform_tools(self.registry, )

    # ---------- line codec ----------

    @staticmethod
    @_mutmut_mutated(mutants_xǁBridgeǁencode__mutmut)
    def encode(pairs: dict) -> str:
        return "&".join(f"{k}={quote(str(v), safe='')}" for k, v in pairs.items())

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_orig(pairs: dict) -> str:
        return "&".join(f"{k}={quote(str(v), safe='')}" for k, v in pairs.items())

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_1(pairs: dict) -> str:
        return "&".join(None)

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_2(pairs: dict) -> str:
        return "XX&XX".join(f"{k}={quote(str(v), safe='')}" for k, v in pairs.items())

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_3(pairs: dict) -> str:
        return "&".join(f"{k}={quote(None, safe='')}" for k, v in pairs.items())

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_4(pairs: dict) -> str:
        return "&".join(f"{k}={quote(str(v), safe=None)}" for k, v in pairs.items())

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_5(pairs: dict) -> str:
        return "&".join(f"{k}={quote(safe='')}" for k, v in pairs.items())

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_6(pairs: dict) -> str:
        return "&".join(f"{k}={quote(str(v), )}" for k, v in pairs.items())

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_7(pairs: dict) -> str:
        return "&".join(f"{k}={quote(str(None), safe='')}" for k, v in pairs.items())

    # ---------- line codec ----------

    @staticmethod
    def xǁBridgeǁencode__mutmut_8(pairs: dict) -> str:
        return "&".join(f"{k}={quote(str(v), safe='XXXX')}" for k, v in pairs.items())

    @staticmethod
    @_mutmut_mutated(mutants_xǁBridgeǁdecode__mutmut)
    def decode(line: str) -> dict:
        return {k: v for k, v in parse_qsl(line, keep_blank_values=True)}

    @staticmethod
    def xǁBridgeǁdecode__mutmut_orig(line: str) -> dict:
        return {k: v for k, v in parse_qsl(line, keep_blank_values=True)}

    @staticmethod
    def xǁBridgeǁdecode__mutmut_1(line: str) -> dict:
        return {k: v for k, v in parse_qsl(None, keep_blank_values=True)}

    @staticmethod
    def xǁBridgeǁdecode__mutmut_2(line: str) -> dict:
        return {k: v for k, v in parse_qsl(line, keep_blank_values=None)}

    @staticmethod
    def xǁBridgeǁdecode__mutmut_3(line: str) -> dict:
        return {k: v for k, v in parse_qsl(keep_blank_values=True)}

    @staticmethod
    def xǁBridgeǁdecode__mutmut_4(line: str) -> dict:
        return {k: v for k, v in parse_qsl(line, )}

    @staticmethod
    def xǁBridgeǁdecode__mutmut_5(line: str) -> dict:
        return {k: v for k, v in parse_qsl(line, keep_blank_values=False)}

    # ---------- dispatch ----------

    @_mutmut_mutated(mutants_xǁBridgeǁhandle_line__mutmut)
    def handle_line(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_orig(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_1(self, line: str) -> str:
        line = None
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_2(self, line: str) -> str:
        line = line.strip()
        if line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_3(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode(None)
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_4(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"XXokXX": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_5(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"OK": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_6(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "XX0XX", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_7(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "XXerror_codeXX": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_8(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "ERROR_CODE": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_9(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "XXempty_lineXX", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_10(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "EMPTY_LINE", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_11(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "XXerrorXX": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_12(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "ERROR": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_13(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "XXempty commandXX"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_14(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "EMPTY COMMAND"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_15(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = None
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_16(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(None)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_17(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = None
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_18(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop(None, "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_19(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", None) in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_20(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_21(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", ) in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_22(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("XX__approveXX", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_23(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__APPROVE", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_24(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "XX0XX") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_25(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") not in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_26(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("XX1XX", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_27(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "XXtrueXX", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_28(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "TRUE", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_29(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "XXyesXX")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_30(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "YES")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_31(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = None
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_32(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop(None, None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_33(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop(None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_34(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", )
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_35(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("XXmethodXX", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_36(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("METHOD", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_37(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is not None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_38(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode(None)
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_39(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"XXokXX": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_40(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"OK": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_41(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "XX0XX", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_42(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "XXerror_codeXX": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_43(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "ERROR_CODE": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_44(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "XXmissing_methodXX", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_45(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "MISSING_METHOD", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_46(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "XXerrorXX": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_47(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "ERROR": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_48(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "XXno method givenXX"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_49(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "NO METHOD GIVEN"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_50(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(None, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_51(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, None, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_52(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=None)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_53(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_54(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_55(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, )
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_56(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode(None)

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_57(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"XXokXX": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_58(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"OK": "0", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_59(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "XX0XX", "error_code": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_60(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "XXerror_codeXX": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_61(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "ERROR_CODE": exc.code, "error": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_62(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "XXerrorXX": exc.message})

    # ---------- dispatch ----------

    def xǁBridgeǁhandle_line__mutmut_63(self, line: str) -> str:
        line = line.strip()
        if not line:
            return self.encode({"ok": "0", "error_code": "empty_line", "error": "empty command"})
        params = self.decode(line)
        # keys with a __ prefix are bridge controls (e.g. __approve)
        approved = params.pop("__approve", "0") in ("1", "true", "yes")
        method = params.pop("method", None)
        if method is None:
            return self.encode({"ok": "0", "error_code": "missing_method", "error": "no method given"})
        try:
            return self.call(method, params, approved=approved)
        except BridgeError as exc:
            return self.encode({"ok": "0", "error_code": exc.code, "ERROR": exc.message})

    @_mutmut_mutated(mutants_xǁBridgeǁcall__mutmut)
    def call(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_orig(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_1(self, method: str, params: dict, approved: bool = True) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_2(self, method: str, params: dict, approved: bool = False) -> str:
        decision = None
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_3(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(None, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_4(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=None)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_5(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_6(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, )
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_7(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_8(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(None, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_9(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, None, params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_10(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", None, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_11(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, None)
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_12(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append("denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_13(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_14(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_15(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, )
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_16(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "XXdeniedXX", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_17(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "DENIED", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_18(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason and "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_19(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "XXXX")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_20(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is not None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_21(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode(None)
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_22(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"XXokXX": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_23(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"OK": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_24(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "XX0XX", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_25(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "XXerror_codeXX": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_26(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "ERROR_CODE": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_27(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "XXunknown_toolXX", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_28(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "UNKNOWN_TOOL", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_29(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "XXerrorXX": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_30(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "ERROR": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_31(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason and "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_32(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "XXunknown toolXX"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_33(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "UNKNOWN TOOL"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_34(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = None
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_35(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "XXokXX": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_36(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "OK": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_37(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "XX0XX",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_38(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "XXerror_codeXX": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_39(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "ERROR_CODE": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_40(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if (not decision.requires_approval) and False else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_41(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if (not decision.requires_approval) or True else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_42(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "XXgate_deniedXX" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_43(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "GATE_DENIED" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_44(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_45(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "XXapproval_requiredXX",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_46(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "APPROVAL_REQUIRED",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_47(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "XXerrorXX": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_48(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "ERROR": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_49(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason and "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_50(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "XXdeniedXX",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_51(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "DENIED",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_52(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = None
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_53(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["XXriskXX"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_54(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["RISK"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_55(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.upper()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_56(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(None)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_57(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = None
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_58(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(None, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_59(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(**params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_60(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, )
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_61(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(None, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_62(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, None, params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_63(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", None)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_64(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append("allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_65(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_66(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", )
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_67(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "XXallowedXX", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_68(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "ALLOWED", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_69(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = None
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_70(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(None)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_71(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode(None)
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_72(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"XXokXX": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_73(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"OK": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_74(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "XX1XX", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_75(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "XXpayloadXX": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_76(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "PAYLOAD": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_77(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode(None)

    def xǁBridgeǁcall__mutmut_78(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"XXokXX": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_79(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"OK": "1", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_80(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "XX1XX", "result": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_81(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "XXresultXX": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_82(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "RESULT": "" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_83(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if (result is None) and False else str(result)})

    def xǁBridgeǁcall__mutmut_84(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if (result is None) or True else str(result)})

    def xǁBridgeǁcall__mutmut_85(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "XXXX" if result is None else str(result)})

    def xǁBridgeǁcall__mutmut_86(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is not None else str(result)})

    def xǁBridgeǁcall__mutmut_87(self, method: str, params: dict, approved: bool = False) -> str:
        decision = self.gate.evaluate(method, approved=approved)
        if not decision.allowed:
            self.audit.append(method, "denied", params, decision.reason or "")
            if decision.risk is None:
                return self.encode({"ok": "0", "error_code": "unknown_tool", "error": decision.reason or "unknown tool"})
            pairs = {
                "ok": "0",
                "error_code": "gate_denied" if not decision.requires_approval else "approval_required",
                "error": decision.reason or "denied",
            }
            pairs["risk"] = decision.risk.name.lower()
            return self.encode(pairs)

        result = self.registry.dispatch(method, **params)
        self.audit.append(method, "allowed", params)
        if isinstance(result, (dict, list)):
            payload = json.dumps(result)
            return self.encode({"ok": "1", "payload": payload})
        return self.encode({"ok": "1", "result": "" if result is None else str(None)})

    # ---------- stdio loop ----------

    @_mutmut_mutated(mutants_xǁBridgeǁserve__mutmut)
    def serve(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_orig(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_1(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = None
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_2(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin and sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_3(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = None
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_4(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout and sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_5(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = None
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_6(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 1
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_7(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_8(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                break
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_9(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = None
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_10(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(None)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_11(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(None)
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_12(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response - "\n")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_13(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "XX\nXX")
            stdout.flush()
            handled += 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_14(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled = 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_15(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled -= 1
        return handled

    # ---------- stdio loop ----------

    def xǁBridgeǁserve__mutmut_16(self, stdin: TextIO = None, stdout: TextIO = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        handled = 0
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle_line(line)
            stdout.write(response + "\n")
            stdout.flush()
            handled += 2
        return handled

mutants_xǁBridgeǁ__init____mutmut['_mutmut_orig'] = Bridge.xǁBridgeǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_1'] = Bridge.xǁBridgeǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_2'] = Bridge.xǁBridgeǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_3'] = Bridge.xǁBridgeǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_4'] = Bridge.xǁBridgeǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_5'] = Bridge.xǁBridgeǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_6'] = Bridge.xǁBridgeǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_7'] = Bridge.xǁBridgeǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_8'] = Bridge.xǁBridgeǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_9'] = Bridge.xǁBridgeǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_10'] = Bridge.xǁBridgeǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_11'] = Bridge.xǁBridgeǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_12'] = Bridge.xǁBridgeǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_13'] = Bridge.xǁBridgeǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_14'] = Bridge.xǁBridgeǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_15'] = Bridge.xǁBridgeǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁBridgeǁ__init____mutmut['xǁBridgeǁ__init____mutmut_16'] = Bridge.xǁBridgeǁ__init____mutmut_16 # type: ignore # mutmut generated

mutants_xǁBridgeǁencode__mutmut['_mutmut_orig'] = Bridge.xǁBridgeǁencode__mutmut_orig # type: ignore # mutmut generated
mutants_xǁBridgeǁencode__mutmut['xǁBridgeǁencode__mutmut_1'] = Bridge.xǁBridgeǁencode__mutmut_1 # type: ignore # mutmut generated
mutants_xǁBridgeǁencode__mutmut['xǁBridgeǁencode__mutmut_2'] = Bridge.xǁBridgeǁencode__mutmut_2 # type: ignore # mutmut generated
mutants_xǁBridgeǁencode__mutmut['xǁBridgeǁencode__mutmut_3'] = Bridge.xǁBridgeǁencode__mutmut_3 # type: ignore # mutmut generated
mutants_xǁBridgeǁencode__mutmut['xǁBridgeǁencode__mutmut_4'] = Bridge.xǁBridgeǁencode__mutmut_4 # type: ignore # mutmut generated
mutants_xǁBridgeǁencode__mutmut['xǁBridgeǁencode__mutmut_5'] = Bridge.xǁBridgeǁencode__mutmut_5 # type: ignore # mutmut generated
mutants_xǁBridgeǁencode__mutmut['xǁBridgeǁencode__mutmut_6'] = Bridge.xǁBridgeǁencode__mutmut_6 # type: ignore # mutmut generated
mutants_xǁBridgeǁencode__mutmut['xǁBridgeǁencode__mutmut_7'] = Bridge.xǁBridgeǁencode__mutmut_7 # type: ignore # mutmut generated
mutants_xǁBridgeǁencode__mutmut['xǁBridgeǁencode__mutmut_8'] = Bridge.xǁBridgeǁencode__mutmut_8 # type: ignore # mutmut generated

mutants_xǁBridgeǁdecode__mutmut['_mutmut_orig'] = Bridge.xǁBridgeǁdecode__mutmut_orig # type: ignore # mutmut generated
mutants_xǁBridgeǁdecode__mutmut['xǁBridgeǁdecode__mutmut_1'] = Bridge.xǁBridgeǁdecode__mutmut_1 # type: ignore # mutmut generated
mutants_xǁBridgeǁdecode__mutmut['xǁBridgeǁdecode__mutmut_2'] = Bridge.xǁBridgeǁdecode__mutmut_2 # type: ignore # mutmut generated
mutants_xǁBridgeǁdecode__mutmut['xǁBridgeǁdecode__mutmut_3'] = Bridge.xǁBridgeǁdecode__mutmut_3 # type: ignore # mutmut generated
mutants_xǁBridgeǁdecode__mutmut['xǁBridgeǁdecode__mutmut_4'] = Bridge.xǁBridgeǁdecode__mutmut_4 # type: ignore # mutmut generated
mutants_xǁBridgeǁdecode__mutmut['xǁBridgeǁdecode__mutmut_5'] = Bridge.xǁBridgeǁdecode__mutmut_5 # type: ignore # mutmut generated

mutants_xǁBridgeǁhandle_line__mutmut['_mutmut_orig'] = Bridge.xǁBridgeǁhandle_line__mutmut_orig # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_1'] = Bridge.xǁBridgeǁhandle_line__mutmut_1 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_2'] = Bridge.xǁBridgeǁhandle_line__mutmut_2 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_3'] = Bridge.xǁBridgeǁhandle_line__mutmut_3 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_4'] = Bridge.xǁBridgeǁhandle_line__mutmut_4 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_5'] = Bridge.xǁBridgeǁhandle_line__mutmut_5 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_6'] = Bridge.xǁBridgeǁhandle_line__mutmut_6 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_7'] = Bridge.xǁBridgeǁhandle_line__mutmut_7 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_8'] = Bridge.xǁBridgeǁhandle_line__mutmut_8 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_9'] = Bridge.xǁBridgeǁhandle_line__mutmut_9 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_10'] = Bridge.xǁBridgeǁhandle_line__mutmut_10 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_11'] = Bridge.xǁBridgeǁhandle_line__mutmut_11 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_12'] = Bridge.xǁBridgeǁhandle_line__mutmut_12 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_13'] = Bridge.xǁBridgeǁhandle_line__mutmut_13 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_14'] = Bridge.xǁBridgeǁhandle_line__mutmut_14 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_15'] = Bridge.xǁBridgeǁhandle_line__mutmut_15 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_16'] = Bridge.xǁBridgeǁhandle_line__mutmut_16 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_17'] = Bridge.xǁBridgeǁhandle_line__mutmut_17 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_18'] = Bridge.xǁBridgeǁhandle_line__mutmut_18 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_19'] = Bridge.xǁBridgeǁhandle_line__mutmut_19 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_20'] = Bridge.xǁBridgeǁhandle_line__mutmut_20 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_21'] = Bridge.xǁBridgeǁhandle_line__mutmut_21 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_22'] = Bridge.xǁBridgeǁhandle_line__mutmut_22 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_23'] = Bridge.xǁBridgeǁhandle_line__mutmut_23 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_24'] = Bridge.xǁBridgeǁhandle_line__mutmut_24 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_25'] = Bridge.xǁBridgeǁhandle_line__mutmut_25 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_26'] = Bridge.xǁBridgeǁhandle_line__mutmut_26 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_27'] = Bridge.xǁBridgeǁhandle_line__mutmut_27 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_28'] = Bridge.xǁBridgeǁhandle_line__mutmut_28 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_29'] = Bridge.xǁBridgeǁhandle_line__mutmut_29 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_30'] = Bridge.xǁBridgeǁhandle_line__mutmut_30 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_31'] = Bridge.xǁBridgeǁhandle_line__mutmut_31 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_32'] = Bridge.xǁBridgeǁhandle_line__mutmut_32 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_33'] = Bridge.xǁBridgeǁhandle_line__mutmut_33 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_34'] = Bridge.xǁBridgeǁhandle_line__mutmut_34 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_35'] = Bridge.xǁBridgeǁhandle_line__mutmut_35 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_36'] = Bridge.xǁBridgeǁhandle_line__mutmut_36 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_37'] = Bridge.xǁBridgeǁhandle_line__mutmut_37 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_38'] = Bridge.xǁBridgeǁhandle_line__mutmut_38 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_39'] = Bridge.xǁBridgeǁhandle_line__mutmut_39 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_40'] = Bridge.xǁBridgeǁhandle_line__mutmut_40 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_41'] = Bridge.xǁBridgeǁhandle_line__mutmut_41 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_42'] = Bridge.xǁBridgeǁhandle_line__mutmut_42 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_43'] = Bridge.xǁBridgeǁhandle_line__mutmut_43 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_44'] = Bridge.xǁBridgeǁhandle_line__mutmut_44 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_45'] = Bridge.xǁBridgeǁhandle_line__mutmut_45 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_46'] = Bridge.xǁBridgeǁhandle_line__mutmut_46 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_47'] = Bridge.xǁBridgeǁhandle_line__mutmut_47 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_48'] = Bridge.xǁBridgeǁhandle_line__mutmut_48 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_49'] = Bridge.xǁBridgeǁhandle_line__mutmut_49 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_50'] = Bridge.xǁBridgeǁhandle_line__mutmut_50 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_51'] = Bridge.xǁBridgeǁhandle_line__mutmut_51 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_52'] = Bridge.xǁBridgeǁhandle_line__mutmut_52 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_53'] = Bridge.xǁBridgeǁhandle_line__mutmut_53 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_54'] = Bridge.xǁBridgeǁhandle_line__mutmut_54 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_55'] = Bridge.xǁBridgeǁhandle_line__mutmut_55 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_56'] = Bridge.xǁBridgeǁhandle_line__mutmut_56 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_57'] = Bridge.xǁBridgeǁhandle_line__mutmut_57 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_58'] = Bridge.xǁBridgeǁhandle_line__mutmut_58 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_59'] = Bridge.xǁBridgeǁhandle_line__mutmut_59 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_60'] = Bridge.xǁBridgeǁhandle_line__mutmut_60 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_61'] = Bridge.xǁBridgeǁhandle_line__mutmut_61 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_62'] = Bridge.xǁBridgeǁhandle_line__mutmut_62 # type: ignore # mutmut generated
mutants_xǁBridgeǁhandle_line__mutmut['xǁBridgeǁhandle_line__mutmut_63'] = Bridge.xǁBridgeǁhandle_line__mutmut_63 # type: ignore # mutmut generated

mutants_xǁBridgeǁcall__mutmut['_mutmut_orig'] = Bridge.xǁBridgeǁcall__mutmut_orig # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_1'] = Bridge.xǁBridgeǁcall__mutmut_1 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_2'] = Bridge.xǁBridgeǁcall__mutmut_2 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_3'] = Bridge.xǁBridgeǁcall__mutmut_3 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_4'] = Bridge.xǁBridgeǁcall__mutmut_4 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_5'] = Bridge.xǁBridgeǁcall__mutmut_5 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_6'] = Bridge.xǁBridgeǁcall__mutmut_6 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_7'] = Bridge.xǁBridgeǁcall__mutmut_7 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_8'] = Bridge.xǁBridgeǁcall__mutmut_8 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_9'] = Bridge.xǁBridgeǁcall__mutmut_9 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_10'] = Bridge.xǁBridgeǁcall__mutmut_10 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_11'] = Bridge.xǁBridgeǁcall__mutmut_11 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_12'] = Bridge.xǁBridgeǁcall__mutmut_12 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_13'] = Bridge.xǁBridgeǁcall__mutmut_13 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_14'] = Bridge.xǁBridgeǁcall__mutmut_14 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_15'] = Bridge.xǁBridgeǁcall__mutmut_15 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_16'] = Bridge.xǁBridgeǁcall__mutmut_16 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_17'] = Bridge.xǁBridgeǁcall__mutmut_17 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_18'] = Bridge.xǁBridgeǁcall__mutmut_18 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_19'] = Bridge.xǁBridgeǁcall__mutmut_19 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_20'] = Bridge.xǁBridgeǁcall__mutmut_20 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_21'] = Bridge.xǁBridgeǁcall__mutmut_21 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_22'] = Bridge.xǁBridgeǁcall__mutmut_22 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_23'] = Bridge.xǁBridgeǁcall__mutmut_23 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_24'] = Bridge.xǁBridgeǁcall__mutmut_24 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_25'] = Bridge.xǁBridgeǁcall__mutmut_25 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_26'] = Bridge.xǁBridgeǁcall__mutmut_26 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_27'] = Bridge.xǁBridgeǁcall__mutmut_27 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_28'] = Bridge.xǁBridgeǁcall__mutmut_28 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_29'] = Bridge.xǁBridgeǁcall__mutmut_29 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_30'] = Bridge.xǁBridgeǁcall__mutmut_30 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_31'] = Bridge.xǁBridgeǁcall__mutmut_31 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_32'] = Bridge.xǁBridgeǁcall__mutmut_32 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_33'] = Bridge.xǁBridgeǁcall__mutmut_33 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_34'] = Bridge.xǁBridgeǁcall__mutmut_34 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_35'] = Bridge.xǁBridgeǁcall__mutmut_35 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_36'] = Bridge.xǁBridgeǁcall__mutmut_36 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_37'] = Bridge.xǁBridgeǁcall__mutmut_37 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_38'] = Bridge.xǁBridgeǁcall__mutmut_38 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_39'] = Bridge.xǁBridgeǁcall__mutmut_39 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_40'] = Bridge.xǁBridgeǁcall__mutmut_40 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_41'] = Bridge.xǁBridgeǁcall__mutmut_41 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_42'] = Bridge.xǁBridgeǁcall__mutmut_42 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_43'] = Bridge.xǁBridgeǁcall__mutmut_43 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_44'] = Bridge.xǁBridgeǁcall__mutmut_44 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_45'] = Bridge.xǁBridgeǁcall__mutmut_45 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_46'] = Bridge.xǁBridgeǁcall__mutmut_46 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_47'] = Bridge.xǁBridgeǁcall__mutmut_47 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_48'] = Bridge.xǁBridgeǁcall__mutmut_48 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_49'] = Bridge.xǁBridgeǁcall__mutmut_49 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_50'] = Bridge.xǁBridgeǁcall__mutmut_50 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_51'] = Bridge.xǁBridgeǁcall__mutmut_51 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_52'] = Bridge.xǁBridgeǁcall__mutmut_52 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_53'] = Bridge.xǁBridgeǁcall__mutmut_53 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_54'] = Bridge.xǁBridgeǁcall__mutmut_54 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_55'] = Bridge.xǁBridgeǁcall__mutmut_55 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_56'] = Bridge.xǁBridgeǁcall__mutmut_56 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_57'] = Bridge.xǁBridgeǁcall__mutmut_57 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_58'] = Bridge.xǁBridgeǁcall__mutmut_58 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_59'] = Bridge.xǁBridgeǁcall__mutmut_59 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_60'] = Bridge.xǁBridgeǁcall__mutmut_60 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_61'] = Bridge.xǁBridgeǁcall__mutmut_61 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_62'] = Bridge.xǁBridgeǁcall__mutmut_62 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_63'] = Bridge.xǁBridgeǁcall__mutmut_63 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_64'] = Bridge.xǁBridgeǁcall__mutmut_64 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_65'] = Bridge.xǁBridgeǁcall__mutmut_65 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_66'] = Bridge.xǁBridgeǁcall__mutmut_66 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_67'] = Bridge.xǁBridgeǁcall__mutmut_67 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_68'] = Bridge.xǁBridgeǁcall__mutmut_68 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_69'] = Bridge.xǁBridgeǁcall__mutmut_69 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_70'] = Bridge.xǁBridgeǁcall__mutmut_70 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_71'] = Bridge.xǁBridgeǁcall__mutmut_71 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_72'] = Bridge.xǁBridgeǁcall__mutmut_72 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_73'] = Bridge.xǁBridgeǁcall__mutmut_73 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_74'] = Bridge.xǁBridgeǁcall__mutmut_74 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_75'] = Bridge.xǁBridgeǁcall__mutmut_75 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_76'] = Bridge.xǁBridgeǁcall__mutmut_76 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_77'] = Bridge.xǁBridgeǁcall__mutmut_77 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_78'] = Bridge.xǁBridgeǁcall__mutmut_78 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_79'] = Bridge.xǁBridgeǁcall__mutmut_79 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_80'] = Bridge.xǁBridgeǁcall__mutmut_80 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_81'] = Bridge.xǁBridgeǁcall__mutmut_81 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_82'] = Bridge.xǁBridgeǁcall__mutmut_82 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_83'] = Bridge.xǁBridgeǁcall__mutmut_83 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_84'] = Bridge.xǁBridgeǁcall__mutmut_84 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_85'] = Bridge.xǁBridgeǁcall__mutmut_85 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_86'] = Bridge.xǁBridgeǁcall__mutmut_86 # type: ignore # mutmut generated
mutants_xǁBridgeǁcall__mutmut['xǁBridgeǁcall__mutmut_87'] = Bridge.xǁBridgeǁcall__mutmut_87 # type: ignore # mutmut generated

mutants_xǁBridgeǁserve__mutmut['_mutmut_orig'] = Bridge.xǁBridgeǁserve__mutmut_orig # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_1'] = Bridge.xǁBridgeǁserve__mutmut_1 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_2'] = Bridge.xǁBridgeǁserve__mutmut_2 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_3'] = Bridge.xǁBridgeǁserve__mutmut_3 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_4'] = Bridge.xǁBridgeǁserve__mutmut_4 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_5'] = Bridge.xǁBridgeǁserve__mutmut_5 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_6'] = Bridge.xǁBridgeǁserve__mutmut_6 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_7'] = Bridge.xǁBridgeǁserve__mutmut_7 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_8'] = Bridge.xǁBridgeǁserve__mutmut_8 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_9'] = Bridge.xǁBridgeǁserve__mutmut_9 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_10'] = Bridge.xǁBridgeǁserve__mutmut_10 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_11'] = Bridge.xǁBridgeǁserve__mutmut_11 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_12'] = Bridge.xǁBridgeǁserve__mutmut_12 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_13'] = Bridge.xǁBridgeǁserve__mutmut_13 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_14'] = Bridge.xǁBridgeǁserve__mutmut_14 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_15'] = Bridge.xǁBridgeǁserve__mutmut_15 # type: ignore # mutmut generated
mutants_xǁBridgeǁserve__mutmut['xǁBridgeǁserve__mutmut_16'] = Bridge.xǁBridgeǁserve__mutmut_16 # type: ignore # mutmut generated
mutants_x_main__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_main__mutmut)
def main() -> int:
    bridge = Bridge()
    bridge.serve()
    return 0


def x_main__mutmut_orig() -> int:
    bridge = Bridge()
    bridge.serve()
    return 0


def x_main__mutmut_1() -> int:
    bridge = None
    bridge.serve()
    return 0


def x_main__mutmut_2() -> int:
    bridge = Bridge()
    bridge.serve()
    return 1

mutants_x_main__mutmut['_mutmut_orig'] = x_main__mutmut_orig # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_1'] = x_main__mutmut_1 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_2'] = x_main__mutmut_2 # type: ignore # mutmut generated


if __name__ == "__main__":
    raise SystemExit(main())
