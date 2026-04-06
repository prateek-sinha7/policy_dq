# Policy Data Quality Engine

A rule-based data quality validation framework.

## Features

- YAML based rules
- CLI interface
- Multiple validators
- Multiple output formats
- MCP style rule loading
- Unit tested

## Supported Rules

| rule | description |
|------|------------|
|required| field must exist |
|regex| pattern validation |
|range| numeric bounds |
|type| datatype check |
|unique| uniqueness |
|cross_field| multi-field logic |

## Installation

uv pip install -e .

## Run validation

policy-dq validate data.csv rules.yaml

## Output formats

--output-format console
--output-format json
--output-format markdown

## Run tests

uv run pytest# policy_dq
# policy_dq
# policy_dq
# policy_dq
