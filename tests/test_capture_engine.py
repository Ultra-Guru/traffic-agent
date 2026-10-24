from __future__ import annotations

import pytest

from tests.helpers import build_client_hello, build_dns_query, build_request_bytes
from traffic_agent import events as ev
from traffic_agent.capture.engine import (
    CAPTURE_CHANNEL,
    CaptureEngine,
    CaptureMode,
    probe_root,
)
from traffic_agent.session import ConnectionSession, Direction, SessionStore, TlsInspectionState


def make_conn(**kwargs):
    base = dict(src_ip="10.0.0.2", src_port=50000, dst_ip="93.184.216.34", dst_port=443)
    base.update(kwargs)
    return ConnectionSession(**base)


class TestProbeRoot:
    def test_no_root(self):
        caps = probe_root()
        assert caps.root_available is False
        assert caps.channels == ()
        assert caps.ebpf_tls == "unavailable"
        assert caps.kernel_version is None
        assert caps.to_dict() == {"root_available": False, "channels": [], "ebpf_tls": "unavailable", "kernel_version": None}

    def test_no_root_explicit_env(self):
        caps = probe_root({"root_available": False, "kernel_version": (5, 15)})
        assert caps.root_available is False

    def test_root_modern_kernel(self):
        caps = probe_root({"root_available": True, "kernel_version": (5, 15)})
        assert caps.root_available is True
        assert caps.channels == ("af_packet", "nfqueue", "tproxy", "ebpf_socket")
        assert len(caps.channels) == 4
        assert "ebpf_socket" in caps.channels
        assert caps.ebpf_tls == "available"
        assert caps.kernel_version == (5, 15)

    def test_root_old_kernel(self):
        caps = probe_root({"root_available": True, "kernel_version": (4, 4)})
        assert caps.ebpf_tls == "unavailable_kernel_too_old"
        assert "ebpf_socket" not in caps.channels
        assert len(caps.channels) == 3

    def test_root_selinux_enforcing(self):
        caps = probe_root({"root_available": True, "kernel_version": (5, 15), "selinux_enforcing": True})
        assert caps.ebpf_tls == "unavailable_selinux"
        assert "ebpf_socket" not in caps.channels

    def test_to_dict_kernel(self):
        caps = probe_root({"root_available": True, "kernel_version": (5, 15)})
        d = caps.to_dict()
        assert d["root_available"] is True
        assert d["kernel_version"] == [5, 15]
        assert d["ebpf_tls"] == "available"


