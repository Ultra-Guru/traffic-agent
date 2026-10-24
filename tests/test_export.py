from __future__ import annotations

import struct
import urllib.parse

import pytest

from tests.helpers import make_session
from traffic_agent.export.codegen import shell_quote, to_curl, to_go, to_js, to_python
from traffic_agent.export.har import export_har, redact_query
from traffic_agent.export.pcap import (
    DEFAULT_SNAPLEN,
    LINKTYPE_RAW,
    PCAP_MAGIC,
    PacketRecord,
    build_pcap,
    export_pcap,
    pcap_global_header,
    pcap_record_header,
)
from traffic_agent.export.sslkeylog import (
    KeyLogError,
    export_sslkeylog,
    format_line,
    parse_sslkeylog,
)


class TestHarExport:
    def test_structure(self):
        har = export_har([make_session()])
        log = har["log"]
        assert log["version"] == "1.2"
        assert log["creator"]["name"] == "traffic-agent"
        assert len(log["entries"]) == 1
        entry = log["entries"][0]
        assert entry["request"]["method"] == "GET"
        assert entry["request"]["url"] == "http://api.example.com/path"
        assert entry["response"]["status"] == 200
        assert entry["startedDateTime"].endswith("Z")
        assert entry["request"]["queryString"] == []

    def test_headers_redacted_by_default(self):
        session = make_session(
            request_headers=[
                ("Authorization", "Bearer secret-token"),
                ("X-Custom", "keep-me"),
                ("Cookie", "session=abc"),
            ]
        )
        har = export_har([session])
        headers = {h["name"]: h["value"] for h in har["log"]["entries"][0]["request"]["headers"]}
        assert headers["authorization"] == "[REDACTED]"
        assert headers["cookie"] == "[REDACTED]"
        assert headers["x-custom"] == "keep-me"

    def test_response_headers_redacted(self):
        session = make_session(response_headers={"set-cookie": "sid=1", "x-keep": "ok"})
        har = export_har([session])
        headers = {h["name"]: h["value"] for h in har["log"]["entries"][0]["response"]["headers"]}
        assert headers["set-cookie"] == "[REDACTED]"
        assert headers["x-keep"] == "ok"

    def test_entry_structure_details(self):
        har = export_har([make_session(body=b"")])
        entry = har["log"]["entries"][0]
        assert entry["cache"] == {}
        assert entry["timings"] == {"send": 1, "wait": 1, "receive": 1}
        req = entry["request"]
        assert set(req.keys()) == {
            "method", "url", "httpVersion", "headers", "queryString", "headersSize", "bodySize",
        }
        assert req["headersSize"] == -1
        assert req["bodySize"] == 0
        assert set(entry["response"].keys()) == {
            "status", "statusText", "httpVersion", "headers", "content", "redirectURL", "headersSize", "bodySize",
        }
        assert entry["response"]["redirectURL"] == ""
        assert entry["response"]["bodySize"] == -1
        assert entry["response"]["content"] == {"size": 0, "text": "", "mimeType": ""}
        assert entry["time"] == 0.0

    def test_creator_customization(self):
        har = export_har([make_session()], creator="my-tool", version="9.9.9")
        assert har["log"]["creator"] == {"name": "my-tool", "version": "9.9.9"}

    def test_response_status_text(self):
        session = make_session()
        har = export_har([session])
        assert har["log"]["entries"][0]["response"]["statusText"] == "OK"
        assert har["log"]["entries"][0]["response"]["httpVersion"] == "HTTP/1.1"

    def test_headers_not_redacted_when_disabled(self):
        session = make_session(request_headers=[("Authorization", "Bearer secret-token")])
        har = export_har([session], redact=False)
        headers = {h["name"]: h["value"] for h in har["log"]["entries"][0]["request"]["headers"]}
        assert headers["authorization"] == "Bearer secret-token"

    def test_query_param_redaction(self):
        session = make_session(path="/search?token=abc123&lang=en")
        har = export_har([session])
        url = har["log"]["entries"][0]["request"]["url"]
        decoded = urllib.parse.unquote(url)
        assert "token=[REDACTED]" in decoded
        assert "lang=en" in decoded
        query_pairs = [(q["name"], q["value"]) for q in har["log"]["entries"][0]["request"]["queryString"]]
        assert ("token", "[REDACTED]") in query_pairs
        assert ("lang", "en") in query_pairs

    def test_query_param_no_sensitive_no_change(self):
        session = make_session(path="/search?lang=en")
        har = export_har([session])
        assert har["log"]["entries"][0]["request"]["url"] == "http://api.example.com/search?lang=en"

    def test_post_data_present(self):
        session = make_session(method="POST", body=b'{"k":"v"}', request_headers=[("Content-Type", "application/json")])
        har = export_har([session])
        assert har["log"]["entries"][0]["request"]["postData"]["text"] == '{"k":"v"}'
        assert har["log"]["entries"][0]["request"]["postData"]["mimeType"] == "application/json"
        assert har["log"]["entries"][0]["request"]["bodySize"] == 9

    def test_post_data_default_mime(self):
        session = make_session(method="POST", body=b"plain")
        har = export_har([session])
        assert har["log"]["entries"][0]["request"]["postData"]["mimeType"] == "application/octet-stream"

    def test_sessions_without_request_skipped(self):
        session = make_session()
        session.request = None
        har = export_har([session])
        assert har["log"]["entries"] == []

    def test_response_content(self):
        session = make_session(body=b"hello", response_headers={"content-type": "text/plain"})
        har = export_har([session])
        content = har["log"]["entries"][0]["response"]["content"]
        assert content["text"] == "hello"
        assert content["size"] == 5
        assert content["mimeType"] == "text/plain"

    def test_no_response_placeholder(self):
        session = make_session()
        session.response = None
        har = export_har([session])
        assert har["log"]["entries"][0]["response"]["status"] == 0


