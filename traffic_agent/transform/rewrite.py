"""L1.5 重写引擎：规则匹配 → 确定性变换（对应 SPEC v2.0 §2.1）。

规则 = ``(matcher, direction, action)``：

- Matcher 支持精确 / 正则（带 ReDoS 防护）/ 脚本条件；
- Action 支持 set_header / remove_header / replace_body / set_status /
  map_remote / map_local / mock_response / delay；
- 所有变换产生 ``TransformApplied`` 事件（含前后 sha256）以供审计；
- ``predict_impact`` 提供规则影响面预判（创新 I10）；
- ``rule_from_example`` 支持由「原始 → 期望」示例生成规则草稿（创新 I7）。
"""

from __future__ import annotations

import copy
import hashlib
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional, Sequence, Tuple

from traffic_agent import events as ev
from traffic_agent.session import ConnectionSession

MAX_REGEX_LENGTH = 512
_NESTED_QUANTIFIER = re.compile(r"\([^()]*[+*][^()]*\)[+*]")
SENSITIVE_HINTS = ("login", "auth", "token", "session", "pay", "password", "credential")


class UnsafePattern(ValueError):
    """正则可能引发灾难性回溯或递归，被拒绝。"""


def validate_regex(pattern: str) -> None:
    """ReDoS 防护：拒绝递归 / 嵌套量词 / 超长 / 非法正则。"""
    if not pattern:
        raise UnsafePattern("empty regex")
    if len(pattern) > MAX_REGEX_LENGTH:
        raise UnsafePattern("regex too long")
    for fragment in ("(?R", "(?1", "(?&"):
        if fragment in pattern:
            raise UnsafePattern("recursive patterns are forbidden")
    if _NESTED_QUANTIFIER.search(pattern):
        raise UnsafePattern("nested quantifiers are forbidden")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise UnsafePattern(f"invalid regex: {exc}") from exc


class MatchMode(str, Enum):
    EXACT = "exact"
    REGEX = "regex"
    SCRIPT = "script"


@dataclass
class RuleMatcher:
    """规则匹配器：host / path / method 组合条件。"""

    host: Optional[str] = None
    path: Optional[str] = None
    path_mode: MatchMode = MatchMode.EXACT
    method: Optional[str] = None
    condition: Optional[Callable[[Any], bool]] = None

    def __post_init__(self) -> None:
        if self.path_mode is MatchMode.REGEX:
            for target in (self.host, self.path):
                if target:
                    validate_regex(target)
        if self.path_mode is not MatchMode.SCRIPT and self.condition is not None:
            raise ValueError("condition requires MatchMode.SCRIPT")
        if self.path_mode is MatchMode.SCRIPT and self.condition is None:
            raise ValueError("MatchMode.SCRIPT requires condition")

    def matches(self, request: Any) -> bool:
        if request is None:
            return False
        if self.method is not None:
            if str(getattr(request, "method", "")).upper() != self.method.upper():
                return False
        host = str(getattr(request, "host", "") or "")
        path = str(getattr(request, "path", "") or "")
        if self.host:
            if self.path_mode is MatchMode.REGEX:
                if re.fullmatch(self.host, host) is None:
                    return False
            elif host.lower() != self.host.lower():
                return False
        if self.path:
            if self.path_mode is MatchMode.REGEX:
                if re.search(self.path, path) is None:
                    return False
            elif path != self.path:
                return False
        if self.path_mode is MatchMode.SCRIPT:
            try:
                return bool(self.condition(request))
            except Exception:  # noqa: BLE001 — 脚本条件异常视为不匹配
                return False
        return True


class ActionKind(str, Enum):
    SET_HEADER = "set_header"
    REMOVE_HEADER = "remove_header"
    REPLACE_BODY = "replace_body"
    SET_STATUS = "set_status"
    MAP_REMOTE = "map_remote"
    MAP_LOCAL = "map_local"
    MOCK_RESPONSE = "mock_response"
    DELAY = "delay"


