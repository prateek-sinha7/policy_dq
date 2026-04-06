from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationError:

    rule_name: str
    field: Optional[str]
    message: str
    row: Optional[int]
    severity: str = "error"