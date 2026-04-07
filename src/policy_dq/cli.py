import csv
import logging

import click

from policy_dq.logging_config import setup_logging
from policy_dq.reporters.console_reporter import print_summary
from policy_dq.reporters.json_reporter import generate_json_report
from policy_dq.reporters.markdown_reporter import generate_markdown_report
from policy_dq.rules.loader import load_rules
from policy_dq.validators.engine import run_validation

logger = logging.getLogger(__name__)


def load_csv(path: str) -> list[dict]:
    logger.debug("Loading CSV from %s", path)
    with open(path) as f:
        return list(csv.DictReader(f))


@click.group()
@click.option("--verbose", is_flag=True, default=False, help="Enable debug logging.")
def cli(verbose: bool) -> None:
    setup_logging(level=logging.DEBUG if verbose else logging.INFO)


@cli.command()
@click.argument("data_path")
@click.argument("rules_path")
@click.option(
    "--output-format",
    default="console",
    type=click.Choice(["console", "json", "markdown"]),
)
def validate(data_path: str, rules_path: str, output_format: str) -> None:
    data = load_csv(data_path)
    rules = load_rules(rules_path)
    errors = run_validation(data, rules)

    if output_format == "console":
        print_summary(errors)
    elif output_format == "json":
        generate_json_report(errors, "report.json")
    elif output_format == "markdown":
        generate_markdown_report(errors, "report.md")


@cli.command()
@click.argument("rules_path")
def summarize(rules_path: str) -> None:
    rules = load_rules(rules_path)
    logger.info("Summarizing %d rules from %s", len(rules), rules_path)
    print(f"{len(rules)} rules found")
    for r in rules:
        print(f"{r['name']} ({r['type']})")


if __name__ == "__main__":
    cli()
