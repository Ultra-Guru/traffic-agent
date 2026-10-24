"""In-memory capture store shared by the agent tools."""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional

_NEXT_ID = itertools.count(1)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


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
mutants_xǁUnknownRequestǁ__init____mutmut: MutantDict = {}  # type: ignore


class UnknownRequest(Exception):
    @_mutmut_mutated(mutants_xǁUnknownRequestǁ__init____mutmut)
    def __init__(self, request_id: int):
        super().__init__(f"no request with id {request_id}")
        self.request_id = request_id
    def xǁUnknownRequestǁ__init____mutmut_orig(self, request_id: int):
        super().__init__(f"no request with id {request_id}")
        self.request_id = request_id
    def xǁUnknownRequestǁ__init____mutmut_1(self, request_id: int):
        super().__init__(None)
        self.request_id = request_id
    def xǁUnknownRequestǁ__init____mutmut_2(self, request_id: int):
        super().__init__(f"no request with id {request_id}")
        self.request_id = None

mutants_xǁUnknownRequestǁ__init____mutmut['_mutmut_orig'] = UnknownRequest.xǁUnknownRequestǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁUnknownRequestǁ__init____mutmut['xǁUnknownRequestǁ__init____mutmut_1'] = UnknownRequest.xǁUnknownRequestǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁUnknownRequestǁ__init____mutmut['xǁUnknownRequestǁ__init____mutmut_2'] = UnknownRequest.xǁUnknownRequestǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁget__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁlist__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁfind__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁstats_summary__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁadd__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁ_update__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁmodify_header__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁremove_header__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁrewrite_url__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCaptureStoreǁset_body__mutmut: MutantDict = {}  # type: ignore


