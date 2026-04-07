import logging

from policy_dq.models import ValidationError

logger = logging.getLogger(__name__)


def validate_range(data, rule):
    errors = []
    field = rule["field"]

    for i, row in enumerate(data):
        raw = row.get(field)
        if raw is None or raw == "":
            continue
        try:
            value = float(raw)
        except (ValueError, TypeError):
            logger.debug("Row %d: skipping non-numeric value '%s' for range check", i, raw)
            continue

        if value < rule["min"] or value > rule["max"]:
            logger.debug("Row %d: '%s' value %s out of range [%s, %s]", i, field, value, rule["min"], rule["max"])
            errors.append(ValidationError(
                rule_name=rule["name"],
                field=field,
                message="value out of range",
                row=i,
            ))

    return errors