@dataclass
class RewriteAction:
    kind: ActionKind
    header_name: Optional[str] = None
    header_value: Optional[str] = None
    search: Optional[str] = None
    replacement: Optional[str] = None
    status: Optional[int] = None
    new_host: Optional[str] = None
    local_body: Optional[bytes] = None
    mock_status: int = 200
    mock_body: str = ""
    mock_headers: dict = field(default_factory=dict)
    delay_ms: int = 0

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.kind is ActionKind.SET_HEADER and not self.header_name:
            raise ValueError("set_header requires header_name")
        if self.kind is ActionKind.REMOVE_HEADER and not self.header_name:
            raise ValueError("remove_header requires header_name")
        if self.kind is ActionKind.REPLACE_BODY:
            if not self.search or self.replacement is None:
                raise ValueError("replace_body requires search and replacement")
        if self.kind is ActionKind.SET_STATUS:
            if self.status is None or not (100 <= self.status <= 599):
                raise ValueError("set_status requires a status between 100 and 599")
        if self.kind is ActionKind.MAP_REMOTE and not self.new_host:
            raise ValueError("map_remote requires new_host")
        if self.kind is ActionKind.MAP_LOCAL and self.local_body is None:
            raise ValueError("map_local requires local_body")
        if self.kind is ActionKind.DELAY and self.delay_ms < 0:
            raise ValueError("delay_ms must be non-negative")


@dataclass
class RewriteRule:
    matcher: RuleMatcher
    action: RewriteAction
    direction: str = "both"  # up | down | both
    name: str = ""
    rule_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    enabled: bool = True
    source: str = "user"  # user | agent
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if self.direction not in ("up", "down", "both"):
            raise ValueError(f"invalid direction: {self.direction}")
        self.action.validate()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def payload_signature(message: Any) -> str:
    """请求 / 响应的规范化签名（TransformApplied 前后对比用）。"""
    if message is None:
        return sha256_hex(b"")
    headers = getattr(message, "headers", None) or {}
    joined = ";".join(f"{k}={headers[k]}" for k in sorted(headers))
    if type(message).__name__ == "Http1Request":
        raw = f"{message.method} {message.target} {message.version}|{joined}|".encode("latin-1") + message.body
    else:
        raw = f"{message.status} {message.version}|{joined}|".encode("latin-1") + message.body
    return sha256_hex(raw)


@dataclass
class TransformApplied:
    """一次成功应用的变换记录（进入事件总线，供审计追溯）。"""

    rule_id: str
    rule_name: str
    direction: str
    kind: str
    before_sha: str
    after_sha: str
    replacements: int
    delay_ms: int
    source: str
    ts: float = field(default_factory=time.time)

    def to_event(self) -> ev.Event:
        return ev.Event(
            ev.EVENT_TRANSFORM_APPLIED,
            {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "direction": self.direction,
                "kind": self.kind,
                "before_sha": self.before_sha,
                "after_sha": self.after_sha,
                "replacements": self.replacements,
                "delay_ms": self.delay_ms,
                "source": self.source,
                "ts": self.ts,
            },
        )


@dataclass
class ImpactEstimate:
    """规则影响面预判（创新 I10：事前风险提示）。"""

    rule: str
    matched_sessions: List[str]
    hosts: List[str]
    sensitive_hits: List[str]
    total_sessions: int

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "matched_sessions": self.matched_sessions,
            "hosts": self.hosts,
            "sensitive_hits": self.sensitive_hits,
            "total_sessions": self.total_sessions,
        }


