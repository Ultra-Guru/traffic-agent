from __future__ import annotations

import pytest

from tests.helpers import build_request_bytes, make_session
from traffic_agent import events as ev
from traffic_agent.transform.rewrite import (
    ActionKind,
    MatchMode,
    RewriteAction,
    RewriteEngine,
    RewriteRule,
    RuleMatcher,
    UnsafePattern,
    payload_signature,
    rule_from_example,
    validate_regex,
)
from traffic_agent.capture.parsers import parse_http1_request


def make_request(target="/api/v1/data", host="api.example.com", method="POST", body=b'{"flag":false}'):
    raw = build_request_bytes(method, target, host, [("Content-Type", "application/json")], body)
    return parse_http1_request(raw)


def make_response(status=200, body=b'{"ok":1}', headers=None):
    from traffic_agent.capture.parsers import Http1Response

    return Http1Response(status=status, reason="OK", version="HTTP/1.1", headers=dict(headers or {}), body=body)


class TestValidateRegex:
    def test_ok(self):
        validate_regex(r"/v\d+/items")

    def test_empty_raises(self):
        with pytest.raises(UnsafePattern):
            validate_regex("")

    def test_too_long_raises(self):
        with pytest.raises(UnsafePattern):
            validate_regex("a" * 513)

    def test_recursive_raises(self):
        for bad in [r"(?R)", r"(?1)x", r"(?&name)"]:
            with pytest.raises(UnsafePattern):
                validate_regex(bad)

    def test_nested_quantifier_raises(self):
        with pytest.raises(UnsafePattern):
            validate_regex(r"(a+)+")
        with pytest.raises(UnsafePattern):
            validate_regex(r"(a*b)*")

    def test_invalid_regex_raises(self):
        with pytest.raises(UnsafePattern):
            validate_regex("([")

    def test_unsafe_pattern_is_value_error(self):
        assert issubclass(UnsafePattern, ValueError)


class TestRuleMatcher:
    def test_exact_host_and_path(self):
        matcher = RuleMatcher(host="api.example.com", path="/api/v1/data")
        assert matcher.matches(make_request()) is True
        assert matcher.matches(make_request(target="/other")) is False
        assert matcher.matches(make_request(host="other.io")) is False

    def test_host_case_insensitive(self):
        matcher = RuleMatcher(host="API.Example.COM")
        assert matcher.matches(make_request()) is True

    def test_method_filter(self):
        matcher = RuleMatcher(method="get")
        assert matcher.matches(make_request(method="GET")) is True
        assert matcher.matches(make_request(method="POST")) is False

    def test_regex_path(self):
        matcher = RuleMatcher(path=r"/v\d+/items", path_mode=MatchMode.REGEX)
        assert matcher.matches(make_request(target="/v2/items")) is True
        assert matcher.matches(make_request(target="/settings")) is False

    def test_regex_host(self):
        matcher = RuleMatcher(host=r".*\.example\.com", path_mode=MatchMode.REGEX)
        assert matcher.matches(make_request()) is True
        assert matcher.matches(make_request(host="api.other.io")) is False

    def test_regex_invalid_pattern_raises_at_construction(self):
        with pytest.raises(UnsafePattern):
            RuleMatcher(path="([", path_mode=MatchMode.REGEX)

    def test_script_condition(self):
        matcher = RuleMatcher(condition=lambda r: r.method == "POST", path_mode=MatchMode.SCRIPT)
        assert matcher.matches(make_request(method="POST")) is True
        assert matcher.matches(make_request(method="GET")) is False

    def test_script_condition_exception_is_no_match(self):
        matcher = RuleMatcher(condition=lambda r: 1 / 0, path_mode=MatchMode.SCRIPT)
        assert matcher.matches(make_request()) is False

    def test_script_requires_condition(self):
        with pytest.raises(ValueError):
            RuleMatcher(path_mode=MatchMode.SCRIPT)

    def test_condition_requires_script_mode(self):
        with pytest.raises(ValueError):
            RuleMatcher(condition=lambda r: True)

    def test_none_request(self):
        assert RuleMatcher(host="x").matches(None) is False


class TestRewriteActionValidation:
    def test_set_header_requires_name(self):
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.SET_HEADER, header_value="v")

    def test_remove_header_requires_name(self):
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.REMOVE_HEADER)

    def test_replace_body_requires_search_and_replacement(self):
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.REPLACE_BODY, search="a")
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.REPLACE_BODY, replacement="b")

    def test_set_status_bounds(self):
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.SET_STATUS, status=99)
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.SET_STATUS, status=600)
        RewriteAction(kind=ActionKind.SET_STATUS, status=200)  # ok

    def test_map_remote_requires_host(self):
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.MAP_REMOTE)

    def test_map_local_requires_body(self):
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.MAP_LOCAL)

    def test_delay_negative_raises(self):
        with pytest.raises(ValueError):
            RewriteAction(kind=ActionKind.DELAY, delay_ms=-1)


