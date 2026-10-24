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


class Bridge:
    """Wires registry + gate + audit together and answers single lines."""

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

    # ---------- line codec ----------

    @staticmethod
    def encode(pairs: dict) -> str:
        return "&".join(f"{k}={quote(str(v), safe='')}" for k, v in pairs.items())

    @staticmethod
    def decode(line: str) -> dict:
        return {k: v for k, v in parse_qsl(line, keep_blank_values=True)}

    # ---------- dispatch ----------

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

    # ---------- stdio loop ----------

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


def main() -> int:
    bridge = Bridge()
    bridge.serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
