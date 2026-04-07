# Implementation Plan: Config File Support

## Overview

Implement `policy_dq.config` for config discovery/parsing/validation, `policy_dq.server` as the
API entry point, wire both into the CLI (`src/policy_dq/cli.py`, which uses Click), and fix the
`policy-dq-api` entry point in `pyproject.toml`. Tests mirror the `src` structure using pytest +
Hypothesis. Add `hypothesis` as a dev dependency in `pyproject.toml`.

## Tasks

- [ ] 0. Expand edge-case test coverage for existing validators, reporters, and engine
  - [ ] 0.1 Expand `tests/unit/test_required.py`
    - field present with value → no error
    - field present but empty string → error
    - field missing from row entirely → error
    - field present with whitespace-only string → documents actual truthy behaviour
    - multiple rows: mix of valid and missing → assert correct error count and row indices
    - assert `rule_name` and `field` are set correctly on the error object
    - _Requirements: existing validator coverage_

  - [ ] 0.2 Expand `tests/unit/test_type.py`
    - valid int string "42" → no error
    - valid float string "3.14" for float dtype → no error
    - "abc" for int dtype → error
    - None value for int dtype → error
    - empty string for int dtype → error
    - bool dtype: "true" → no error, empty string → error
    - error message contains the dtype name
    - multiple rows: only invalid rows produce errors
    - _Requirements: existing validator coverage_

  - [ ] 0.3 Add `tests/unit/test_range.py`
    - value within range → no error
    - value at exact min boundary → no error
    - value at exact max boundary → no error
    - value below min → error with message "value out of range"
    - value above max → error with message "value out of range"
    - non-numeric string → skipped (no error)
    - None value → skipped
    - empty string → skipped
    - multiple rows: only out-of-range rows produce errors
    - _Requirements: existing validator coverage_

  - [ ] 0.4 Add `tests/unit/test_regex.py`
    - value matching pattern → no error
    - value not matching pattern → error with message "regex failed"
    - empty string → skipped (no error)
    - None / missing field → skipped
    - multiple rows: only non-matching rows produce errors
    - assert `rule_name` and `field` set correctly on error
    - _Requirements: existing validator coverage_

  - [ ] 0.5 Expand `tests/unit/test_unique.py`
    - all unique values → no errors
    - one duplicate → one error on the second occurrence row
    - multiple duplicates of same value → errors on all rows after first
    - None values: two None values → duplicate error
    - mixed types: "1" (str) and 1 (int) are treated as distinct (no error)
    - error message is "duplicate value"
    - _Requirements: existing validator coverage_

  - [ ] 0.6 Expand `tests/unit/test_cross_field.py`
    - condition passes → no error
    - condition fails → error with field set to comma-joined field names
    - missing field in row → error with message "invalid cross-field rule"
    - invalid condition expression → error with message "invalid cross-field rule"
    - multiple rows: only failing rows produce errors
    - error message is "cross field condition failed" for valid but failing condition
    - _Requirements: existing validator coverage_

  - [ ] 0.7 Expand `tests/unit/test_json_reporter.py`
    - empty errors list → file created with empty JSON array `[]`
    - single error → file contains correct keys: rule_name, field, message, row
    - multiple errors → all errors serialised in order
    - output file is valid JSON (use `json.loads` to verify)
    - severity field is NOT included in JSON output
    - _Requirements: existing reporter coverage_

  - [ ] 0.8 Add `tests/unit/test_markdown_reporter.py`
    - empty errors list → file contains header rows only, no data rows
    - single error → file contains one data row with correct values
    - multiple errors → all errors appear as table rows in order
    - output file starts with "# Validation Report"
    - None field value → rendered as "None" in table (does not crash)
    - _Requirements: existing reporter coverage_

  - [ ] 0.9 Add `tests/unit/test_console_reporter.py`
    - empty errors list → prints "All validations passed"
    - single error → prints count line and one error line
    - multiple errors → prints correct count and all error lines
    - output format: "rule_name | field | message | row N"
    - use `capsys` pytest fixture to capture stdout
    - _Requirements: existing reporter coverage_

  - [ ] 0.10 Expand `tests/unit/test_rule_loader.py`
    - `FileRuleLoader` with `.yml` extension → loads successfully
    - `FileRuleLoader` with missing file → raises `FileNotFoundError`
    - `APIRuleLoader` with custom timeout → passes timeout to `requests.get`
    - `get_loader` with `.json` extension → returns `FileRuleLoader`
    - `load_rules` with http source → returns rules from mocked API
    - _Requirements: existing loader coverage_

  - [ ] 0.11 Add `tests/unit/test_engine.py`
    - unknown rule type → raises `ValueError` with message containing the type name
    - empty rules list → returns empty errors list
    - empty data list → returns empty errors list
    - multiple rules applied → errors from all rules are combined
    - rule with unknown type → raises `ValueError` with type name in message
    - _Requirements: existing engine coverage_

