"""L1 会话模型：五元组连接、会话指纹与会话存储。

对应 SPEC v2.0 第 2 章（L1 抓包数据面）与创新 I1（会话指纹）、
I10（重写规则影响面预判——`ConnectionSession.fingerprint()` 跨会话稳定）。
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Transport(str, Enum):
    TCP = "tcp"
    UDP = "udp"


class Direction(str, Enum):
    """流量方向：相对设备视角。"""

    UPSTREAM = "up"      # 客户端 -> 服务器
    DOWNSTREAM = "down"  # 服务器 -> 客户端


class TlsInspectionState(str, Enum):
    """TLS 可见性状态——诚实标注原则（I9 的延伸）。"""

    PLAINTEXT = "plaintext"
    DECRYPTED = "decrypted"
    PINNED_BLOCKED = "pinned_blocked"
    PASSTHROUGH = "passthrough"


@dataclass
class Chunk:
    """一次抓到的数据块（PCAP 导出与回放序列的基础）。"""

    direction: Direction
    ts: float
    data: bytes


@dataclass
class ConnectionSession:
    """一条被观测的连接：五元组 + 应用/协议元数据 + 载荷统计。"""

    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str = "tcp"
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    app_uid: Optional[int] = None
    app_package: Optional[str] = None
    sni: Optional[str] = None
    host: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    tls_state: TlsInspectionState = TlsInspectionState.PLAINTEXT
    quic_bypass: bool = False
    capture_channel: str = "tun"
    bytes_up: int = 0
    bytes_down: int = 0
    request_count: int = 0
    response_count: int = 0
    tags: List[str] = field(default_factory=list)
    chunks: List[Chunk] = field(default_factory=list)
    request: Any = None
    response: Any = None
    dns: Any = None

    @property
    def five_tuple(self) -> tuple:
        return (self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.protocol)

    def fingerprint(self) -> str:
        """跨会话稳定指纹：与 session_id / 时间戳无关，供影响面预判使用。"""
        material = "|".join(
            [
                self.src_ip,
                str(self.src_port),
                self.dst_ip,
                str(self.dst_port),
                self.protocol,
                self.app_package or "",
                self.sni or "",
                self.host or "",
            ]
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]

    def add_bytes(self, direction: Direction, size: int, ts: Optional[float] = None, data: bytes = b"") -> int:
        if size < 0:
            raise ValueError("size must be non-negative")
        if direction is Direction.UPSTREAM:
            self.bytes_up += size
        elif direction is Direction.DOWNSTREAM:
            self.bytes_down += size
        else:
            raise ValueError(f"unknown direction: {direction!r}")
        self.chunks.append(Chunk(direction, ts if ts is not None else time.time(), data))
        return self.bytes_up + self.bytes_down

    def close(self, ts: Optional[float] = None) -> float:
        self.ended_at = ts if ts is not None else time.time()
        return self.ended_at

    @property
    def duration_ms(self) -> float:
        end = self.ended_at if self.ended_at is not None else self.started_at
        return max(0.0, (end - self.started_at) * 1000.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "five_tuple": list(self.five_tuple),
            "app_package": self.app_package,
            "sni": self.sni,
            "host": self.host,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "tls_state": self.tls_state.value,
            "quic_bypass": self.quic_bypass,
            "capture_channel": self.capture_channel,
            "bytes_up": self.bytes_up,
            "bytes_down": self.bytes_down,
            "fingerprint": self.fingerprint(),
        }


class SessionStore:
    """进程内会话存储：Agent 工具 `query_connections` 的后端。"""

    def __init__(self) -> None:
        self._sessions: Dict[str, ConnectionSession] = {}

    def add(self, session: ConnectionSession) -> ConnectionSession:
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Optional[ConnectionSession]:
        return self._sessions.get(session_id)

    def all(self) -> List[ConnectionSession]:
        return sorted(self._sessions.values(), key=lambda s: (s.started_at, s.session_id))

    def count(self) -> int:
        return len(self._sessions)

    def clear(self) -> None:
        self._sessions.clear()

    def query(
        self,
        host: Optional[str] = None,
        app: Optional[str] = None,
        method: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[ConnectionSession]:
        results: List[ConnectionSession] = []
        for session in self.all():
            if host is not None and (session.host or "").lower() != host.lower():
                continue
            if app is not None and session.app_package != app:
                continue
            if tag is not None and tag not in session.tags:
                continue
            if method is not None:
                request_method = getattr(session.request, "method", None)
                if request_method is None or request_method.upper() != method.upper():
                    continue
            results.append(session)
        if limit is not None:
            if limit < 0:
                raise ValueError("limit must be non-negative")
            results = results[:limit]
        return results
