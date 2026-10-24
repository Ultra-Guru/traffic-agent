from __future__ import annotations

import pytest

from tests.helpers import build_client_hello, build_dns_query, build_request_bytes
from traffic_agent.capture import parsers
from traffic_agent.capture.parsers import (
    ProtocolError,
    decode_ws_frame,
    encode_grpc_frame,
    encode_ws_frame,
    is_quic_initial_packet,
    is_tls_record,
    looks_like_http_request,
    parse_dns_message,
    parse_grpc_frames,
    parse_h2_frame_header,
    parse_header_lines,
    parse_http1_request,
    parse_http1_response,
    parse_tls_client_hello,
)


# ---------------------------------------------------------------------------
# HTTP/1.x
# ---------------------------------------------------------------------------

class TestHttp1Request:
    def test_basic(self):
        data = build_request_bytes("POST", "/submit?x=1", "api.example.com", [("Content-Type", "application/json")], b'{"k":1}')
        req = parse_http1_request(data)
        assert req.method == "POST"
        assert req.target == "/submit?x=1"
        assert req.version == "HTTP/1.1"
        assert req.headers == {"host": "api.example.com", "content-type": "application/json"}
        assert req.body == b'{"k":1}'

    def test_path_query_properties(self):
        req = parse_http1_request(build_request_bytes("GET", "/a/b?x=1&y=2", "h.io"))
        assert req.path == "/a/b"
        assert req.query == "x=1&y=2"
        assert req.host == "h.io"
        req2 = parse_http1_request(build_request_bytes("GET", "/plain", "h.io"))
        assert req2.path == "/plain"
        assert req2.query == ""

    def test_duplicate_headers_joined(self):
        data = b"GET / HTTP/1.1\r\nHost: h.io\r\nX-Test: a\r\nX-Test: b\r\n\r\n"
        req = parse_http1_request(data)
        assert req.headers["x-test"] == "a, b"

    def test_missing_terminator_raises(self):
        with pytest.raises(ProtocolError):
            parse_http1_request(b"GET / HTTP/1.1\r\nHost: h.io\r\n")

    def test_malformed_request_line(self):
        with pytest.raises(ProtocolError):
            parse_http1_request(b"GET /\r\nHost: h.io\r\n\r\n")

    def test_non_http_version_raises(self):
        with pytest.raises(ProtocolError):
            parse_http1_request(b"GET / WEIRD/1.1\r\nHost: h.io\r\n\r\n")

    def test_header_without_colon_raises(self):
        with pytest.raises(ProtocolError):
            parse_http1_request(b"GET / HTTP/1.1\r\nBrokenHeader\r\n\r\n")

    def test_empty_header_name_raises(self):
        with pytest.raises(ProtocolError):
            parse_header_lines([b": value"])

    def test_empty_header_line_ignored(self):
        assert parse_header_lines([b""]) == {}

    def test_header_value_stripped(self):
        headers = parse_header_lines([b"Host:   h.io   "])
        assert headers == {"host": "h.io"}


class TestHttp1Response:
    def test_basic(self):
        data = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<body>"
        resp = parse_http1_response(data)
        assert resp.status == 404
        assert resp.reason == "Not Found"
        assert resp.version == "HTTP/1.1"
        assert resp.headers == {"content-type": "text/html"}
        assert resp.body == b"<body>"

    def test_status_line_without_reason(self):
        resp = parse_http1_response(b"HTTP/1.1 204\r\n\r\n")
        assert resp.status == 204
        assert resp.reason == ""

    def test_missing_terminator_raises(self):
        with pytest.raises(ProtocolError):
            parse_http1_response(b"HTTP/1.1 200 OK\r\n")

    def test_malformed_status_line_raises(self):
        with pytest.raises(ProtocolError):
            parse_http1_response(b"OK\r\n\r\n")

    def test_non_numeric_status_raises(self):
        with pytest.raises(ProtocolError):
            parse_http1_response(b"HTTP/1.1 abc OK\r\n\r\n")

    def test_non_http_version_raises(self):
        with pytest.raises(ProtocolError):
            parse_http1_response(b"FTP/1.1 200 OK\r\n\r\n")


class TestLooksLikeHttpRequest:
    def test_positive(self):
        assert looks_like_http_request(build_request_bytes()) is True
        assert looks_like_http_request(build_request_bytes("PROPFIND", "/d", "h")) is True

    def test_negative(self):
        assert looks_like_http_request(b"FOO / HTTP/1.1\r\n\r\n") is False
        assert looks_like_http_request(b"GET /\r\n") is False
        assert looks_like_http_request(b"") is False
        assert looks_like_http_request(b"GET / FTP/1.1\r\n\r\n") is False


# ---------------------------------------------------------------------------
# TLS ClientHello
# ---------------------------------------------------------------------------