- [ ] 1. Implement `policy_dq.config` module
  - [ ] 1.1 Create `src/policy_dq/config.py` with `AppConfig` dataclass and `ConfigValidationError`
    - Define `AppConfig` dataclass with all fields, types, and defaults from Requirements 2.3
    - Define `ConfigValidationError(ValueError)`
    - Add module-level docstring listing every Config_Key, type, default, and description
    - _Requirements: 2.1, 2.3, 5.1_

  - [ ] 1.2 Implement `_find_config_file` discovery logic in `src/policy_dq/config.py`
    - Walk from `start_dir` (default `Path.cwd()`) up to filesystem root via `path.parents`
    - At each level check `policy-dq.toml` first, then `pyproject.toml`
    - Return `tuple[Path, Literal["toml", "pyproject"]]` or `tuple[None, None]`
    - _Requirements: 1.1_

  - [ ] 1.3 Implement `_validate_and_build` and `load_config_from_dict` in `src/policy_dq/config.py`
    - Collect all keys not in `AppConfig.__dataclass_fields__`; raise `ConfigValidationError` listing each
    - Type-check each field; coerce `str → int` for `int`-typed fields via `int(value)`
    - Validate `Literal` fields against their `__args__`; raise `ConfigValidationError` naming key and allowed values
    - Return populated `AppConfig`
    - _Requirements: 1.4, 2.2, 2.4, 2.5, 6.3_

  - [ ] 1.4 Implement `load_config` and `config_to_dict` public functions in `src/policy_dq/config.py`
    - `load_config(start_dir: Path | None = None) -> AppConfig`: call `_find_config_file`, open with `tomllib.open`, delegate to `load_config_from_dict`; return `AppConfig()` when no file found
    - For `pyproject.toml`: extract only `data.get("tool", {}).get("policy-dq", {})` before passing to `load_config_from_dict`
    - `config_to_dict(config: AppConfig) -> dict[str, Any]`: use `dataclasses.asdict(config)`
    - _Requirements: 1.2, 1.3, 1.5, 6.1_

  - [ ] 1.5 Write unit tests for `config.py` in `tests/unit/test_config.py`
    - `load_config()` with no file present returns `AppConfig()` with all documented defaults (Req 1.2, 2.3)
    - `load_config(start_dir=tmp_path)` reads `policy-dq.toml` written to `tmp_path` and returns correct values
    - `load_config(start_dir=tmp_path)` reads `[tool.policy-dq]` from `pyproject.toml` and ignores other tables (Req 1.3)
    - `load_config_from_dict({"unknown_key": 1})` raises `ConfigValidationError` containing `"unknown_key"`
    - `load_config_from_dict({"api_port": "not-an-int"})` raises `ConfigValidationError` naming `api_port`
    - `load_config_from_dict({"api_port": "8080"})` returns `AppConfig` with `api_port == 8080` (Req 2.4)
    - `load_config_from_dict({"output_format": "xml"})` raises `ConfigValidationError` listing allowed values
    - `AppConfig()` field defaults match the table in Requirements 2.3
    - _Requirements: 1.2, 1.3, 1.4, 2.2, 2.3, 2.4_

  - [ ]* 1.6 Write property test: Property 3 — unrecognised keys always raise
    - `# Feature: config-file-support, Property 3: Unrecognised keys always raise`
    - Strategy: `st.dictionaries(st.text().filter(lambda k: k not in KNOWN_KEYS), st.text(), min_size=1)`
    - Assert `ConfigValidationError` message contains every unrecognised key name
    - _Requirements: 1.4, 6.3_

  - [ ]* 1.7 Write property test: Property 4 — type mismatch raises with field name
    - `# Feature: config-file-support, Property 4: Type mismatch always raises with field name`
    - Strategy: pairs of `(int-typed key, st.text().filter(lambda s: not s.lstrip("-").isdigit()))`
    - Assert `ConfigValidationError` message names the offending key
    - _Requirements: 2.2_

  - [ ]* 1.8 Write property test: Property 5 — integer string coercion
    - `# Feature: config-file-support, Property 5: Integer string coercion`
    - Strategy: `st.integers(min_value=1, max_value=65535).map(str)` for `api_port`
    - Assert resulting `AppConfig.api_port` equals `int(value)` with no error raised
    - _Requirements: 2.4_

  - [ ]* 1.9 Write property test: Property 6 — invalid Literal raises with allowed set
    - `# Feature: config-file-support, Property 6: Invalid Literal values raise with allowed set`
    - Strategy: `st.sampled_from(LITERAL_KEYS)` × `st.text().filter(lambda v: v not in allowed_set)`
    - Assert `ConfigValidationError` names the key and lists every allowed value
    - _Requirements: 2.5_

  - [ ]* 1.10 Write property test: Property 10 — round-trip serialisation
    - `# Feature: config-file-support, Property 10: Round-trip serialisation`
    - Strategy: `st.builds(AppConfig, ...)` with valid values for every field
    - Assert `load_config_from_dict(config_to_dict(c)) == c`
    - _Requirements: 6.2_

