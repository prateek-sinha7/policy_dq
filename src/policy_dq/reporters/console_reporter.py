import logging

logger = logging.getLogger(__name__)


def print_summary(errors):
    if not errors:
        logger.info("Validation passed with no errors")
        print("All validations passed")
        return

    logger.info("Validation complete: %d error(s)", len(errors))
    print(f"{len(errors)} validation errors found")
    for e in errors:
        print(f"{e.rule_name} | {e.field} | {e.message} | row {e.row}")
