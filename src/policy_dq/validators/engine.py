from policy_dq.validators.required import validate_required
from policy_dq.validators.regex import validate_regex
from policy_dq.validators.range import validate_range
from policy_dq.validators.type_check import validate_type
from policy_dq.validators.uniqueness import validate_unique
from policy_dq.validators.cross_field import validate_cross_field


VALIDATORS = {

    "required": validate_required,
    "regex": validate_regex,
    "range": validate_range,
    "type": validate_type,
    "unique": validate_unique,
    "cross_field": validate_cross_field,
}


def run_validation(data, rules):

    errors = []

    for rule in rules:

        validator = VALIDATORS.get(rule["type"])

        if not validator:

            raise ValueError(
                f"unknown rule type {rule['type']}"
            )

        errors.extend(
            validator(data, rule)
        )

    return errors