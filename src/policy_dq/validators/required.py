import logging

from policy_dq.models import ValidationError

logger = logging.getLogger(__name__)


def validate_required(data, rule):
    errors = []
    field = rule["field"]

    for i, row in enumerate(data):
        if not row.get(field):
            logger.debug("Row %d: required field '%s' is missing", i, field)
            errors.append(ValidationError(
                rule_name=rule["name"],
                field=field,
                message="field is required",
                row=i,
            ))

    return errors
