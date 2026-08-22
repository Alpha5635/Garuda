import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class FieldCorrection(Base, TimestampMixin):
    __tablename__ = "field_corrections"

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
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    original_ocr_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    corrected_value: Mapped[str] = mapped_column(String(500), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    inspection = relationship("Inspection")
    reviewer = relationship("User")


class ViolationReview(Base, TimestampMixin):
    __tablename__ = "violation_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    violation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("violations.id", ondelete="CASCADE"),
        nullable=False
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    decision: Mapped[str] = mapped_column(String(50), nullable=False) # accepted, rejected, waived
    justification_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    violation = relationship("Violation")
    reviewer = relationship("User")
