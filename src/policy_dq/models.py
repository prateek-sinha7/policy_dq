from dataclasses import dataclass


@dataclass(slots=True)
class ValidationError:
    rule_name: str
    field: str | None
    message: str
    row: int | None
    severity: str = "error"