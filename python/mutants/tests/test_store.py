import pytest

from traffic_agent.store import CaptureStore, StoredRequest, UnknownRequest


def make_store(n=3):
    s = CaptureStore()
    for i in range(n):
        s.add(StoredRequest(host=f"h{i}.example.com", path=f"/p{i}", method="GET",
                            status=200 + i % 100, timestamp_ms=1000 + i))
    return s


def test_add_assigns_unique_ids():
    s = make_store(3)
    ids = [r.id for r in s.list()]
    assert len(set(ids)) == 3


def test_get_returns_the_stored_request():
    s = make_store(2)
    got = s.get(s.list()[0].id)
    assert got.host == "h0.example.com"


def test_get_unknown_raises():
    with pytest.raises(UnknownRequest) as exc:
        CaptureStore().get(4242)
    assert exc.value.request_id == 4242


def test_list_respects_limit_and_offset():
    s = make_store(5)
    assert len(s.list(limit=2)) == 2
    assert [r.host for r in s.list(limit=2, offset=2)] == ["h2.example.com", "h3.example.com"]


def test_find_by_host_regex():
    s = make_store(3)
    found = s.find(host_regex=r"h[12]\.example\.com")
    assert {r.host for r in found} == {"h1.example.com", "h2.example.com"}


def test_find_by_method_and_status():
    s = make_store(3)
    assert len(s.find(method="GET")) == 3
    assert len(s.find(method="POST")) == 0
    assert all(r.status == 200 for r in s.find(status=200))


def test_find_by_path_contains():
    s = make_store(3)
    assert len(s.find(path_contains="p1")) == 1
    assert s.find(path_contains="zzz") == []


def test_stats_summary():
    s = make_store(4)
    s.add(StoredRequest(host="h0.example.com", path="/again", method="GET"))
    stats = s.stats_summary()
    assert stats["count"] == 5
    assert stats["hosts"]["h0.example.com"] == 2
    assert stats["methods"] == {"GET": 5}


def test_stats_summary_orders_top_hosts_by_request_count():
    s = CaptureStore()
    for i in range(6):
        s.add(StoredRequest(host=f"host{i}.io", path="/"))
    for _ in range(3):
        s.add(StoredRequest(host="busy.io", path="/"))
    for _ in range(2):
        s.add(StoredRequest(host="mid.io", path="/"))
    stats = s.stats_summary()
    hosts = list(stats["hosts"].items())
    # busy.io leads, then mid.io, then the single-request hosts alphabetically
    assert hosts[0][0] == "busy.io"
    assert hosts[0][1] == 3
    assert hosts[1][0] == "mid.io"
    assert hosts[1][1] == 2
    # top list is capped at five entries
    assert len(hosts) == 5


def test_modify_header_replaces_case_insensitively(store):
    target = store.list()[0]
    updated = store.modify_header(target.id, "accept", "text/plain")
    # full-dict assertion catches phase mix-ups (mutant killing)
    assert updated.headers == {"accept": "text/plain", "X-Api": "1"}


def test_modify_header_on_response_phase(store):
    target = store.list()[0]
    updated = store.modify_header(target.id, "X-Cache", "hit", phase="response")
    assert updated.response_headers == {"Content-Type": "application/json", "X-Cache": "hit"}
    # request headers must be untouched by a response-phase rewrite
    assert updated.headers == {"Accept": "application/json", "X-Api": "1"}


def test_remove_header(store):
    target = store.list()[0]
    updated = store.remove_header(target.id, "x-API")
    assert updated.headers == {"Accept": "application/json"}


def test_rewrite_url_partial(store):
    target = store.list()[1]
    updated = store.rewrite_url(target.id, path="/assets/new.js")
    assert updated.host == "cdn.example.com"
    assert updated.path == "/assets/new.js"
    updated2 = store.rewrite_url(target.id, host="mirror.example.net")
    assert updated2.path == "/assets/new.js"
    assert updated2.host == "mirror.example.net"


def test_set_body_phases(store):
    target = store.list()[2]
    store.set_body(target.id, "req", "request")
    store.set_body(target.id, "resp", "response")
    final = store.get(target.id)
    assert final.body == "req"
    assert final.response_body == "resp"
