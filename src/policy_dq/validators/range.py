from policy_dq.models import ValidationError


def validate_range(data, rule):

    errors = []

    for i, row in enumerate(data):

        value = float(row.get(rule["field"], 0))

        if value < rule["min"] or value > rule["max"]:

            errors.append(
                ValidationError(
                    rule_name=rule["name"],
                    field=rule["field"],
                    message="value out of range",
                    row=i
                )
            )

    return errors