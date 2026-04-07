import logging
from typing import Any

from policy_dq.models import ValidationError

logger = logging.getLogger(__name__)

# Restrict eval sandbox — no builtins, no globals
_EVAL_GLOBALS: dict[str, Any] = {"__builtins__": {}}


def validate_cross_field(data: list[dict[str, Any]], rule: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    fields: list[str] = rule["fields"]
    condition: str = rule["condition"]
    field_label = ",".join(fields)

    for i, row in enumerate(data):
        context = {f: row.get(f) for f in fields}
        try:
            if not eval(condition, _EVAL_GLOBALS, context):  # noqa: S307
                logger.debug("Row %d: cross-field condition failed: %s", i, condition)
                errors.append(ValidationError(
                    rule_name=rule["name"],
                    field=field_label,
                    message="cross field condition failed",
                    row=i,
                ))
        except Exception as exc:
            logger.warning("Row %d: error evaluating cross-field rule '%s': %s", i, rule["name"], exc)
            errors.append(ValidationError(
                rule_name=rule["name"],
                field=field_label,
                message="invalid cross-field rule",
                row=i,
            ))

    return errors
