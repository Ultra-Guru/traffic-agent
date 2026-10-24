"""Read-only tools over the capture store."""

from __future__ import annotations

from typing import List, Optional

from ..store import CaptureStore, StoredRequest


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__to_dict__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__to_dict__mutmut)
def _to_dict(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_orig(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_1(req: StoredRequest) -> dict:
    return {
        "XXidXX": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_2(req: StoredRequest) -> dict:
    return {
        "ID": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_3(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "XXhostXX": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_4(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "HOST": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_5(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "XXpathXX": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_6(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "PATH": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_7(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "XXmethodXX": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_8(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "METHOD": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_9(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "XXstatusXX": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_10(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "STATUS": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_11(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "XXrequest_headersXX": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_12(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "REQUEST_HEADERS": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_13(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(None),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_14(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "XXresponse_headersXX": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_15(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "RESPONSE_HEADERS": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_16(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(None),
        "body": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_17(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "XXbodyXX": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_18(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "BODY": req.body,
        "response_body": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_19(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "XXresponse_bodyXX": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_20(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "RESPONSE_BODY": req.response_body,
        "timestamp_ms": req.timestamp_ms,
    }


def x__to_dict__mutmut_21(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "XXtimestamp_msXX": req.timestamp_ms,
    }


def x__to_dict__mutmut_22(req: StoredRequest) -> dict:
    return {
        "id": req.id,
        "host": req.host,
        "path": req.path,
        "method": req.method,
        "status": req.status,
        "request_headers": dict(req.headers),
        "response_headers": dict(req.response_headers),
        "body": req.body,
        "response_body": req.response_body,
        "TIMESTAMP_MS": req.timestamp_ms,
    }

mutants_x__to_dict__mutmut['_mutmut_orig'] = x__to_dict__mutmut_orig # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_1'] = x__to_dict__mutmut_1 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_2'] = x__to_dict__mutmut_2 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_3'] = x__to_dict__mutmut_3 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_4'] = x__to_dict__mutmut_4 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_5'] = x__to_dict__mutmut_5 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_6'] = x__to_dict__mutmut_6 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_7'] = x__to_dict__mutmut_7 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_8'] = x__to_dict__mutmut_8 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_9'] = x__to_dict__mutmut_9 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_10'] = x__to_dict__mutmut_10 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_11'] = x__to_dict__mutmut_11 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_12'] = x__to_dict__mutmut_12 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_13'] = x__to_dict__mutmut_13 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_14'] = x__to_dict__mutmut_14 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_15'] = x__to_dict__mutmut_15 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_16'] = x__to_dict__mutmut_16 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_17'] = x__to_dict__mutmut_17 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_18'] = x__to_dict__mutmut_18 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_19'] = x__to_dict__mutmut_19 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_20'] = x__to_dict__mutmut_20 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_21'] = x__to_dict__mutmut_21 # type: ignore # mutmut generated
mutants_x__to_dict__mutmut['x__to_dict__mutmut_22'] = x__to_dict__mutmut_22 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_register_capture_tools__mutmut)
def register_capture_tools(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_orig(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_1(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 1) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_2(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_3(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if (limit is not None) and False else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_4(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if (limit is not None) or True else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_5(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(None) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_6(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_7(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = None
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_8(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(None)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_9(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(None) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_10(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=None, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_11(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=None)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_12(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_13(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, )]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_14(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(None)

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_15(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(None))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_16(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(None)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_17(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_18(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if (status is not None) and False else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_19(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if (status is not None) or True else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_20(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(None) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_21(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_22(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(None)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_23(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=None,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_24(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=None,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_25(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=None,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_26(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=None,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_27(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_28(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_29(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_30(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_31(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.rfind(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_32(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register(None, list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_33(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", None, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_34(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, None)
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_35(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register(list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_36(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_37(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, )
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_38(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("XXlist_requestsXX", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_39(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("LIST_REQUESTS", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_40(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "XXlist captured requests (limit, offset)XX")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_41(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "LIST CAPTURED REQUESTS (LIMIT, OFFSET)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_42(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register(None, read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_43(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", None, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_44(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, None)
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_45(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register(read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_46(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_47(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, )
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_48(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("XXread_requestXX", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_49(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("READ_REQUEST", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_50(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "XXread one captured exchange by idXX")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_51(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "READ ONE CAPTURED EXCHANGE BY ID")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_52(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register(None, filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_53(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", None, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_54(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, None)
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_55(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register(filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_56(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_57(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, )
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_58(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("XXfilter_requestsXX", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_59(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("FILTER_REQUESTS", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_60(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "XXsearch captures (host_regex, method, status, path_contains)XX")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_61(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "SEARCH CAPTURES (HOST_REGEX, METHOD, STATUS, PATH_CONTAINS)")
    registry.register("stats_summary", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_62(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register(None, stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_63(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", None, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_64(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, None)


def x_register_capture_tools__mutmut_65(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register(stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_66(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", "aggregate stats over the current store")


def x_register_capture_tools__mutmut_67(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, )


def x_register_capture_tools__mutmut_68(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("XXstats_summaryXX", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_69(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("STATS_SUMMARY", stats_summary, "aggregate stats over the current store")


def x_register_capture_tools__mutmut_70(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "XXaggregate stats over the current storeXX")


def x_register_capture_tools__mutmut_71(registry, store: CaptureStore) -> None:
    def list_requests(limit: Optional[int] = None, offset: int = 0) -> List[dict]:
        # bridge params arrive as strings; coerce before use
        effective_limit = int(limit) if limit is not None else None
        effective_offset = int(offset)
        return [_to_dict(r) for r in store.list(limit=effective_limit, offset=effective_offset)]

    def read_request(request_id: int) -> dict:
        return _to_dict(store.get(int(request_id)))

    def filter_requests(
        host_regex: Optional[str] = None,
        method: Optional[str] = None,
        status: Optional[int] = None,
        path_contains: Optional[str] = None,
    ) -> List[dict]:
        effective_status = int(status) if status is not None else None
        return [
            _to_dict(r)
            for r in store.find(
                host_regex=host_regex,
                method=method,
                status=effective_status,
                path_contains=path_contains,
            )
        ]

    def stats_summary() -> dict:
        return store.stats_summary()

    registry.register("list_requests", list_requests, "list captured requests (limit, offset)")
    registry.register("read_request", read_request, "read one captured exchange by id")
    registry.register("filter_requests", filter_requests, "search captures (host_regex, method, status, path_contains)")
    registry.register("stats_summary", stats_summary, "AGGREGATE STATS OVER THE CURRENT STORE")

mutants_x_register_capture_tools__mutmut['_mutmut_orig'] = x_register_capture_tools__mutmut_orig # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_1'] = x_register_capture_tools__mutmut_1 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_2'] = x_register_capture_tools__mutmut_2 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_3'] = x_register_capture_tools__mutmut_3 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_4'] = x_register_capture_tools__mutmut_4 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_5'] = x_register_capture_tools__mutmut_5 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_6'] = x_register_capture_tools__mutmut_6 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_7'] = x_register_capture_tools__mutmut_7 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_8'] = x_register_capture_tools__mutmut_8 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_9'] = x_register_capture_tools__mutmut_9 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_10'] = x_register_capture_tools__mutmut_10 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_11'] = x_register_capture_tools__mutmut_11 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_12'] = x_register_capture_tools__mutmut_12 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_13'] = x_register_capture_tools__mutmut_13 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_14'] = x_register_capture_tools__mutmut_14 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_15'] = x_register_capture_tools__mutmut_15 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_16'] = x_register_capture_tools__mutmut_16 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_17'] = x_register_capture_tools__mutmut_17 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_18'] = x_register_capture_tools__mutmut_18 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_19'] = x_register_capture_tools__mutmut_19 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_20'] = x_register_capture_tools__mutmut_20 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_21'] = x_register_capture_tools__mutmut_21 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_22'] = x_register_capture_tools__mutmut_22 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_23'] = x_register_capture_tools__mutmut_23 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_24'] = x_register_capture_tools__mutmut_24 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_25'] = x_register_capture_tools__mutmut_25 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_26'] = x_register_capture_tools__mutmut_26 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_27'] = x_register_capture_tools__mutmut_27 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_28'] = x_register_capture_tools__mutmut_28 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_29'] = x_register_capture_tools__mutmut_29 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_30'] = x_register_capture_tools__mutmut_30 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_31'] = x_register_capture_tools__mutmut_31 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_32'] = x_register_capture_tools__mutmut_32 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_33'] = x_register_capture_tools__mutmut_33 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_34'] = x_register_capture_tools__mutmut_34 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_35'] = x_register_capture_tools__mutmut_35 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_36'] = x_register_capture_tools__mutmut_36 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_37'] = x_register_capture_tools__mutmut_37 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_38'] = x_register_capture_tools__mutmut_38 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_39'] = x_register_capture_tools__mutmut_39 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_40'] = x_register_capture_tools__mutmut_40 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_41'] = x_register_capture_tools__mutmut_41 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_42'] = x_register_capture_tools__mutmut_42 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_43'] = x_register_capture_tools__mutmut_43 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_44'] = x_register_capture_tools__mutmut_44 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_45'] = x_register_capture_tools__mutmut_45 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_46'] = x_register_capture_tools__mutmut_46 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_47'] = x_register_capture_tools__mutmut_47 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_48'] = x_register_capture_tools__mutmut_48 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_49'] = x_register_capture_tools__mutmut_49 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_50'] = x_register_capture_tools__mutmut_50 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_51'] = x_register_capture_tools__mutmut_51 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_52'] = x_register_capture_tools__mutmut_52 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_53'] = x_register_capture_tools__mutmut_53 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_54'] = x_register_capture_tools__mutmut_54 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_55'] = x_register_capture_tools__mutmut_55 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_56'] = x_register_capture_tools__mutmut_56 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_57'] = x_register_capture_tools__mutmut_57 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_58'] = x_register_capture_tools__mutmut_58 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_59'] = x_register_capture_tools__mutmut_59 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_60'] = x_register_capture_tools__mutmut_60 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_61'] = x_register_capture_tools__mutmut_61 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_62'] = x_register_capture_tools__mutmut_62 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_63'] = x_register_capture_tools__mutmut_63 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_64'] = x_register_capture_tools__mutmut_64 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_65'] = x_register_capture_tools__mutmut_65 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_66'] = x_register_capture_tools__mutmut_66 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_67'] = x_register_capture_tools__mutmut_67 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_68'] = x_register_capture_tools__mutmut_68 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_69'] = x_register_capture_tools__mutmut_69 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_70'] = x_register_capture_tools__mutmut_70 # type: ignore # mutmut generated
mutants_x_register_capture_tools__mutmut['x_register_capture_tools__mutmut_71'] = x_register_capture_tools__mutmut_71 # type: ignore # mutmut generated
