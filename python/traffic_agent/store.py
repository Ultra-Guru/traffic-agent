"""In-memory capture store shared by the agent tools."""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional

_NEXT_ID = itertools.count(1)


@dataclass
class StoredRequest:
    host: str
    path: str
    method: str = "GET"
    status: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: str = ""
    timestamp_ms: int = 0
    id: int = field(default_factory=lambda: next(_NEXT_ID))


class UnknownRequest(Exception):
    def __init__(self, request_id: int):
        super().__init__(f"no request with id {request_id}")
        self.request_id = request_id


class CaptureStore:
    """Mutable store of captured exchanges; the tools operate on it."""

    def __init__(self) -> None:
        self._by_id: Dict[int, StoredRequest] = {}
        self._order: List[int] = []

    # ---------- read side ----------

    def get(self, request_id: int) -> StoredRequest:
        try:
            return self._by_id[request_id]
        except KeyError:
            raise UnknownRequest(request_id) from None

    def list(self, limit: Optional[int] = None, offset: int = 0) -> List[StoredRequest]:
        items = [self._by_id[i] for i in self._order[offset:]]
        if limit is not None:
            items = items[:limit]
        return items

    def find(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = self._by_id[rid]
            if host_regex is not None and not re.search(host_regex, req.host):
                continue
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def count(self) -> int:
        return len(self._order)

    def stats_summary(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    # ---------- write side (used by transform tools) ----------

    def add(self, request: StoredRequest) -> StoredRequest:
        self._by_id[request.id] = request
        self._order.append(request.id)
        return request

    def _update(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(request_id)
        updated = replace(req, **changes)
        self._by_id[request_id] = updated
        return updated

    def modify_header(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def remove_header(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def rewrite_url(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def set_body(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=body)
