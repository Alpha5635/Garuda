import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class SessionCreateRequest(BaseModel):
    organisation_id: uuid.UUID | None = None
    client_session_id: str | None = Field(None, max_length=100)
    idempotency_key: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    gps_accuracy: float | None = None
    metadata_json: dict[str, Any] | None = None


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organisation_id: uuid.UUID | None = None
    inspector_id: uuid.UUID
    client_session_id: str | None = None
    idempotency_key: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    gps_accuracy: float | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: str
    total_images: int
    total_products: int
    processed_products: int
    high_priority: int = 0
    medium_priority: int = 0
    low_priority: int = 0
    needs_recapture: int = 0
    review_required: int = 0
    violations: int = 0
    created_at: datetime
    updated_at: datetime


class SessionStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: uuid.UUID
    status: str
    total_images: int
    total_products: int
    processed_products: int
    high_priority: int = 0
    medium_priority: int = 0
    low_priority: int = 0
    needs_recapture: int = 0
    review_required: int = 0
    violations: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BatchImageUploadItem(BaseModel):
    filename: str = Field(..., max_length=255)
    sha256_hash: str = Field(..., min_length=64, max_length=64)
    mime_type: str = Field(..., max_length=100)
    file_size: int = Field(..., gt=0)
    width: int | None = None
    height: int | None = None
    capture_timestamp: datetime | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None


class BatchImageUploadRequest(BaseModel):
    images: list[BatchImageUploadItem]


class BatchImageUploadItemResponse(BaseModel):
    image_id: uuid.UUID
    upload_url: str
    object_key: str
    expiration: int = 3600


class BatchImageUploadResponse(BaseModel):
    session_id: uuid.UUID
    uploads: list[BatchImageUploadItemResponse]


class ProductDetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    image_id: uuid.UUID
    bbox_x: float
    bbox_y: float
    bbox_width: float
    bbox_height: float
    confidence: float
    crop_object_key: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class SessionProductItemResponse(BaseModel):
    product_id: uuid.UUID
    detection_id: uuid.UUID
    inspection_id: uuid.UUID | None = None
    image_id: uuid.UUID
    bounding_box: dict[str, float]
    confidence: float
    crop_reference: str | None = None
    processing_status: str
    inspection_status: str | None = None
    priority: str | None = None
    priority_reason: str | None = None
    priority_confidence: float | None = None
    underlying_rule_result: str | None = None
    review_required: bool = False


class SessionProductListResponse(BaseModel):
    session_id: uuid.UUID
    total_products: int
    products: list[SessionProductItemResponse]


# Smart Recapture Schemas
class RecaptureProductItem(BaseModel):
    product_id: uuid.UUID
    detection_id: uuid.UUID
    inspection_id: uuid.UUID | None = None
    image_id: uuid.UUID | None = None
    reason: str
    bounding_box: dict[str, float]
    current_status: str


class RecaptureProductListResponse(BaseModel):
    session_id: uuid.UUID
    total_recapture_needed: int
    items: list[RecaptureProductItem]


class RecaptureUploadResponse(BaseModel):
    session_id: uuid.UUID
    product_id: uuid.UUID
    image_id: uuid.UUID
    status: str
    message: str