class TestCaptureEngine:
    def _engine(self, mode=CaptureMode.VPN):
        store = SessionStore()
        bus = ev.EventBus()
        engine = CaptureEngine(store, bus, mode=mode)
        return store, bus, engine

    def test_channel_mapping(self):
        assert CAPTURE_CHANNEL[CaptureMode.VPN] == "tun"
        assert CAPTURE_CHANNEL[CaptureMode.ROOT_PACKET] == "af_packet"
        assert CAPTURE_CHANNEL[CaptureMode.ROOT_NFQUEUE] == "nfqueue"
        assert CAPTURE_CHANNEL[CaptureMode.ROOT_EBPF] == "ebpf_socket"

    def test_start_stop_events(self):
        _, bus, engine = self._engine()
        event = engine.start()
        assert event.type == ev.EVENT_CAPTURE_STATE
        assert event.payload["state"] == "started"
        assert event.payload["mode"] == "vpn"
        assert event.payload["channel"] == "tun"
        assert event.payload["root_capabilities"]["root_available"] is False
        stop_event = engine.stop()
        assert stop_event.payload["state"] == "stopped"

    def test_start_twice_raises(self):
        _, _, engine = self._engine()
        engine.start()
        with pytest.raises(RuntimeError):
            engine.start()

    def test_stop_before_start_raises(self):
        _, _, engine = self._engine()
        with pytest.raises(RuntimeError):
            engine.stop()

    def test_ingest_before_start_raises(self):
        store, _, engine = self._engine()
        conn = store.add(make_conn())
        with pytest.raises(RuntimeError):
            engine.ingest(conn, Direction.UPSTREAM, b"data")

    def test_ingest_non_bytes_raises(self):
        store, _, engine = self._engine()
        engine.start()
        conn = store.add(make_conn())
        with pytest.raises(TypeError):
            engine.ingest(conn, Direction.UPSTREAM, "not-bytes")

    def test_ingest_dns(self):
        store, bus, engine = self._engine()
        engine.start()
        conn = store.add(make_conn(protocol="udp", dst_port=53))
        event = engine.ingest(conn, Direction.UPSTREAM, build_dns_query("a.b.c"), ts=1.0)
        assert event.payload["kind"] == "dns"
        assert conn.dns is not None
        assert conn.dns.questions[0].name == "a.b.c"
        assert conn.bytes_up == len(build_dns_query("a.b.c"))

    def test_ingest_dns_malformed(self):
        store, _, engine = self._engine()
        engine.start()
        conn = store.add(make_conn(protocol="udp", dst_port=53))
        event = engine.ingest(conn, Direction.UPSTREAM, b"\x00\x01", ts=1.0)
        assert event.payload["kind"] == "dns_malformed"

    def test_ingest_tls_client_hello(self):
        store, bus, engine = self._engine()
        engine.start()
        conn = store.add(make_conn())
        raw = build_client_hello(sni="secure.example.com")
        event = engine.ingest(conn, Direction.UPSTREAM, raw, ts=1.0)
        assert event.payload["kind"] == "tls_client_hello"
        assert conn.sni == "secure.example.com"
        assert conn.host == "secure.example.com"
        assert event.payload["capture_channel"] == "tun"
        assert event.payload["capture_method"] == "tun"
        assert event.payload["bytes"] == len(raw)
        assert event.payload["session_id"] == conn.session_id

    def test_ingest_http_request(self):
        store, bus, engine = self._engine()
        engine.start()
        conn = store.add(make_conn())
        raw = build_request_bytes("GET", "/v1/users", "api.example.com")
        event = engine.ingest(conn, Direction.UPSTREAM, raw, ts=1.0)
        assert event.payload["kind"] == "http1_request"
        assert conn.host == "api.example.com"
        assert conn.request_count == 1
        assert conn.request.path == "/v1/users"

    def test_ingest_http_response(self):
        store, _, engine = self._engine()
        engine.start()
        conn = store.add(make_conn())
        event = engine.ingest(conn, Direction.DOWNSTREAM, b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nhi", ts=2.0)
        assert event.payload["kind"] == "http1_response"
        assert conn.response.status == 200
        assert conn.response_count == 1

    def test_ingest_http_malformed_response(self):
        store, _, engine = self._engine()
        engine.start()
        conn = store.add(make_conn())
        event = engine.ingest(conn, Direction.DOWNSTREAM, b"HTTP/1.1 abc OK\r\n\r\n", ts=2.0)
        assert event.payload["kind"] == "http1_malformed"

    def test_ingest_quic_initial_marks_bypass(self):
        store, _, engine = self._engine()
        engine.start()
        conn = store.add(make_conn(protocol="udp", dst_port=443))
        raw = b"\x40" + b"\x00\x00\x00\x01" + b"\x00" * 16
        event = engine.ingest(conn, Direction.UPSTREAM, raw, ts=1.0)
        assert event.payload["kind"] == "quic_initial"
        assert conn.quic_bypass is True
        report = CaptureEngine.visibility_report(conn)
        assert len(report) == 1
        assert "QUIC" in report[0]

    def test_ingest_raw(self):
        store, _, engine = self._engine()
        engine.start()
        conn = store.add(make_conn())
        event = engine.ingest(conn, Direction.UPSTREAM, b"\x07\x08\x09", ts=1.0)
        assert event.payload["kind"] == "raw"

    def test_ingest_chunk_recorded(self):
        store, _, engine = self._engine()
        engine.start()
        conn = store.add(make_conn())
        engine.ingest(conn, Direction.UPSTREAM, b"abc", ts=5.0)
        engine.ingest(conn, Direction.DOWNSTREAM, b"de", ts=6.0)
        assert [(c.direction, c.ts, c.data) for c in conn.chunks] == [
            (Direction.UPSTREAM, 5.0, b"abc"),
            (Direction.DOWNSTREAM, 6.0, b"de"),
        ]
        assert conn.bytes_up == 3
        assert conn.bytes_down == 2

    def test_root_mode_channel_in_event(self):
        store, bus, engine = self._engine(mode=CaptureMode.ROOT_EBPF)
        engine.root_capabilities = probe_root({"root_available": True, "kernel_version": (5, 15)})
        event = engine.start()
        assert event.payload["channel"] == "ebpf_socket"
        assert event.payload["root_capabilities"]["ebpf_tls"] == "available"
        conn = store.add(make_conn(protocol="udp", dst_port=443))
        engine.ingest(conn, Direction.UPSTREAM, b"\x40\x00\x00\x00\x01" + b"\x00" * 8, ts=1.0)
        traffic = bus.events(topic=ev.EVENT_TRAFFIC)
        assert traffic[-1].payload["capture_channel"] == "ebpf_socket"

    def test_visibility_report_pinned(self):
        conn = make_conn()
        conn.tls_state = TlsInspectionState.PINNED_BLOCKED
        report = CaptureEngine.visibility_report(conn)
        assert len(report) == 1
        assert "PINNED_BLOCKED" in report[0]

    def test_visibility_report_clean(self):
        conn = make_conn()
        assert CaptureEngine.visibility_report(conn) == []
