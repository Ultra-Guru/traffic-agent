"""SSLKEYLOGFILE 导出（供 Wireshark 解密，对应 SPEC v2.0 §1.5）。"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

CLIENT_RANDOM_LEN = 32
MASTER_SECRET_LEN = 48


class KeyLogError(ValueError):
    """密钥日志格式非法。"""


def format_line(client_random: bytes, secret: bytes) -> str:
    if len(client_random) != CLIENT_RANDOM_LEN:
        raise KeyLogError(f"client_random must be {CLIENT_RANDOM_LEN} bytes, got {len(client_random)}")
    if len(secret) != MASTER_SECRET_LEN:
        raise KeyLogError(f"secret must be {MASTER_SECRET_LEN} bytes, got {len(secret)}")
    return f"CLIENT_RANDOM {client_random.hex()} {secret.hex()}"


def export_sslkeylog(secrets: Sequence[Tuple[bytes, bytes]]) -> str:
    """按 client_random 去重（首个优先）并排序输出。"""
    unique: Dict[bytes, bytes] = {}
    for client_random, secret in secrets:
        if client_random in unique:
            continue
        unique[client_random] = secret
    lines = [format_line(client_random, unique[client_random]) for client_random in sorted(unique)]
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def parse_sslkeylog(text: str) -> List[Tuple[bytes, bytes]]:
    entries: List[Tuple[bytes, bytes]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 3 or parts[0] != "CLIENT_RANDOM":
            raise KeyLogError(f"malformed line: {line!r}")
        try:
            client_random = bytes.fromhex(parts[1])
            secret = bytes.fromhex(parts[2])
        except ValueError as exc:
            raise KeyLogError(f"malformed hex in line: {line!r}") from exc
        if len(client_random) != CLIENT_RANDOM_LEN or len(secret) != MASTER_SECRET_LEN:
            raise KeyLogError(f"bad lengths in line: {line!r}")
        entries.append((client_random, secret))
    return entries