class TestRedactQuery:
    def test_sensitive_keys(self):
        for key in ("token", "access_token", "password", "api_key", "KEY"):
            url = redact_query(f"https://x.io/p?{key}=v")
            assert "[REDACTED]" in urllib.parse.unquote(url), key

    def test_no_query(self):
        assert redact_query("https://x.io/p") == "https://x.io/p"


class TestPcapExport:
    def test_global_header_exact_bytes(self):
        header = pcap_global_header()
        assert len(header) == 24
        assert header == struct.pack("<IHHiIII", PCAP_MAGIC, 2, 4, 0, 0, DEFAULT_SNAPLEN, LINKTYPE_RAW)
        assert PCAP_MAGIC == 0xA1B2C3D4
        assert LINKTYPE_RAW == 101

    def test_global_header_custom(self):
        header = pcap_global_header(snaplen=128, linktype=1)
        assert struct.unpack("<IHHiIII", header) == (0xA1B2C3D4, 2, 4, 0, 0, 128, 1)

    def test_global_header_invalid_snaplen(self):
        with pytest.raises(ValueError):
            pcap_global_header(snaplen=0)

    def test_record_header(self):
        header = pcap_record_header(1.5, 10, 20)
        assert struct.unpack("<IIII", header) == (1, 500000, 10, 20)

    def test_record_header_usec_rollover(self):
        header = pcap_record_header(0.9999995, 1, 1)
        sec, usec, _, _ = struct.unpack("<IIII", header)
        assert (sec, usec) == (1, 0)

    def test_record_header_negative_raises(self):
        with pytest.raises(ValueError):
            pcap_record_header(1.0, -1, 1)
        with pytest.raises(ValueError):
            pcap_record_header(-1.0, 1, 1)

    def test_build_pcap_empty(self):
        blob = build_pcap([])
        assert len(blob) == 24

    def test_build_pcap_layout(self):
        records = [PacketRecord(data=b"A" * 10, ts=1.0), PacketRecord(data=b"B" * 5, ts=2.0)]
        blob = build_pcap(records)
        assert len(blob) == 24 + 16 + 10 + 16 + 5
        sec, usec, incl, orig = struct.unpack("<IIII", blob[24:40])
        assert (sec, usec, incl, orig) == (1, 0, 10, 10)

    def test_snaplen_truncates_incl_len(self):
        records = [PacketRecord(data=b"Z" * 30, ts=1.0)]
        blob = build_pcap(records, snaplen=10)
        _, _, incl, orig = struct.unpack("<IIII", blob[24:40])
        assert incl == 10
        assert orig == 30
        assert len(blob) == 24 + 16 + 10

    def test_record_default_orig_len(self):
        record = PacketRecord(data=b"xyz", ts=0.0)
        assert record.orig_len == 3

    def test_export_pcap_from_session_chunks(self):
        from traffic_agent.session import Direction

        session = make_session()
        session.add_bytes(Direction.UPSTREAM, 3, ts=1.0, data=b"abc")
        session.add_bytes(Direction.DOWNSTREAM, 2, ts=1.5, data=b"de")
        blob = export_pcap([session])
        assert len(blob) == 24 + 16 + 3 + 16 + 2


