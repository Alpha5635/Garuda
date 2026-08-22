from pydantic import BaseModel, ConfigDict


class RuleDefinition(BaseModel):
    rule_id: str
    clause: str
    description: str
    applicability: list[str]
    validation: str
    field: str
    severity: str
    source: str
    source_url: str
    effective_date: str
    version: str


class RuleEvaluationResult(BaseModel):
    rule_id: str
    rule_version: str
    clause: str
    result: str # pass, violation, review_required, not_evaluable, not_applicable
    severity: str # critical, major, minor
    confidence: float
    explanation: str
    evidence_reference: str | None = None

    model_config = ConfigDict(from_attributes=True)
