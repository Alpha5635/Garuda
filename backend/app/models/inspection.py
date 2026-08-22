import uuid
from enum import Enum
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class InspectionStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    QUALITY_CHECK = "quality_check"
    OCR = "ocr"
    NEEDS_RECAPTURE = "needs_recapture"
    COMPLETE = "complete"
    FAILED = "failed"


class Inspection(Base, TimestampMixin):
    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    inspection_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    officer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    organisation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="SET NULL"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default=InspectionStatus.DRAFT.value, nullable=False)
    channel: Mapped[str | None] = mapped_column(String(100), nullable=True) # Retail store, E-commerce, Warehouse
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    officer = relationship("User", back_populates="inspections")
    organisation = relationship("Organisation", back_populates="inspections")
    images = relationship("Image", back_populates="inspection", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="inspection", cascade="all, delete-orphan")
