# Requirements Document

## Introduction

This feature adds config file support to policy-dq so that default values for CLI options and API
server settings can be supplied via `pyproject.toml` (under a `[tool.policy-dq]` table) or a
dedicated `policy-dq.toml` file. Config loading lives entirely in the business-logic layer; the
CLI and API layers only consume the resolved config object. The feature also fixes the broken
`policy-dq-api` entry point by replacing it with a proper wrapper that reads host/port/log-level
from the resolved config.

## Glossary

- **Config_Loader**: The module (`policy_dq.config`) responsible for discovering, parsing, and
  validating configuration files.
- **AppConfig**: The typed dataclass that holds all resolved configuration values.
- **CLI**: The command-line interface (`policy_dq.cli`) built with Typer.
- **API_Server**: The FastAPI application and its Uvicorn wrapper (`policy_dq.server`).
- **Config_File**: Either `pyproject.toml` (section `[tool.policy-dq]`) or `policy-dq.toml` in
  the working directory or any ancestor directory up to the filesystem root.
- **Config_Key**: A named, documented setting within the Config_File.
- **Severity_Threshold**: The minimum error severity level that causes the CLI to exit non-zero.

---

## Requirements

### Requirement 1: Config File Discovery

**User Story:** As a data engineer, I want policy-dq to automatically find a config file in my
project directory, so that I do not have to pass the same CLI flags on every invocation.

#### Acceptance Criteria

1. WHEN the Config_Loader is invoked, THE Config_Loader SHALL search for `policy-dq.toml` and
   then `pyproject.toml` starting from the current working directory and traversing up to the
   filesystem root, stopping at the first file found.
2. WHEN neither `policy-dq.toml` nor `pyproject.toml` is found, THE Config_Loader SHALL return
   an AppConfig populated entirely with documented default values.
3. WHEN `pyproject.toml` is found, THE Config_Loader SHALL read configuration exclusively from
   the `[tool.policy-dq]` table and ignore all other tables.
4. IF a Config_File contains a key that is not a recognised Config_Key, THEN THE Config_Loader
   SHALL raise a `ConfigValidationError` listing each unrecognised key.
5. THE Config_Loader SHALL expose a `load_config(start_dir: Path | None = None) -> AppConfig`
   function as its public interface.

---

### Requirement 2: Typed and Validated AppConfig Model

**User Story:** As a data engineer, I want config values to be type-checked and validated on
load, so that misconfigured projects fail fast with a clear error rather than silently misbehaving.

#### Acceptance Criteria

1. THE Config_Loader SHALL represent all configuration as an `AppConfig` dataclass with explicit
   type annotations for every field.
2. WHEN a Config_File supplies a value whose type does not match the declared field type, THE
   Config_Loader SHALL raise a `ConfigValidationError` that names the offending key and its
   expected type.
3. THE AppConfig SHALL define the following Config_Keys with the stated types and defaults:

   | Config_Key          | Type                              | Default     | Description                                      |
   |---------------------|-----------------------------------|-------------|--------------------------------------------------|
   | `output_format`     | `Literal["console","json","markdown"]` | `"console"` | Default reporter for the `validate` command      |
   | `data_path`         | `str \| None`                     | `None`      | Default path to the input dataset                |
   | `rules_path`        | `str \| None`                     | `None`      | Default path to the rules file                   |
   | `json_output_path`  | `str`                             | `"report.json"` | Output path for JSON reports                 |
   | `markdown_output_path` | `str`                          | `"report.md"`   | Output path for Markdown reports             |
   | `severity_threshold`| `Literal["error","warning","info"]` | `"error"` | Minimum severity that triggers a non-zero exit   |
   | `api_host`          | `str`                             | `"127.0.0.1"` | Host address for the API server                |
   | `api_port`          | `int`                             | `8000`      | Port for the API server                          |
   | `api_log_level`     | `Literal["critical","error","warning","info","debug","trace"]` | `"info"` | Uvicorn log level |

4. WHEN an `int`-typed Config_Key is supplied as a string that represents a valid integer, THE
   Config_Loader SHALL coerce the value to `int` without raising an error.
5. IF a `Literal`-typed Config_Key is supplied with a value not in the allowed set, THEN THE
   Config_Loader SHALL raise a `ConfigValidationError` naming the key and listing the allowed
   values.

---

### Requirement 3: CLI Consumes AppConfig

**User Story:** As a data engineer, I want CLI flags to override config file values, so that I
can run one-off commands without editing the config file.

#### Acceptance Criteria

1. WHEN the CLI is invoked, THE CLI SHALL call `Config_Loader.load_config()` once and pass the
   resulting AppConfig to the command handler.
2. WHEN a CLI option is explicitly provided by the user, THE CLI SHALL use the user-supplied
   value and ignore the corresponding AppConfig field.
3. WHEN a CLI option is not provided by the user, THE CLI SHALL use the value from AppConfig as
   the effective default.
4. THE CLI SHALL NOT contain any config-parsing, file-reading, or type-coercion logic; those
   responsibilities belong exclusively to Config_Loader.
5. WHEN `AppConfig.severity_threshold` is set and validation produces at least one error whose
   severity matches or exceeds the threshold, THE CLI SHALL exit with a non-zero status code.

---

### Requirement 4: API Server Entry Point

**User Story:** As a data engineer, I want a working `policy-dq-api` command that reads host,
port, and log-level from the config file, so that I can start the API server without specifying
flags every time.

#### Acceptance Criteria

1. THE API_Server module SHALL provide a `serve()` function that calls `Config_Loader.load_config()`
   and starts Uvicorn with `api_host`, `api_port`, and `api_log_level` from the resolved AppConfig.
2. THE `policy-dq-api` entry point in `pyproject.toml` SHALL point to `policy_dq.server:serve`
   instead of `uvicorn:main`.
3. WHEN `policy-dq-api` is invoked, THE API_Server SHALL start and listen on the host and port
   specified in AppConfig.
4. IF Uvicorn fails to bind to the configured host/port, THEN THE API_Server SHALL log the error
   at `critical` level and exit with status code 1.

---

### Requirement 5: Config File Documentation

**User Story:** As a data engineer, I want all supported config keys documented in one place, so
that I can configure policy-dq without reading source code.

#### Acceptance Criteria

1. THE Config_Loader module SHALL include a module-level docstring that lists every Config_Key,
   its type, its default value, and a one-line description.
2. WHEN a new Config_Key is added to AppConfig, THE Config_Loader module docstring SHALL be
   updated to include the new key before the change is merged.

---

### Requirement 6: Round-Trip Config Parsing

**User Story:** As a data engineer, I want confidence that config serialisation and deserialisation
are consistent, so that saving and reloading a config produces identical settings.

#### Acceptance Criteria

1. THE Config_Loader SHALL provide a `config_to_dict(config: AppConfig) -> dict[str, Any]`
   function that serialises an AppConfig to a plain dictionary.
2. FOR ALL valid AppConfig objects `c`, calling `load_config_from_dict(config_to_dict(c))` SHALL
   return an AppConfig equal to `c` (round-trip property).
3. WHEN `load_config_from_dict` receives a dictionary with an unrecognised key, THE Config_Loader
   SHALL raise a `ConfigValidationError`.
