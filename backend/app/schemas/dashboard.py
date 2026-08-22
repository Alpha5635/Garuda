from pydantic import BaseModel, ConfigDict


class DistrictMetric(BaseModel):
    district: str
    total_inspections: int
    violations_count: int


class RepeatBrandSignal(BaseModel):
    brand_name: str
    violations_count: int
    latest_violation_clause: str


class DashboardOverviewResponse(BaseModel):
    total_inspections: int
    total_violations: int
    review_backlog_count: int
    compliance_rate_percent: float
    rule_frequency_breakdown: dict[str, int] = {}
    district_metrics: list[DistrictMetric] = []
    repeat_brand_signals: list[RepeatBrandSignal] = []

    model_config = ConfigDict(from_attributes=True)
