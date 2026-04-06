from policy_dq.models import ValidationError


TYPE_MAP = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
}


def validate_type(data, rule):

    errors = []

    expected_type = TYPE_MAP[rule["dtype"]]

    for i, row in enumerate(data):

        value = row.get(rule["field"])

        try:

            expected_type(value)

        except Exception:

            errors.append(
                ValidationError(
                    rule_name=rule["name"],
                    field=rule["field"],
                    message=f"invalid type expected {rule['dtype']}",
                    row=i,
                )
            )

    return errors