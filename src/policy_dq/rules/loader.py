import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import requests
import yaml

logger = logging.getLogger(__name__)


class RuleLoader(ABC):
    """Abstract base for all rule loaders."""

    @abstractmethod
    def load(self) -> list[dict[str, Any]]:
        ...


class FileRuleLoader(RuleLoader):
    """Loads rules from a local YAML or JSON file."""

    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> list[dict[str, Any]]:
        logger.debug("Loading rules from file: %s", self.path)
        if self.path.endswith(".yaml") or self.path.endswith(".yml"):
            with open(self.path, encoding="utf-8") as f:
                data: dict[str, Any] = yaml.safe_load(f)
        elif self.path.endswith(".json"):
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {self.path}")
        rules: list[dict[str, Any]] = data["rules"]
        logger.info("Loaded %d rules from %s", len(rules), self.path)
        return rules


class APIRuleLoader(RuleLoader):
    """Loads rules from an HTTP API endpoint."""

    def __init__(self, url: str, timeout: int = 10) -> None:
        self.url = url
        self.timeout = timeout

    def load(self) -> list[dict[str, Any]]:
        logger.debug("Fetching rules from API: %s", self.url)
        response = requests.get(self.url, timeout=self.timeout)
        response.raise_for_status()
        rules: list[dict[str, Any]] = response.json()["rules"]
        logger.info("Loaded %d rules from API %s", len(rules), self.url)
        return rules


def get_loader(source: str) -> RuleLoader:
    """Return the appropriate RuleLoader for the given source string."""
    if source.startswith("http://") or source.startswith("https://"):
        return APIRuleLoader(url=source)
    if source.startswith("mcp://"):
        # Resolve legacy mcp:// URIs to the local API endpoint
        url = source.replace("mcp://", "http://", 1)
        logger.debug("Resolved mcp:// URI to %s", url)
        return APIRuleLoader(url=url)
    return FileRuleLoader(path=source)


def load_rules(source: str) -> list[dict[str, Any]]:
    """Convenience wrapper — resolves source and loads rules."""
    return get_loader(source).load()
