from policy_dq.models import ValidationError


def validate_cross_field(data, rule):

    errors = []

    fields = rule["fields"]

    for i, row in enumerate(data):

        context = {f: row.get(f) for f in fields}

        try:

            if not eval(rule["condition"], {}, context):

                errors.append(
                    ValidationError(
                        rule_name=rule["name"],
                        field=",".join(fields),
                        message="cross field condition failed",
                        row=i,
                    )
                )

        except Exception:

            errors.append(
                ValidationError(
                    rule_name=rule["name"],
                    field=",".join(fields),
                    message="invalid cross-field rule",
                    row=i,
                )
            )

    return errors