class TestTlsClientHello:
    def test_parse_sni_alpn(self):
        info = parse_tls_client_hello(build_client_hello(sni="cdn.example.org"))
        assert info.sni == "cdn.example.org"
        assert info.alpn == ["h2", "http/1.1"]
        assert info.legacy_version == "0x0303"
        assert len(info.random_hex) == 64
        assert info.cipher_count == 1

    def test_no_sni(self):
        info = parse_tls_client_hello(build_client_hello(sni=None))
        assert info.sni is None

    def test_no_alpn(self):
        info = parse_tls_client_hello(build_client_hello(alpn=()))
        assert info.alpn == []

    def test_multiple_ciphers(self):
        info = parse_tls_client_hello(build_client_hello(ciphers=(0x1301, 0x1302, 0x1303)))
        assert info.cipher_count == 3

    def test_is_tls_record(self):
        assert is_tls_record(build_client_hello()) is True
        assert is_tls_record(b"\x17\x03\x03\x00\x01\x00") is False
        assert is_tls_record(b"\x16\x03\x01\x00") is False

    def test_truncated_raises(self):
        with pytest.raises(ProtocolError):
            parse_tls_client_hello(build_client_hello()[:10])

    def test_not_handshake_raises(self):
        with pytest.raises(ProtocolError):
            parse_tls_client_hello(b"\x16\x03\x01\x00\x01\x00")

    def test_not_record_raises(self):
        with pytest.raises(ProtocolError):
            parse_tls_client_hello(b"\x17\x03\x03\x00\x05\x01\x00\x00\x00\x00")

    def test_record_length_mismatch_raises(self):
        raw = build_client_hello()
        # 把 record 长度字段改大 → body 截断
        tampered = bytearray(raw)
        tampered[3:5] = (9999).to_bytes(2, "big")
        with pytest.raises(ProtocolError):
            parse_tls_client_hello(bytes(tampered))


# ---------------------------------------------------------------------------
# DNS
# ---------------------------------------------------------------------------

