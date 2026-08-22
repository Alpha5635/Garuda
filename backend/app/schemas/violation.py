import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ViolationSchema(BaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID
    image_id: uuid.UUID | None = None
    rule_id: str
    rule_version: str
    clause: str
    severity: str
    message: str
    evidence_bbox: list | None = None
    evidence_crop_key: str
    ocr_text: str | None = None
    normalized_value: str | None = None
    confidence: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
