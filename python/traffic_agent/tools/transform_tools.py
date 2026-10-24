"""Mutation tools over the capture store (risk-gated at the bridge)."""

from __future__ import annotations

import re
from typing import Dict, Optional

from ..store import CaptureStore

_BREAKPOINTS: Dict[int, str] = {}  # request id -> phase


def register_transform_tools(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, path=path)
        return {"id": updated.id, "host": updated.host, "path": updated.path}

    def modify_body(
        request_id: int,
        pattern: str,
        replacement: str,
        phase: str = "request",
        max_replacements: int = 10,
    ) -> dict:
        req = store.get(int(request_id))
        target = req.body if phase == "request" else req.response_body
        updated_text, count = re.subn(
            pattern, replacement, target, count=max(0, int(max_replacements))
        )
        store.set_body(int(request_id), updated_text, phase=phase)
        return {"id": int(request_id), "replacements": count, "phase": phase}

    def set_breakpoint(request_id: int, phase: str = "request") -> dict:
        rid = int(request_id)
        _BREAKPOINTS[rid] = phase
        return {"id": rid, "phase": phase, "pending": len(_BREAKPOINTS)}

    def pending_breakpoints() -> dict:
        return {str(k): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")
