"""PCAP 导出（小端 PCAP 格式；对应 SPEC v2.0 §1.5 的 packet_level_reliable 诚实标注）。

VpnService 数据面只能重建 L4 语义流，无法保真逐包边界——
`packet_level_reliable=False` 的会话导出时在 README / 事件中标注；
root 的 AF_PACKET 通道才提供真正的逐包保真。
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Iterable, List, Optional

PCAP_MAGIC = 0xA1B2C3D4
PCAP_VERSION_MAJOR = 2
PCAP_VERSION_MINOR = 4
LINKTYPE_RAW = 101
DEFAULT_SNAPLEN = 65535


@dataclass
class PacketRecord:
    data: bytes
    ts: float
    orig_len: Optional[int] = None

    def __post_init__(self) -> None:
        if self.orig_len is None:
            self.orig_len = len(self.data)


def pcap_global_header(snaplen: int = DEFAULT_SNAPLEN, linktype: int = LINKTYPE_RAW) -> bytes:
    if snaplen <= 0:
        raise ValueError("snaplen must be positive")
    return struct.pack(
        "<IHHiIII",
        PCAP_MAGIC,
        PCAP_VERSION_MAJOR,
        PCAP_VERSION_MINOR,
        0,  # thiszone
        0,  # sigfigs
        snaplen,
        linktype,
    )


def pcap_record_header(ts: float, incl_len: int, orig_len: int) -> bytes:
    if incl_len < 0 or orig_len < 0:
        raise ValueError("lengths must be non-negative")
    if ts < 0:
        raise ValueError("timestamp must be non-negative")
    ts_sec = int(ts)
    ts_usec = int(round((ts - ts_sec) * 1_000_000))
    if ts_usec >= 1_000_000:
        ts_sec += 1
        ts_usec -= 1_000_000
    return struct.pack("<IIII", ts_sec, ts_usec, incl_len, orig_len)


def build_pcap(
    records: Iterable[PacketRecord],
    snaplen: int = DEFAULT_SNAPLEN,
    linktype: int = LINKTYPE_RAW,
) -> bytes:
    out = bytearray(pcap_global_header(snaplen, linktype))
    for record in records:
        incl = len(record.data)
        orig = record.orig_len if record.orig_len is not None else incl
        if incl > snaplen:
            incl = snaplen
        out += pcap_record_header(record.ts, incl, orig)
        out += record.data[:incl]
    return bytes(out)


def export_pcap(sessions: Iterable[Any], snaplen: int = DEFAULT_SNAPLEN) -> bytes:
    """按会话 chunks 导出 PCAP 字节流。"""
    records: List[PacketRecord] = []
    for session in sessions:
        for chunk in getattr(session, "chunks", []) or []:
            records.append(PacketRecord(data=bytes(chunk.data), ts=float(chunk.ts)))
    return build_pcap(records, snaplen=snaplen)
