"""Read-only tools over the capture store."""

from __future__ import annotations

from typing import List, Optional

from ..store import CaptureStore, StoredRequest


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
