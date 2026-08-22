import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.rule_engine import RuleEvaluationResult


class EcommerceListingRequest(BaseModel):
    platform: str # Amazon, Flipkart, Blinkit
    listing_id: str
    url: str
    seller_name: str | None = None
    snapshot_base64: str | None = None
    declarations: dict | None = None # key-value pairs submitted


class EcommerceListingResponse(BaseModel):
    id: uuid.UUID
    platform: str
    listing_id: str
    url: str
    seller_name: str | None = None
    content_hash: str
    rule_evaluations: list[RuleEvaluationResult] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
