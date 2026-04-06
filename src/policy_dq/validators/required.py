from policy_dq.models import ValidationError


def validate_required(data, rule):

    errors = []

    for i, row in enumerate(data):

        if not row.get(rule["field"]):

            errors.append(
                ValidationError(
                    rule_name=rule["name"],
                    field=rule["field"],
                    message="field is required",
                    row=i
                )
            )

    return errors