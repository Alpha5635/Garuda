import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.ocr import OcrResultContainer, ExtractedFieldCandidate


class JobResponse(BaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID
    image_id: uuid.UUID | None = None
    status: str
    error_reason: str | None = None
    retry_count: int = 0
    quality_metrics_json: dict | None = None
    ocr_data_json: dict | None = None
    extracted_fields_json: list | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
