from __future__ import annotations

import pytest

from tests.helpers import make_session
from traffic_agent.analysis.diff import (
    ChangeKind,
    DiffEngine,
    EndpointKey,
    RegressionReport,
    Severity,
    body_signature,
    normalize_shape,
    top_level_fields,
)
from traffic_agent.analysis.proto_infer import BinaryProtocolInference, InferredProtocol


class TestNormalizeShape:
    def test_scalars(self):
        assert normalize_shape(True) == "bool"
        assert normalize_shape(False) == "bool"
        assert normalize_shape(1) == "int"
        assert normalize_shape(1.5) == "float"
        assert normalize_shape("s") == "str"
        assert normalize_shape(None) == "null"

    def test_bool_not_int(self):
        assert normalize_shape(True) != normalize_shape(1)

    def test_dict_sorted_keys(self):
        assert normalize_shape({"b": 1, "a": "x"}) == "{a:str,b:int}"

    def test_nested(self):
        value = {"z": {"inner": [1, 2, 3]}, "a": None}
        assert normalize_shape(value) == "{a:null,z:{inner:[int]}}"

    def test_lists(self):
        assert normalize_shape([]) == "[]"
        assert normalize_shape([1, 2, 3]) == "[int]"
        assert normalize_shape(["a", "b"]) == "[str]"


class TestBodySignature:
    def test_empty(self):
        assert body_signature(b"") == "empty"

    def test_json(self):
        assert body_signature(b'{"a": 1}') == "{a:int}"

    def test_binary(self):
        sig = body_signature(b"\x00\x01\x02")
        assert sig.startswith("raw:")
        assert len(sig) == 4 + 12

    def test_different_bodies_same_shape_same_signature(self):
        # 结构签名只看类型形状，不看具体值
        assert body_signature(b'{"a":1}') == body_signature(b'{"a":2}')

    def test_different_shapes_different_signature(self):
        assert body_signature(b'{"a":1}') != body_signature(b'{"a":"x"}')
        assert body_signature(b'{"a":1}') != body_signature(b'{"a":1,"b":2}')
        assert body_signature(b'[1,2]') != body_signature(b'{"a":1}')


class TestTopLevelFields:
    def test_dict(self):
        assert top_level_fields({"a": 1, "b": 2}) == {"a", "b"}

    def test_non_dict(self):
        assert top_level_fields([1, 2]) == set()
        assert top_level_fields("x") == set()
        assert top_level_fields(None) == set()


