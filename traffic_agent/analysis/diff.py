"""L3 差分回归引擎：抓包即测试基线（对应 SPEC v2.0 创新 I8）。

``DiffEngine.diff(baseline, candidate)`` 输出回归报告：
新增 / 删除 / 变更的端点、状态码、响应体结构，并区分
INFO / WARNING / BREAKING 三级严重度；预期内变更可标记 ``expected``
从 breaking 列表排除——把抓包工具升级为 CI/CD 可用的接口契约监控器。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set


class ChangeKind(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    STATUS_CHANGED = "status_changed"
    SCHEMA_CHANGED = "schema_changed"
    HEADER_CHANGED = "header_changed"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    BREAKING = "breaking"


@dataclass(frozen=True)
class EndpointKey:
    method: str
    host: str
    path: str

    @classmethod
    def from_session(cls, session: Any) -> "EndpointKey":
        request = getattr(session, "request", None)
        if request is None:
            raise ValueError("session has no request")
        return cls(
            method=str(getattr(request, "method", "")).upper(),
            host=str(getattr(request, "host", "") or ""),
            path=str(getattr(request, "path", "") or getattr(request, "target", "")),
        )

    def as_text(self) -> str:
        return f"{self.method} {self.host}{self.path}"


def normalize_shape(value: Any) -> str:
    """值的结构签名：bool 与 int 区分、dict 键排序、list 以首元素同构。"""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if value is None:
        return "null"
    if isinstance(value, dict):
        inner = ",".join(f"{k}:{normalize_shape(value[k])}" for k in sorted(value, key=str))
        return "{" + inner + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        return "[" + normalize_shape(value[0]) + "]"
    return type(value).__name__


def body_signature(body: bytes) -> str:
    """响应体签名：JSON 走结构签名，二进制走 sha256 前 12 位。"""
    if not body:
        return "empty"
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "raw:" + hashlib.sha256(body).hexdigest()[:12]
    return normalize_shape(parsed)


def parse_body(body: Any) -> Any:
    if body is None or body == b"":
        return None
    try:
        return json.loads(body)
    except Exception:  # noqa: BLE001 — 非 JSON 体返回 None
        return None


def top_level_fields(value: Any) -> Set[str]:
    if isinstance(value, dict):
        return set(value.keys())
    return set()


@dataclass
class DiffEntry:
    key: EndpointKey
    change: ChangeKind
    severity: Severity
    detail: str
    baseline_status: Optional[int] = None
    candidate_status: Optional[int] = None
    baseline_shape: Optional[str] = None
    candidate_shape: Optional[str] = None
    expected: bool = False


@dataclass
class RegressionReport:
    entries: List[DiffEntry] = field(default_factory=list)
    baseline_count: int = 0
    candidate_count: int = 0

    def counts(self) -> Dict[str, int]:
        result = {kind.value: 0 for kind in ChangeKind}
        for entry in self.entries:
            result[entry.change.value] += 1
        return result

    def breaking(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.severity is Severity.BREAKING and not e.expected]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_count": self.baseline_count,
            "candidate_count": self.candidate_count,
            "counts": self.counts(),
            "breaking": [e.key.as_text() for e in self.breaking()],
            "entries": [
                {
                    "endpoint": e.key.as_text(),
                    "change": e.change.value,
                    "severity": e.severity.value,
                    "detail": e.detail,
                    "expected": e.expected,
                }
                for e in self.entries
            ],
        }


class DiffEngine:
    """两次抓包的语义级差分。"""

    def diff(self, baseline: Sequence[Any], candidate: Sequence[Any]) -> RegressionReport:
        base_index = self._index(baseline)
        cand_index = self._index(candidate)
        report = RegressionReport(baseline_count=len(base_index), candidate_count=len(cand_index))
        for key in sorted(base_index, key=lambda k: k.as_text()):
            if key not in cand_index:
                report.entries.append(
                    DiffEntry(key, ChangeKind.REMOVED, Severity.WARNING, "endpoint disappeared in candidate")
                )
        for key in sorted(cand_index, key=lambda k: k.as_text()):
            base_session = base_index.get(key)
            cand_session = cand_index[key]
            if base_session is None:
                report.entries.append(
                    DiffEntry(key, ChangeKind.ADDED, Severity.INFO, "new endpoint in candidate")
                )
                continue
            self._diff_pair(report, key, base_session, cand_session)
        return report

    @staticmethod
    def _index(sessions: Sequence[Any]) -> Dict[EndpointKey, Any]:
        index: Dict[EndpointKey, Any] = {}
        for session in sessions:
            if getattr(session, "request", None) is None:
                continue
            key = EndpointKey.from_session(session)
            index[key] = session
        return index

    @staticmethod
    def _body_of(session: Any) -> bytes:
        body = getattr(getattr(session, "response", None), "body", b"") or b""
        return body if isinstance(body, bytes) else str(body).encode("utf-8")

    @classmethod
    def _diff_pair(cls, report: RegressionReport, key: EndpointKey, base: Any, cand: Any) -> None:
        base_status = getattr(getattr(base, "response", None), "status", None)
        cand_status = getattr(getattr(cand, "response", None), "status", None)
        base_shape = body_signature(cls._body_of(base))
        cand_shape = body_signature(cls._body_of(cand))
        if base_status != cand_status:
            if cand_status is not None and cand_status >= 500:
                severity = Severity.BREAKING
            elif cand_status is not None and cand_status >= 400 and (base_status is None or base_status < 400):
                severity = Severity.BREAKING
            else:
                severity = Severity.WARNING
            report.entries.append(
                DiffEntry(
                    key,
                    ChangeKind.STATUS_CHANGED,
                    severity,
                    f"status {base_status} -> {cand_status}",
                    baseline_status=base_status,
                    candidate_status=cand_status,
                )
            )
        if base_shape != cand_shape:
            base_fields = top_level_fields(parse_body(cls._body_of(base)))
            cand_fields = top_level_fields(parse_body(cls._body_of(cand)))
            missing = base_fields - cand_fields
            if missing:
                report.entries.append(
                    DiffEntry(
                        key,
                        ChangeKind.SCHEMA_CHANGED,
                        Severity.BREAKING,
                        f"fields missing: {sorted(missing)}",
                        baseline_shape=base_shape,
                        candidate_shape=cand_shape,
                    )
                )
            else:
                report.entries.append(
                    DiffEntry(
                        key,
                        ChangeKind.SCHEMA_CHANGED,
                        Severity.WARNING,
                        "response shape changed",
                        baseline_shape=base_shape,
                        candidate_shape=cand_shape,
                    )
                )
        base_headers = set(getattr(getattr(base, "response", None), "headers", {}) or {})
        cand_headers = set(getattr(getattr(cand, "response", None), "headers", {}) or {})
        if base_headers != cand_headers:
            report.entries.append(
                DiffEntry(key, ChangeKind.HEADER_CHANGED, Severity.INFO, "response headers changed")
            )

    @staticmethod
    def mark_expected(report: RegressionReport, endpoints: Sequence[str]) -> RegressionReport:
        """把预期内的变更从 breaking 列表排除。"""
        for entry in report.entries:
            if entry.key.as_text() in endpoints:
                entry.expected = True
        return report
