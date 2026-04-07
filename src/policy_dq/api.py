"""FastAPI application — exposes policy-dq validation via HTTP with Swagger UI at /docs."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from policy_dq.rules.loader import load_rules
from policy_dq.validators.engine import run_validation

logger = logging.getLogger(__name__)

app = FastAPI(
    title="policy-dq",
    description="Validate structured data against configurable rules.",
    version="0.1.0",
)


# ---------- request / response models ----------

class RuleDict(BaseModel):
    model_config = {"extra": "allow"}
    name: str
    type: str


class ValidateRequest(BaseModel):
    data: list[dict[str, Any]]
    rules_source: str  # file path, http(s):// URL, or mcp:// URI


class ValidationErrorOut(BaseModel):
    rule_name: str
    field: str | None
    message: str
    row: int | None
    severity: str


class ValidateResponse(BaseModel):
    total_errors: int
    errors: list[ValidationErrorOut]


class SummarizeResponse(BaseModel):
    total_rules: int
    rules: list[RuleDict]


# ---------- endpoints ----------

@app.post("/validate", response_model=ValidateResponse, tags=["validation"])
def validate(request: ValidateRequest) -> ValidateResponse:
    """Validate a dataset against rules loaded from *rules_source*."""
    logger.info("POST /validate — source=%s rows=%d", request.rules_source, len(request.data))
    try:
        rules = load_rules(request.rules_source)
    except Exception as exc:
        logger.error("Failed to load rules: %s", exc)
        raise HTTPException(status_code=422, detail=f"Could not load rules: {exc}") from exc

    try:
        errors = run_validation(request.data, rules)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ValidateResponse(
        total_errors=len(errors),
        errors=[
            ValidationErrorOut(
                rule_name=e.rule_name,
                field=e.field,
                message=e.message,
                row=e.row,
                severity=e.severity,
            )
            for e in errors
        ],
    )


@app.get("/rules/summarize", response_model=SummarizeResponse, tags=["rules"])
def summarize_rules(rules_source: str) -> SummarizeResponse:
    """Return the list of rules available at *rules_source*."""
    logger.info("GET /rules/summarize — source=%s", rules_source)
    try:
        rules = load_rules(rules_source)
    except Exception as exc:
        logger.error("Failed to load rules: %s", exc)
        raise HTTPException(status_code=422, detail=f"Could not load rules: {exc}") from exc

    return SummarizeResponse(
        total_rules=len(rules),
        rules=[RuleDict(**r) for r in rules],
    )


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}
