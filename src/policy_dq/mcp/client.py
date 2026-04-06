import requests


def load_mcp_rules(uri: str):

    url = "http://localhost:8000/rules/basic"

    return requests.get(url).json()["rules"]