class TestDiffEngine:
    def test_identical_sessions_no_entries(self):
        baseline = [make_session(host="a.io", path="/x", body=b'{"k":1}', started_at=1.0)]
        candidate = [make_session(host="a.io", path="/x", body=b'{"k":1}', started_at=2.0)]
        report = DiffEngine().diff(baseline, candidate)
        assert report.entries == []
        assert report.baseline_count == 1
        assert report.candidate_count == 1
        assert report.counts() == {"added": 0, "removed": 0, "status_changed": 0, "schema_changed": 0, "header_changed": 0}

    def test_added_endpoint(self):
        baseline = [make_session(host="a.io", path="/x", started_at=1.0)]
        candidate = [
            make_session(host="a.io", path="/x", started_at=1.0),
            make_session(host="a.io", path="/new", started_at=2.0),
        ]
        report = DiffEngine().diff(baseline, candidate)
        assert report.counts()["added"] == 1
        entry = report.entries[0]
        assert entry.change is ChangeKind.ADDED
        assert entry.severity is Severity.INFO

    def test_removed_endpoint(self):
        baseline = [
            make_session(host="a.io", path="/x", started_at=1.0),
            make_session(host="a.io", path="/gone", started_at=2.0),
        ]
        candidate = [make_session(host="a.io", path="/x", started_at=1.0)]
        report = DiffEngine().diff(baseline, candidate)
        assert report.counts()["removed"] == 1
        assert report.entries[0].severity is Severity.WARNING

    def test_status_change_5xx_breaking(self):
        baseline = [make_session(host="a.io", path="/x", status=200, started_at=1.0)]
        candidate = [make_session(host="a.io", path="/x", status=500, started_at=2.0)]
        report = DiffEngine().diff(baseline, candidate)
        entry = report.entries[0]
        assert entry.change is ChangeKind.STATUS_CHANGED
        assert entry.severity is Severity.BREAKING
        assert entry.baseline_status == 200
        assert entry.candidate_status == 500
        assert [e.key.as_text() for e in report.breaking()] == ["GET a.io/x"]

    def test_status_change_2xx_to_4xx_breaking(self):
        baseline = [make_session(host="a.io", path="/x", status=200)]
        candidate = [make_session(host="a.io", path="/x", status=404)]
        report = DiffEngine().diff(baseline, candidate)
        assert report.entries[0].severity is Severity.BREAKING

    def test_status_change_within_4xx_warning(self):
        baseline = [make_session(host="a.io", path="/x", status=404)]
        candidate = [make_session(host="a.io", path="/x", status=410)]
        report = DiffEngine().diff(baseline, candidate)
        assert report.entries[0].severity is Severity.WARNING
        assert report.breaking() == []

    def test_status_change_3xx_warning(self):
        baseline = [make_session(host="a.io", path="/x", status=200)]
        candidate = [make_session(host="a.io", path="/x", status=301)]
        report = DiffEngine().diff(baseline, candidate)
        assert report.entries[0].severity is Severity.WARNING

    def test_schema_missing_field_breaking(self):
        baseline = [make_session(host="a.io", path="/x", body=b'{"a":1,"b":2}')]
        candidate = [make_session(host="a.io", path="/x", body=b'{"a":1}')]
        report = DiffEngine().diff(baseline, candidate)
        entry = report.entries[0]
        assert entry.change is ChangeKind.SCHEMA_CHANGED
        assert entry.severity is Severity.BREAKING
        assert "b" in entry.detail

    def test_schema_added_field_warning(self):
        baseline = [make_session(host="a.io", path="/x", body=b'{"a":1}')]
        candidate = [make_session(host="a.io", path="/x", body=b'{"a":1,"c":2}')]
        report = DiffEngine().diff(baseline, candidate)
        entry = report.entries[0]
        assert entry.change is ChangeKind.SCHEMA_CHANGED
        assert entry.severity is Severity.WARNING

    def test_non_json_body_change(self):
        baseline = [make_session(host="a.io", path="/x", body=b"<html>old</html>")]
        candidate = [make_session(host="a.io", path="/x", body=b"<html>new</html>")]
        report = DiffEngine().diff(baseline, candidate)
        assert report.counts()["schema_changed"] == 1
        assert report.entries[0].severity is Severity.WARNING

    def test_header_change_info(self):
        baseline = [make_session(host="a.io", path="/x", response_headers={"x-a": "1"})]
        candidate = [make_session(host="a.io", path="/x", response_headers={"x-b": "2"})]
        report = DiffEngine().diff(baseline, candidate)
        entry = [e for e in report.entries if e.change is ChangeKind.HEADER_CHANGED][0]
        assert entry.severity is Severity.INFO

    def test_sessions_without_request_ignored(self):
        baseline = [make_session()]
        candidate = [make_session()]
        baseline[0].request = None
        report = DiffEngine().diff(baseline, candidate)
        assert report.baseline_count == 0
        assert report.candidate_count == 1

    def test_method_distinguishes_endpoints(self):
        baseline = [make_session(method="GET", path="/x", host="a.io")]
        candidate = [make_session(method="POST", path="/x", host="a.io")]
        report = DiffEngine().diff(baseline, candidate)
        assert report.counts()["removed"] == 1
        assert report.counts()["added"] == 1

    def test_mark_expected_excludes_from_breaking(self):
        baseline = [make_session(host="a.io", path="/x", status=200)]
        candidate = [make_session(host="a.io", path="/x", status=500)]
        engine = DiffEngine()
        report = engine.diff(baseline, candidate)
        assert len(report.breaking()) == 1
        engine.mark_expected(report, ["GET a.io/x"])
        assert report.breaking() == []
        assert report.entries[0].expected is True

    def test_report_to_dict(self):
        baseline = [make_session(host="a.io", path="/x", status=200)]
        candidate = [make_session(host="a.io", path="/x", status=500)]
        report = DiffEngine().diff(baseline, candidate)
        d = report.to_dict()
        assert d["baseline_count"] == 1
        assert d["candidate_count"] == 1
        assert d["breaking"] == ["GET a.io/x"]
        assert d["entries"][0]["change"] == "status_changed"
        assert d["entries"][0]["severity"] == "breaking"

    def test_endpoint_key_from_session_without_request(self):
        session = make_session()
        session.request = None
        with pytest.raises(ValueError):
            EndpointKey.from_session(session)


