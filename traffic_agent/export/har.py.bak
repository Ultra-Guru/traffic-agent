"""HAR 1.2 导出（默认脱敏，对应 SPEC v2.0 §1.5「本地隐私闭环」）。"""

from __future__ import annotations

import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

REDACTED = "[REDACTED]"
SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "proxy-authorization",
    "x-api-key",
    "x-auth-token",
    "x-session-id",
}
SENSITIVE_QUERY_KEYS = {
    "token",
    "access_token",
    "secret",
    "password",
    "signature",
    "api_key",
    "apikey",
    "key",
}


def redact_query(url: str, keys: Optional[set] = None) -> str:
    """对 URL 查询参数中的敏感键脱敏，其余参数原样保留。"""
    keys = SENSITIVE_QUERY_KEYS if keys is None else keys
    parts = urllib.parse.urlsplit(url)
    if not parts.query:
        return url
    pairs = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    kept = []
    changed = False
    for name, value in pairs:
        if name.lower() in keys:
            kept.append((name, REDACTED))
            changed = True
        else:
            kept.append((name, value))
    if not changed:
        return url
    query = urllib.parse.urlencode(kept)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def _request_headers(request: Any) -> Dict[str, str]:
    headers = getattr(request, "headers", None) or {}
    return {str(k): str(v) for k, v in headers.items()}


def _entry(session: Any, redact: bool) -> Optional[Dict[str, Any]]:
    request = getattr(session, "request", None)
    if request is None:
        return None
    headers = _request_headers(request)
    host = str(getattr(request, "host", "") or "")
    target = str(getattr(request, "target", ""))
    url = target if target.startswith(("http://", "https://")) else f"http://{host}{target}"
    if redact:
        url = redact_query(url)
    entry_headers = []
    for name in sorted(headers):
        value = headers[name]
        if redact and name.lower() in SENSITIVE_HEADERS:
            value = REDACTED
        entry_headers.append({"name": name, "value": value})
    query_pairs = urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query, keep_blank_values=True)
    body = getattr(request, "body", b"") or b""
    if not isinstance(body, bytes):
        body = str(body).encode("utf-8")
    entry_request: Dict[str, Any] = {
        "method": str(getattr(request, "method", "GET")),
        "url": url,
        "httpVersion": str(getattr(request, "version", "HTTP/1.1")),
        "headers": entry_headers,
        "queryString": [{"name": n, "value": v} for n, v in query_pairs],
        "headersSize": -1,
        "bodySize": len(body),
    }
    if body:
        mime = headers.get("content-type", "application/octet-stream")
        entry_request["postData"] = {
            "mimeType": mime,
            "text": body.decode("latin-1", "replace"),
        }
    response = getattr(session, "response", None)
    if response is not None:
        resp_headers_map = {str(k): str(v) for k, v in (getattr(response, "headers", None) or {}).items()}
        resp_headers = []
        for name in sorted(resp_headers_map):
            value = resp_headers_map[name]
            if redact and name.lower() in SENSITIVE_HEADERS:
                value = REDACTED
            resp_headers.append({"name": name, "value": value})
        resp_body = getattr(response, "body", b"") or b""
        if not isinstance(resp_body, bytes):
            resp_body = str(resp_body).encode("utf-8")
        entry_response = {
            "status": int(getattr(response, "status", 0)),
            "statusText": str(getattr(response, "reason", "")),
            "httpVersion": str(getattr(response, "version", "HTTP/1.1")),
            "headers": resp_headers,
            "content": {
                "size": len(resp_body),
                "text": resp_body.decode("latin-1", "replace"),
                "mimeType": resp_headers_map.get("content-type", ""),
            },
            "redirectURL": "",
            "headersSize": -1,
            "bodySize": -1,
        }
    else:
        entry_response = {
            "status": 0,
            "statusText": "",
            "httpVersion": "",
            "headers": [],
            "content": {"size": 0, "text": "", "mimeType": ""},
            "redirectURL": "",
            "headersSize": -1,
            "bodySize": -1,
        }
    ts = float(getattr(session, "started_at", 0.0) or 0.0)
    started = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "startedDateTime": started,
        "time": float(getattr(session, "duration_ms", 0.0) or 0.0),
        "request": entry_request,
        "response": entry_response,
        "cache": {},
        "timings": {"send": 1, "wait": 1, "receive": 1},
    }


def export_har(
    sessions: Iterable[Any],
    redact: bool = True,
    creator: str = "traffic-agent",
    version: str = "2.0.0",
) -> Dict[str, Any]:
    """导出 HAR 1.2 结构；无请求的会话跳过。"""
    entries = []
    for session in sessions:
        entry = _entry(session, redact)
        if entry is not None:
            entries.append(entry)
    return {
        "log": {
            "version": "1.2",
            "creator": {"name": creator, "version": version},
            "entries": entries,
        }
    }