class TestRewriteRuleValidation:
    def test_invalid_direction(self):
        with pytest.raises(ValueError):
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="x", header_value="y"),
                direction="sideways",
            )

    def test_valid_directions(self):
        for direction in ("up", "down", "both"):
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="x", header_value="y"),
                direction=direction,
            )


class TestRewriteEngine:
    def _engine(self):
        bus = ev.EventBus()
        return RewriteEngine(bus=bus), bus

    def test_apply_no_match_returns_none(self):
        engine, _ = self._engine()
        assert engine.apply("up", request=make_request()) is None

    def test_apply_set_header_new(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(host="api.example.com"),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="x-trace", header_value="1"),
            )
        )
        req, _, applied = engine.apply("up", request=make_request())
        assert req.headers["x-trace"] == "1"
        assert applied.kind == "set_header"
        assert applied.replacements == 0

    def test_apply_set_header_overrides_existing(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="content-type", header_value="text/plain"),
            )
        )
        req, _, _ = engine.apply("up", request=make_request())
        assert req.headers["content-type"] == "text/plain"

    def test_apply_remove_header(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.REMOVE_HEADER, header_name="content-type"),
            )
        )
        req, _, _ = engine.apply("up", request=make_request())
        assert "content-type" not in req.headers

    def test_apply_replace_body_counts(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.REPLACE_BODY, search="false", replacement="true"),
            )
        )
        req, _, applied = engine.apply("up", request=make_request(body=b'{"a":false,"b":false}'))
        assert req.body == b'{"a":true,"b":true}'
        assert applied.replacements == 2

    def test_apply_map_remote(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.MAP_REMOTE, new_host="mock.example.io"),
            )
        )
        req, _, _ = engine.apply("up", request=make_request())
        assert req.headers["host"] == "mock.example.io"

    def test_apply_map_remote_absolute_target(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.MAP_REMOTE, new_host="mock.example.io"),
            )
        )
        req, _, _ = engine.apply("up", request=make_request(target="http://api.example.com/v1/x"))
        assert req.target == "http://mock.example.io/v1/x"
        assert req.headers["host"] == "mock.example.io"

    def test_apply_map_local(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.MAP_LOCAL, local_body=b"local-mock"),
            )
        )
        req, _, _ = engine.apply("up", request=make_request())
        assert req.body == b"local-mock"

    def test_apply_set_status_on_response(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_STATUS, status=503),
                direction="down",
            )
        )
        _, resp, applied = engine.apply("down", response=make_response(status=200))
        assert resp.status == 503
        assert applied.kind == "set_status"

    def test_apply_mock_response(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(
                    kind=ActionKind.MOCK_RESPONSE, mock_status=201, mock_body='{"mocked":true}', mock_headers={"content-type": "application/json"}
                ),
                direction="down",
            )
        )
        _, resp, applied = engine.apply("down", response=make_response())
        assert resp.status == 201
        assert resp.body == b'{"mocked":true}'
        assert resp.headers == {"content-type": "application/json"}
        assert applied.kind == "mock_response"

    def test_apply_delay_keeps_payload(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.DELAY, delay_ms=5000),
            )
        )
        req, _, applied = engine.apply("up", request=make_request())
        assert req.body == b'{"flag":false}'
        assert applied.delay_ms == 5000
        assert applied.before_sha == applied.after_sha

    def test_apply_does_not_mutate_original(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.REPLACE_BODY, search="false", replacement="true"),
            )
        )
        original = make_request()
        req, _, _ = engine.apply("up", request=original)
        assert original.body == b'{"flag":false}'
        assert req.body == b'{"flag":true}'

    def test_direction_filtering(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_STATUS, status=500),
                direction="down",
            )
        )
        assert engine.apply("up", request=make_request()) is None
        assert engine.apply("down", response=make_response()) is not None

    def test_disabled_rule_skipped(self):
        engine, _ = self._engine()
        rule = engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="x", header_value="y"),
            )
        )
        rule.enabled = False
        assert engine.apply("up", request=make_request()) is None

    def test_first_matching_rule_wins(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="first", header_value="1"),
            )
        )
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="second", header_value="2"),
            )
        )
        req, _, applied = engine.apply("up", request=make_request())
        assert req.headers["first"] == "1"
        assert "second" not in req.headers
        assert applied.kind == "set_header"

    def test_transform_applied_event_published(self):
        engine, bus = self._engine()
        engine.add_rule(
            RewriteRule(
                name="flag-flip",
                matcher=RuleMatcher(host="api.example.com"),
                action=RewriteAction(kind=ActionKind.REPLACE_BODY, search="false", replacement="true"),
                source="agent",
            )
        )
        engine.apply("up", request=make_request())
        transform_events = bus.events(topic=ev.EVENT_TRANSFORM_APPLIED)
        assert len(transform_events) == 1
        payload = transform_events[0].payload
        assert payload["rule_name"] == "flag-flip"
        assert payload["kind"] == "replace_body"
        assert payload["replacements"] == 1
        assert payload["source"] == "agent"
        assert payload["before_sha"] != payload["after_sha"]
        assert payload["direction"] == "up"

    def test_invalid_direction_apply(self):
        engine, _ = self._engine()
        with pytest.raises(ValueError):
            engine.apply("sideways", request=make_request())

    def test_remove_rule(self):
        engine, _ = self._engine()
        rule = engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="x", header_value="y"),
            )
        )
        assert engine.remove_rule(rule.rule_id) is True
        assert engine.remove_rule(rule.rule_id) is False
        assert engine.apply("up", request=make_request()) is None

    def test_disable_all(self):
        engine, _ = self._engine()
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="a", header_value="1"),
            )
        )
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="b", header_value="2"),
            )
        )
        engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(),
                action=RewriteAction(kind=ActionKind.SET_HEADER, header_name="c", header_value="3"),
            )
        )
        engine.rules[0].enabled = False
        assert engine.disable_all() == 2  # 已禁用的不重复计数
        assert all(r.enabled is False for r in engine.rules)
        assert engine.disable_all() == 0


