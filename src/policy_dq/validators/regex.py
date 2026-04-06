import re
from policy_dq.models import ValidationError


def validate_regex(data, rule):

    errors = []

    pattern = re.compile(rule["pattern"])

    for i, row in enumerate(data):

        value = row.get(rule["field"])

        if value and not pattern.match(value):

            errors.append(
                ValidationError(
                    rule_name=rule["name"],
                    field=rule["field"],
                    message="regex failed",
                    row=i
                )
            )

    return errors