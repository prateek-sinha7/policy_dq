import json
import logging

logger = logging.getLogger(__name__)


def generate_json_report(errors, output_path):
    logger.info("Writing JSON report to %s (%d errors)", output_path, len(errors))
    result = [
        {"rule_name": e.rule_name, "field": e.field, "message": e.message, "row": e.row}
        for e in errors
    ]
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    logger.debug("JSON report written successfully")
