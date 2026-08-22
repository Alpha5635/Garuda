import uuid
from sqlalchemy import String, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class Violation(Base, TimestampMixin):
    __tablename__ = "violations"

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
    rule_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    rule_version: Mapped[str] = mapped_column(String(50), nullable=False)
    clause: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False) # critical, major, minor
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    
    evidence_bbox: Mapped[list | None] = mapped_column(JSON, nullable=True)
    evidence_crop_key: Mapped[str] = mapped_column(String(500), nullable=False) # object-storage key of evidence crop
    ocr_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    normalized_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    inspection = relationship("Inspection")
    image = relationship("Image")
