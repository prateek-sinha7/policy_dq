import logging
import re

from policy_dq.models import ValidationError

logger = logging.getLogger(__name__)

_PHONE_RE = re.compile(
    r"^\+?1?\s*[-.]?\s*\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}$"
)


def validate_phone(data: list[dict], rule: dict) -> list[ValidationError]:
    errors = []
    field = rule["field"]

    for i, row in enumerate(data):
        value = row.get(field)
        if value and not _PHONE_RE.match(str(value)):
            logger.debug("Row %d: invalid phone '%s' in field '%s'", i, value, field)
            errors.append(ValidationError(
                rule_name=rule["name"],
                field=field,
                message="invalid phone number",
                row=i,
            ))

    return errors
