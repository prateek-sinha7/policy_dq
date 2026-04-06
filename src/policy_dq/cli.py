import click
import csv
import yaml

from policy_dq.validators.engine import run_validation
from policy_dq.reporters.json_reporter import generate_json_report
from policy_dq.reporters.markdown_reporter import generate_markdown_report
from policy_dq.reporters.console_reporter import print_summary
from policy_dq.mcp.rule_loader import MCPRuleLoader


def load_csv(path):

    with open(path) as f:

        reader = csv.DictReader(f)

        return list(reader)


def load_yaml(path):

    with open(path) as f:

        return yaml.safe_load(f)["rules"]


@click.group()
def cli():
    pass


@cli.command()
@click.argument("data_path")
@click.argument("rules_path")
@click.option(
    "--output-format",
    default="console",
    type=click.Choice(
        ["console", "json", "markdown"]
    ),
)
def validate(
    data_path,
    rules_path,
    output_format,
):

    data = load_csv(data_path)

    loader = MCPRuleLoader(rules_path)

    # rules = load_yaml(rules_path)
    rules = loader.load_rules()

    errors = run_validation(
        data,
        rules,
    )

    if output_format == "console":

        print_summary(errors)

    elif output_format == "json":

        generate_json_report(
            errors,
            "report.json",
        )

    elif output_format == "markdown":

        generate_markdown_report(
            errors,
            "report.md",
        )


@cli.command()
@click.argument("rules_path")
def summarize(rules_path):

    loader = MCPRuleLoader(rules_path)

    rules = loader.load_rules()

    print(f"{len(rules)} rules found")

    for r in rules:

        print(
            f"{r['name']} ({r['type']})"
        )


if __name__ == "__main__":

    cli()