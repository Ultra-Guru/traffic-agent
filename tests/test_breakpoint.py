from __future__ import annotations

import pytest

from tests.helpers import build_request_bytes
from traffic_agent import events as ev
from traffic_agent.capture.parsers import parse_http1_request
from traffic_agent.transform.breakpoint import (
    BreakpointEngine,
    BreakpointError,
    HitState,
)
from traffic_agent.transform.rewrite import RuleMatcher


def make_request(target="/pay", host="api.example.com"):
    return parse_http1_request(build_request_bytes("POST", target, host))


class TestBreakpointEngine:
    def _engine(self):
        bus = ev.EventBus()
        return BreakpointEngine(bus=bus), bus

    def test_set_and_intercept(self):
        engine, bus = self._engine()
        spec = engine.set_breakpoint(RuleMatcher(host="api.example.com"), direction="both")
        assert spec.direction == "both"
        assert spec.enabled is True
        assert spec.hits == 0
        request = make_request()
        hit = engine.intercept("up", request=request, ts=1.0)
        assert hit is not None
        assert hit.state is HitState.PENDING
        assert hit.direction == "up"
        assert hit.request.target == "/pay"
        assert spec.hits == 1
        hits = bus.events(topic=ev.EVENT_BREAKPOINT_HIT)
        assert len(hits) == 1
        assert hits[0].payload["bp_id"] == spec.bp_id

    def test_intercept_no_match_returns_none(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher(host="other.io"))
        assert engine.intercept("up", request=make_request()) is None

    def test_direction_compatibility(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher(), direction="up")
        assert engine.intercept("down", request=make_request()) is None
        assert engine.intercept("up", request=make_request()) is not None

    def test_scope_session(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher(), direction="both", scope_session="sess-42")
        assert engine.intercept("up", request=make_request(), session_id="sess-41") is None
        assert engine.intercept("up", request=make_request(), session_id="sess-42") is not None

    def test_disabled_breakpoint_skipped(self):
        engine, _ = self._engine()
        spec = engine.set_breakpoint(RuleMatcher())
        spec.enabled = False
        assert engine.intercept("up", request=make_request()) is None

    def test_disabled_breakpoint_via_clear(self):
        engine, _ = self._engine()
        spec = engine.set_breakpoint(RuleMatcher())
        assert engine.clear_breakpoint(spec.bp_id) is True
        assert engine.clear_breakpoint(spec.bp_id) is False
        assert engine.intercept("up", request=make_request()) is None

    def test_clear_all(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        engine.set_breakpoint(RuleMatcher())
        assert engine.clear_all() == 2
        assert engine.breakpoints == []

    def test_invalid_direction_raises(self):
        engine, _ = self._engine()
        with pytest.raises(ValueError):
            engine.set_breakpoint(RuleMatcher(), direction="sideways")

    def test_resolve_release(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        request = make_request()
        hit = engine.intercept("up", request=request)
        resolved = engine.resolve(hit.hit_id, "release")
        assert resolved.state is HitState.RELEASED
        payload_req, payload_resp = resolved.resolved_payload
        assert payload_req.target == "/pay"
        assert payload_resp is None
        assert engine.pending_hits() == []
        assert engine.resolved_count() == 1

    def test_resolve_modify(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        hit = engine.intercept("up", request=make_request())
        modified = make_request(target="/modified")
        resolved = engine.resolve(hit.hit_id, "modify", modified_request=modified)
        assert resolved.state is HitState.MODIFIED
        req, _ = resolved.resolved_payload
        assert req.target == "/modified"

    def test_resolve_drop(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        hit = engine.intercept("up", request=make_request())
        resolved = engine.resolve(hit.hit_id, "drop")
        assert resolved.state is HitState.DROPPED
        assert resolved.resolved_payload is None

    def test_resolve_twice_raises(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        hit = engine.intercept("up", request=make_request())
        engine.resolve(hit.hit_id, "release")
        with pytest.raises(BreakpointError):
            engine.resolve(hit.hit_id, "release")

    def test_resolve_unknown_hit_raises(self):
        engine, _ = self._engine()
        with pytest.raises(BreakpointError):
            engine.resolve("nope", "release")

    def test_resolve_unknown_action_raises(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        hit = engine.intercept("up", request=make_request())
        with pytest.raises(BreakpointError):
            engine.resolve(hit.hit_id, "explode")

    def test_pending_hits_filtering(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        h1 = engine.intercept("up", request=make_request(), ts=1.0)
        h2 = engine.intercept("down", request=make_request(), response=object(), ts=2.0)
        up_hits = engine.pending_hits(direction="up")
        assert [h.hit_id for h in up_hits] == [h1.hit_id]
        all_hits = engine.pending_hits()
        assert [h.hit_id for h in all_hits] == [h1.hit_id, h2.hit_id]  # 按 ts 排序
        engine.resolve(h1.hit_id, "release")
        assert [h.hit_id for h in engine.pending_hits()] == [h2.hit_id]

    def test_get_hit(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        hit = engine.intercept("up", request=make_request())
        assert engine.get_hit(hit.hit_id) is hit
        engine.resolve(hit.hit_id, "release")
        assert engine.get_hit(hit.hit_id) is hit
        assert engine.get_hit("missing") is None

    def test_intercept_snapshots_are_copies(self):
        engine, _ = self._engine()
        engine.set_breakpoint(RuleMatcher())
        request = make_request()
        hit = engine.intercept("up", request=request)
        request.headers["host"] = "changed.example.com"
        assert hit.request.headers["host"] == "api.example.com"
