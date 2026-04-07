import json
from policy_dq.models import ValidationError
from policy_dq.reporters.json_reporter import generate_json_report


def test_empty_errors_creates_empty_array(tmp_path) -> None:
    out = tmp_path / "report.json"
    generate_json_report([], out)
    assert out.exists()
    assert json.loads(out.read_text()) == []


def test_single_error_correct_keys(tmp_path) -> None:
    error = ValidationError(rule_name="r1", field="age", message="invalid", row=0)
    out = tmp_path / "report.json"
    generate_json_report([error], out)
    data = json.loads(out.read_text())
    assert len(data) == 1
    record = data[0]
    assert record["rule_name"] == "r1"
    assert record["field"] == "age"
    assert record["message"] == "invalid"
    assert record["row"] == 0


def test_multiple_errors_serialised_in_order(tmp_path) -> None:
    errors = [
        ValidationError(rule_name="r1", field="a", message="m1", row=0),
        ValidationError(rule_name="r2", field="b", message="m2", row=1),
        ValidationError(rule_name="r3", field="c", message="m3", row=2),
    ]
    out = tmp_path / "report.json"
    generate_json_report(errors, out)
    data = json.loads(out.read_text())
    assert len(data) == 3
    assert [r["rule_name"] for r in data] == ["r1", "r2", "r3"]
    assert [r["row"] for r in data] == [0, 1, 2]


def test_output_is_valid_json(tmp_path) -> None:
    errors = [ValidationError(rule_name="x", field="f", message="msg", row=5)]
    out = tmp_path / "report.json"
    generate_json_report(errors, out)
    # json.loads raises if invalid
    parsed = json.loads(out.read_text())
    assert isinstance(parsed, list)


def test_severity_not_included_in_output(tmp_path) -> None:
    error = ValidationError(rule_name="r1", field="f", message="m", row=0, severity="warning")
    out = tmp_path / "report.json"
    generate_json_report([error], out)
    record = json.loads(out.read_text())[0]
    assert "severity" not in record
