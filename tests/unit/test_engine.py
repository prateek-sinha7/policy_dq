import pytest
from policy_dq.validators.engine import run_validation


def test_unknown_rule_type_raises_value_error() -> None:
    data = [{"field": "value"}]
    rules = [{"name": "bad_rule", "type": "nonexistent_type", "field": "field"}]
    with pytest.raises(ValueError, match="nonexistent_type"):
        run_validation(data, rules)


def test_empty_rules_returns_empty_list() -> None:
    data = [{"field": "value"}]
    errors = run_validation(data, [])
    assert errors == []


def test_empty_data_returns_empty_list() -> None:
    rules = [{"name": "r1", "type": "required", "field": "email"}]
    errors = run_validation([], rules)
    assert errors == []


def test_multiple_rules_errors_combined() -> None:
    data = [{"email": "", "age": "abc"}]
    rules = [
        {"name": "email_required", "type": "required", "field": "email"},
        {"name": "age_type", "type": "type", "field": "age", "dtype": "int"},
    ]
    errors = run_validation(data, rules)
    assert len(errors) == 2
    rule_names = {e.rule_name for e in errors}
    assert rule_names == {"email_required", "age_type"}


def test_rule_with_unknown_type_raises_with_type_name() -> None:
    data = [{"x": "1"}]
    rules = [{"name": "r1", "type": "totally_unknown", "field": "x"}]
    with pytest.raises(ValueError) as exc_info:
        run_validation(data, rules)
    assert "totally_unknown" in str(exc_info.value)
