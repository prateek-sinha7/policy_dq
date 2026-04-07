from policy_dq.models import ValidationError
from policy_dq.reporters.markdown_reporter import generate_markdown_report


def test_empty_errors_header_only(tmp_path) -> None:
    out = tmp_path / "report.md"
    generate_markdown_report([], out)
    content = out.read_text()
    assert "# Validation Report" in content
    # header row and separator row present, but no data rows
    lines = [l for l in content.splitlines() if l.startswith("|")]
    assert len(lines) == 2  # header + separator


def test_single_error_one_data_row(tmp_path) -> None:
    error = ValidationError(rule_name="r1", field="age", message="invalid", row=3)
    out = tmp_path / "report.md"
    generate_markdown_report([error], out)
    content = out.read_text()
    data_lines = [l for l in content.splitlines() if l.startswith("|") and "---" not in l and "Rule" not in l]
    assert len(data_lines) == 1
    assert "r1" in data_lines[0]
    assert "age" in data_lines[0]
    assert "invalid" in data_lines[0]
    assert "3" in data_lines[0]


def test_multiple_errors_all_appear_as_rows(tmp_path) -> None:
    errors = [
        ValidationError(rule_name="r1", field="a", message="m1", row=0),
        ValidationError(rule_name="r2", field="b", message="m2", row=1),
        ValidationError(rule_name="r3", field="c", message="m3", row=2),
    ]
    out = tmp_path / "report.md"
    generate_markdown_report(errors, out)
    content = out.read_text()
    data_lines = [l for l in content.splitlines() if l.startswith("|") and "---" not in l and "Rule" not in l]
    assert len(data_lines) == 3
    assert "r1" in data_lines[0]
    assert "r2" in data_lines[1]
    assert "r3" in data_lines[2]


def test_output_starts_with_validation_report_header(tmp_path) -> None:
    out = tmp_path / "report.md"
    generate_markdown_report([], out)
    assert out.read_text().startswith("# Validation Report")


def test_none_field_rendered_as_none_string(tmp_path) -> None:
    error = ValidationError(rule_name="r1", field=None, message="msg", row=0)
    out = tmp_path / "report.md"
    generate_markdown_report([error], out)
    content = out.read_text()
    assert "None" in content
