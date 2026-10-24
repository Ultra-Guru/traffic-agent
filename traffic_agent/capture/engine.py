"""L1 抓包引擎：多通道数据面（VpnService / root 通道）与流量分类。

对应 SPEC v2.0 第 2 章与 Root 增量第 1 章：

- ``CaptureMode`` 可切换数据通道（vpn / root_packet / root_nfqueue / root_ebpf）；
- 事件携带 ``capture_channel`` / ``capture_method`` 字段；
- QUIC 旁路与 PINNED_BLOCKED 按创新 I9「诚实报告」原则标注。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from traffic_agent import events as ev
from traffic_agent.capture import parsers
from traffic_agent.session import ConnectionSession, Direction, SessionStore, TlsInspectionState


class CaptureMode(str, Enum):
    VPN = "vpn"
    ROOT_PACKET = "root_packet"
    ROOT_NFQUEUE = "root_nfqueue"
    ROOT_EBPF = "root_ebpf"


CAPTURE_CHANNEL = {
    CaptureMode.VPN: "tun",
    CaptureMode.ROOT_PACKET: "af_packet",
    CaptureMode.ROOT_NFQUEUE: "nfqueue",
    CaptureMode.ROOT_EBPF: "ebpf_socket",
}

EBPF_MIN_KERNEL = (4, 9)


@dataclass
class RootCapabilities:
    """root 能力探测结果（Root 增量 §1.2 的诚实性约束）。"""

    root_available: bool = False
    channels: Tuple[str, ...] = ()
    ebpf_tls: str = "unavailable"  # available | unavailable_kernel_too_old | unavailable_selinux
    kernel_version: Optional[Tuple[int, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_available": self.root_available,
            "channels": list(self.channels),
            "ebpf_tls": self.ebpf_tls,
            "kernel_version": list(self.kernel_version) if self.kernel_version else None,
        }


def probe_root(env: Optional[Dict[str, Any]] = None) -> RootCapabilities:
    """根据设备环境探测可用 root 通道（参考实现中以 env 字典模拟设备状态）。"""
    env = dict(env or {})
    if not env.get("root_available", False):
        return RootCapabilities()
    kernel = tuple(env.get("kernel_version", (0, 0)))
    ebpf_tls: str
    if env.get("selinux_enforcing", False):
        ebpf_tls = "unavailable_selinux"
    elif tuple(kernel) >= EBPF_MIN_KERNEL:
        ebpf_tls = "available"
    else:
        ebpf_tls = "unavailable_kernel_too_old"
    channels: List[str] = ["af_packet", "nfqueue", "tproxy"]
    if ebpf_tls == "available":
        channels.append("ebpf_socket")
    return RootCapabilities(
        root_available=True,
        channels=tuple(channels),
        ebpf_tls=ebpf_tls,
        kernel_version=tuple(kernel),
    )


class CaptureEngine:
    """把原始字节块分类为结构化流量事件，并维护会话元数据。"""

    def __init__(
        self,
        store: SessionStore,
        bus: ev.EventBus,
        mode: CaptureMode = CaptureMode.VPN,
        root_capabilities: Optional[RootCapabilities] = None,
    ) -> None:
        self.store = store
        self.bus = bus
        self.mode = mode
        self.channel = CAPTURE_CHANNEL[mode]
        self.root_capabilities = root_capabilities or RootCapabilities()
        self.state = "stopped"

    def start(self) -> ev.Event:
        if self.state == "started":
            raise RuntimeError("capture already started")
        self.state = "started"
        event = ev.Event(
            ev.EVENT_CAPTURE_STATE,
            {
                "state": "started",
                "mode": self.mode.value,
                "channel": self.channel,
                "root_capabilities": self.root_capabilities.to_dict(),
            },
        )
        self.bus.publish(event)
        return event

    def stop(self) -> ev.Event:
        if self.state != "started":
            raise RuntimeError("capture not started")
        self.state = "stopped"
        event = ev.Event(ev.EVENT_CAPTURE_STATE, {"state": "stopped", "mode": self.mode.value})
        self.bus.publish(event)
        return event

    def ingest(
        self,
        conn: ConnectionSession,
        direction: Direction,
        data: bytes,
        ts: Optional[float] = None,
    ) -> Optional[ev.Event]:
        if self.state != "started":
            raise RuntimeError("capture not started")
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("data must be bytes")
        data = bytes(data)
        ts = ts if ts is not None else conn.started_at
        conn.add_bytes(direction, len(data), ts=ts, data=data)
        kind = self._classify(conn, direction, data)
        event = ev.Event(
            ev.EVENT_TRAFFIC,
            {
                "session_id": conn.session_id,
                "direction": direction.value,
                "kind": kind,
                "capture_channel": self.channel,
                "capture_method": self.channel,
                "bytes": len(data),
            },
        )
        self.bus.publish(event)
        return event

    def _classify(self, conn: ConnectionSession, direction: Direction, data: bytes) -> str:
        if conn.protocol == "udp" and conn.dst_port == 53:
            try:
                conn.dns = parsers.parse_dns_message(data)
            except parsers.ProtocolError:
                return "dns_malformed"
            return "dns"
        if conn.protocol == "udp" and conn.dst_port == 443 and parsers.is_quic_initial_packet(data):
            conn.quic_bypass = True
            return "quic_initial"
        if direction is Direction.UPSTREAM:
            if parsers.is_tls_record(data) and data[5] == 0x01:
                try:
                    hello = parsers.parse_tls_client_hello(data)
                except parsers.ProtocolError:
                    return "tls_malformed"
                conn.sni = hello.sni
                if hello.sni:
                    conn.host = conn.host or hello.sni
                return "tls_client_hello"
            if parsers.looks_like_http_request(data):
                try:
                    request = parsers.parse_http1_request(data)
                except parsers.ProtocolError:
                    return "http1_malformed"
                conn.request = request
                conn.request_count += 1
                conn.host = request.host or conn.host
                return "http1_request"
        else:
            if data.startswith(b"HTTP/"):
                try:
                    response = parsers.parse_http1_response(data)
                except parsers.ProtocolError:
                    return "http1_malformed"
                conn.response = response
                conn.response_count += 1
                return "http1_response"
        return "raw"

    @staticmethod
    def visibility_report(conn: ConnectionSession) -> List[str]:
        """I9 诚实报告：明确标注抓不到的部分，而不是假装抓全了。"""
        notes: List[str] = []
        if conn.quic_bypass:
            notes.append(
                "QUIC connection observed but not fully captured; HTTP/3 payload may bypass this proxy"
            )
        if conn.tls_state is TlsInspectionState.PINNED_BLOCKED:
            notes.append("TLS pinned by target app; payload not decrypted (PINNED_BLOCKED)")
        return notes
