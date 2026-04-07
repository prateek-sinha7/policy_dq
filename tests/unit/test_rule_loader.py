import json
from unittest.mock import MagicMock, patch

import pytest

from policy_dq.rules.loader import APIRuleLoader, FileRuleLoader, get_loader, load_rules


SAMPLE_RULES = [{"name": "email_required", "type": "required", "field": "email"}]


# --- FileRuleLoader ---

def test_file_loader_yaml(tmp_path) -> None:
    f = tmp_path / "rules.yaml"
    f.write_text("rules:\n  - name: r1\n    type: required\n    field: x\n")
    rules = FileRuleLoader(str(f)).load()
    assert rules == [{"name": "r1", "type": "required", "field": "x"}]


def test_file_loader_yml_extension(tmp_path) -> None:
    f = tmp_path / "rules.yml"
    f.write_text("rules:\n  - name: r1\n    type: required\n    field: x\n")
    rules = FileRuleLoader(str(f)).load()
    assert rules == [{"name": "r1", "type": "required", "field": "x"}]


def test_file_loader_json(tmp_path) -> None:
    f = tmp_path / "rules.json"
    f.write_text(json.dumps({"rules": SAMPLE_RULES}))
    rules = FileRuleLoader(str(f)).load()
    assert rules == SAMPLE_RULES


def test_file_loader_unsupported_format(tmp_path) -> None:
    f = tmp_path / "rules.txt"
    f.write_text("rules: []")
    with pytest.raises(ValueError, match="Unsupported file format"):
        FileRuleLoader(str(f)).load()


def test_file_loader_missing_file_raises(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        FileRuleLoader(str(tmp_path / "nonexistent.yaml")).load()


# --- APIRuleLoader ---

def test_api_loader_success() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {"rules": SAMPLE_RULES}
    mock_response.raise_for_status = MagicMock()

    with patch("policy_dq.rules.loader.requests.get", return_value=mock_response) as mock_get:
        rules = APIRuleLoader(url="http://example.com/rules").load()

    mock_get.assert_called_once_with("http://example.com/rules", timeout=10)
    assert rules == SAMPLE_RULES


def test_api_loader_custom_timeout() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {"rules": SAMPLE_RULES}
    mock_response.raise_for_status = MagicMock()

    with patch("policy_dq.rules.loader.requests.get", return_value=mock_response) as mock_get:
        APIRuleLoader(url="http://example.com/rules", timeout=30).load()

    mock_get.assert_called_once_with("http://example.com/rules", timeout=30)


def test_api_loader_http_error() -> None:
    import requests as req

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = req.HTTPError("404")

    with patch("policy_dq.rules.loader.requests.get", return_value=mock_response):
        with pytest.raises(req.HTTPError):
            APIRuleLoader(url="http://example.com/rules").load()


# --- get_loader / load_rules ---

def test_get_loader_returns_file_loader_for_yaml() -> None:
    loader = get_loader("rules.yaml")
    assert isinstance(loader, FileRuleLoader)


def test_get_loader_returns_file_loader_for_json() -> None:
    loader = get_loader("rules.json")
    assert isinstance(loader, FileRuleLoader)


def test_get_loader_returns_api_loader_for_http() -> None:
    loader = get_loader("http://example.com/rules")
    assert isinstance(loader, APIRuleLoader)


def test_get_loader_returns_api_loader_for_https() -> None:
    loader = get_loader("https://example.com/rules")
    assert isinstance(loader, APIRuleLoader)


def test_get_loader_resolves_mcp_uri() -> None:
    loader = get_loader("mcp://localhost:8000/rules/basic")
    assert isinstance(loader, APIRuleLoader)
    assert loader.url == "http://localhost:8000/rules/basic"


def test_load_rules_delegates_to_loader(tmp_path) -> None:
    f = tmp_path / "rules.yaml"
    f.write_text("rules:\n  - name: r1\n    type: required\n    field: x\n")
    rules = load_rules(str(f))
    assert rules[0]["name"] == "r1"


def test_load_rules_http_source_returns_rules() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {"rules": SAMPLE_RULES}
    mock_response.raise_for_status = MagicMock()

    with patch("policy_dq.rules.loader.requests.get", return_value=mock_response):
        rules = load_rules("http://example.com/rules")

    assert rules == SAMPLE_RULES
