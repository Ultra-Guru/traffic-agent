"""Append-only audit log for every gated tool call."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AuditEntry:
    timestamp_ms: int
    tool: str
    decision: str
    params_digest: str
    detail: str = ""


def _digest(params: Optional[dict]) -> str:
    if not params:
        return "-"
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


class AuditLog:
    def __init__(self, clock=None):
        self._entries: List[AuditEntry] = []
        self._persisted: int = 0  # number of entries already flushed to disk
        self._clock = clock or (lambda: int(time.time() * 1000))

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

    def tail(self, n: int = 20) -> List[AuditEntry]:
        if n <= 0:
            return []
        return list(self._entries[-n:])

    def count(self) -> int:
        return len(self._entries)

    def by_tool(self, tool: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.tool == tool]

    def clear(self) -> None:
        self._entries.clear()
        self._persisted = 0

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
