import yaml


class MCPRuleLoader:

    """
    Simulates loading rules
    from external MCP source
    """

    def __init__(self, source):

        self.source = source


    def load_rules(self):

        if self.source.endswith(".yaml"):

            return self._load_yaml()

        raise ValueError(
            "unsupported MCP source"
        )


    def _load_yaml(self):

        with open(self.source) as f:

            data = yaml.safe_load(f)

        return data["rules"]