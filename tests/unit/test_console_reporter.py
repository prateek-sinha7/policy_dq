from policy_dq.models import ValidationError
from policy_dq.reporters.console_reporter import print_summary


def test_empty_errors_prints_all_passed(capsys) -> None:
    print_summary([])
    captured = capsys.readouterr()
    assert "All validations passed" in captured.out


def test_single_error_prints_count_and_error_line(capsys) -> None:
    error = ValidationError(rule_name="r1", field="age", message="invalid", row=2)
    print_summary([error])
    captured = capsys.readouterr()
    assert "1" in captured.out
    assert "r1 | age | invalid | row 2" in captured.out


def test_multiple_errors_prints_correct_count_and_all_lines(capsys) -> None:
    errors = [
        ValidationError(rule_name="r1", field="a", message="m1", row=0),
        ValidationError(rule_name="r2", field="b", message="m2", row=1),
        ValidationError(rule_name="r3", field="c", message="m3", row=2),
    ]
    print_summary(errors)
    captured = capsys.readouterr()
    assert "3" in captured.out
    assert "r1 | a | m1 | row 0" in captured.out
    assert "r2 | b | m2 | row 1" in captured.out
    assert "r3 | c | m3 | row 2" in captured.out


def test_output_format_pipe_separated(capsys) -> None:
    error = ValidationError(rule_name="myrule", field="myfield", message="mymsg", row=7)
    print_summary([error])
    captured = capsys.readouterr()
    assert "myrule | myfield | mymsg | row 7" in captured.out