class TestPayloadSignature:
    def test_none(self):
        assert payload_signature(None) == payload_signature(None)

    def test_request_changes_with_body(self):
        a = payload_signature(make_request(body=b"1"))
        b = payload_signature(make_request(body=b"2"))
        assert a != b

    def test_response_signature(self):
        assert payload_signature(make_response(status=200)) != payload_signature(make_response(status=201))


class TestPredictImpact:
    def test_impact_estimate(self):
        bus = ev.EventBus()
        engine = RewriteEngine(bus=bus)
        rule = engine.add_rule(
            RewriteRule(
                matcher=RuleMatcher(host="api.example.com"),
                action=RewriteAction(kind=ActionKind.REPLACE_BODY, search="false", replacement="true"),
            )
        )
        sessions = [
            make_session(host="api.example.com", path="/login", started_at=1.0),
            make_session(host="api.example.com", path="/profile", started_at=2.0),
            make_session(host="cdn.example.net", path="/img", started_at=3.0),
            make_session(host="no-request.example.com", started_at=4.0),
        ]
        sessions[3].request = None
        estimate = engine.predict_impact(rule, sessions)
        assert estimate.total_sessions == 4
        assert estimate.matched_sessions == [sessions[0].session_id, sessions[1].session_id]
        assert estimate.hosts == ["api.example.com"]
        assert estimate.sensitive_hits == [sessions[0].session_id]  # /login 命中敏感关键词
        d = estimate.to_dict()
        assert d["rule"] == rule.rule_id
        assert d["total_sessions"] == 4


class TestRuleFromExample:
    def test_builds_rule(self):
        rule = rule_from_example(host="api.example.com", before='"vip":false', after='"vip":true', path_regex=r"/user/\d+")
        assert rule.source == "agent"
        assert rule.name == "generated-from-example"
        assert rule.action.kind is ActionKind.REPLACE_BODY
        assert rule.action.search == '"vip":false'
        assert rule.action.replacement == '"vip":true'
        req = make_request(target="/user/42")
        req2, _, applied = RewriteEngine().apply("up", request=req) or (None, None, None)
        # 直接验证 matcher
        assert rule.matcher.matches(make_request(target="/user/42")) is True
        assert rule.matcher.matches(make_request(target="/other")) is False

    def test_before_empty_raises(self):
        with pytest.raises(ValueError):
            rule_from_example(host="h", before="", after="x")

    def test_before_equals_after_raises(self):
        with pytest.raises(ValueError):
            rule_from_example(host="h", before="same", after="same")

    def test_bad_path_regex_raises(self):
        with pytest.raises(UnsafePattern):
            rule_from_example(host="h", before="a", after="b", path_regex="([")
