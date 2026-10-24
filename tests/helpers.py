"""共享测试工具：手工构造 TLS ClientHello / DNS 报文。"""

from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple

from traffic_agent.capture.parsers import Http1Response, parse_http1_request
from traffic_agent.session import ConnectionSession


def build_client_hello(
    sni: Optional[str] = "api.example.com",
    alpn: Sequence[bytes] = (b"h2", b"http/1.1"),
    ciphers: Sequence[int] = (0x1301,),
) -> bytes:
    exts = b""
    if sni:
        name = sni.encode()
        sni_entry = b"\x00" + len(name).to_bytes(2, "big") + name
        sni_body = len(sni_entry).to_bytes(2, "big") + sni_entry
        exts += (0).to_bytes(2, "big") + len(sni_body).to_bytes(2, "big") + sni_body
    if alpn:
        protos = b"".join(bytes([len(p)]) + p for p in alpn)
        alpn_body = len(protos).to_bytes(2, "big") + protos
        exts += (16).to_bytes(2, "big") + len(alpn_body).to_bytes(2, "big") + alpn_body
    body = b"\x03\x03" + b"\x11" * 32  # legacy_version + random
    body += b"\x00"  # session_id_len
    cipher_bytes = b"".join(c.to_bytes(2, "big") for c in ciphers)
    body += len(cipher_bytes).to_bytes(2, "big") + cipher_bytes
    body += b"\x01\x00"  # compression: null
    body += len(exts).to_bytes(2, "big") + exts
    handshake = b"\x01" + len(body).to_bytes(3, "big") + body
    return b"\x16\x03\x01" + len(handshake).to_bytes(2, "big") + handshake


def build_dns_query(name: str = "api.example.com", txid: int = 0x1234, flags: int = 0x0100) -> bytes:
    qname = b"".join(bytes([len(label)]) + label.encode() for label in name.split(".")) + b"\x00"
    header = txid.to_bytes(2, "big") + flags.to_bytes(2, "big") + (1).to_bytes(2, "big") + b"\x00" * 6
    return header + qname + (1).to_bytes(2, "big") + (1).to_bytes(2, "big")


def build_request_bytes(
    method: str = "GET",
    target: str = "/path?a=1",
    host: str = "api.example.com",
    headers: Iterable[Tuple[str, str]] = (),
    body: bytes = b"",
) -> bytes:
    lines = [f"{method} {target} HTTP/1.1".encode(), f"Host: {host}".encode()]
    lines.extend(f"{k}: {v}".encode() for k, v in headers)
    return b"\r\n".join(lines) + b"\r\n\r\n" + body


def make_session(
    method: str = "GET",
    host: str = "api.example.com",
    path: str = "/path",
    status: int = 200,
    body: bytes = b"{}",
    started_at: float = 1.0,
    request_headers: Iterable[Tuple[str, str]] = (),
    response_headers: Optional[dict] = None,
) -> ConnectionSession:
    session = ConnectionSession("10.0.0.2", 50000, "93.184.216.34", 443, "tcp")
    session.request = parse_http1_request(build_request_bytes(method, path, host, request_headers, body))
    session.response = Http1Response(
        status=status, reason="OK", version="HTTP/1.1", headers=dict(response_headers or {}), body=body
    )
    session.host = host
    session.started_at = started_at
    return session
