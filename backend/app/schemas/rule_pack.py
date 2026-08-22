import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RulePackVersionRequest(BaseModel):
    version: str # e.g. rp-2026.04
    name: str
    rules_json: dict


class RulePackVersionResponse(BaseModel):
    id: uuid.UUID
    version: str
    name: str
    status: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
