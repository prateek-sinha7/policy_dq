import pytest
from policy_dq.validators.phone import validate_phone

RULE = {"name": "phone_format", "type": "phone", "field": "phone"}


@pytest.mark.parametrize("value", [
    "+18005550100",
    "+1-800-555-0100",
    "(800) 555-0100",
    "800.555.0100",
    "800-555-0100",
    "8005550100",
])
def test_valid_phones(value: str) -> None:
    errors = validate_phone([{"phone": value}], RULE)
    assert errors == []


@pytest.mark.parametrize("value", [
    "123",
    "not-a-phone",
    "12345",
    "++18005550100",
])
def test_invalid_phones(value: str) -> None:
    errors = validate_phone([{"phone": value}], RULE)
    assert len(errors) == 1
    assert errors[0].field == "phone"
    assert errors[0].row == 0


def test_empty_value_skipped() -> None:
    errors = validate_phone([{"phone": ""}], RULE)
    assert errors == []


def test_missing_field_skipped() -> None:
    errors = validate_phone([{}], RULE)
    assert errors == []


def test_multiple_rows() -> None:
    data = [
        {"phone": "800-555-0100"},
        {"phone": "bad"},
        {"phone": "(800) 555-0100"},
    ]
    errors = validate_phone(data, RULE)
    assert len(errors) == 1
    assert errors[0].row == 1
