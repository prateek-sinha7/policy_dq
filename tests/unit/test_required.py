import pytest
from policy_dq.validators.required import validate_required

RULE = {"name": "email_required", "type": "required", "field": "email"}


def test_field_present_with_value() -> None:
    errors = validate_required([{"email": "user@example.com"}], RULE)
    assert errors == []


def test_field_present_empty_string() -> None:
    errors = validate_required([{"email": ""}], RULE)
    assert len(errors) == 1
    assert errors[0].field == "email"
    assert errors[0].row == 0


def test_field_missing_from_row() -> None:
    errors = validate_required([{}], RULE)
    assert len(errors) == 1
    assert errors[0].field == "email"
    assert errors[0].row == 0


def test_field_whitespace_only() -> None:
    # whitespace-only is falsy via not row.get(field) — "   " is truthy, so
    # the validator does NOT flag it; document actual behaviour here.
    # The current implementation uses `not row.get(field)`, so "   " passes.
    errors = validate_required([{"email": "   "}], RULE)
    # "   " is truthy — no error expected from current implementation
    assert errors == []


def test_rule_name_and_field_on_error() -> None:
    errors = validate_required([{"email": ""}], RULE)
    assert errors[0].rule_name == "email_required"
    assert errors[0].field == "email"


@pytest.mark.parametrize("rows,expected_error_rows", [
    (
        [{"email": "a@b.com"}, {"email": ""}, {"email": "c@d.com"}, {}],
        [1, 3],
    ),
    (
        [{"email": ""}, {"email": ""}, {"email": "ok@ok.com"}],
        [0, 1],
    ),
])
def test_multiple_rows_mixed(rows: list, expected_error_rows: list) -> None:
    errors = validate_required(rows, RULE)
    assert len(errors) == len(expected_error_rows)
    assert [e.row for e in errors] == expected_error_rows
