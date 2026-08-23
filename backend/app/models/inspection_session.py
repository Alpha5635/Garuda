import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy import String, ForeignKey, Integer, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class SessionStatus(str, Enum):
    QUEUED = "queued"
    DETECTING_PRODUCTS = "detecting_products"
    PROCESSING_PRODUCTS = "processing_products"
    AGGREGATING_RESULTS = "aggregating_results"
    COMPLETE = "complete"
    PARTIAL_FAILURE = "partial_failure"
    FAILED = "failed"


class InspectionSession(Base, TimestampMixin):
    __tablename__ = "inspection_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    organisation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    inspector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    client_session_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), unique=True, index=True, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=SessionStatus.QUEUED.value, nullable=False)
    total_images: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_products: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_products: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    inspector = relationship("User", back_populates="inspection_sessions")
    organisation = relationship("Organisation", back_populates="inspection_sessions")
    images = relationship("Image", back_populates="session", cascade="all, delete-orphan")
    detections = relationship("ProductDetection", back_populates="session", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="session")
    audit_events = relationship("AuditChain", back_populates="session", cascade="all, delete-orphan")
    reports = relationship("ReportMetadata", back_populates="session", cascade="all, delete-orphan")