class RewriteEngine:
    """重写引擎：首个命中的启用规则生效，产出变换后的请求/响应。"""

    def __init__(self, bus: Optional[ev.EventBus] = None) -> None:
        self.bus = bus
        self.rules: List[RewriteRule] = []

    def add_rule(self, rule: RewriteRule) -> RewriteRule:
        self.rules.append(rule)
        return rule

    def remove_rule(self, rule_id: str) -> bool:
        before = len(self.rules)
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
        return len(self.rules) < before

    def disable_all(self) -> int:
        """一键禁用全部规则（风险登记表：重写导致 App 崩溃时的逃生门）。"""
        count = 0
        for rule in self.rules:
            if rule.enabled:
                rule.enabled = False
                count += 1
        return count

    def first_match(self, direction: str, request: Any) -> Optional[RewriteRule]:
        for rule in self.rules:
            if not rule.enabled:
                continue
            if rule.direction not in ("both", direction):
                continue
            if rule.matcher.matches(request):
                return rule
        return None

    def apply(
        self,
        direction: str,
        request: Any = None,
        response: Any = None,
    ) -> Optional[Tuple[Any, Any, TransformApplied]]:
        """应用首个命中规则，返回 ``(request, response, TransformApplied)``。"""
        if direction not in ("up", "down"):
            raise ValueError(f"invalid direction: {direction}")
        target = request if direction == "up" else response
        rule = self.first_match(direction, target)
        if rule is None:
            return None
        before_sha = payload_signature(target)
        if direction == "up":
            request = copy.deepcopy(request)
            replacements = self._apply_to_request(request, rule.action)
        else:
            response = copy.deepcopy(response)
            replacements = self._apply_to_response(response, rule.action)
        after_target = request if direction == "up" else response
        applied = TransformApplied(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            direction=direction,
            kind=rule.action.kind.value,
            before_sha=before_sha,
            after_sha=payload_signature(after_target),
            replacements=replacements,
            delay_ms=rule.action.delay_ms,
            source=rule.source,
        )
        if self.bus is not None:
            self.bus.publish(applied.to_event())
        return request, response, applied

    @staticmethod
    def _apply_to_request(request: Any, action: RewriteAction) -> int:
        replaced = 0
        if action.kind is ActionKind.SET_HEADER:
            request.headers[action.header_name] = action.header_value or ""
        elif action.kind is ActionKind.REMOVE_HEADER:
            request.headers.pop(action.header_name, None)
        elif action.kind is ActionKind.REPLACE_BODY:
            needle = action.search.encode("utf-8")
            replaced = request.body.count(needle)
            request.body = request.body.replace(needle, action.replacement.encode("utf-8"))
        elif action.kind is ActionKind.MAP_REMOTE:
            request.headers["host"] = action.new_host
            if request.target.startswith(("http://", "https://")):
                parts = request.target.split("/", 3)
                if len(parts) >= 3:
                    parts[2] = action.new_host
                    request.target = "/".join(parts)
        elif action.kind is ActionKind.MAP_LOCAL:
            request.body = action.local_body or b""
        elif action.kind is ActionKind.DELAY:
            pass
        else:
            raise ValueError(f"action {action.kind.value} cannot apply to requests")
        return replaced

    @staticmethod
    def _apply_to_response(response: Any, action: RewriteAction) -> int:
        replaced = 0
        if action.kind is ActionKind.SET_HEADER:
            response.headers[action.header_name] = action.header_value or ""
        elif action.kind is ActionKind.REMOVE_HEADER:
            response.headers.pop(action.header_name, None)
        elif action.kind is ActionKind.REPLACE_BODY:
            needle = action.search.encode("utf-8")
            replaced = response.body.count(needle)
            response.body = response.body.replace(needle, action.replacement.encode("utf-8"))
        elif action.kind is ActionKind.SET_STATUS:
            response.status = action.status
        elif action.kind is ActionKind.MOCK_RESPONSE:
            response.status = action.mock_status
            response.body = action.mock_body.encode("utf-8")
            response.headers = dict(action.mock_headers)
        elif action.kind is ActionKind.DELAY:
            pass
        else:
            raise ValueError(f"action {action.kind.value} cannot apply to responses")
        return replaced

    def predict_impact(self, rule: RewriteRule, sessions: Sequence[ConnectionSession]) -> ImpactEstimate:
        """对历史会话预判规则影响面：匹配数、涉及 Host、敏感端点命中。"""
        matched: List[str] = []
        hosts: List[str] = []
        sensitive: List[str] = []
        for session in sessions:
            request = session.request
            if request is None:
                continue
            if not rule.matcher.matches(request):
                continue
            matched.append(session.session_id)
            host_value = session.host or str(getattr(request, "host", "") or "")
            if host_value and host_value not in hosts:
                hosts.append(host_value)
            hay = f"{host_value}{getattr(request, 'path', '')}".lower()
            if any(hint in hay for hint in SENSITIVE_HINTS):
                sensitive.append(session.session_id)
        return ImpactEstimate(rule.rule_id, matched, hosts, sensitive, len(sessions))


def rule_from_example(host: str, before: str, after: str, path_regex: Optional[str] = None) -> RewriteRule:
    """创新 I7：用户给一条「原始 → 期望」示例，Agent 生成规则草稿。"""
    if not before:
        raise ValueError("before must be non-empty")
    if before == after:
        raise ValueError("before and after must differ")
    if path_regex:
        validate_regex(path_regex)
    matcher = RuleMatcher(
        host=host or None,
        path=path_regex,
        path_mode=MatchMode.REGEX if path_regex else MatchMode.EXACT,
    )
    action = RewriteAction(kind=ActionKind.REPLACE_BODY, search=before, replacement=after)
    return RewriteRule(matcher=matcher, action=action, name="generated-from-example", source="agent")
