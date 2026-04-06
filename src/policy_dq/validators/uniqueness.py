from policy_dq.models import ValidationError


def validate_unique(data, rule):

    seen = set()

    errors = []

    for i, row in enumerate(data):

        value = row.get(rule["field"])

        if value in seen:

            errors.append(
                ValidationError(
                    rule_name=rule["name"],
                    field=rule["field"],
                    message="duplicate value",
                    row=i,
                )
            )

        seen.add(value)

    return errors