class CaptureStore:
    """Mutable store of captured exchanges; the tools operate on it."""

    @_mutmut_mutated(mutants_xǁCaptureStoreǁ__init____mutmut)
    def __init__(self) -> None:
        self._by_id: Dict[int, StoredRequest] = {}
        self._order: List[int] = []

    def xǁCaptureStoreǁ__init____mutmut_orig(self) -> None:
        self._by_id: Dict[int, StoredRequest] = {}
        self._order: List[int] = []

    def xǁCaptureStoreǁ__init____mutmut_1(self) -> None:
        self._by_id: Dict[int, StoredRequest] = None
        self._order: List[int] = []

    def xǁCaptureStoreǁ__init____mutmut_2(self) -> None:
        self._by_id: Dict[int, StoredRequest] = {}
        self._order: List[int] = None

    # ---------- read side ----------

    @_mutmut_mutated(mutants_xǁCaptureStoreǁget__mutmut)
    def get(self, request_id: int) -> StoredRequest:
        try:
            return self._by_id[request_id]
        except KeyError:
            raise UnknownRequest(request_id) from None

    # ---------- read side ----------

    def xǁCaptureStoreǁget__mutmut_orig(self, request_id: int) -> StoredRequest:
        try:
            return self._by_id[request_id]
        except KeyError:
            raise UnknownRequest(request_id) from None

    # ---------- read side ----------

    def xǁCaptureStoreǁget__mutmut_1(self, request_id: int) -> StoredRequest:
        try:
            return self._by_id[request_id]
        except KeyError:
            raise UnknownRequest(None) from None

    @_mutmut_mutated(mutants_xǁCaptureStoreǁlist__mutmut)
    def list(self, limit: Optional[int] = None, offset: int = 0) -> List[StoredRequest]:
        items = [self._by_id[i] for i in self._order[offset:]]
        if limit is not None:
            items = items[:limit]
        return items

    def xǁCaptureStoreǁlist__mutmut_orig(self, limit: Optional[int] = None, offset: int = 0) -> List[StoredRequest]:
        items = [self._by_id[i] for i in self._order[offset:]]
        if limit is not None:
            items = items[:limit]
        return items

    def xǁCaptureStoreǁlist__mutmut_1(self, limit: Optional[int] = None, offset: int = 1) -> List[StoredRequest]:
        items = [self._by_id[i] for i in self._order[offset:]]
        if limit is not None:
            items = items[:limit]
        return items

    def xǁCaptureStoreǁlist__mutmut_2(self, limit: Optional[int] = None, offset: int = 0) -> List[StoredRequest]:
        items = None
        if limit is not None:
            items = items[:limit]
        return items

    def xǁCaptureStoreǁlist__mutmut_3(self, limit: Optional[int] = None, offset: int = 0) -> List[StoredRequest]:
        items = [self._by_id[i] for i in self._order[offset:]]
        if limit is None:
            items = items[:limit]
        return items

    def xǁCaptureStoreǁlist__mutmut_4(self, limit: Optional[int] = None, offset: int = 0) -> List[StoredRequest]:
        items = [self._by_id[i] for i in self._order[offset:]]
        if limit is not None:
            items = None
        return items

    @_mutmut_mutated(mutants_xǁCaptureStoreǁfind__mutmut)
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

    def xǁCaptureStoreǁfind__mutmut_orig(
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

    def xǁCaptureStoreǁfind__mutmut_1(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = None
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

    def xǁCaptureStoreǁfind__mutmut_2(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = None
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

    def xǁCaptureStoreǁfind__mutmut_3(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = self._by_id[rid]
            if host_regex is not None or not re.search(host_regex, req.host):
                continue
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_4(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = self._by_id[rid]
            if host_regex is None and not re.search(host_regex, req.host):
                continue
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_5(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = self._by_id[rid]
            if host_regex is not None and re.search(host_regex, req.host):
                continue
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_6(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = self._by_id[rid]
            if host_regex is not None and not re.search(None, req.host):
                continue
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_7(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = self._by_id[rid]
            if host_regex is not None and not re.search(host_regex, None):
                continue
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_8(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = self._by_id[rid]
            if host_regex is not None and not re.search(req.host):
                continue
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_9(
        self,
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[StoredRequest]:
        out = []
        for rid in self._order:
            req = self._by_id[rid]
            if host_regex is not None and not re.search(host_regex, ):
                continue
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_10(
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
                break
            if method is not None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_11(
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
            if method is not None or req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_12(
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
            if method is None and req.method != method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_13(
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
            if method is not None and req.method == method:
                continue
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_14(
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
                break
            if status is not None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_15(
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
            if status is not None or req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_16(
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
            if status is None and req.status != status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_17(
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
            if status is not None and req.status == status:
                continue
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_18(
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
                break
            if path_contains is not None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_19(
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
            if path_contains is not None or path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_20(
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
            if path_contains is None and path_contains not in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_21(
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
            if path_contains is not None and path_contains in req.path:
                continue
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_22(
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
                break
            out.append(req)
        return out

    def xǁCaptureStoreǁfind__mutmut_23(
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
            out.append(None)
        return out

    def count(self) -> int:
        return len(self._order)

    @_mutmut_mutated(mutants_xǁCaptureStoreǁstats_summary__mutmut)
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

    def xǁCaptureStoreǁstats_summary__mutmut_orig(self) -> dict:
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

    def xǁCaptureStoreǁstats_summary__mutmut_1(self) -> dict:
        hosts: Dict[str, int] = None
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

    def xǁCaptureStoreǁstats_summary__mutmut_2(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = None
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

    def xǁCaptureStoreǁstats_summary__mutmut_3(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = None
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_4(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = None
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_5(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) - 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_6(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(None, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_7(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, None) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_8(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_9(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, ) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_10(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 1) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_11(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 2
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_12(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = None
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_13(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) - 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_14(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(None, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_15(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, None) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_16(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_17(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, ) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_18(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 1) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_19(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 2
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_20(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = None
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_21(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(None, key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_22(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=None)[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_23(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_24(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), )[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_25(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: None)[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_26(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (+kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_27(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[2], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_28(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[1]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_29(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
        return {
            "count": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_30(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "XXcountXX": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_31(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "COUNT": len(self._order),
            "hosts": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_32(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "XXhostsXX": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_33(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "HOSTS": dict(top_hosts),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_34(self) -> dict:
        hosts: Dict[str, int] = {}
        methods: Dict[str, int] = {}
        for rid in self._order:
            req = self._by_id[rid]
            hosts[req.host] = hosts.get(req.host, 0) + 1
            methods[req.method] = methods.get(req.method, 0) + 1
        top_hosts = sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        return {
            "count": len(self._order),
            "hosts": dict(None),
            "methods": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_35(self) -> dict:
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
            "XXmethodsXX": methods,
        }

    def xǁCaptureStoreǁstats_summary__mutmut_36(self) -> dict:
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
            "METHODS": methods,
        }

    # ---------- write side (used by transform tools) ----------

    @_mutmut_mutated(mutants_xǁCaptureStoreǁadd__mutmut)
    def add(self, request: StoredRequest) -> StoredRequest:
        self._by_id[request.id] = request
        self._order.append(request.id)
        return request

    # ---------- write side (used by transform tools) ----------

    def xǁCaptureStoreǁadd__mutmut_orig(self, request: StoredRequest) -> StoredRequest:
        self._by_id[request.id] = request
        self._order.append(request.id)
        return request

    # ---------- write side (used by transform tools) ----------

    def xǁCaptureStoreǁadd__mutmut_1(self, request: StoredRequest) -> StoredRequest:
        self._by_id[request.id] = None
        self._order.append(request.id)
        return request

    # ---------- write side (used by transform tools) ----------

    def xǁCaptureStoreǁadd__mutmut_2(self, request: StoredRequest) -> StoredRequest:
        self._by_id[request.id] = request
        self._order.append(None)
        return request

    @_mutmut_mutated(mutants_xǁCaptureStoreǁ_update__mutmut)
    def _update(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(request_id)
        updated = replace(req, **changes)
        self._by_id[request_id] = updated
        return updated

    def xǁCaptureStoreǁ_update__mutmut_orig(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(request_id)
        updated = replace(req, **changes)
        self._by_id[request_id] = updated
        return updated

    def xǁCaptureStoreǁ_update__mutmut_1(self, request_id: int, **changes) -> StoredRequest:
        req = None
        updated = replace(req, **changes)
        self._by_id[request_id] = updated
        return updated

    def xǁCaptureStoreǁ_update__mutmut_2(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(None)
        updated = replace(req, **changes)
        self._by_id[request_id] = updated
        return updated

    def xǁCaptureStoreǁ_update__mutmut_3(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(request_id)
        updated = None
        self._by_id[request_id] = updated
        return updated

    def xǁCaptureStoreǁ_update__mutmut_4(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(request_id)
        updated = replace(None, **changes)
        self._by_id[request_id] = updated
        return updated

    def xǁCaptureStoreǁ_update__mutmut_5(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(request_id)
        updated = replace(**changes)
        self._by_id[request_id] = updated
        return updated

    def xǁCaptureStoreǁ_update__mutmut_6(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(request_id)
        updated = replace(req, )
        self._by_id[request_id] = updated
        return updated

    def xǁCaptureStoreǁ_update__mutmut_7(self, request_id: int, **changes) -> StoredRequest:
        req = self.get(request_id)
        updated = replace(req, **changes)
        self._by_id[request_id] = None
        return updated

    @_mutmut_mutated(mutants_xǁCaptureStoreǁmodify_header__mutmut)
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

    def xǁCaptureStoreǁmodify_header__mutmut_orig(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_1(self, request_id: int, name: str, value: str, phase: str = "XXrequestXX") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_2(self, request_id: int, name: str, value: str, phase: str = "REQUEST") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_3(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = None
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_4(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(None)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_5(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = None
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_6(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(None)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_7(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if (phase == "request") and False else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_8(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if (phase == "request") or True else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_9(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase != "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_10(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "XXrequestXX" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_11(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "REQUEST" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_12(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.upper() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_13(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() != name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_14(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.upper()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_15(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = None
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_16(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase != "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_17(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "XXrequestXX":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_18(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "REQUEST":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_19(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(None, headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_20(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=None)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_21(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(headers=headers)
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_22(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, )
        return self._update(request_id, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_23(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(None, response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_24(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, response_headers=None)

    def xǁCaptureStoreǁmodify_header__mutmut_25(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(response_headers=headers)

    def xǁCaptureStoreǁmodify_header__mutmut_26(self, request_id: int, name: str, value: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = dict(req.headers if phase == "request" else req.response_headers)
        # case-insensitive replace: drop any existing casing of the header
        for existing in [k for k in headers if k.lower() == name.lower()]:
            del headers[existing]
        headers[name] = value
        if phase == "request":
            return self._update(request_id, headers=headers)
        return self._update(request_id, )

    @_mutmut_mutated(mutants_xǁCaptureStoreǁremove_header__mutmut)
    def remove_header(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_orig(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_1(self, request_id: int, name: str, phase: str = "XXrequestXX") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_2(self, request_id: int, name: str, phase: str = "REQUEST") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_3(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = None
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_4(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(None)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_5(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = None
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_6(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if (phase == "request") and False else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_7(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if (phase == "request") or True else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_8(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase != "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_9(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "XXrequestXX" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_10(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "REQUEST" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_11(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = None
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_12(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.upper() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_13(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() == name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_14(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.upper()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_15(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase != "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_16(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "XXrequestXX":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_17(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "REQUEST":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_18(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(None, headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_19(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=None)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_20(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(headers=kept)
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_21(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, )
        return self._update(request_id, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_22(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(None, response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_23(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, response_headers=None)

    def xǁCaptureStoreǁremove_header__mutmut_24(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(response_headers=kept)

    def xǁCaptureStoreǁremove_header__mutmut_25(self, request_id: int, name: str, phase: str = "request") -> StoredRequest:
        req = self.get(request_id)
        headers = req.headers if phase == "request" else req.response_headers
        kept = {k: v for k, v in headers.items() if k.lower() != name.lower()}
        if phase == "request":
            return self._update(request_id, headers=kept)
        return self._update(request_id, )

    @_mutmut_mutated(mutants_xǁCaptureStoreǁrewrite_url__mutmut)
    def rewrite_url(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_orig(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_1(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = None
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_2(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(None)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_3(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = None
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_4(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if (host is not None) and False else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_5(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if (host is not None) or True else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_6(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_7(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = None
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_8(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if (path is not None) and False else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_9(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if (path is not None) or True else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_10(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is None else req.path
        return self._update(request_id, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_11(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(None, host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_12(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=None, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_13(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, path=None)

    def xǁCaptureStoreǁrewrite_url__mutmut_14(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(host=new_host, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_15(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, path=new_path)

    def xǁCaptureStoreǁrewrite_url__mutmut_16(self, request_id: int, host: Optional[str] = None, path: Optional[str] = None) -> StoredRequest:
        req = self.get(request_id)
        new_host = host if host is not None else req.host
        new_path = path if path is not None else req.path
        return self._update(request_id, host=new_host, )

    @_mutmut_mutated(mutants_xǁCaptureStoreǁset_body__mutmut)
    def set_body(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_orig(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_1(self, request_id: int, body: str, phase: str = "XXrequestXX") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_2(self, request_id: int, body: str, phase: str = "REQUEST") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_3(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase != "request":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_4(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "XXrequestXX":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_5(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "REQUEST":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_6(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(None, body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_7(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=None)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_8(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(body=body)
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_9(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, )
        return self._update(request_id, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_10(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(None, response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_11(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(request_id, response_body=None)

    def xǁCaptureStoreǁset_body__mutmut_12(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(response_body=body)

    def xǁCaptureStoreǁset_body__mutmut_13(self, request_id: int, body: str, phase: str = "request") -> StoredRequest:
        if phase == "request":
            return self._update(request_id, body=body)
        return self._update(request_id, )

mutants_xǁCaptureStoreǁ__init____mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ__init____mutmut['xǁCaptureStoreǁ__init____mutmut_1'] = CaptureStore.xǁCaptureStoreǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ__init____mutmut['xǁCaptureStoreǁ__init____mutmut_2'] = CaptureStore.xǁCaptureStoreǁ__init____mutmut_2 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁget__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁget__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁget__mutmut['xǁCaptureStoreǁget__mutmut_1'] = CaptureStore.xǁCaptureStoreǁget__mutmut_1 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁlist__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁlist__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁlist__mutmut['xǁCaptureStoreǁlist__mutmut_1'] = CaptureStore.xǁCaptureStoreǁlist__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁlist__mutmut['xǁCaptureStoreǁlist__mutmut_2'] = CaptureStore.xǁCaptureStoreǁlist__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁlist__mutmut['xǁCaptureStoreǁlist__mutmut_3'] = CaptureStore.xǁCaptureStoreǁlist__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁlist__mutmut['xǁCaptureStoreǁlist__mutmut_4'] = CaptureStore.xǁCaptureStoreǁlist__mutmut_4 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁfind__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_1'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_2'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_3'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_4'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_5'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_6'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_7'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_8'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_9'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_10'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_11'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_12'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_13'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_14'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_15'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_16'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_17'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_17 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_18'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_18 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_19'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_19 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_20'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_20 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_21'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_21 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_22'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_22 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁfind__mutmut['xǁCaptureStoreǁfind__mutmut_23'] = CaptureStore.xǁCaptureStoreǁfind__mutmut_23 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁstats_summary__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_1'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_2'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_3'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_4'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_5'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_6'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_7'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_8'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_9'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_10'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_11'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_12'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_13'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_14'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_15'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_16'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_17'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_17 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_18'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_18 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_19'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_19 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_20'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_20 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_21'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_21 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_22'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_22 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_23'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_23 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_24'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_24 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_25'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_25 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_26'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_26 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_27'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_27 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_28'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_28 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_29'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_29 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_30'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_30 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_31'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_31 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_32'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_32 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_33'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_33 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_34'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_34 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_35'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_35 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁstats_summary__mutmut['xǁCaptureStoreǁstats_summary__mutmut_36'] = CaptureStore.xǁCaptureStoreǁstats_summary__mutmut_36 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁadd__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁadd__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁadd__mutmut['xǁCaptureStoreǁadd__mutmut_1'] = CaptureStore.xǁCaptureStoreǁadd__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁadd__mutmut['xǁCaptureStoreǁadd__mutmut_2'] = CaptureStore.xǁCaptureStoreǁadd__mutmut_2 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁ_update__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁ_update__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ_update__mutmut['xǁCaptureStoreǁ_update__mutmut_1'] = CaptureStore.xǁCaptureStoreǁ_update__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ_update__mutmut['xǁCaptureStoreǁ_update__mutmut_2'] = CaptureStore.xǁCaptureStoreǁ_update__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ_update__mutmut['xǁCaptureStoreǁ_update__mutmut_3'] = CaptureStore.xǁCaptureStoreǁ_update__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ_update__mutmut['xǁCaptureStoreǁ_update__mutmut_4'] = CaptureStore.xǁCaptureStoreǁ_update__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ_update__mutmut['xǁCaptureStoreǁ_update__mutmut_5'] = CaptureStore.xǁCaptureStoreǁ_update__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ_update__mutmut['xǁCaptureStoreǁ_update__mutmut_6'] = CaptureStore.xǁCaptureStoreǁ_update__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁ_update__mutmut['xǁCaptureStoreǁ_update__mutmut_7'] = CaptureStore.xǁCaptureStoreǁ_update__mutmut_7 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁmodify_header__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_1'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_2'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_3'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_4'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_5'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_6'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_7'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_8'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_9'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_10'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_11'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_12'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_13'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_14'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_15'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_16'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_17'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_17 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_18'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_18 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_19'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_19 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_20'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_20 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_21'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_21 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_22'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_22 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_23'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_23 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_24'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_24 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_25'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_25 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁmodify_header__mutmut['xǁCaptureStoreǁmodify_header__mutmut_26'] = CaptureStore.xǁCaptureStoreǁmodify_header__mutmut_26 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁremove_header__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_1'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_2'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_3'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_4'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_5'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_6'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_7'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_8'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_9'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_10'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_11'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_12'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_13'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_14'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_15'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_16'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_17'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_17 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_18'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_18 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_19'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_19 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_20'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_20 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_21'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_21 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_22'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_22 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_23'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_23 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_24'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_24 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁremove_header__mutmut['xǁCaptureStoreǁremove_header__mutmut_25'] = CaptureStore.xǁCaptureStoreǁremove_header__mutmut_25 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁrewrite_url__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_1'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_2'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_3'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_4'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_5'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_6'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_7'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_8'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_9'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_10'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_11'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_12'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_13'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_14'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_15'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁrewrite_url__mutmut['xǁCaptureStoreǁrewrite_url__mutmut_16'] = CaptureStore.xǁCaptureStoreǁrewrite_url__mutmut_16 # type: ignore # mutmut generated

mutants_xǁCaptureStoreǁset_body__mutmut['_mutmut_orig'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_1'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_2'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_3'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_4'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_5'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_6'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_7'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_8'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_9'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_10'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_11'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_12'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCaptureStoreǁset_body__mutmut['xǁCaptureStoreǁset_body__mutmut_13'] = CaptureStore.xǁCaptureStoreǁset_body__mutmut_13 # type: ignore # mutmut generated
