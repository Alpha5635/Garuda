import uuid
from enum import Enum
from sqlalchemy import String, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class JobState(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    QUALITY_CHECK = "quality_check"
    OCR = "ocr"
    COMPLETE = "complete"
    FAILED = "failed"
    NEEDS_RECAPTURE = "needs_recapture"


class ProcessingJob(Base, TimestampMixin):
    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False
    )
    image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("images.id", ondelete="SET NULL"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default=JobState.QUEUED.value, nullable=False)
    error_reason: Mapped[str | None] = mapped_column(String(255), nullable=True) # glare, blur, low_resolution, bad_orientation, system_error
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    quality_metrics_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ocr_data_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extracted_fields_json: Mapped[list | None] = mapped_column(JSON, nullable=True)

    inspection = relationship("Inspection", back_populates="jobs")
    image = relationship("Image", back_populates="jobs")
