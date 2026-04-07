import logging
from typing import Any

from policy_dq.models import ValidationError

logger = logging.getLogger(__name__)

TYPE_MAP: dict[str, type] = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
}


def validate_type(data: list[dict[str, Any]], rule: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    dtype = rule["dtype"]
    expected_type = TYPE_MAP.get(dtype)
    if expected_type is None:
        raise ValueError(f"unknown dtype {dtype!r}; supported: {list(TYPE_MAP)}")
    field = rule["field"]

    for i, row in enumerate(data):
        value = row.get(field)
        try:
            expected_type(value)
        except (ValueError, TypeError):
            logger.debug("Row %d: field '%s' value '%s' is not of type %s", i, field, value, dtype)
            errors.append(ValidationError(
                rule_name=rule["name"],
                field=field,
                message=f"invalid type expected {dtype}",
                row=i,
            ))

    return errors
