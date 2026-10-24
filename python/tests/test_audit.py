from traffic_agent.risk.audit import AuditLog, _digest


def test_append_and_tail():
    log = AuditLog(clock=lambda: 1000)
    log.append("list_requests", "allowed", {"limit": 10})
    log.append("modify_body", "denied", {"id": 1})
    entries = log.tail(10)
    assert len(entries) == 2
    assert entries[0].tool == "list_requests"
    assert entries[0].timestamp_ms == 1000
    assert entries[1].decision == "denied"


def test_tail_returns_most_recent_n():
    log = AuditLog()
    for i in range(5):
        log.append(f"tool-{i}", "allowed")
    tail = log.tail(2)
    assert [e.tool for e in tail] == ["tool-3", "tool-4"]


def test_tail_zero_or_negative_empty():
    log = AuditLog()
    log.append("x", "allowed")
    assert log.tail(0) == []
    assert log.tail(-1) == []


def test_count_and_by_tool():
    log = AuditLog()
    log.append("a", "allowed")
    log.append("a", "denied")
    log.append("b", "allowed")
    assert log.count() == 3
    assert len(log.by_tool("a")) == 2
    assert len(log.by_tool("missing")) == 0


def test_params_digest_is_stable_and_truncated():
    d1 = _digest({"a": 1, "b": 2})
    d2 = _digest({"b": 2, "a": 1})
    assert d1 == d2
    assert len(d1) == 12
    assert _digest(None) == "-"


def test_clear():
    log = AuditLog()
    log.append("a", "allowed")
    log.clear()
    assert log.count() == 0


def test_persist_appends_jsonl(tmp_path):
    log = AuditLog()
    log.append("list_requests", "allowed", {"limit": 5})
    path = tmp_path / "audit.jsonl"
    first = log.persist(str(path))
    assert first == 1
    log.append("modify_body", "denied")
    assert log.persist(str(path)) == 1  # only new entries are written
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2
    import json
    parsed = json.loads(lines[0])
    assert parsed["tool"] == "list_requests"
    assert parsed["decision"] == "allowed"
    assert len(parsed["digest"]) == 12
