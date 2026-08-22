import uuid
from sqlalchemy import String, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class NormalizedField(Base, TimestampMixin):
    __tablename__ = "normalized_fields"

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
    field_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    raw_value: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    numeric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bounding_box: Mapped[list | None] = mapped_column(JSON, nullable=True)

    inspection = relationship("Inspection")
