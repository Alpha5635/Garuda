import uuid
from sqlalchemy import String, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class CalibrationData(Base, TimestampMixin):
    __tablename__ = "calibration_data"

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
    calibration_type: Mapped[str] = mapped_column(String(50), nullable=False) # aruco, qr, credit_card, coin, manual
    reference_width_mm: Mapped[float] = mapped_column(Float, nullable=False)
    reference_width_px: Mapped[float] = mapped_column(Float, nullable=False)
    pixels_per_mm: Mapped[float] = mapped_column(Float, nullable=False)
    measurement_error: Mapped[float] = mapped_column(Float, nullable=False, default=0.0) # +/- mm
    calibration_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    perspective_transform: Mapped[list | None] = mapped_column(JSON, nullable=True) # 3x3 matrix

    inspection = relationship("Inspection")
    image = relationship("Image")
