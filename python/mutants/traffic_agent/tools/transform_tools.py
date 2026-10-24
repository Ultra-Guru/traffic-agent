"""Mutation tools over the capture store (risk-gated at the bridge)."""

from __future__ import annotations

import re
from typing import Dict, Optional

from ..store import CaptureStore

_BREAKPOINTS: Dict[int, str] = {}  # request id -> phase


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_register_transform_tools__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_register_transform_tools__mutmut)
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


def x_register_transform_tools__mutmut_orig(registry, store: CaptureStore) -> None:
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


def x_register_transform_tools__mutmut_1(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "XXrequestXX") -> dict:
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


def x_register_transform_tools__mutmut_2(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "REQUEST") -> dict:
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


def x_register_transform_tools__mutmut_3(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = None
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


def x_register_transform_tools__mutmut_4(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(None, name, value, phase=phase)
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


def x_register_transform_tools__mutmut_5(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), None, value, phase=phase)
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


def x_register_transform_tools__mutmut_6(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, None, phase=phase)
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


def x_register_transform_tools__mutmut_7(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=None)
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


def x_register_transform_tools__mutmut_8(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(name, value, phase=phase)
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


def x_register_transform_tools__mutmut_9(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), value, phase=phase)
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


def x_register_transform_tools__mutmut_10(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, phase=phase)
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


def x_register_transform_tools__mutmut_11(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, )
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


def x_register_transform_tools__mutmut_12(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(None), name, value, phase=phase)
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


def x_register_transform_tools__mutmut_13(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"XXidXX": updated.id, "headers": dict(updated.headers)}

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


def x_register_transform_tools__mutmut_14(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"ID": updated.id, "headers": dict(updated.headers)}

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


def x_register_transform_tools__mutmut_15(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "XXheadersXX": dict(updated.headers)}

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


def x_register_transform_tools__mutmut_16(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "HEADERS": dict(updated.headers)}

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


def x_register_transform_tools__mutmut_17(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(None)}

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


def x_register_transform_tools__mutmut_18(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "XXrequestXX") -> dict:
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


def x_register_transform_tools__mutmut_19(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "REQUEST") -> dict:
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


def x_register_transform_tools__mutmut_20(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = None
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


def x_register_transform_tools__mutmut_21(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(None, name, phase=phase)
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


def x_register_transform_tools__mutmut_22(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), None, phase=phase)
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


def x_register_transform_tools__mutmut_23(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=None)
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


def x_register_transform_tools__mutmut_24(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(name, phase=phase)
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


def x_register_transform_tools__mutmut_25(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), phase=phase)
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


def x_register_transform_tools__mutmut_26(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, )
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


def x_register_transform_tools__mutmut_27(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(None), name, phase=phase)
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


def x_register_transform_tools__mutmut_28(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"XXidXX": updated.id, "headers": dict(updated.headers)}

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


def x_register_transform_tools__mutmut_29(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"ID": updated.id, "headers": dict(updated.headers)}

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


def x_register_transform_tools__mutmut_30(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "XXheadersXX": dict(updated.headers)}

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


def x_register_transform_tools__mutmut_31(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "HEADERS": dict(updated.headers)}

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


def x_register_transform_tools__mutmut_32(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(None)}

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


def x_register_transform_tools__mutmut_33(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = None
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


def x_register_transform_tools__mutmut_34(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(None, host=host, path=path)
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


def x_register_transform_tools__mutmut_35(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=None, path=path)
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


def x_register_transform_tools__mutmut_36(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, path=None)
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


def x_register_transform_tools__mutmut_37(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(host=host, path=path)
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


def x_register_transform_tools__mutmut_38(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), path=path)
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


def x_register_transform_tools__mutmut_39(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, )
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


def x_register_transform_tools__mutmut_40(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(None), host=host, path=path)
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


def x_register_transform_tools__mutmut_41(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, path=path)
        return {"XXidXX": updated.id, "host": updated.host, "path": updated.path}

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


def x_register_transform_tools__mutmut_42(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, path=path)
        return {"ID": updated.id, "host": updated.host, "path": updated.path}

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


def x_register_transform_tools__mutmut_43(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, path=path)
        return {"id": updated.id, "XXhostXX": updated.host, "path": updated.path}

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


def x_register_transform_tools__mutmut_44(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, path=path)
        return {"id": updated.id, "HOST": updated.host, "path": updated.path}

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


def x_register_transform_tools__mutmut_45(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, path=path)
        return {"id": updated.id, "host": updated.host, "XXpathXX": updated.path}

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


def x_register_transform_tools__mutmut_46(registry, store: CaptureStore) -> None:
    def modify_header(request_id: int, name: str, value: str, phase: str = "request") -> dict:
        updated = store.modify_header(int(request_id), name, value, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def remove_header(request_id: int, name: str, phase: str = "request") -> dict:
        updated = store.remove_header(int(request_id), name, phase=phase)
        return {"id": updated.id, "headers": dict(updated.headers)}

    def rewrite_url(request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> dict:
        updated = store.rewrite_url(int(request_id), host=host, path=path)
        return {"id": updated.id, "host": updated.host, "PATH": updated.path}

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


def x_register_transform_tools__mutmut_47(registry, store: CaptureStore) -> None:
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
        phase: str = "XXrequestXX",
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


def x_register_transform_tools__mutmut_48(registry, store: CaptureStore) -> None:
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
        phase: str = "REQUEST",
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


def x_register_transform_tools__mutmut_49(registry, store: CaptureStore) -> None:
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
        max_replacements: int = 11,
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


def x_register_transform_tools__mutmut_50(registry, store: CaptureStore) -> None:
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
        req = None
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


def x_register_transform_tools__mutmut_51(registry, store: CaptureStore) -> None:
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
        req = store.get(None)
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


def x_register_transform_tools__mutmut_52(registry, store: CaptureStore) -> None:
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
        req = store.get(int(None))
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


def x_register_transform_tools__mutmut_53(registry, store: CaptureStore) -> None:
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
        target = None
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


def x_register_transform_tools__mutmut_54(registry, store: CaptureStore) -> None:
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
        target = req.body if (phase == "request") and False else req.response_body
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


def x_register_transform_tools__mutmut_55(registry, store: CaptureStore) -> None:
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
        target = req.body if (phase == "request") or True else req.response_body
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


def x_register_transform_tools__mutmut_56(registry, store: CaptureStore) -> None:
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
        target = req.body if phase != "request" else req.response_body
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


def x_register_transform_tools__mutmut_57(registry, store: CaptureStore) -> None:
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
        target = req.body if phase == "XXrequestXX" else req.response_body
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


def x_register_transform_tools__mutmut_58(registry, store: CaptureStore) -> None:
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
        target = req.body if phase == "REQUEST" else req.response_body
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


def x_register_transform_tools__mutmut_59(registry, store: CaptureStore) -> None:
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
        updated_text, count = None
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


def x_register_transform_tools__mutmut_60(registry, store: CaptureStore) -> None:
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
            None, replacement, target, count=max(0, int(max_replacements))
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


def x_register_transform_tools__mutmut_61(registry, store: CaptureStore) -> None:
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
            pattern, None, target, count=max(0, int(max_replacements))
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


def x_register_transform_tools__mutmut_62(registry, store: CaptureStore) -> None:
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
            pattern, replacement, None, count=max(0, int(max_replacements))
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


def x_register_transform_tools__mutmut_63(registry, store: CaptureStore) -> None:
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
            pattern, replacement, target, count=None
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


def x_register_transform_tools__mutmut_64(registry, store: CaptureStore) -> None:
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
            replacement, target, count=max(0, int(max_replacements))
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


def x_register_transform_tools__mutmut_65(registry, store: CaptureStore) -> None:
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
            pattern, target, count=max(0, int(max_replacements))
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


def x_register_transform_tools__mutmut_66(registry, store: CaptureStore) -> None:
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
            pattern, replacement, count=max(0, int(max_replacements))
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


def x_register_transform_tools__mutmut_67(registry, store: CaptureStore) -> None:
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
            pattern, replacement, target, )
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


def x_register_transform_tools__mutmut_68(registry, store: CaptureStore) -> None:
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
            pattern, replacement, target, count=max(None, int(max_replacements))
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


def x_register_transform_tools__mutmut_69(registry, store: CaptureStore) -> None:
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
            pattern, replacement, target, count=max(0, None)
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


def x_register_transform_tools__mutmut_70(registry, store: CaptureStore) -> None:
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
            pattern, replacement, target, count=max(int(max_replacements))
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


def x_register_transform_tools__mutmut_71(registry, store: CaptureStore) -> None:
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
            pattern, replacement, target, count=max(0, )
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


def x_register_transform_tools__mutmut_72(registry, store: CaptureStore) -> None:
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
            pattern, replacement, target, count=max(1, int(max_replacements))
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


def x_register_transform_tools__mutmut_73(registry, store: CaptureStore) -> None:
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
            pattern, replacement, target, count=max(0, int(None))
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


def x_register_transform_tools__mutmut_74(registry, store: CaptureStore) -> None:
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
        store.set_body(None, updated_text, phase=phase)
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


def x_register_transform_tools__mutmut_75(registry, store: CaptureStore) -> None:
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
        store.set_body(int(request_id), None, phase=phase)
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


def x_register_transform_tools__mutmut_76(registry, store: CaptureStore) -> None:
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
        store.set_body(int(request_id), updated_text, phase=None)
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


def x_register_transform_tools__mutmut_77(registry, store: CaptureStore) -> None:
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
        store.set_body(updated_text, phase=phase)
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


def x_register_transform_tools__mutmut_78(registry, store: CaptureStore) -> None:
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
        store.set_body(int(request_id), phase=phase)
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


def x_register_transform_tools__mutmut_79(registry, store: CaptureStore) -> None:
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
        store.set_body(int(request_id), updated_text, )
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


def x_register_transform_tools__mutmut_80(registry, store: CaptureStore) -> None:
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
        store.set_body(int(None), updated_text, phase=phase)
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


def x_register_transform_tools__mutmut_81(registry, store: CaptureStore) -> None:
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
        return {"XXidXX": int(request_id), "replacements": count, "phase": phase}

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


def x_register_transform_tools__mutmut_82(registry, store: CaptureStore) -> None:
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
        return {"ID": int(request_id), "replacements": count, "phase": phase}

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


def x_register_transform_tools__mutmut_83(registry, store: CaptureStore) -> None:
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
        return {"id": int(None), "replacements": count, "phase": phase}

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


def x_register_transform_tools__mutmut_84(registry, store: CaptureStore) -> None:
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
        return {"id": int(request_id), "XXreplacementsXX": count, "phase": phase}

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


def x_register_transform_tools__mutmut_85(registry, store: CaptureStore) -> None:
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
        return {"id": int(request_id), "REPLACEMENTS": count, "phase": phase}

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


def x_register_transform_tools__mutmut_86(registry, store: CaptureStore) -> None:
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
        return {"id": int(request_id), "replacements": count, "XXphaseXX": phase}

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


def x_register_transform_tools__mutmut_87(registry, store: CaptureStore) -> None:
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
        return {"id": int(request_id), "replacements": count, "PHASE": phase}

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


def x_register_transform_tools__mutmut_88(registry, store: CaptureStore) -> None:
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

    def set_breakpoint(request_id: int, phase: str = "XXrequestXX") -> dict:
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


def x_register_transform_tools__mutmut_89(registry, store: CaptureStore) -> None:
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

    def set_breakpoint(request_id: int, phase: str = "REQUEST") -> dict:
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


def x_register_transform_tools__mutmut_90(registry, store: CaptureStore) -> None:
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
        rid = None
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


def x_register_transform_tools__mutmut_91(registry, store: CaptureStore) -> None:
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
        rid = int(None)
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


def x_register_transform_tools__mutmut_92(registry, store: CaptureStore) -> None:
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
        _BREAKPOINTS[rid] = None
        return {"id": rid, "phase": phase, "pending": len(_BREAKPOINTS)}

    def pending_breakpoints() -> dict:
        return {str(k): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_93(registry, store: CaptureStore) -> None:
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
        return {"XXidXX": rid, "phase": phase, "pending": len(_BREAKPOINTS)}

    def pending_breakpoints() -> dict:
        return {str(k): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_94(registry, store: CaptureStore) -> None:
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
        return {"ID": rid, "phase": phase, "pending": len(_BREAKPOINTS)}

    def pending_breakpoints() -> dict:
        return {str(k): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_95(registry, store: CaptureStore) -> None:
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
        return {"id": rid, "XXphaseXX": phase, "pending": len(_BREAKPOINTS)}

    def pending_breakpoints() -> dict:
        return {str(k): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_96(registry, store: CaptureStore) -> None:
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
        return {"id": rid, "PHASE": phase, "pending": len(_BREAKPOINTS)}

    def pending_breakpoints() -> dict:
        return {str(k): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_97(registry, store: CaptureStore) -> None:
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
        return {"id": rid, "phase": phase, "XXpendingXX": len(_BREAKPOINTS)}

    def pending_breakpoints() -> dict:
        return {str(k): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_98(registry, store: CaptureStore) -> None:
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
        return {"id": rid, "phase": phase, "PENDING": len(_BREAKPOINTS)}

    def pending_breakpoints() -> dict:
        return {str(k): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_99(registry, store: CaptureStore) -> None:
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
        return {str(None): v for k, v in _BREAKPOINTS.items()}

    registry.register("modify_header", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_100(registry, store: CaptureStore) -> None:
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

    registry.register(None, modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_101(registry, store: CaptureStore) -> None:
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

    registry.register("modify_header", None, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_102(registry, store: CaptureStore) -> None:
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

    registry.register("modify_header", modify_header, None)
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_103(registry, store: CaptureStore) -> None:
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

    registry.register(modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_104(registry, store: CaptureStore) -> None:
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

    registry.register("modify_header", "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_105(registry, store: CaptureStore) -> None:
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

    registry.register("modify_header", modify_header, )
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_106(registry, store: CaptureStore) -> None:
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

    registry.register("XXmodify_headerXX", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_107(registry, store: CaptureStore) -> None:
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

    registry.register("MODIFY_HEADER", modify_header, "set a header on a stored exchange")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_108(registry, store: CaptureStore) -> None:
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

    registry.register("modify_header", modify_header, "XXset a header on a stored exchangeXX")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_109(registry, store: CaptureStore) -> None:
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

    registry.register("modify_header", modify_header, "SET A HEADER ON A STORED EXCHANGE")
    registry.register("remove_header", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_110(registry, store: CaptureStore) -> None:
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
    registry.register(None, remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_111(registry, store: CaptureStore) -> None:
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
    registry.register("remove_header", None, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_112(registry, store: CaptureStore) -> None:
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
    registry.register("remove_header", remove_header, None)
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_113(registry, store: CaptureStore) -> None:
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
    registry.register(remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_114(registry, store: CaptureStore) -> None:
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
    registry.register("remove_header", "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_115(registry, store: CaptureStore) -> None:
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
    registry.register("remove_header", remove_header, )
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_116(registry, store: CaptureStore) -> None:
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
    registry.register("XXremove_headerXX", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_117(registry, store: CaptureStore) -> None:
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
    registry.register("REMOVE_HEADER", remove_header, "remove a header from a stored exchange")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_118(registry, store: CaptureStore) -> None:
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
    registry.register("remove_header", remove_header, "XXremove a header from a stored exchangeXX")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_119(registry, store: CaptureStore) -> None:
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
    registry.register("remove_header", remove_header, "REMOVE A HEADER FROM A STORED EXCHANGE")
    registry.register("rewrite_url", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_120(registry, store: CaptureStore) -> None:
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
    registry.register(None, rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_121(registry, store: CaptureStore) -> None:
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
    registry.register("rewrite_url", None, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_122(registry, store: CaptureStore) -> None:
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
    registry.register("rewrite_url", rewrite_url, None)
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_123(registry, store: CaptureStore) -> None:
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
    registry.register(rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_124(registry, store: CaptureStore) -> None:
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
    registry.register("rewrite_url", "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_125(registry, store: CaptureStore) -> None:
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
    registry.register("rewrite_url", rewrite_url, )
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_126(registry, store: CaptureStore) -> None:
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
    registry.register("XXrewrite_urlXX", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_127(registry, store: CaptureStore) -> None:
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
    registry.register("REWRITE_URL", rewrite_url, "rewrite host/path of a stored exchange")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_128(registry, store: CaptureStore) -> None:
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
    registry.register("rewrite_url", rewrite_url, "XXrewrite host/path of a stored exchangeXX")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_129(registry, store: CaptureStore) -> None:
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
    registry.register("rewrite_url", rewrite_url, "REWRITE HOST/PATH OF A STORED EXCHANGE")
    registry.register("modify_body", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_130(registry, store: CaptureStore) -> None:
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
    registry.register(None, modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_131(registry, store: CaptureStore) -> None:
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
    registry.register("modify_body", None, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_132(registry, store: CaptureStore) -> None:
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
    registry.register("modify_body", modify_body, None)
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_133(registry, store: CaptureStore) -> None:
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
    registry.register(modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_134(registry, store: CaptureStore) -> None:
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
    registry.register("modify_body", "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_135(registry, store: CaptureStore) -> None:
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
    registry.register("modify_body", modify_body, )
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_136(registry, store: CaptureStore) -> None:
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
    registry.register("XXmodify_bodyXX", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_137(registry, store: CaptureStore) -> None:
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
    registry.register("MODIFY_BODY", modify_body, "regex-replace a stored body (bounded)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_138(registry, store: CaptureStore) -> None:
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
    registry.register("modify_body", modify_body, "XXregex-replace a stored body (bounded)XX")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_139(registry, store: CaptureStore) -> None:
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
    registry.register("modify_body", modify_body, "REGEX-REPLACE A STORED BODY (BOUNDED)")
    registry.register("set_breakpoint", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_140(registry, store: CaptureStore) -> None:
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
    registry.register(None, set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_141(registry, store: CaptureStore) -> None:
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
    registry.register("set_breakpoint", None, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_142(registry, store: CaptureStore) -> None:
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
    registry.register("set_breakpoint", set_breakpoint, None)
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_143(registry, store: CaptureStore) -> None:
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
    registry.register(set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_144(registry, store: CaptureStore) -> None:
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
    registry.register("set_breakpoint", "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_145(registry, store: CaptureStore) -> None:
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
    registry.register("set_breakpoint", set_breakpoint, )
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_146(registry, store: CaptureStore) -> None:
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
    registry.register("XXset_breakpointXX", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_147(registry, store: CaptureStore) -> None:
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
    registry.register("SET_BREAKPOINT", set_breakpoint, "park a stored exchange at a breakpoint")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_148(registry, store: CaptureStore) -> None:
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
    registry.register("set_breakpoint", set_breakpoint, "XXpark a stored exchange at a breakpointXX")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_149(registry, store: CaptureStore) -> None:
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
    registry.register("set_breakpoint", set_breakpoint, "PARK A STORED EXCHANGE AT A BREAKPOINT")
    registry.register("pending_breakpoints", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_150(registry, store: CaptureStore) -> None:
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
    registry.register(None, pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_151(registry, store: CaptureStore) -> None:
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
    registry.register("pending_breakpoints", None, "list pending breakpoints")


def x_register_transform_tools__mutmut_152(registry, store: CaptureStore) -> None:
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
    registry.register("pending_breakpoints", pending_breakpoints, None)


def x_register_transform_tools__mutmut_153(registry, store: CaptureStore) -> None:
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
    registry.register(pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_154(registry, store: CaptureStore) -> None:
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
    registry.register("pending_breakpoints", "list pending breakpoints")


def x_register_transform_tools__mutmut_155(registry, store: CaptureStore) -> None:
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
    registry.register("pending_breakpoints", pending_breakpoints, )


def x_register_transform_tools__mutmut_156(registry, store: CaptureStore) -> None:
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
    registry.register("XXpending_breakpointsXX", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_157(registry, store: CaptureStore) -> None:
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
    registry.register("PENDING_BREAKPOINTS", pending_breakpoints, "list pending breakpoints")


def x_register_transform_tools__mutmut_158(registry, store: CaptureStore) -> None:
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
    registry.register("pending_breakpoints", pending_breakpoints, "XXlist pending breakpointsXX")


def x_register_transform_tools__mutmut_159(registry, store: CaptureStore) -> None:
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
    registry.register("pending_breakpoints", pending_breakpoints, "LIST PENDING BREAKPOINTS")

mutants_x_register_transform_tools__mutmut['_mutmut_orig'] = x_register_transform_tools__mutmut_orig # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_1'] = x_register_transform_tools__mutmut_1 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_2'] = x_register_transform_tools__mutmut_2 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_3'] = x_register_transform_tools__mutmut_3 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_4'] = x_register_transform_tools__mutmut_4 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_5'] = x_register_transform_tools__mutmut_5 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_6'] = x_register_transform_tools__mutmut_6 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_7'] = x_register_transform_tools__mutmut_7 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_8'] = x_register_transform_tools__mutmut_8 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_9'] = x_register_transform_tools__mutmut_9 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_10'] = x_register_transform_tools__mutmut_10 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_11'] = x_register_transform_tools__mutmut_11 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_12'] = x_register_transform_tools__mutmut_12 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_13'] = x_register_transform_tools__mutmut_13 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_14'] = x_register_transform_tools__mutmut_14 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_15'] = x_register_transform_tools__mutmut_15 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_16'] = x_register_transform_tools__mutmut_16 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_17'] = x_register_transform_tools__mutmut_17 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_18'] = x_register_transform_tools__mutmut_18 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_19'] = x_register_transform_tools__mutmut_19 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_20'] = x_register_transform_tools__mutmut_20 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_21'] = x_register_transform_tools__mutmut_21 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_22'] = x_register_transform_tools__mutmut_22 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_23'] = x_register_transform_tools__mutmut_23 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_24'] = x_register_transform_tools__mutmut_24 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_25'] = x_register_transform_tools__mutmut_25 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_26'] = x_register_transform_tools__mutmut_26 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_27'] = x_register_transform_tools__mutmut_27 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_28'] = x_register_transform_tools__mutmut_28 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_29'] = x_register_transform_tools__mutmut_29 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_30'] = x_register_transform_tools__mutmut_30 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_31'] = x_register_transform_tools__mutmut_31 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_32'] = x_register_transform_tools__mutmut_32 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_33'] = x_register_transform_tools__mutmut_33 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_34'] = x_register_transform_tools__mutmut_34 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_35'] = x_register_transform_tools__mutmut_35 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_36'] = x_register_transform_tools__mutmut_36 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_37'] = x_register_transform_tools__mutmut_37 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_38'] = x_register_transform_tools__mutmut_38 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_39'] = x_register_transform_tools__mutmut_39 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_40'] = x_register_transform_tools__mutmut_40 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_41'] = x_register_transform_tools__mutmut_41 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_42'] = x_register_transform_tools__mutmut_42 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_43'] = x_register_transform_tools__mutmut_43 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_44'] = x_register_transform_tools__mutmut_44 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_45'] = x_register_transform_tools__mutmut_45 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_46'] = x_register_transform_tools__mutmut_46 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_47'] = x_register_transform_tools__mutmut_47 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_48'] = x_register_transform_tools__mutmut_48 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_49'] = x_register_transform_tools__mutmut_49 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_50'] = x_register_transform_tools__mutmut_50 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_51'] = x_register_transform_tools__mutmut_51 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_52'] = x_register_transform_tools__mutmut_52 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_53'] = x_register_transform_tools__mutmut_53 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_54'] = x_register_transform_tools__mutmut_54 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_55'] = x_register_transform_tools__mutmut_55 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_56'] = x_register_transform_tools__mutmut_56 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_57'] = x_register_transform_tools__mutmut_57 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_58'] = x_register_transform_tools__mutmut_58 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_59'] = x_register_transform_tools__mutmut_59 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_60'] = x_register_transform_tools__mutmut_60 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_61'] = x_register_transform_tools__mutmut_61 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_62'] = x_register_transform_tools__mutmut_62 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_63'] = x_register_transform_tools__mutmut_63 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_64'] = x_register_transform_tools__mutmut_64 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_65'] = x_register_transform_tools__mutmut_65 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_66'] = x_register_transform_tools__mutmut_66 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_67'] = x_register_transform_tools__mutmut_67 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_68'] = x_register_transform_tools__mutmut_68 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_69'] = x_register_transform_tools__mutmut_69 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_70'] = x_register_transform_tools__mutmut_70 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_71'] = x_register_transform_tools__mutmut_71 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_72'] = x_register_transform_tools__mutmut_72 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_73'] = x_register_transform_tools__mutmut_73 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_74'] = x_register_transform_tools__mutmut_74 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_75'] = x_register_transform_tools__mutmut_75 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_76'] = x_register_transform_tools__mutmut_76 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_77'] = x_register_transform_tools__mutmut_77 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_78'] = x_register_transform_tools__mutmut_78 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_79'] = x_register_transform_tools__mutmut_79 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_80'] = x_register_transform_tools__mutmut_80 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_81'] = x_register_transform_tools__mutmut_81 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_82'] = x_register_transform_tools__mutmut_82 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_83'] = x_register_transform_tools__mutmut_83 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_84'] = x_register_transform_tools__mutmut_84 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_85'] = x_register_transform_tools__mutmut_85 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_86'] = x_register_transform_tools__mutmut_86 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_87'] = x_register_transform_tools__mutmut_87 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_88'] = x_register_transform_tools__mutmut_88 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_89'] = x_register_transform_tools__mutmut_89 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_90'] = x_register_transform_tools__mutmut_90 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_91'] = x_register_transform_tools__mutmut_91 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_92'] = x_register_transform_tools__mutmut_92 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_93'] = x_register_transform_tools__mutmut_93 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_94'] = x_register_transform_tools__mutmut_94 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_95'] = x_register_transform_tools__mutmut_95 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_96'] = x_register_transform_tools__mutmut_96 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_97'] = x_register_transform_tools__mutmut_97 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_98'] = x_register_transform_tools__mutmut_98 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_99'] = x_register_transform_tools__mutmut_99 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_100'] = x_register_transform_tools__mutmut_100 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_101'] = x_register_transform_tools__mutmut_101 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_102'] = x_register_transform_tools__mutmut_102 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_103'] = x_register_transform_tools__mutmut_103 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_104'] = x_register_transform_tools__mutmut_104 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_105'] = x_register_transform_tools__mutmut_105 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_106'] = x_register_transform_tools__mutmut_106 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_107'] = x_register_transform_tools__mutmut_107 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_108'] = x_register_transform_tools__mutmut_108 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_109'] = x_register_transform_tools__mutmut_109 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_110'] = x_register_transform_tools__mutmut_110 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_111'] = x_register_transform_tools__mutmut_111 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_112'] = x_register_transform_tools__mutmut_112 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_113'] = x_register_transform_tools__mutmut_113 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_114'] = x_register_transform_tools__mutmut_114 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_115'] = x_register_transform_tools__mutmut_115 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_116'] = x_register_transform_tools__mutmut_116 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_117'] = x_register_transform_tools__mutmut_117 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_118'] = x_register_transform_tools__mutmut_118 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_119'] = x_register_transform_tools__mutmut_119 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_120'] = x_register_transform_tools__mutmut_120 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_121'] = x_register_transform_tools__mutmut_121 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_122'] = x_register_transform_tools__mutmut_122 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_123'] = x_register_transform_tools__mutmut_123 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_124'] = x_register_transform_tools__mutmut_124 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_125'] = x_register_transform_tools__mutmut_125 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_126'] = x_register_transform_tools__mutmut_126 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_127'] = x_register_transform_tools__mutmut_127 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_128'] = x_register_transform_tools__mutmut_128 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_129'] = x_register_transform_tools__mutmut_129 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_130'] = x_register_transform_tools__mutmut_130 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_131'] = x_register_transform_tools__mutmut_131 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_132'] = x_register_transform_tools__mutmut_132 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_133'] = x_register_transform_tools__mutmut_133 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_134'] = x_register_transform_tools__mutmut_134 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_135'] = x_register_transform_tools__mutmut_135 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_136'] = x_register_transform_tools__mutmut_136 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_137'] = x_register_transform_tools__mutmut_137 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_138'] = x_register_transform_tools__mutmut_138 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_139'] = x_register_transform_tools__mutmut_139 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_140'] = x_register_transform_tools__mutmut_140 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_141'] = x_register_transform_tools__mutmut_141 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_142'] = x_register_transform_tools__mutmut_142 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_143'] = x_register_transform_tools__mutmut_143 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_144'] = x_register_transform_tools__mutmut_144 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_145'] = x_register_transform_tools__mutmut_145 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_146'] = x_register_transform_tools__mutmut_146 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_147'] = x_register_transform_tools__mutmut_147 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_148'] = x_register_transform_tools__mutmut_148 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_149'] = x_register_transform_tools__mutmut_149 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_150'] = x_register_transform_tools__mutmut_150 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_151'] = x_register_transform_tools__mutmut_151 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_152'] = x_register_transform_tools__mutmut_152 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_153'] = x_register_transform_tools__mutmut_153 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_154'] = x_register_transform_tools__mutmut_154 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_155'] = x_register_transform_tools__mutmut_155 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_156'] = x_register_transform_tools__mutmut_156 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_157'] = x_register_transform_tools__mutmut_157 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_158'] = x_register_transform_tools__mutmut_158 # type: ignore # mutmut generated
mutants_x_register_transform_tools__mutmut['x_register_transform_tools__mutmut_159'] = x_register_transform_tools__mutmut_159 # type: ignore # mutmut generated
