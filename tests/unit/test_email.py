import pytest
from policy_dq.validators.email import validate_email

RULE = {"name": "email_format", "type": "email", "field": "email"}


@pytest.mark.parametrize("value", [
    "user@example.com",
    "user.name+tag@sub.domain.org",
    "x@y.io",
])
def test_valid_emails(value: str) -> None:
    errors = validate_email([{"email": value}], RULE)
    assert errors == []


@pytest.mark.parametrize("value", [
    "notanemail",
    "missing@tld",
    "@nodomain.com",
    "spaces @example.com",
])
def test_invalid_emails(value: str) -> None:
    errors = validate_email([{"email": value}], RULE)
    assert len(errors) == 1
    assert errors[0].field == "email"
    assert errors[0].row == 0


def test_empty_value_skipped() -> None:
    errors = validate_email([{"email": ""}], RULE)
    assert errors == []


def test_missing_field_skipped() -> None:
    errors = validate_email([{}], RULE)
    assert errors == []


def test_multiple_rows() -> None:
    data = [
        {"email": "good@example.com"},
        {"email": "bad-email"},
        {"email": "also@good.net"},
    ]
    errors = validate_email(data, RULE)
    assert len(errors) == 1
    assert errors[0].row == 1