- [ ] 2. Checkpoint — config module
  - Run `python -m pytest tests/unit/test_config.py -v` and confirm all tests pass before proceeding.
  - Ask the user if any config behaviour is unclear before moving on.

- [ ] 3. Implement `policy_dq.server` module and fix entry point
  - [ ] 3.1 Create `src/policy_dq/server.py` with `serve()` function
    - Import `load_config` from `policy_dq.config` and `uvicorn`
    - Call `cfg = load_config()`, then `uvicorn.run("policy_dq.api:app", host=cfg.api_host, port=cfg.api_port, log_level=cfg.api_log_level)`
    - Wrap in `try/except OSError`: log via `logging.getLogger(__name__).critical(...)` and call `sys.exit(1)`
    - _Requirements: 4.1, 4.3, 4.4_

  - [ ] 3.2 Fix `policy-dq-api` entry point in `pyproject.toml`
    - Change `policy-dq-api = "uvicorn:main"` → `policy-dq-api = "policy_dq.server:serve"`
    - _Requirements: 4.2_

  - [ ] 3.3 Write unit tests for `server.py` in `tests/unit/test_server.py`
    - Mock `uvicorn.run` with `unittest.mock.patch`; call `serve()`; assert `uvicorn.run` called with `host`, `port`, `log_level` matching `AppConfig` defaults
    - Mock `uvicorn.run` to raise `OSError`; assert `sys.exit` called with `1` and `logging.critical` was invoked
    - Use `tmp_path` + a `policy-dq.toml` to verify `serve()` picks up non-default `api_port`
    - _Requirements: 4.1, 4.4_

- [ ] 4. Modify `src/policy_dq/cli.py` to consume `AppConfig`
  - [ ] 4.1 Call `load_config()` in the `cli` group callback and store result on Click context
    - Add `pass_context=True` to `@click.group()`; call `ctx.ensure_object(dict)`; store `AppConfig` as `ctx.obj["config"]`
    - Remove any hardcoded default strings or type-coercion logic from the CLI layer
    - _Requirements: 3.1, 3.4_

  - [ ] 4.2 Update `validate` command in `src/policy_dq/cli.py` to read defaults from `AppConfig`
    - Add `pass_context=True` to `@cli.command()`; read `cfg: AppConfig = ctx.obj["config"]`
    - Change `data_path` and `rules_path` from `click.argument` to `click.option` with `default=None`; fall back to `cfg.data_path` / `cfg.rules_path` when `None`
    - Set `--output-format` default to `None`; use `cfg.output_format` when not provided
    - Set `--json-output-path` default to `None`; use `cfg.json_output_path` when not provided
    - Set `--markdown-output-path` default to `None`; use `cfg.markdown_output_path` when not provided
    - After `run_validation`, exit non-zero via `sys.exit(1)` when any error's severity meets or exceeds `cfg.severity_threshold`
    - _Requirements: 3.2, 3.3, 3.5_

  - [ ]* 4.3 Write property test: Property 7 — CLI explicit flag overrides AppConfig
    - `# Feature: config-file-support, Property 7: CLI explicit flag overrides AppConfig`
    - Strategy: `st.builds(AppConfig, ...)` × `st.sampled_from(["--output-format", "--json-output-path", "--markdown-output-path"])` × valid override values
    - Invoke CLI via `click.testing.CliRunner`; assert effective value equals CLI-supplied value
    - _Requirements: 3.2_

  - [ ]* 4.4 Write property test: Property 8 — CLI uses AppConfig when no flag provided
    - `# Feature: config-file-support, Property 8: CLI uses AppConfig when no flag provided`
    - Strategy: `st.builds(AppConfig, ...)` with omitted CLI options
    - Invoke CLI via `click.testing.CliRunner`; assert effective value equals AppConfig field value
    - _Requirements: 3.3_

  - [ ]* 4.5 Write property test: Property 9 — severity threshold exit code
    - `# Feature: config-file-support, Property 9: Severity threshold exit code`
    - Strategy: `st.sampled_from(["error", "warning", "info"])` × `st.lists(st.builds(ValidationError, ...))`
    - Assert `result.exit_code != 0` iff at least one error severity meets or exceeds threshold
    - _Requirements: 3.5_

