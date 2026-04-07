# Policy Data Quality Engine

A rule-based data quality validation framework for data engineers and ML engineers.

## Features

- YAML/JSON rule configuration
- CLI interface with config file support
- REST API with Swagger UI
- Multiple validators (required, regex, range, type, unique, cross-field, email, phone)
- Multiple output formats (console, JSON, markdown)
- Structured logging with debug mode

## Installation

```bash
uv sync
uv pip install -e .
```

## Supported Rules

| Rule | Description |
|------|-------------|
| `required` | Field must be present and non-empty |
| `regex` | Value must match a regex pattern |
| `range` | Numeric value must be within `min`/`max` bounds |
| `type` | Value must be coercible to `dtype` (`int`, `float`, `str`, `bool`) |
| `unique` | All values in the field must be unique across rows |
| `cross_field` | Multi-field condition evaluated as a Python expression |
| `email` | Value must be a valid email address |
| `phone` | Value must be a valid phone number |

## Rule Sources

Rules can be loaded from multiple sources:

| Source | Example |
|--------|---------|
| Local YAML file | `rules.yaml` or `rules.yml` |
| Local JSON file | `rules.json` |
| HTTP/HTTPS API | `https://example.com/rules` |
| MCP URI (legacy) | `mcp://localhost:8000/rules` → resolved to `http://` |

The API endpoint must return a JSON body with a top-level `"rules"` key.

## CLI Usage

### Validate a dataset

```bash
uv run policy-dq validate sample_data/customer_invalid.csv sample_rules/customer_rules.yaml
```

### Change output format

```bash
# JSON report → report.json
uv run policy-dq validate sample_data/customer_invalid.csv sample_rules/customer_rules.yaml --output-format json

# Markdown report → report.md
uv run policy-dq validate sample_data/customer_invalid.csv sample_rules/customer_rules.yaml --output-format markdown
```

### Summarize rules

```bash
uv run policy-dq summarize sample_rules/customer_rules.yaml
```

### Enable debug logging

```bash
uv run policy-dq --verbose validate sample_data/customer_invalid.csv sample_rules/customer_rules.yaml
```

## API Server

Start the REST API server:

```bash
uv run uvicorn policy_dq.api:app --reload
```

The server starts on `http://localhost:8000` by default.

| URL | Description |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI (interactive) |
| `http://localhost:8000/redoc` | ReDoc |
| `http://localhost:8000/openapi.json` | Raw OpenAPI spec |

### Available endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/validate` | Validate a dataset against rules |
| `GET` | `/rules/summarize` | List rules from a source |
| `GET` | `/health` | Liveness check |

## Run Tests

```bash
uv run pytest
```

Run with verbose output:

```bash
uv run pytest -v
```

## Lint and Type Check

```bash
uv run ruff check src/ tests/
uv run mypy --strict src/
```
