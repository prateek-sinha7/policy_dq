import yaml
import json


def load_rules(path: str):

    if path.startswith("mcp://"):
        from src.policy_dq.mcp.client import load_mcp_rules
        return load_mcp_rules(path)

    if path.endswith(".yaml"):

        with open(path) as f:
            return yaml.safe_load(f)["rules"]

    if path.endswith(".json"):

        with open(path) as f:
            return json.load(f)["rules"]

    raise ValueError("unsupported rules format")