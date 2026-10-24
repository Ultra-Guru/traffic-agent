"""L2 事件总线：TrafficEvent / TransformApplied / 工具调用等事件的发布订阅。

对应 SPEC v2.0 第 2 章——「所有变换操作产生 TransformApplied 事件」，
事件总线是 L1 数据面与 L3 分析、L4 Agent 控制面之间的唯一通道。
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

EVENT_TRAFFIC = "traffic"
EVENT_CAPTURE_STATE = "capture_state_changed"
EVENT_TRANSFORM_APPLIED = "transform_applied"
EVENT_BREAKPOINT_HIT = "breakpoint_hit"
EVENT_TOOL_INVOKED = "tool_invoked"
EVENT_GATE_DECISION = "gate_decision"

ALL_TOPICS = "*"


@dataclass
class Event:
    """总线上的事件：类型 + 载荷 + 时间戳。"""

    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


Handler = Callable[[Event], None]


class EventBus:
    """同步事件总线。

    - 订阅者按 topic 匹配；``ALL_TOPICS``（"*"）订阅全部事件。
    - handler 抛出的异常不会中断发布，而是记录到 ``errors``。
    - 保留最近 ``history_limit`` 条事件用于回放与审计。
    """

    def __init__(self, history_limit: int = 500) -> None:
        if history_limit <= 0:
            raise ValueError("history_limit must be positive")
        self._handlers: Dict[str, List[Handler]] = {}
        self._history: List[Event] = []
        self._lock = threading.Lock()
        self.history_limit = history_limit
        self.errors: List[Dict[str, str]] = []

    def subscribe(self, topic: str, handler: Handler) -> Callable[[], None]:
        if not topic:
            raise ValueError("topic must be non-empty")
        if not callable(handler):
            raise TypeError("handler must be callable")
        with self._lock:
            self._handlers.setdefault(topic, []).append(handler)

        def unsubscribe() -> None:
            with self._lock:
                listeners = self._handlers.get(topic, [])
                if handler in listeners:
                    listeners.remove(handler)

        return unsubscribe

    def publish(self, event: Event) -> int:
        if not isinstance(event, Event):
            raise TypeError("event must be an Event instance")
        with self._lock:
            self._history.append(event)
            if len(self._history) > self.history_limit:
                del self._history[: len(self._history) - self.history_limit]
            targets = list(self._handlers.get(event.type, [])) + list(self._handlers.get(ALL_TOPICS, []))
        delivered = 0
        for handler in targets:
            try:
                handler(event)
                delivered += 1
            except Exception as exc:  # noqa: BLE001 — 记录而不是中断
                self.errors.append({"topic": event.type, "error": f"{type(exc).__name__}: {exc}"})
        return delivered

    def events(self, topic: Optional[str] = None, limit: Optional[int] = None) -> List[Event]:
        with self._lock:
            events = [e for e in self._history if topic is None or e.type == topic]
        if limit is not None:
            if limit < 0:
                raise ValueError("limit must be non-negative")
            events = events[:limit]
        return list(events)

    def clear(self) -> None:
        with self._lock:
            self._history.clear()
            self.errors.clear()
