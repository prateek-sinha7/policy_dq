import pytest
from policy_dq.validators.uniqueness import validate_unique


RULE = {"name": "unique_id", "type": "unique", "field": "id"}


def test_all_unique_no_errors() -> None:
    data = [{"id": 1}, {"id": 2}, {"id": 3}]
    errors = validate_unique(data, RULE)
    assert errors == []


def test_one_duplicate_error_on_second_occurrence() -> None:
    data = [{"id": "a"}, {"id": "b"}, {"id": "a"}]
    errors = validate_unique(data, RULE)
    assert len(errors) == 1
    assert errors[0].row == 2
    assert errors[0].message == "duplicate value"


def test_multiple_duplicates_of_same_value() -> None:
    data = [{"id": "x"}, {"id": "x"}, {"id": "x"}]
    errors = validate_unique(data, RULE)
    assert len(errors) == 2
    assert [e.row for e in errors] == [1, 2]


def test_two_none_values_produce_duplicate_error() -> None:
    data = [{"id": None}, {"id": None}]
    errors = validate_unique(data, RULE)
    assert len(errors) == 1
    assert errors[0].row == 1


def test_mixed_types_treated_as_distinct() -> None:
    # "1" (str) and 1 (int) are different values — no duplicate
    data = [{"id": "1"}, {"id": 1}]
    errors = validate_unique(data, RULE)
    assert errors == []


@pytest.mark.parametrize("rows,expected_error_rows", [
    (
        [{"id": 1}, {"id": 2}, {"id": 1}, {"id": 3}, {"id": 2}],
        [2, 4],
    ),
    (
        [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        [],
    ),
])
def test_multiple_rows(rows: list, expected_error_rows: list) -> None:
    errors = validate_unique(rows, RULE)
    assert [e.row for e in errors] == expected_error_rows
