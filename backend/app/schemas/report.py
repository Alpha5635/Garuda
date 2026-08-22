import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReportRequest(BaseModel):
    format: str = "pdf" # pdf, docx, csv


class ReportResponse(BaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID
    format: str
    object_key: str
    file_size: int
    sha256_hash: str
    download_url: str
    expires_in_seconds: int = 3600
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
