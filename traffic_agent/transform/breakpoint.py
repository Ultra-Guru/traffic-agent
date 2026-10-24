"""L4 断点引擎：拦截 → 编辑 → 放行（移动端原生，对应 SPEC v2.0 §1.3 / M4）。

Reqable 移动端砍掉了断点能力（只在桌面协同模式保留）；
本引擎在移动端原生提供「请求/响应断点」——这是对当前
HttpCanary / Reqable 移动端的直接功能优势窗口。
"""

from __future__ import annotations

import copy
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from traffic_agent import events as ev
from traffic_agent.transform.rewrite import RuleMatcher


class BreakpointError(RuntimeError):
    """断点操作非法（未知断点、重复 resolve、非法动作等）。"""


class HitState(str, Enum):
    PENDING = "pending"
    RELEASED = "released"
    MODIFIED = "modified"
    DROPPED = "dropped"


RESOLVE_ACTIONS = ("release", "modify", "drop")


@dataclass
class BreakpointSpec:
    """一条断点：匹配器 + 方向 + 作用域（可限定单条会话）。"""

    matcher: RuleMatcher
    direction: str = "both"  # up | down | both
    scope_session: Optional[str] = None
    bp_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    enabled: bool = True
    hits: int = 0

    def __post_init__(self) -> None:
        if self.direction not in ("up", "down", "both"):
            raise ValueError(f"invalid direction: {self.direction}")


@dataclass
class BreakpointHit:
    """断点命中：挂起的请求/响应快照，等待用户/脚本 resolve。"""

    bp_id: str
    direction: str
    request: Any = None
    response: Any = None
    hit_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    state: HitState = HitState.PENDING
    ts: float = field(default_factory=time.time)
    resolved_payload: Any = None


class BreakpointEngine:
    """断点引擎：命中入队 → 等待 resolve（放行 / 修改 / 丢弃）。"""

    def __init__(self, bus: Optional[ev.EventBus] = None) -> None:
        self.bus = bus
        self.breakpoints: List[BreakpointSpec] = []
        self._pending: Dict[str, BreakpointHit] = {}
        self._resolved: Dict[str, BreakpointHit] = {}

    def set_breakpoint(
        self,
        matcher: RuleMatcher,
        direction: str = "both",
        scope_session: Optional[str] = None,
    ) -> BreakpointSpec:
        spec = BreakpointSpec(matcher=matcher, direction=direction, scope_session=scope_session)
        self.breakpoints.append(spec)
        return spec

    def clear_breakpoint(self, bp_id: str) -> bool:
        before = len(self.breakpoints)
        self.breakpoints = [bp for bp in self.breakpoints if bp.bp_id != bp_id]
        return len(self.breakpoints) < before

    def clear_all(self) -> int:
        count = len(self.breakpoints)
        self.breakpoints = []
        return count

    def matches(self, direction: str, request: Any, session_id: Optional[str] = None) -> Optional[BreakpointSpec]:
        for spec in self.breakpoints:
            if not spec.enabled:
                continue
            if spec.direction not in ("both", direction):
                continue
            if spec.scope_session is not None and session_id != spec.scope_session:
                continue
            if spec.matcher.matches(request):
                return spec
        return None

    def intercept(
        self,
        direction: str,
        request: Any = None,
        response: Any = None,
        session_id: Optional[str] = None,
        ts: Optional[float] = None,
    ) -> Optional[BreakpointHit]:
        """命中则挂起（快照入队）并发布 BreakpointHit 事件；未命中返回 None。"""
        spec = self.matches(direction, request, session_id)
        if spec is None:
            return None
        spec.hits += 1
        hit = BreakpointHit(
            bp_id=spec.bp_id,
            direction=direction,
            request=copy.deepcopy(request),
            response=copy.deepcopy(response),
            ts=ts if ts is not None else time.time(),
        )
        self._pending[hit.hit_id] = hit
        if self.bus is not None:
            self.bus.publish(
                ev.Event(ev.EVENT_BREAKPOINT_HIT, {"hit_id": hit.hit_id, "bp_id": spec.bp_id, "direction": direction})
            )
        return hit

    def resolve(
        self,
        hit_id: str,
        action: str,
        modified_request: Any = None,
        modified_response: Any = None,
    ) -> BreakpointHit:
        """对命中断点执行 release / modify / drop。"""
        if action not in RESOLVE_ACTIONS:
            raise BreakpointError(f"unknown resolve action: {action}")
        hit = self._pending.get(hit_id)
        if hit is None:
            raise BreakpointError(f"unknown or already-resolved hit: {hit_id}")
        if hit.state is not HitState.PENDING:
            raise BreakpointError(f"hit {hit_id} already resolved")
        if action == "release":
            hit.state = HitState.RELEASED
            hit.resolved_payload = (hit.request, hit.response)
        elif action == "modify":
            hit.state = HitState.MODIFIED
            hit.resolved_payload = (
                copy.deepcopy(modified_request) if modified_request is not None else hit.request,
                copy.deepcopy(modified_response) if modified_response is not None else hit.response,
            )
        else:  # drop
            hit.state = HitState.DROPPED
            hit.resolved_payload = None
        self._pending.pop(hit_id, None)
        self._resolved[hit_id] = hit
        return hit

    def pending_hits(self, direction: Optional[str] = None) -> List[BreakpointHit]:
        hits = list(self._pending.values())
        if direction is not None:
            hits = [h for h in hits if h.direction == direction]
        return sorted(hits, key=lambda h: h.ts)

    def get_hit(self, hit_id: str) -> Optional[BreakpointHit]:
        return self._pending.get(hit_id) or self._resolved.get(hit_id)

    def resolved_count(self) -> int:
        return len(self._resolved)
