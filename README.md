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
|range| numeric bounds check; rows with missing or non-numeric values are skipped (type errors are handled by the `type` validator) |
|type| datatype check |
|unique| uniqueness |
|cross_field| multi-field logic |

## Installation

uv pip install -e .

## Rule Sources

Rules can be loaded from multiple sources:

| source | example |
|--------|---------|
| local YAML file | `rules.yaml` or `rules.yml` |
| local JSON file | `rules.json` |
| HTTP/HTTPS API | `https://example.com/rules` |
| MCP URI (legacy) | `mcp://localhost:8080/rules` → resolved to `http://` |

The API endpoint must return a JSON body with a top-level `"rules"` key.

## Run validation

policy-dq validate data.csv rules.yaml
policy-dq validate data.csv https://example.com/api/rules

Pass `--verbose` to enable debug-level logging for any command:

policy-dq --verbose validate data.csv rules.yaml

## Output formats

--output-format console
--output-format json
--output-format markdown

## API Server

Start the REST API server with:

```
policy-dq-api --app policy_dq.api:app --host 127.0.0.1 --port 8000
```

The API exposes the same validation logic over HTTP. See the FastAPI docs at `http://localhost:8000/docs` once the server is running.

## Run tests

uv run pytest