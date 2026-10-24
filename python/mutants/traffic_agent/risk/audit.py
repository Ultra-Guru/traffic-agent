"""Append-only audit log for every gated tool call."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import List, Optional


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass
class AuditEntry:
    timestamp_ms: int
    tool: str
    decision: str
    params_digest: str
    detail: str = ""
mutants_x__digest__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__digest__mutmut)
def _digest(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_orig(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_1(params: Optional[dict]) -> str:
    if params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_2(params: Optional[dict]) -> str:
    if not params:
        return "XX-XX"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_3(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = None
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_4(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(None, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_5(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=None, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_6(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=None)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_7(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_8(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_9(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_10(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def x__digest__mutmut_11(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(None).hexdigest()[:12]


def x__digest__mutmut_12(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode(None)).hexdigest()[:12]


def x__digest__mutmut_13(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("XXutf-8XX")).hexdigest()[:12]


def x__digest__mutmut_14(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("UTF-8")).hexdigest()[:12]


def x__digest__mutmut_15(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:13]

mutants_x__digest__mutmut['_mutmut_orig'] = x__digest__mutmut_orig # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_1'] = x__digest__mutmut_1 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_2'] = x__digest__mutmut_2 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_3'] = x__digest__mutmut_3 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_4'] = x__digest__mutmut_4 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_5'] = x__digest__mutmut_5 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_6'] = x__digest__mutmut_6 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_7'] = x__digest__mutmut_7 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_8'] = x__digest__mutmut_8 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_9'] = x__digest__mutmut_9 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_10'] = x__digest__mutmut_10 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_11'] = x__digest__mutmut_11 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_12'] = x__digest__mutmut_12 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_13'] = x__digest__mutmut_13 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_14'] = x__digest__mutmut_14 # type: ignore # mutmut generated
mutants_x__digest__mutmut['x__digest__mutmut_15'] = x__digest__mutmut_15 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁAuditLogǁappend__mutmut: MutantDict = {}  # type: ignore
mutants_xǁAuditLogǁtail__mutmut: MutantDict = {}  # type: ignore
mutants_xǁAuditLogǁby_tool__mutmut: MutantDict = {}  # type: ignore
mutants_xǁAuditLogǁclear__mutmut: MutantDict = {}  # type: ignore
mutants_xǁAuditLogǁpersist__mutmut: MutantDict = {}  # type: ignore


class AuditLog:
    @_mutmut_mutated(mutants_xǁAuditLogǁ__init____mutmut)
    def __init__(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(time.time() * 1000))
    def xǁAuditLogǁ__init____mutmut_orig(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(time.time() * 1000))
    def xǁAuditLogǁ__init____mutmut_1(self, clock=None):
        self._entries: List[AuditEntry] = None
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(time.time() * 1000))
    def xǁAuditLogǁ__init____mutmut_2(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = None  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(time.time() * 1000))
    def xǁAuditLogǁ__init____mutmut_3(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 1  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(time.time() * 1000))
    def xǁAuditLogǁ__init____mutmut_4(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = None
    def xǁAuditLogǁ__init____mutmut_5(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock and (lambda: int(time.time() * 1000))
    def xǁAuditLogǁ__init____mutmut_6(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock or (lambda: None)
    def xǁAuditLogǁ__init____mutmut_7(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(None))
    def xǁAuditLogǁ__init____mutmut_8(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(time.time() / 1000))
    def xǁAuditLogǁ__init____mutmut_9(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(time.time() * 1001))

    @_mutmut_mutated(mutants_xǁAuditLogǁappend__mutmut)
    def append(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_orig(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_1(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "XXXX") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_2(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = None
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_3(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=None,
            tool=tool,
            decision=decision,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_4(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=None,
            decision=decision,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_5(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=None,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_6(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            params_digest=None,
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_7(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            params_digest=_digest(params),
            detail=None,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_8(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            tool=tool,
            decision=decision,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_9(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            decision=decision,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_10(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_11(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_12(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            params_digest=_digest(params),
            )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_13(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            params_digest=_digest(None),
            detail=detail,
        )
        self._entries.append(entry)
        return entry

    def xǁAuditLogǁappend__mutmut_14(self, tool: str, decision: str, params: Optional[dict] = None, detail: str = "") -> AuditEntry:
        entry = AuditEntry(
            timestamp_ms=self._clock(),
            tool=tool,
            decision=decision,
            params_digest=_digest(params),
            detail=detail,
        )
        self._entries.append(None)
        return entry

    @_mutmut_mutated(mutants_xǁAuditLogǁtail__mutmut)
    def tail(self, n: int = 20) -> List[AuditEntry]:
        if n <= 0:
            return []
        return list(self._entries[-n:])

    def xǁAuditLogǁtail__mutmut_orig(self, n: int = 20) -> List[AuditEntry]:
        if n <= 0:
            return []
        return list(self._entries[-n:])

    def xǁAuditLogǁtail__mutmut_1(self, n: int = 21) -> List[AuditEntry]:
        if n <= 0:
            return []
        return list(self._entries[-n:])

    def xǁAuditLogǁtail__mutmut_2(self, n: int = 20) -> List[AuditEntry]:
        if n < 0:
            return []
        return list(self._entries[-n:])

    def xǁAuditLogǁtail__mutmut_3(self, n: int = 20) -> List[AuditEntry]:
        if n <= 1:
            return []
        return list(self._entries[-n:])

    def xǁAuditLogǁtail__mutmut_4(self, n: int = 20) -> List[AuditEntry]:
        if n <= 0:
            return []
        return list(None)

    def xǁAuditLogǁtail__mutmut_5(self, n: int = 20) -> List[AuditEntry]:
        if n <= 0:
            return []
        return list(self._entries[+n:])

    def count(self) -> int:
        return len(self._entries)

    @_mutmut_mutated(mutants_xǁAuditLogǁby_tool__mutmut)
    def by_tool(self, tool: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.tool == tool]

    def xǁAuditLogǁby_tool__mutmut_orig(self, tool: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.tool == tool]

    def xǁAuditLogǁby_tool__mutmut_1(self, tool: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.tool != tool]

    @_mutmut_mutated(mutants_xǁAuditLogǁclear__mutmut)
    def clear(self) -> None:
        self._entries.clear()
        self._persisted = 0

    def xǁAuditLogǁclear__mutmut_orig(self) -> None:
        self._entries.clear()
        self._persisted = 0

    def xǁAuditLogǁclear__mutmut_1(self) -> None:
        self._entries.clear()
        self._persisted = None

    def xǁAuditLogǁclear__mutmut_2(self) -> None:
        self._entries.clear()
        self._persisted = 1

    @_mutmut_mutated(mutants_xǁAuditLogǁpersist__mutmut)
    def persist(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_orig(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_1(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = None
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_2(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 1
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_3(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(None, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_4(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, None, encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_5(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding=None) as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_6(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open("a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_7(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_8(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", ) as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_9(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "XXaXX", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_10(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "A", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_11(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="XXutf-8XX") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_12(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="UTF-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_13(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    None
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_14(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    ) - "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_15(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        None
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_16(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "XXtsXX": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_17(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "TS": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_18(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "XXtoolXX": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_19(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "TOOL": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_20(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "XXdecisionXX": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_21(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "DECISION": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_22(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "XXdigestXX": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_23(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "DIGEST": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_24(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "XXdetailXX": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_25(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "DETAIL": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_26(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "XX\nXX"
                )
                written += 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_27(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written = 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_28(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written -= 1
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_29(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 2
        self._persisted = len(self._entries)
        return written

    def xǁAuditLogǁpersist__mutmut_30(self, path: str) -> int:
        """Appends entries not yet persisted as JSON lines; returns the record count written."""
        written = 0
        with open(path, "a", encoding="utf-8") as fh:
            for entry in self._entries[self._persisted:]:
                fh.write(
                    json.dumps(
                        {
                            "ts": entry.timestamp_ms,
                            "tool": entry.tool,
                            "decision": entry.decision,
                            "digest": entry.params_digest,
                            "detail": entry.detail,
                        }
                    )
                    + "\n"
                )
                written += 1
        self._persisted = None
        return written

mutants_xǁAuditLogǁ__init____mutmut['_mutmut_orig'] = AuditLog.xǁAuditLogǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_1'] = AuditLog.xǁAuditLogǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_2'] = AuditLog.xǁAuditLogǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_3'] = AuditLog.xǁAuditLogǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_4'] = AuditLog.xǁAuditLogǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_5'] = AuditLog.xǁAuditLogǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_6'] = AuditLog.xǁAuditLogǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_7'] = AuditLog.xǁAuditLogǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_8'] = AuditLog.xǁAuditLogǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁAuditLogǁ__init____mutmut['xǁAuditLogǁ__init____mutmut_9'] = AuditLog.xǁAuditLogǁ__init____mutmut_9 # type: ignore # mutmut generated

mutants_xǁAuditLogǁappend__mutmut['_mutmut_orig'] = AuditLog.xǁAuditLogǁappend__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_1'] = AuditLog.xǁAuditLogǁappend__mutmut_1 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_2'] = AuditLog.xǁAuditLogǁappend__mutmut_2 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_3'] = AuditLog.xǁAuditLogǁappend__mutmut_3 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_4'] = AuditLog.xǁAuditLogǁappend__mutmut_4 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_5'] = AuditLog.xǁAuditLogǁappend__mutmut_5 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_6'] = AuditLog.xǁAuditLogǁappend__mutmut_6 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_7'] = AuditLog.xǁAuditLogǁappend__mutmut_7 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_8'] = AuditLog.xǁAuditLogǁappend__mutmut_8 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_9'] = AuditLog.xǁAuditLogǁappend__mutmut_9 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_10'] = AuditLog.xǁAuditLogǁappend__mutmut_10 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_11'] = AuditLog.xǁAuditLogǁappend__mutmut_11 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_12'] = AuditLog.xǁAuditLogǁappend__mutmut_12 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_13'] = AuditLog.xǁAuditLogǁappend__mutmut_13 # type: ignore # mutmut generated
mutants_xǁAuditLogǁappend__mutmut['xǁAuditLogǁappend__mutmut_14'] = AuditLog.xǁAuditLogǁappend__mutmut_14 # type: ignore # mutmut generated

mutants_xǁAuditLogǁtail__mutmut['_mutmut_orig'] = AuditLog.xǁAuditLogǁtail__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAuditLogǁtail__mutmut['xǁAuditLogǁtail__mutmut_1'] = AuditLog.xǁAuditLogǁtail__mutmut_1 # type: ignore # mutmut generated
mutants_xǁAuditLogǁtail__mutmut['xǁAuditLogǁtail__mutmut_2'] = AuditLog.xǁAuditLogǁtail__mutmut_2 # type: ignore # mutmut generated
mutants_xǁAuditLogǁtail__mutmut['xǁAuditLogǁtail__mutmut_3'] = AuditLog.xǁAuditLogǁtail__mutmut_3 # type: ignore # mutmut generated
mutants_xǁAuditLogǁtail__mutmut['xǁAuditLogǁtail__mutmut_4'] = AuditLog.xǁAuditLogǁtail__mutmut_4 # type: ignore # mutmut generated
mutants_xǁAuditLogǁtail__mutmut['xǁAuditLogǁtail__mutmut_5'] = AuditLog.xǁAuditLogǁtail__mutmut_5 # type: ignore # mutmut generated

mutants_xǁAuditLogǁby_tool__mutmut['_mutmut_orig'] = AuditLog.xǁAuditLogǁby_tool__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAuditLogǁby_tool__mutmut['xǁAuditLogǁby_tool__mutmut_1'] = AuditLog.xǁAuditLogǁby_tool__mutmut_1 # type: ignore # mutmut generated

mutants_xǁAuditLogǁclear__mutmut['_mutmut_orig'] = AuditLog.xǁAuditLogǁclear__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAuditLogǁclear__mutmut['xǁAuditLogǁclear__mutmut_1'] = AuditLog.xǁAuditLogǁclear__mutmut_1 # type: ignore # mutmut generated
mutants_xǁAuditLogǁclear__mutmut['xǁAuditLogǁclear__mutmut_2'] = AuditLog.xǁAuditLogǁclear__mutmut_2 # type: ignore # mutmut generated

mutants_xǁAuditLogǁpersist__mutmut['_mutmut_orig'] = AuditLog.xǁAuditLogǁpersist__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_1'] = AuditLog.xǁAuditLogǁpersist__mutmut_1 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_2'] = AuditLog.xǁAuditLogǁpersist__mutmut_2 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_3'] = AuditLog.xǁAuditLogǁpersist__mutmut_3 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_4'] = AuditLog.xǁAuditLogǁpersist__mutmut_4 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_5'] = AuditLog.xǁAuditLogǁpersist__mutmut_5 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_6'] = AuditLog.xǁAuditLogǁpersist__mutmut_6 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_7'] = AuditLog.xǁAuditLogǁpersist__mutmut_7 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_8'] = AuditLog.xǁAuditLogǁpersist__mutmut_8 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_9'] = AuditLog.xǁAuditLogǁpersist__mutmut_9 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_10'] = AuditLog.xǁAuditLogǁpersist__mutmut_10 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_11'] = AuditLog.xǁAuditLogǁpersist__mutmut_11 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_12'] = AuditLog.xǁAuditLogǁpersist__mutmut_12 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_13'] = AuditLog.xǁAuditLogǁpersist__mutmut_13 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_14'] = AuditLog.xǁAuditLogǁpersist__mutmut_14 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_15'] = AuditLog.xǁAuditLogǁpersist__mutmut_15 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_16'] = AuditLog.xǁAuditLogǁpersist__mutmut_16 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_17'] = AuditLog.xǁAuditLogǁpersist__mutmut_17 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_18'] = AuditLog.xǁAuditLogǁpersist__mutmut_18 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_19'] = AuditLog.xǁAuditLogǁpersist__mutmut_19 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_20'] = AuditLog.xǁAuditLogǁpersist__mutmut_20 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_21'] = AuditLog.xǁAuditLogǁpersist__mutmut_21 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_22'] = AuditLog.xǁAuditLogǁpersist__mutmut_22 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_23'] = AuditLog.xǁAuditLogǁpersist__mutmut_23 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_24'] = AuditLog.xǁAuditLogǁpersist__mutmut_24 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_25'] = AuditLog.xǁAuditLogǁpersist__mutmut_25 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_26'] = AuditLog.xǁAuditLogǁpersist__mutmut_26 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_27'] = AuditLog.xǁAuditLogǁpersist__mutmut_27 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_28'] = AuditLog.xǁAuditLogǁpersist__mutmut_28 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_29'] = AuditLog.xǁAuditLogǁpersist__mutmut_29 # type: ignore # mutmut generated
mutants_xǁAuditLogǁpersist__mutmut['xǁAuditLogǁpersist__mutmut_30'] = AuditLog.xǁAuditLogǁpersist__mutmut_30 # type: ignore # mutmut generated