class TestSslkeylogExport:
    def test_format_line(self):
        client_random = bytes(range(32))
        secret = bytes(range(48))
        line = format_line(client_random, secret)
        parts = line.split(" ")
        assert parts[0] == "CLIENT_RANDOM"
        assert parts[1] == client_random.hex()
        assert parts[2] == secret.hex()
        assert len(parts[1]) == 64
        assert len(parts[2]) == 96

    def test_format_line_bad_random_length(self):
        with pytest.raises(KeyLogError):
            format_line(b"\x00" * 31, b"\x00" * 48)

    def test_format_line_bad_secret_length(self):
        with pytest.raises(KeyLogError):
            format_line(b"\x00" * 32, b"\x00" * 47)

    def test_export_dedup_first_wins(self):
        cr1, cr2 = b"\x01" * 32, b"\x02" * 32
        content = export_sslkeylog([(cr1, b"\xAA" * 48), (cr1, b"\xBB" * 48), (cr2, b"\xCC" * 48)])
        lines = content.strip().splitlines()
        assert len(lines) == 2
        assert lines[0].endswith((b"\xAA" * 48).hex())
        assert lines[1].endswith((b"\xCC" * 48).hex())  # 按 random 排序

    def test_export_sorted_by_random(self):
        content = export_sslkeylog([(b"\x02" * 32, b"\xAA" * 48), (b"\x01" * 32, b"\xBB" * 48)])
        lines = content.strip().splitlines()
        assert lines[0].split()[1] == (b"\x01" * 32).hex()

    def test_export_empty(self):
        assert export_sslkeylog([]) == ""

    def test_roundtrip_parse(self):
        pairs = [(b"\x01" * 32, b"\xAA" * 48), (b"\x02" * 32, b"\xBB" * 48)]
        content = export_sslkeylog(pairs)
        parsed = parse_sslkeylog(content)
        assert parsed == sorted(pairs)

    def test_parse_skips_comments_and_blank(self):
        text = "# a comment\n\nCLIENT_RANDOM " + "11" * 32 + " " + "22" * 48 + "\n"
        parsed = parse_sslkeylog(text)
        assert len(parsed) == 1

    def test_parse_malformed_line(self):
        with pytest.raises(KeyLogError):
            parse_sslkeylog("GARBAGE line here")
        with pytest.raises(KeyLogError):
            parse_sslkeylog("CLIENT_RANDOM xyz zz")
        with pytest.raises(KeyLogError):
            parse_sslkeylog("CLIENT_RANDOM " + "11" * 31 + " " + "22" * 48)


class TestCodegen:
    def test_shell_quote_safe_chars(self):
        assert shell_quote("simple-value.1") == "simple-value.1"
        assert shell_quote("a=b:c@d") == "a=b:c@d"

    def test_shell_quote_specials(self):
        assert shell_quote("hello world") == "'hello world'"
        assert shell_quote("it's") == "'it'\"'\"'s'"
        assert shell_quote("") == "''"

    def test_to_curl(self):
        session = make_session(
            method="POST",
            path="/submit?x=1",
            request_headers=[("Authorization", "Bearer t"), ("Content-Type", "application/json")],
            body=b'{"k":1}',
        )
        curl = to_curl(session.request)
        expected = (
            "curl -X POST 'http://api.example.com/submit?x=1' "
            "-H 'authorization: Bearer t' -H 'content-type: application/json' -H 'host: api.example.com' "
            "--data-raw '{\"k\":1}'"
        )
        assert curl == expected

    def test_to_curl_no_body(self):
        session = make_session(method="GET", path="/plain", body=b"")
        assert to_curl(session.request) == "curl -X GET http://api.example.com/plain -H 'host: api.example.com'"

    def test_to_python(self):
        session = make_session(method="DELETE", path="/items/9")
        code = to_python(session.request)
        assert "import requests" in code
        assert "requests.delete(" in code
        assert "'http://api.example.com/items/9'" in code

    def test_to_python_with_headers_and_body(self):
        session = make_session(
            method="POST",
            path="/x",
            request_headers=[("Content-Type", "application/json")],
            body=b"data",
        )
        code = to_python(session.request)
        assert "headers={'host': 'api.example.com', 'content-type': 'application/json'}" in code
        assert "data=b'data'" in code

    def test_to_js(self):
        session = make_session(method="PUT", path="/x", request_headers=[("X-Test", "1")], body=b"payload")
        code = to_js(session.request)
        assert code.startswith('fetch("http://api.example.com/x"')
        assert 'method: "PUT"' in code
        assert '"x-test": "1"' in code
        assert '"payload"' in code

    def test_to_js_minimal(self):
        session = make_session(method="GET", path="/y", body=b"")
        code = to_js(session.request)
        assert code == (
            'fetch("http://api.example.com/y", {\n'
            '  method: "GET",\n'
            '  headers: {"host": "api.example.com"},\n'
            "});"
        )

    def test_to_go(self):
        session = make_session(method="POST", path="/go", request_headers=[("X-Test", "1")], body=b"b")
        code = to_go(session.request)
        assert "package main" in code
        assert 'http.NewRequest("POST", "http://api.example.com/go"' in code
        assert 'strings.NewReader("b")' in code
        assert 'req.Header.Set("x-test", "1")' in code
        assert "http.DefaultClient.Do(req)" in code

    def test_to_go_no_body(self):
        session = make_session(method="GET", path="/g", body=b"")
        code = to_go(session.request)
        assert 'strings.NewReader("")' in code
        assert 'req.Header.Set("host", "api.example.com")' in code
        assert 'req.Header.Set("x-test", "1")' not in code