class TestRegressionReportDefaults:
    def test_empty_report(self):
        report = RegressionReport()
        assert report.entries == []
        assert report.breaking() == []
        assert report.to_dict()["counts"] == {
            "added": 0, "removed": 0, "status_changed": 0, "schema_changed": 0, "header_changed": 0,
        }


# ---------------------------------------------------------------------------
# 二进制协议推断
# ---------------------------------------------------------------------------

class TestBinaryProtocolInference:
    def test_empty_samples_raises(self):
        with pytest.raises(ValueError):
            BinaryProtocolInference().infer([])

    @pytest.mark.parametrize(
        "samples,expected_framing",
        [
            ([b"\x03abc", b"\x02xy"], "length_prefix_u8"),
            ([b"\x00\x03abc", b"\x00\x02xy"], "length_prefix_be16"),
            ([b"\x03\x00abc", b"\x02\x00xy"], "length_prefix_le16"),
            ([b"\x00\x00\x00\x03abc", b"\x00\x00\x00\x02xy"], "length_prefix_be32"),
            ([b"\x03\x00\x00\x00abc", b"\x02\x00\x00\x00xy"], "length_prefix_le32"),
        ],
    )
    def test_length_prefix_detection(self, samples, expected_framing):
        result = BinaryProtocolInference().infer(samples)
        assert result.framing == expected_framing
        assert result.confidence == 0.9
        assert result.sample_count == len(samples)
        assert [f.type for f in result.fields] == ["length", "payload"]
        assert result.fields[0].name == "length"
        assert result.fields[0].offset == 0
        assert result.fields[0].length == len(samples[0][0:1]) * (2 if "16" in expected_framing else (4 if "32" in expected_framing else 1))

    def test_u8_prefix_fields(self):
        result = BinaryProtocolInference().infer([b"\x03abc"])
        assert result.fields[0].to_dict() == {"name": "length", "offset": 0, "length": 1, "type": "length"}
        assert result.fields[1].to_dict() == {"name": "payload", "offset": 1, "length": 3, "type": "payload"}
        assert result.to_dict()["framing"] == "length_prefix_u8"

    def test_positional_constants_and_text(self):
        samples = [b"ID:1", b"ID:2", b"ID:3"]
        result = BinaryProtocolInference().infer(samples)
        assert result.framing == "positional"
        types = [f.type for f in result.fields]
        assert types == ["constant", "text"]
        assert result.fields[0].length == 3  # "ID:"
        assert result.fields[1].length == 1
        assert result.confidence == 1.0

    def test_positional_binary(self):
        samples = [b"\xaa\x01", b"\xab\x02", b"\xac\x03"]
        result = BinaryProtocolInference().infer(samples)
        # 第 0 位可打印且恒定 → constant；第 1 位值不同且可打印 → text
        assert result.framing == "positional"

    def test_identical_samples_all_constant(self):
        result = BinaryProtocolInference().infer([b"\xff\xee", b"\xff\xee"])
        assert all(f.type == "constant" for f in result.fields)
        # 相邻同类位置合并为单个字段
        assert len(result.fields) == 1
        assert result.fields[0].name == "constant_1"
        assert result.fields[0].length == 2
        assert result.confidence == 1.0

    def test_positional_binary_merged(self):
        samples = [b"\x01\x02", b"\x03\x04", b"\x05\x06"]
        result = BinaryProtocolInference().infer(samples)
        # 两个位置均为非可打印且值不同 → 合并为一个 binary 字段
        assert [f.type for f in result.fields] == ["binary"]
        assert result.fields[0].length == 2
        assert result.fields[0].name == "binary_1"
        assert result.confidence == 0.0

    def test_merge_adjacent_classes(self):
        fields = BinaryProtocolInference._merge(["constant", "constant", "text", "binary", "binary", "text"])
        assert [(f.type, f.offset, f.length) for f in fields] == [
            ("constant", 0, 2),
            ("text", 2, 1),
            ("binary", 3, 2),
            ("text", 5, 1),
        ]
        assert [f.name for f in fields] == ["constant_1", "text_1", "binary_1", "text_2"]

    def test_ascii_ratio_boundary(self):
        # pos0：值全不同且非可打印 → binary；pos1：一半可打印（0.5 < 0.9）→ binary
        samples = [b"\x01\x41", b"\x02\x42", b"\x03\x01", b"\x04\x02"]
        result = BinaryProtocolInference().infer(samples)
        assert result.framing == "positional"
        assert [f.type for f in result.fields] == ["binary"]
        assert result.fields[0].offset == 0
        assert result.fields[0].length == 2
