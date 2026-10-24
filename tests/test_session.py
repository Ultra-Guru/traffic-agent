from __future__ import annotations

import pytest

from traffic_agent.session import (
    Chunk,
    ConnectionSession,
    Direction,
    SessionStore,
    TlsInspectionState,
    Transport,
)


def make_conn(**kwargs):
    base = dict(src_ip="10.0.0.2", src_port=50000, dst_ip="93.184.216.34", dst_port=443)
    base.update(kwargs)
    return ConnectionSession(**base)


class TestConnectionSession:
    def test_five_tuple(self):
        conn = make_conn()
        assert conn.five_tuple == ("10.0.0.2", 50000, "93.184.216.34", 443, "tcp")

    def test_defaults(self):
        conn = make_conn()
        assert conn.protocol == "tcp"
        assert conn.tls_state is TlsInspectionState.PLAINTEXT
        assert conn.quic_bypass is False
        assert conn.capture_channel == "tun"
        assert conn.bytes_up == 0
        assert conn.bytes_down == 0
        assert conn.chunks == []
        assert conn.ended_at is None

    def test_add_bytes_up_down(self):
        conn = make_conn()
        total = conn.add_bytes(Direction.UPSTREAM, 100, ts=1.0, data=b"a" * 100)
        assert total == 100
        total = conn.add_bytes(Direction.DOWNSTREAM, 40, ts=1.5, data=b"b" * 40)
        assert total == 140
        assert conn.bytes_up == 100
        assert conn.bytes_down == 40
        assert len(conn.chunks) == 2
        chunk = conn.chunks[0]
        assert isinstance(chunk, Chunk)
        assert chunk.direction is Direction.UPSTREAM
        assert chunk.ts == 1.0
        assert chunk.data == b"a" * 100

    def test_add_bytes_negative_size_raises(self):
        conn = make_conn()
        with pytest.raises(ValueError):
            conn.add_bytes(Direction.UPSTREAM, -1)

    def test_add_bytes_default_ts(self):
        conn = make_conn()
        conn.add_bytes(Direction.DOWNSTREAM, 1)
        assert conn.chunks[0].ts > 0

    def test_close(self):
        conn = make_conn()
        ended = conn.close(ts=99.5)
        assert conn.ended_at == 99.5
        assert ended == 99.5

    def test_close_default_ts(self):
        conn = make_conn()
        conn.close()
        assert conn.ended_at >= conn.started_at

    def test_duration_ms(self):
        conn = make_conn()
        conn.started_at = 10.0
        conn.close(ts=10.25)
        assert conn.duration_ms == pytest.approx(250.0)

    def test_duration_ms_open_session(self):
        conn = make_conn()
        conn.started_at = 10.0
        assert conn.duration_ms == 0.0

    def test_fingerprint_stable_and_sensitive(self):
        a = make_conn()
        b = make_conn()
        assert a.fingerprint() == b.fingerprint()
        c = make_conn(sni="other.example.com")
        assert a.fingerprint() != c.fingerprint()
        d = make_conn(dst_port=8443)
        assert a.fingerprint() != d.fingerprint()

    def test_fingerprint_independent_of_session_id_and_time(self):
        a = make_conn()
        b = make_conn()
        a.session_id = "aaa"
        b.session_id = "bbb"
        a.started_at = 1.0
        b.started_at = 999.0
        assert a.fingerprint() == b.fingerprint()

    def test_fingerprint_hex_len(self):
        conn = make_conn()
        assert len(conn.fingerprint()) == 16

    def test_to_dict(self):
        conn = make_conn(app_package="com.demo.app", sni="api.example.com")
        d = conn.to_dict()
        assert d["five_tuple"] == ["10.0.0.2", 50000, "93.184.216.34", 443, "tcp"]
        assert d["app_package"] == "com.demo.app"
        assert d["sni"] == "api.example.com"
        assert d["tls_state"] == "plaintext"
        assert d["fingerprint"] == conn.fingerprint()
        assert d["quic_bypass"] is False


class TestSessionStore:
    def test_add_get(self):
        store = SessionStore()
        conn = store.add(make_conn())
        assert store.get(conn.session_id) is conn
        assert store.get("nope") is None

    def test_all_sorted_by_started_at(self):
        store = SessionStore()
        c3 = store.add(make_conn())
        c1 = store.add(make_conn())
        c2 = store.add(make_conn())
        c1.started_at = 1.0
        c2.started_at = 2.0
        c3.started_at = 3.0
        assert store.all() == [c1, c2, c3]

    def test_count_and_clear(self):
        store = SessionStore()
        store.add(make_conn())
        store.add(make_conn())
        assert store.count() == 2
        store.clear()
        assert store.count() == 0

    def test_query_by_host_case_insensitive(self):
        from tests.helpers import make_session

        store = SessionStore()
        s1 = store.add(make_session(host="api.example.com"))
        store.add(make_session(host="cdn.example.net"))
        assert store.query(host="API.EXAMPLE.COM") == [s1]

    def test_query_by_app_and_tag(self):
        from tests.helpers import make_session

        store = SessionStore()
        s1 = make_session(host="a.com")
        s1.app_package = "com.app.one"
        s1.tags = ["blocked"]
        store.add(s1)
        s2 = store.add(make_session(host="b.com"))
        assert store.query(app="com.app.one") == [s1]
        assert store.query(tag="blocked") == [s1]
        assert store.query(app="com.other") == []

    def test_query_by_method(self):
        from tests.helpers import make_session

        store = SessionStore()
        post = store.add(make_session(method="POST", host="api.com"))
        store.add(make_session(method="GET", host="api.com"))
        assert store.query(host="api.com", method="post") == [post]

    def test_query_limit(self):
        from tests.helpers import make_session

        store = SessionStore()
        for i in range(5):
            s = make_session(host=f"h{i}.com")
            s.started_at = float(i)
            store.add(s)
        assert len(store.query(limit=3)) == 3
        assert len(store.query(limit=0)) == 0
        assert len(store.query()) == 5

    def test_query_negative_limit_raises(self):
        store = SessionStore()
        with pytest.raises(ValueError):
            store.query(limit=-1)


def test_enums():
    assert Transport.TCP.value == "tcp"
    assert Transport.UDP.value == "udp"
    assert Direction.UPSTREAM.value == "up"
    assert Direction.DOWNSTREAM.value == "down"
    assert TlsInspectionState.PINNED_BLOCKED.value == "pinned_blocked"