- [ ] 5. Checkpoint — CLI integration
  - Run `python -m pytest tests/unit/ -v` and confirm all unit tests pass before proceeding.
  - Ask the user if any CLI override behaviour needs adjustment.

- [ ] 6. Add config discovery property tests in `tests/unit/test_config_properties.py`
  - [ ]* 6.1 Write property test: Property 1 — discovery finds nearest ancestor
    - `# Feature: config-file-support, Property 1: Config discovery finds nearest ancestor`
    - Use `tmp_path` fixture; build a directory tree with `policy-dq.toml` at a random ancestor level
    - Strategy: `st.integers(min_value=1, max_value=5)` for depth; place config at a random ancestor
    - Assert `load_config(start_dir=leaf_dir)` returns values from the nearest ancestor config, not a more distant one
    - _Requirements: 1.1_

  - [ ]* 6.2 Write property test: Property 2 — pyproject.toml table isolation
    - `# Feature: config-file-support, Property 2: pyproject.toml isolation`
    - Strategy: `st.dictionaries(st.text().filter(lambda k: k != "tool"), st.dictionaries(st.text(), st.text()))` for arbitrary extra tables
    - Write a `pyproject.toml` to `tmp_path` containing both the extra tables and a valid `[tool.policy-dq]` section
    - Assert `load_config(start_dir=tmp_path)` result equals `load_config` result from a file with only `[tool.policy-dq]`
    - _Requirements: 1.3_

- [ ] 7. Write integration tests in `tests/integration/test_cli_config.py`
  - [ ] 7.1 Test that CLI picks up defaults from `policy-dq.toml` in a temp directory
    - Write a `policy-dq.toml` with `output_format = "json"` and `json_output_path = "out.json"` to `tmp_path`
    - Invoke `cli validate` via `click.testing.CliRunner` with `mix_stderr=False`, passing valid `data_path` and `rules_path`
    - Assert the runner does not raise and the output file `out.json` is created in the expected location
    - _Requirements: 1.1, 3.3_

  - [ ] 7.2 Test that explicit CLI flags override config file values
    - Write a `policy-dq.toml` with `output_format = "json"` to `tmp_path`
    - Invoke `cli validate --output-format console` via `CliRunner`
    - Assert console output is produced and no JSON file is written
    - _Requirements: 3.2_

  - [ ] 7.3 Test that CLI exits non-zero when severity threshold is met
    - Write a `policy-dq.toml` with `severity_threshold = "warning"` to `tmp_path`
    - Provide a dataset and rules file that produce at least one `warning`-level error
    - Invoke `cli validate` via `CliRunner`; assert `result.exit_code != 0`
    - _Requirements: 3.5_

  - [ ] 7.4 Test that CLI exits zero when no errors meet the threshold
    - Write a `policy-dq.toml` with `severity_threshold = "error"` to `tmp_path`
    - Provide a dataset and rules file that produce only `warning`-level errors (none at `error`)
    - Invoke `cli validate` via `CliRunner`; assert `result.exit_code == 0`
    - _Requirements: 3.5_

- [ ] 8. Add `hypothesis` dev dependency to `pyproject.toml`
  - Add `hypothesis>=6.0` to the `[dependency-groups] dev` table in `pyproject.toml`
  - Run `uv sync` to update the lockfile
  - _Requirements: (testing infrastructure for property tests)_

- [ ] 9. Final checkpoint — full test suite
  - Run `python -m pytest tests/ -v` and confirm all tests pass.
  - Verify `ruff check src/ tests/` and `mypy --strict src/` report no errors.
  - Ask the user if any issues arise before closing out.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Property tests live in `tests/unit/test_config_properties.py`; unit tests in `tests/unit/test_config.py` and `tests/unit/test_server.py`
- Each property test must include the comment `# Feature: config-file-support, Property N: <title>`
- `tomllib` is stdlib in Python 3.11+; no extra dependency needed for TOML parsing
- `cli.py` uses Click (not Typer); use `click.testing.CliRunner` for all CLI tests
- `hypothesis` must be added to `[dependency-groups] dev` in `pyproject.toml` before running property tests
- All tests must be deterministic; use `tmp_path` for filesystem tests, `unittest.mock.patch` for `uvicorn.run` and `sys.exit`
