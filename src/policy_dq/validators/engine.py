from typing import Any

import logging

from policy_dq.validators.required import validate_required
from policy_dq.validators.regex import validate_regex
from policy_dq.validators.range import validate_range
from policy_dq.validators.type_check import validate_type
from policy_dq.validators.uniqueness import validate_unique
from policy_dq.validators.cross_field import validate_cross_field
from policy_dq.validators.email import validate_email
from policy_dq.validators.phone import validate_phone
from policy_dq.models import ValidationError

logger = logging.getLogger(__name__)

ValidatorFn = Any  # callable[[list[dict], dict], list[ValidationError]]

VALIDATORS: dict[str, ValidatorFn] = {
    "required": validate_required,
    "regex": validate_regex,
    "range": validate_range,
    "type": validate_type,
    "unique": validate_unique,
    "cross_field": validate_cross_field,
    "email": validate_email,
    "phone": validate_phone,
}


def run_validation(data: list[dict[str, Any]], rules: list[dict[str, Any]]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    logger.info("Starting validation: %d rows, %d rules", len(data), len(rules))

    for rule in rules:
        rule_type = rule["type"]
        validator = VALIDATORS.get(rule_type)
        if not validator:
            logger.error("Unknown rule type: %s", rule_type)
            raise ValueError(f"unknown rule type {rule_type!r}")

        logger.debug("Running rule: %s (%s)", rule["name"], rule_type)
        rule_errors = validator(data, rule)
        if rule_errors:
            logger.debug("Rule '%s' found %d error(s)", rule["name"], len(rule_errors))
        errors.extend(rule_errors)

    logger.info("Validation complete: %d error(s) found", len(errors))
    return errors
