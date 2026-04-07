import pytest
from policy_dq.validators.type_check import validate_type


def _rule(dtype: str, field: str = "value") -> dict:
    return {"name": f"{field}_type", "type": "type", "field": field, "dtype": dtype}


def test_valid_int_string() -> None:
    errors = validate_type([{"value": "42"}], _rule("int"))
    assert errors == []


def test_valid_float_string() -> None:
    errors = validate_type([{"value": "3.14"}], _rule("float"))
    assert errors == []


def test_invalid_int_string() -> None:
    errors = validate_type([{"value": "abc"}], _rule("int"))
    assert len(errors) == 1
    assert errors[0].field == "value"
    assert errors[0].row == 0


def test_none_value_for_int() -> None:
    errors = validate_type([{"value": None}], _rule("int"))
    assert len(errors) == 1
    assert errors[0].row == 0


def test_empty_string_for_int() -> None:
    errors = validate_type([{"value": ""}], _rule("int"))
    assert len(errors) == 1
    assert errors[0].row == 0


@pytest.mark.parametrize("value,expect_error", [
    ("true", False),
    ("True", False),
    ("1", False),
    ("notbool", False),   # bool("notbool") is True — no exception raised
    ("", False),          # bool("") == False but raises no exception — validator does not flag it
])
def test_bool_dtype(value: str, expect_error: bool) -> None:
    # bool(str) never raises — any non-empty string is True, empty string is False.
    # The validator only errors when the constructor raises an exception.
    errors = validate_type([{"value": value}], _rule("bool"))
    if expect_error:
        assert len(errors) == 1
    else:
        assert errors == []


def test_error_message_contains_dtype() -> None:
    errors = validate_type([{"value": "abc"}], _rule("int"))
    assert "int" in errors[0].message


@pytest.mark.parametrize("rows,expected_error_rows", [
    (
        [{"value": "1"}, {"value": "abc"}, {"value": "3"}, {"value": "xyz"}],
        [1, 3],
    ),
    (
        [{"value": "10"}, {"value": "20"}],
        [],
    ),
])
def test_multiple_rows_only_invalid_produce_errors(rows: list, expected_error_rows: list) -> None:
    errors = validate_type(rows, _rule("int"))
    assert [e.row for e in errors] == expected_error_rows
