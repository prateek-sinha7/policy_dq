import pytest
from policy_dq.validators.cross_field import validate_cross_field


RULE = {
    "name": "date_order",
    "type": "cross_field",
    "fields": ["start_date", "end_date"],
    "condition": "end_date >= start_date",
}


def test_condition_passes_no_error() -> None:
    data = [{"start_date": 1, "end_date": 10}]
    errors = validate_cross_field(data, RULE)
    assert errors == []


def test_condition_fails_error() -> None:
    data = [{"start_date": 10, "end_date": 5}]
    errors = validate_cross_field(data, RULE)
    assert len(errors) == 1
    assert errors[0].field == "start_date,end_date"
    assert errors[0].message == "cross field condition failed"
    assert errors[0].row == 0


def test_field_set_to_comma_joined_names() -> None:
    data = [{"start_date": 10, "end_date": 5}]
    errors = validate_cross_field(data, RULE)
    assert errors[0].field == "start_date,end_date"


def test_missing_field_in_row_produces_error() -> None:
    # end_date missing → context has None → None >= 10 raises TypeError
    data = [{"start_date": 10}]
    errors = validate_cross_field(data, RULE)
    assert len(errors) == 1
    assert errors[0].message == "invalid cross-field rule"


def test_invalid_condition_expression_produces_error() -> None:
    rule = {
        "name": "bad_rule",
        "type": "cross_field",
        "fields": ["a", "b"],
        "condition": "a ??? b",
    }
    data = [{"a": 1, "b": 2}]
    errors = validate_cross_field(data, rule)
    assert len(errors) == 1
    assert errors[0].message == "invalid cross-field rule"


@pytest.mark.parametrize("rows,expected_error_rows", [
    (
        [
            {"start_date": 1, "end_date": 5},
            {"start_date": 10, "end_date": 3},
            {"start_date": 2, "end_date": 2},
        ],
        [1],
    ),
    (
        [
            {"start_date": 5, "end_date": 1},
            {"start_date": 5, "end_date": 1},
        ],
        [0, 1],
    ),
])
def test_multiple_rows_only_failing_produce_errors(rows: list, expected_error_rows: list) -> None:
    errors = validate_cross_field(rows, RULE)
    assert [e.row for e in errors] == expected_error_rows
