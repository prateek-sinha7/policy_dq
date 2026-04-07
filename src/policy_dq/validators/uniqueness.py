import logging

from policy_dq.models import ValidationError

logger = logging.getLogger(__name__)


def validate_unique(data: list[dict], rule: dict) -> list[ValidationError]:
    seen: set[str] = set()
    errors: list[ValidationError] = []
    field = rule["field"]

    for i, row in enumerate(data):
        value = row.get(field)
        if value in seen:
            logger.debug("Row %d: duplicate value '%s' in field '%s'", i, value, field)
            errors.append(ValidationError(
                rule_name=rule["name"],
                field=field,
                message="duplicate value",
                row=i,
            ))
        seen.add(value)

    return errors
