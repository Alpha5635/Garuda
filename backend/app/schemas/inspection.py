import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.image import ImageResponse
from app.schemas.job import JobResponse


class InspectionCreate(BaseModel):
    channel: str | None = "Retail store"
    state: str | None = None
    district: str | None = None
    product_name: str | None = None
    brand_name: str | None = None
    organisation_id: uuid.UUID | None = None
    metadata_json: dict | None = None


class InspectionResponse(BaseModel):
    id: uuid.UUID
    inspection_number: str
    officer_id: uuid.UUID
    organisation_id: uuid.UUID | None = None
    status: str
    channel: str | None = None
    state: str | None = None
    district: str | None = None
    product_name: str | None = None
    brand_name: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InspectionDetailResponse(InspectionResponse):
    images: list[ImageResponse] = []
    latest_job: JobResponse | None = None

    model_config = ConfigDict(from_attributes=True)
