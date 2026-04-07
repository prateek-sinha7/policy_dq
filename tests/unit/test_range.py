import pytest
from policy_dq.validators.range import validate_range


def _rule(min_val: float, max_val: float, field: str = "score") -> dict:
    return {"name": "score_range", "type": "range", "field": field, "min": min_val, "max": max_val}


def test_value_within_range() -> None:
    errors = validate_range([{"score": "50"}], _rule(0, 100))
    assert errors == []


def test_value_at_exact_min() -> None:
    errors = validate_range([{"score": "0"}], _rule(0, 100))
    assert errors == []


def test_value_at_exact_max() -> None:
    errors = validate_range([{"score": "100"}], _rule(0, 100))
    assert errors == []


def test_value_below_min() -> None:
    errors = validate_range([{"score": "-1"}], _rule(0, 100))
    assert len(errors) == 1
    assert errors[0].field == "score"
    assert errors[0].row == 0
    assert errors[0].message == "value out of range"


def test_value_above_max() -> None:
    errors = validate_range([{"score": "101"}], _rule(0, 100))
    assert len(errors) == 1
    assert errors[0].row == 0
    assert errors[0].message == "value out of range"


def test_non_numeric_string_skipped() -> None:
    errors = validate_range([{"score": "abc"}], _rule(0, 100))
    assert errors == []


def test_none_value_skipped() -> None:
    errors = validate_range([{"score": None}], _rule(0, 100))
    assert errors == []


def test_empty_string_skipped() -> None:
    errors = validate_range([{"score": ""}], _rule(0, 100))
    assert errors == []


@pytest.mark.parametrize("rows,expected_error_rows", [
    (
        [{"score": "10"}, {"score": "-5"}, {"score": "50"}, {"score": "200"}],
        [1, 3],
    ),
    (
        [{"score": "0"}, {"score": "100"}, {"score": "50"}],
        [],
    ),
])
def test_multiple_rows_only_out_of_range_produce_errors(rows: list, expected_error_rows: list) -> None:
    errors = validate_range(rows, _rule(0, 100))
    assert [e.row for e in errors] == expected_error_rows
