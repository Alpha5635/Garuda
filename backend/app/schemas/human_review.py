import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FieldCorrectionRequest(BaseModel):
    field_name: str
    original_ocr_value: str | None = None
    corrected_value: str
    reason: str | None = None


class ViolationReviewRequest(BaseModel):
    violation_id: uuid.UUID
    decision: str # accepted, rejected, waived
    justification_reason: str | None = None


class HumanReviewResponse(BaseModel):
    status: str = "success"
    message: str
    updated_record_id: uuid.UUID
