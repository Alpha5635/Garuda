import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ImageUploadUrlRequest(BaseModel):
    filename: str
    mime_type: str = "image/jpeg"
    file_size: int
    sha256_hash: str
    width: int | None = None
    height: int | None = None
    capture_timestamp: datetime | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None


class ImageUploadUrlResponse(BaseModel):
    image_id: uuid.UUID
    upload_url: str
    object_key: str
    expires_in_seconds: int = 3600


class ImageResponse(BaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID
    object_key: str
    original_filename: str | None = None
    sha256_hash: str
    mime_type: str
    file_size: int
    width: int | None = None
    height: int | None = None
    capture_timestamp: datetime | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
