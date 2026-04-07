import pytest
from policy_dq.validators.regex import validate_regex


RULE = {"name": "zip_format", "type": "regex", "field": "zip", "pattern": r"^\d{5}$"}


def test_matching_value_no_error() -> None:
    errors = validate_regex([{"zip": "12345"}], RULE)
    assert errors == []


def test_non_matching_value_error() -> None:
    errors = validate_regex([{"zip": "ABCDE"}], RULE)
    assert len(errors) == 1
    assert errors[0].field == "zip"
    assert errors[0].row == 0
    assert errors[0].message == "regex failed"


def test_empty_string_skipped() -> None:
    # regex validator uses `if value` — empty string is falsy, so skipped
    errors = validate_regex([{"zip": ""}], RULE)
    assert errors == []


def test_none_value_skipped() -> None:
    errors = validate_regex([{"zip": None}], RULE)
    assert errors == []


def test_missing_field_skipped() -> None:
    errors = validate_regex([{}], RULE)
    assert errors == []


def test_rule_name_and_field_on_error() -> None:
    errors = validate_regex([{"zip": "bad"}], RULE)
    assert errors[0].rule_name == "zip_format"
    assert errors[0].field == "zip"


@pytest.mark.parametrize("rows,expected_error_rows", [
    (
        [{"zip": "12345"}, {"zip": "bad"}, {"zip": "99999"}, {"zip": "1234"}],
        [1, 3],
    ),
    (
        [{"zip": "00000"}, {"zip": "54321"}],
        [],
    ),
])
def test_multiple_rows_only_non_matching_produce_errors(rows: list, expected_error_rows: list) -> None:
    errors = validate_regex(rows, RULE)
    assert [e.row for e in errors] == expected_error_rows