class TestDns:
    def test_query(self):
        msg = parse_dns_message(build_dns_query("api.example.com", txid=0xABCD))
        assert msg.txid == 0xABCD
        assert msg.is_response is False
        assert msg.rcode == 0
        assert len(msg.questions) == 1
        q = msg.questions[0]
        assert q.name == "api.example.com"
        assert q.qtype == 1
        assert q.qclass == 1
        assert msg.first_question is q

    def test_response_flag(self):
        msg = parse_dns_message(build_dns_query(flags=0x8183))
        assert msg.is_response is True
        assert msg.rcode == 3

    def test_no_questions(self):
        msg = parse_dns_message(b"\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        assert msg.questions == []
        assert msg.first_question is None

    def test_truncated_header_raises(self):
        with pytest.raises(ProtocolError):
            parse_dns_message(b"\x00\x01")

    def test_truncated_name_raises(self):
        raw = build_dns_query("a.b")
        with pytest.raises(ProtocolError):
            parse_dns_message(raw[: len(raw) - 6])

    def test_truncated_tail_raises(self):
        raw = build_dns_query("a.b")
        with pytest.raises(ProtocolError):
            parse_dns_message(raw[: len(raw) - 2])

    def test_compression_pointer_raises(self):
        msg = b"\x00\x01\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00" + b"\xc0\x0c" + b"\x00\x01" + b"\x00\x01"
        with pytest.raises(ProtocolError):
            parse_dns_message(msg)


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

class TestWebSocket:
    def test_roundtrip_unmasked_text(self):
        frame_bytes = encode_ws_frame(True, 0x1, b"Hello")
        frame = decode_ws_frame(frame_bytes)
        assert frame.fin is True
        assert frame.opcode == 0x1
        assert frame.masked is False
        assert frame.payload == b"Hello"
        assert frame.payload_len == 5
        assert frame.opcode_name == "text"

    def test_roundtrip_masked(self):
        frame_bytes = encode_ws_frame(False, 0x2, b"\x01\x02\x03\x04\x05", mask_key=b"\xAA\xBB\xCC\xDD")
        frame = decode_ws_frame(frame_bytes)
        assert frame.masked is True
        assert frame.fin is False
        assert frame.payload == b"\x01\x02\x03\x04\x05"
        assert frame.opcode_name == "binary"
        # 掩码确实生效：密文与明文不同
        assert frame_bytes[2:6] != b"\x01\x02\x03\x04"

    def test_length_boundary_125(self):
        payload = b"x" * 125
        frame_bytes = encode_ws_frame(True, 0x1, payload)
        # 2 字节头（无扩展长度）
        assert len(frame_bytes) == 2 + 125
        assert decode_ws_frame(frame_bytes).payload == payload

    def test_length_boundary_126(self):
        payload = b"x" * 126
        frame_bytes = encode_ws_frame(True, 0x1, payload)
        # 2 字节头 + 2 字节扩展长度
        assert len(frame_bytes) == 4 + 126
        assert decode_ws_frame(frame_bytes).payload == payload

    def test_length_64bit(self):
        payload = b"y" * 70000
        frame_bytes = encode_ws_frame(True, 0x2, payload)
        assert len(frame_bytes) == 10 + 70000
        assert decode_ws_frame(frame_bytes).payload == payload

    def test_opcode_names(self):
        assert decode_ws_frame(encode_ws_frame(True, 0x8, b"")).opcode_name == "close"
        assert decode_ws_frame(encode_ws_frame(True, 0x9, b"")).opcode_name == "ping"
        assert decode_ws_frame(encode_ws_frame(True, 0xA, b"")).opcode_name == "pong"
        assert decode_ws_frame(encode_ws_frame(True, 0x0, b"")).opcode_name == "continuation"
        assert decode_ws_frame(encode_ws_frame(True, 0xF, b"")).opcode_name == "unknown"

    def test_invalid_mask_key_raises(self):
        with pytest.raises(ProtocolError):
            encode_ws_frame(True, 0x1, b"data", mask_key=b"\x01\x02")

    def test_truncated_header_raises(self):
        with pytest.raises(ProtocolError):
            decode_ws_frame(b"\x81")

    def test_truncated_payload_raises(self):
        frame_bytes = encode_ws_frame(True, 0x1, b"Hello")
        with pytest.raises(ProtocolError):
            decode_ws_frame(frame_bytes[:5])

    def test_truncated_masked_raises(self):
        frame_bytes = encode_ws_frame(True, 0x1, b"Hello", mask_key=b"\x01\x02\x03\x04")
        with pytest.raises(ProtocolError):
            decode_ws_frame(frame_bytes[:5])


# ---------------------------------------------------------------------------
# QUIC
# ---------------------------------------------------------------------------

class TestQuic:
    def test_initial_detected(self):
        assert is_quic_initial_packet(b"\x40" + b"\x00\x00\x00\x01" + b"\x00" * 16) is True

    def test_short_header_not_detected(self):
        assert is_quic_initial_packet(b"\x00\x00\x00\x00\x01" + b"\x00" * 8) is False

    def test_version_negotiation_not_initial(self):
        assert is_quic_initial_packet(b"\x40" + b"\x00\x00\x00\x00" + b"\x00" * 8) is False

    def test_too_short(self):
        assert is_quic_initial_packet(b"\x40\x00") is False
        assert is_quic_initial_packet(b"") is False


# ---------------------------------------------------------------------------
# HTTP/2 与 gRPC
# ---------------------------------------------------------------------------

class TestHttp2:
    def test_header_fields(self):
        data = (0x010203).to_bytes(3, "big") + bytes([0x4, 0x01]) + (0x80000007).to_bytes(4, "big")
        header = parse_h2_frame_header(data)
        assert header.length == 0x010203
        assert header.type == 4
        assert header.flags == 0x01
        assert header.stream_id == 7  # R bit 被剥离
        assert header.type_name == "SETTINGS"

    def test_type_names(self):
        for type_id, name in [(0x0, "DATA"), (0x1, "HEADERS"), (0x3, "RST_STREAM"), (0x6, "PING"), (0x7, "GOAWAY"), (0x9, "CONTINUATION"), (0xF, "UNKNOWN")]:
            data = (0).to_bytes(3, "big") + bytes([type_id, 0]) + (0).to_bytes(4, "big")
            assert parse_h2_frame_header(data).type_name == name

    def test_truncated_raises(self):
        with pytest.raises(ProtocolError):
            parse_h2_frame_header(b"\x00\x00")


class TestGrpc:
    def test_roundtrip_single(self):
        encoded = encode_grpc_frame(b"hello", compressed=False)
        assert encoded == b"\x00" + (5).to_bytes(4, "big") + b"hello"
        frames = parse_grpc_frames(encoded)
        assert len(frames) == 1
        assert frames[0].compressed is False
        assert frames[0].message == b"hello"
        assert frames[0].length == 5

    def test_roundtrip_multiple_and_compressed(self):
        data = encode_grpc_frame(b"one") + encode_grpc_frame(b"", compressed=True) + encode_grpc_frame(b"three")
        frames = parse_grpc_frames(data)
        assert [f.message for f in frames] == [b"one", b"", b"three"]
        assert [f.compressed for f in frames] == [False, True, False]

    def test_empty_input(self):
        assert parse_grpc_frames(b"") == []

    def test_truncated_header_raises(self):
        with pytest.raises(ProtocolError):
            parse_grpc_frames(b"\x00\x00\x00")

    def test_truncated_message_raises(self):
        with pytest.raises(ProtocolError):
            parse_grpc_frames(b"\x00" + (5).to_bytes(4, "big") + b"abc")


def test_protocol_error_is_value_error():
    assert issubclass(ProtocolError, ValueError)
