import uuid
from enum import Enum
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class DetectionStatus(str, Enum):
    DETECTED = "detected"
    CROPPED = "cropped"
    INSPECTED = "inspected"
    IGNORED = "ignored"
    FAILED = "failed"


class ProductDetection(Base, TimestampMixin):
    __tablename__ = "product_detections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspection_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("images.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    bbox_x: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_width: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_height: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    crop_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=DetectionStatus.DETECTED.value, nullable=False)

    session = relationship("InspectionSession", back_populates="detections")
    image = relationship("Image", back_populates="detections")
    inspection = relationship("Inspection", back_populates="detection", uselist=False)
