import logging

logger = logging.getLogger(__name__)


def generate_markdown_report(errors, output_path):
    logger.info("Writing Markdown report to %s (%d errors)", output_path, len(errors))
    lines = [
        "# Validation Report",
        "",
        "| Rule | Field | Message | Row |",
        "|------|-------|---------|-----|",
    ]
    for e in errors:
        lines.append(f"| {e.rule_name} | {e.field} | {e.message} | {e.row} |")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    logger.debug("Markdown report written successfully")
