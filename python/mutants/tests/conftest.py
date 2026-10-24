"""Shared fixtures for the traffic_agent test suite."""

import pytest

from traffic_agent.risk.audit import AuditLog
from traffic_agent.risk.gate import RiskGate, RiskPolicy, RiskLevel
from traffic_agent.store import CaptureStore, StoredRequest


@pytest.fixture
def store():
    s = CaptureStore()
    s.add(StoredRequest(host="api.example.com", path="/v1/users", method="GET", status=200,
                        headers={"Accept": "application/json", "X-Api": "1"}, body="",
                        response_headers={"Content-Type": "application/json"}, response_body='{"ok":true}',
                        timestamp_ms=1000))
    s.add(StoredRequest(host="cdn.example.com", path="/assets/app.js", method="GET", status=200,
                        headers={}, body="", timestamp_ms=1100))
    s.add(StoredRequest(host="api.example.com", path="/v1/login", method="POST", status=403,
                        headers={"Content-Type": "application/json"}, body='{"user":"u"}',
                        response_body='{"error":"denied"}', timestamp_ms=1200))
    return s


@pytest.fixture
def gate():
    return RiskGate(RiskPolicy(max_level=RiskLevel.CAUTION))


@pytest.fixture
def audit():
    return AuditLog()
