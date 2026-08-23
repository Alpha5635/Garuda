import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SessionReportGenerateRequest(BaseModel):
    format: str = Field("pdf", pattern="^(pdf|docx|csv)$")
    idempotency_key: str | None = Field(None, max_length=100)


class SessionReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    format: str
    object_key: str
    file_size: int
    sha256_hash: str
    created_at: datetime
