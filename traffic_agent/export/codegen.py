"""代码生成导出：cURL / Python(requests) / JS(fetch) / Go(net/http)。

对应 SPEC v2.0 §1.5「复制 cURL」+ 代码生成（支持 Python/JS/Go）。
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict

_SHELL_SAFE = re.compile(r"^[A-Za-z0-9_\-./:=@]+$")


def shell_quote(value: str) -> str:
    """POSIX 单引号规则：安全字符不引用，含特殊字符则单引号包裹。"""
    if value == "":
        return "''"
    if _SHELL_SAFE.fullmatch(value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def _headers(request: Any) -> Dict[str, str]:
    headers = getattr(request, "headers", None) or {}
    return {str(k): str(v) for k, v in headers.items()}


def _url(request: Any) -> str:
    host = str(getattr(request, "host", "") or "")
    target = str(getattr(request, "target", ""))
    if target.startswith(("http://", "https://")):
        return target
    return f"http://{host}{target}"


def _body(request: Any) -> bytes:
    body = getattr(request, "body", b"") or b""
    if not isinstance(body, bytes):
        body = str(body).encode("utf-8")
    return body


def to_curl(request: Any) -> str:
    parts = ["curl", "-X", str(getattr(request, "method", "GET")), shell_quote(_url(request))]
    headers = _headers(request)
    for name in sorted(headers):
        parts.append("-H")
        parts.append(shell_quote(f"{name}: {headers[name]}"))
    body = _body(request)
    if body:
        parts.append("--data-raw")
        parts.append(shell_quote(body.decode("latin-1", "replace")))
    return " ".join(parts)


def to_python(request: Any) -> str:
    method = str(getattr(request, "method", "GET"))
    url = _url(request)
    headers = _headers(request)
    body = _body(request)
    lines = ["import requests", "", f"response = requests.{method.lower()}(", f"    {url!r},"]
    if headers:
        lines.append(f"    headers={headers!r},")
    if body:
        lines.append(f"    data={body!r},")
    lines.append(")")
    return "\n".join(lines)


def to_js(request: Any) -> str:
    method = str(getattr(request, "method", "GET"))
    url = _url(request)
    headers = _headers(request)
    body = _body(request)
    parts = [f"fetch({json.dumps(url)}, {{", f"  method: {json.dumps(method)},"]
    if headers:
        parts.append(f"  headers: {json.dumps(headers, sort_keys=True)},")
    if body:
        parts.append(f"  body: {json.dumps(body.decode('latin-1', 'replace'))},")
    parts.append("});")
    return "\n".join(parts)


def to_go(request: Any) -> str:
    method = str(getattr(request, "method", "GET"))
    url = _url(request)
    headers = _headers(request)
    body = _body(request)
    lines = [
        "package main",
        "",
        "import (",
        '\t"io"',
        '\t"net/http"',
        '\t"strings"',
        ")",
        "",
        "func main() {",
        f"\treq, _ := http.NewRequest({json.dumps(method)}, {json.dumps(url)}, strings.NewReader({json.dumps(body.decode('latin-1', 'replace'))}))",
    ]
    for name in sorted(headers):
        lines.append(f"\treq.Header.Set({json.dumps(name)}, {json.dumps(headers[name])})")
    lines.append("\tresp, _ := http.DefaultClient.Do(req)")
    lines.append("\tdefer resp.Body.Close()")
    lines.append("\t_, _ = io.Copy(io.Discard, resp.Body)")
    lines.append("}")
    return "\n".join(lines)
