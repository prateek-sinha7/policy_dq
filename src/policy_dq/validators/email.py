import logging
import re

from policy_dq.models import ValidationError

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(data: list[dict], rule: dict) -> list[ValidationError]:
    errors = []
    field = rule["field"]

    for i, row in enumerate(data):
        value = row.get(field)
        if value and not _EMAIL_RE.match(str(value)):
            logger.debug("Row %d: invalid email '%s' in field '%s'", i, value, field)
            errors.append(ValidationError(
                rule_name=rule["name"],
                field=field,
                message="invalid email address",
                row=i,
            ))

    return errors
