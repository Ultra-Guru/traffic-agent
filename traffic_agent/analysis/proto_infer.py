"""L3 二进制协议推断：给定样本，提出字段分割假设（对应 SPEC v2.0 §1.1）。

Agent 辅助逆向：LLM 提出字段分割假设，本插件做确定性验证——
先尝试长度前缀定界（u8 / be16 / le16 / be32 / le32），
再退回逐位置分类（constant / text / binary）并合并相邻同类段。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

ASCII_PRINTABLE_LOW = 0x20
ASCII_PRINTABLE_HIGH = 0x7E


@dataclass
class InferredField:
    name: str
    offset: int
    length: int
    type: str  # constant | text | binary | length | payload

    def to_dict(self) -> dict:
        return {"name": self.name, "offset": self.offset, "length": self.length, "type": self.type}


@dataclass
class InferredProtocol:
    framing: str
    fields: List[InferredField]
    confidence: float
    sample_count: int

    def to_dict(self) -> dict:
        return {
            "framing": self.framing,
            "confidence": round(self.confidence, 3),
            "sample_count": self.sample_count,
            "fields": [f.to_dict() for f in self.fields],
        }


_LENGTH_PREFIX_CANDIDATES = (
    (1, "big", "length_prefix_u8"),
    (2, "big", "length_prefix_be16"),
    (2, "little", "length_prefix_le16"),
    (4, "big", "length_prefix_be32"),
    (4, "little", "length_prefix_le32"),
)


class BinaryProtocolInference:
    def infer(self, samples: Sequence[bytes]) -> InferredProtocol:
        if not samples:
            raise ValueError("no samples provided")
        normalized = [bytes(s) for s in samples]
        for width, byteorder, framing in _LENGTH_PREFIX_CANDIDATES:
            if all(len(s) > width for s in normalized):
                values = [int.from_bytes(s[:width], byteorder) for s in normalized]
                if all(v == len(s) - width for v, s in zip(values, normalized)):
                    fields = [
                        InferredField("length", 0, width, "length"),
                        InferredField("payload", width, len(normalized[0]) - width, "payload"),
                    ]
                    return InferredProtocol(
                        framing=framing, fields=fields, confidence=0.9, sample_count=len(normalized)
                    )
        return self._infer_positional(normalized)

    def _infer_positional(self, samples: List[bytes]) -> InferredProtocol:
        common = min(len(s) for s in samples)
        classes: List[str] = []
        for pos in range(common):
            column = {s[pos] for s in samples}
            if len(column) == 1:
                classes.append("constant")
            elif self._ascii_ratio(samples, pos) >= 0.9:
                classes.append("text")
            else:
                classes.append("binary")
        fields = self._merge(classes)
        avg_len = sum(len(s) for s in samples) / len(samples)
        explained = sum(f.length for f in fields if f.type in ("constant", "text"))
        confidence = min(1.0, explained / avg_len) if avg_len > 0 else 0.0
        return InferredProtocol(
            framing="positional", fields=fields, confidence=confidence, sample_count=len(samples)
        )

    @staticmethod
    def _ascii_ratio(samples: List[bytes], pos: int) -> float:
        printable = sum(1 for s in samples if ASCII_PRINTABLE_LOW <= s[pos] <= ASCII_PRINTABLE_HIGH)
        return printable / len(samples)

    @staticmethod
    def _merge(classes: List[str]) -> List[InferredField]:
        """相邻同类位置合并为一个字段。"""
        fields: List[InferredField] = []
        counters: Dict[str, int] = {}
        start = 0
        for i in range(1, len(classes) + 1):
            if i == len(classes) or classes[i] != classes[start]:
                kind = classes[start]
                counters[kind] = counters.get(kind, 0) + 1
                fields.append(InferredField(f"{kind}_{counters[kind]}", start, i - start, kind))
                start = i
        return fields
