"""L1 协议解析器：HTTP/1.x、TLS ClientHello(SNI/ALPN)、DNS、WebSocket、QUIC、HTTP/2、gRPC。

对应 SPEC v2.0 §1.1「抓包与协议」功能对等矩阵。全部为纯函数、无 IO，
是变异验证的重点模块（`mutation-verification` 工作流的 TB1 目标）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ProtocolError(ValueError):
    """协议解析失败。"""


def _u16(data: bytes, offset: int) -> int:
    return (data[offset] << 8) | data[offset + 1]


def _u24(data: bytes, offset: int) -> int:
    return (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]


def _u32(data: bytes, offset: int) -> int:
    return (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]


# --------------------------------------------------------------------------
# HTTP/1.x
# --------------------------------------------------------------------------

HTTP_METHODS = (
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS",
    "TRACE", "CONNECT", "PROPFIND",
)


@dataclass
class Http1Request:
    method: str
    target: str
    version: str
    headers: Dict[str, str]
    body: bytes

    @property
    def path(self) -> str:
        return self.target.split("?", 1)[0]

    @property
    def host(self) -> str:
        return self.headers.get("host", "")

    @property
    def query(self) -> str:
        parts = self.target.split("?", 1)
        return parts[1] if len(parts) == 2 else ""


@dataclass
class Http1Response:
    status: int
    reason: str
    version: str
    headers: Dict[str, str]
    body: bytes


def parse_header_lines(lines: List[bytes]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    for raw in lines:
        if not raw:
            continue
        name, sep, value = raw.partition(b":")
        if not sep:
            raise ProtocolError("malformed header line")
        key = name.decode("latin-1").strip().lower()
        if not key:
            raise ProtocolError("empty header name")
        val = value.decode("latin-1").strip()
        if key in headers:
            headers[key] = headers[key] + ", " + val
        else:
            headers[key] = val
    return headers


def parse_http1_request(data: bytes) -> Http1Request:
    head, sep, body = data.partition(b"\r\n\r\n")
    if not sep:
        raise ProtocolError("missing header terminator")
    lines = head.split(b"\r\n")
    request_line = lines[0].decode("latin-1")
    parts = request_line.split()
    if len(parts) != 3:
        raise ProtocolError("malformed request line")
    method, target, version = parts
    if not method or not target:
        raise ProtocolError("malformed request line")
    if not version.startswith("HTTP/"):
        raise ProtocolError(f"unsupported version: {version}")
    headers = parse_header_lines(lines[1:])
    return Http1Request(method=method, target=target, version=version, headers=headers, body=body)


def parse_http1_response(data: bytes) -> Http1Response:
    head, sep, body = data.partition(b"\r\n\r\n")
    if not sep:
        raise ProtocolError("missing header terminator")
    lines = head.split(b"\r\n")
    status_line = lines[0].decode("latin-1")
    parts = status_line.split(" ", 2)
    if len(parts) < 2:
        raise ProtocolError("malformed status line")
    version = parts[0]
    if not version.startswith("HTTP/"):
        raise ProtocolError(f"unsupported version: {version}")
    try:
        status = int(parts[1])
    except ValueError as exc:
        raise ProtocolError(f"invalid status code: {parts[1]}") from exc
    reason = parts[2] if len(parts) == 3 else ""
    headers = parse_header_lines(lines[1:])
    return Http1Response(status=status, reason=reason, version=version, headers=headers, body=body)


def looks_like_http_request(data: bytes) -> bool:
    first_line = data.split(b"\r\n", 1)[0]
    if not first_line:
        return False
    tokens = first_line.split()
    if len(tokens) != 3:
        return False
    return tokens[0].decode("latin-1", "ignore").upper() in HTTP_METHODS and tokens[2].startswith(b"HTTP/")


# --------------------------------------------------------------------------
# TLS ClientHello（SNI / ALPN）
# --------------------------------------------------------------------------

@dataclass
class ClientHelloInfo:
    sni: Optional[str]
    alpn: List[str]
    legacy_version: str
    random_hex: str
    cipher_count: int


def is_tls_record(data: bytes) -> bool:
    return len(data) >= 6 and data[0] == 0x16


def parse_tls_client_hello(data: bytes) -> ClientHelloInfo:
    if len(data) < 6:
        raise ProtocolError("truncated TLS record")
    if data[0] != 0x16:
        raise ProtocolError("not a handshake record")
    rec_len = _u16(data, 3)
    if len(data) < 5 + rec_len:
        raise ProtocolError("truncated TLS record body")
    if data[5] != 0x01:
        raise ProtocolError("not a ClientHello handshake")
    pos = 9  # record header(5) + handshake type(1) + length(3)
    end = 5 + rec_len
    if pos + 34 > end:  # legacy_version(2) + random(32)
        raise ProtocolError("truncated ClientHello body")
    legacy_version = "0x%04x" % _u16(data, pos)
    random_hex = data[pos + 2 : pos + 34].hex()
    pos += 34
    if pos >= end:
        raise ProtocolError("truncated session id")
    sid_len = data[pos]
    pos += 1 + sid_len
    if pos + 2 > end:
        raise ProtocolError("truncated cipher suites")
    cipher_len = _u16(data, pos)
    pos += 2 + cipher_len
    cipher_count = cipher_len // 2
    if pos >= end:
        raise ProtocolError("truncated compression methods")
    comp_len = data[pos]
    pos += 1 + comp_len
    if pos + 2 > end:
        raise ProtocolError("truncated extensions length")
    ext_total = _u16(data, pos)
    pos += 2
    ext_end = min(pos + ext_total, end)
    sni: Optional[str] = None
    alpn: List[str] = []
    while pos + 4 <= ext_end:
        ext_type = _u16(data, pos)
        ext_len = _u16(data, pos + 2)
        body_start = pos + 4
        body_end = body_start + ext_len
        if body_end > ext_end:
            raise ProtocolError("truncated extension")
        if ext_type == 0x0000 and sni is None:
            # server_name_list: list_len(2) + type(1) + name_len(2) + name
            if ext_len >= 5:
                name_len = _u16(data, body_start + 3)
                name = data[body_start + 5 : body_start + 5 + name_len].decode("latin-1")
                if name:
                    sni = name
        elif ext_type == 0x0010:
            p = body_start + 2
            while p < body_end:
                proto_len = data[p]
                if p + 1 + proto_len > body_end:
                    break
                proto = data[p + 1 : p + 1 + proto_len].decode("latin-1")
                if proto:
                    alpn.append(proto)
                p += 1 + proto_len
        pos = body_end
    return ClientHelloInfo(
        sni=sni,
        alpn=alpn,
        legacy_version=legacy_version,
        random_hex=random_hex,
        cipher_count=cipher_count,
    )


# --------------------------------------------------------------------------
# DNS
# --------------------------------------------------------------------------

@dataclass
class DnsQuestion:
    name: str
    qtype: int
    qclass: int


@dataclass
class DnsMessage:
    txid: int
    is_response: bool
    rcode: int
    questions: List[DnsQuestion]

    @property
    def first_question(self) -> Optional[DnsQuestion]:
        return self.questions[0] if self.questions else None


def parse_dns_message(data: bytes) -> DnsMessage:
    if len(data) < 12:
        raise ProtocolError("truncated DNS header")
    txid = _u16(data, 0)
    flags = _u16(data, 2)
    qdcount = _u16(data, 4)
    is_response = bool(flags & 0x8000)
    rcode = flags & 0x000F
    pos = 12
    questions: List[DnsQuestion] = []
    for _ in range(qdcount):
        labels: List[str] = []
        while True:
            if pos >= len(data):
                raise ProtocolError("truncated DNS question name")
            length = data[pos]
            pos += 1
            if length == 0:
                break
            if length & 0xC0:
                raise ProtocolError("compression pointers are not supported in questions")
            if pos + length > len(data):
                raise ProtocolError("truncated DNS label")
            labels.append(data[pos : pos + length].decode("latin-1"))
            pos += length
        if pos + 4 > len(data):
            raise ProtocolError("truncated DNS question tail")
        qtype = _u16(data, pos)
        qclass = _u16(data, pos + 2)
        pos += 4
        questions.append(DnsQuestion(name=".".join(labels), qtype=qtype, qclass=qclass))
    return DnsMessage(txid=txid, is_response=is_response, rcode=rcode, questions=questions)


# --------------------------------------------------------------------------
# WebSocket
# --------------------------------------------------------------------------

WS_OP_CONT = 0x0
WS_OP_TEXT = 0x1
WS_OP_BINARY = 0x2
WS_OP_CLOSE = 0x8
WS_OP_PING = 0x9
WS_OP_PONG = 0xA

WS_OPCODE_NAMES = {
    0x0: "continuation",
    0x1: "text",
    0x2: "binary",
    0x8: "close",
    0x9: "ping",
    0xA: "pong",
}


@dataclass
class WsFrame:
    fin: bool
    opcode: int
    masked: bool
    payload: bytes

    @property
    def opcode_name(self) -> str:
        return WS_OPCODE_NAMES.get(self.opcode, "unknown")

    @property
    def payload_len(self) -> int:
        return len(self.payload)


def encode_ws_frame(fin: bool, opcode: int, payload: bytes, mask_key: Optional[bytes] = None) -> bytes:
    if mask_key is not None and len(mask_key) != 4:
        raise ProtocolError("mask key must be 4 bytes")
    b0 = (0x80 if fin else 0x00) | (opcode & 0x0F)
    masked = mask_key is not None
    length = len(payload)
    header = bytearray([b0])
    if length < 126:
        header.append((0x80 if masked else 0x00) | length)
    elif length <= 0xFFFF:
        header.append((0x80 if masked else 0x00) | 126)
        header += length.to_bytes(2, "big")
    else:
        header.append((0x80 if masked else 0x00) | 127)
        header += length.to_bytes(8, "big")
    if masked:
        header += mask_key
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    return bytes(header) + payload


def decode_ws_frame(data: bytes) -> WsFrame:
    if len(data) < 2:
        raise ProtocolError("truncated WebSocket frame header")
    b0, b1 = data[0], data[1]
    fin = bool(b0 & 0x80)
    opcode = b0 & 0x0F
    masked = bool(b1 & 0x80)
    length = b1 & 0x7F
    pos = 2
    if length == 126:
        if len(data) < pos + 2:
            raise ProtocolError("truncated WebSocket extended length")
        length = _u16(data, pos)
        pos += 2
    elif length == 127:
        if len(data) < pos + 8:
            raise ProtocolError("truncated WebSocket extended length")
        length = int.from_bytes(data[pos : pos + 8], "big")
        pos += 8
    if masked:
        if len(data) < pos + 4:
            raise ProtocolError("truncated WebSocket mask key")
        mask_key = data[pos : pos + 4]
        pos += 4
    else:
        mask_key = b""
    if len(data) < pos + length:
        raise ProtocolError("truncated WebSocket payload")
    payload = data[pos : pos + length]
    if masked:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    return WsFrame(fin=fin, opcode=opcode, masked=masked, payload=payload)


# --------------------------------------------------------------------------
# QUIC（I9：旁路诚实报告）
# --------------------------------------------------------------------------

def is_quic_initial_packet(data: bytes) -> bool:
    """检测 QUIC 长头 Initial 包。

    VpnService 的 protect() 与 Chrome 等 QUIC 连接池存在已知旁路问题；
    明确标注 QUIC 而非静默丢失（SPEC v2.0 创新 I9）。
    """
    if len(data) < 5:
        return False
    if (data[0] & 0xC0) != 0x40:
        return False
    if data[1:5] == b"\x00\x00\x00\x00":
        return False  # Version Negotiation 包
    return True


# --------------------------------------------------------------------------
# HTTP/2 与 gRPC
# --------------------------------------------------------------------------

H2_FRAME_TYPES = {
    0x0: "DATA",
    0x1: "HEADERS",
    0x2: "PRIORITY",
    0x3: "RST_STREAM",
    0x4: "SETTINGS",
    0x5: "PUSH_PROMISE",
    0x6: "PING",
    0x7: "GOAWAY",
    0x8: "WINDOW_UPDATE",
    0x9: "CONTINUATION",
}


@dataclass
class H2FrameHeader:
    length: int
    type: int
    flags: int
    stream_id: int

    @property
    def type_name(self) -> str:
        return H2_FRAME_TYPES.get(self.type, "UNKNOWN")


def parse_h2_frame_header(data: bytes) -> H2FrameHeader:
    if len(data) < 9:
        raise ProtocolError("truncated HTTP/2 frame header")
    length = int.from_bytes(data[0:3], "big")
    frame_type = data[3]
    flags = data[4]
    stream_id = _u32(data, 5) & 0x7FFFFFFF
    return H2FrameHeader(length=length, type=frame_type, flags=flags, stream_id=stream_id)


@dataclass
class GrpcFrame:
    compressed: bool
    message: bytes

    @property
    def length(self) -> int:
        return len(self.message)


def encode_grpc_frame(message: bytes, compressed: bool = False) -> bytes:
    return bytes([1 if compressed else 0]) + len(message).to_bytes(4, "big") + message


def parse_grpc_frames(data: bytes) -> List[GrpcFrame]:
    frames: List[GrpcFrame] = []
    pos = 0
    while pos < len(data):
        if len(data) - pos < 5:
            raise ProtocolError("truncated gRPC frame header")
        compressed = data[pos] == 1
        length = _u32(data, pos + 1)
        pos += 5
        if len(data) - pos < length:
            raise ProtocolError("truncated gRPC message")
        frames.append(GrpcFrame(compressed=compressed, message=data[pos : pos + length]))
        pos += length
    return frames
