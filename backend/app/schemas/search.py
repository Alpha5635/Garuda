import uuid
from pydantic import BaseModel, ConfigDict
from app.schemas.inspection import InspectionResponse


class SearchQuery(BaseModel):
    query: str | None = None
    product_name: str | None = None
    manufacturer: str | None = None
    rule_id: str | None = None
    district: str | None = None
    status: str | None = None
    skip: int = 0
    limit: int = 50


class SearchResultResponse(BaseModel):
    total_results: int
    results: list[InspectionResponse] = []

    model_config = ConfigDict(from_attributes=True)
