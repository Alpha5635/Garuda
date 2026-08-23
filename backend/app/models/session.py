"""Inspection Session, Batch Image, and Product Detection models for batch/shelf inspection."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from backend.app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.organisation import Organisation
    from backend.app.models.user import User
    from backend.app.models.inspection import Inspection


class InspectionSession(Base, TimestampMixin):
    """
    Session container for inspections, supporting both single product captures
    and multi-product batch / retail shelf captures.
    """
    __tablename__ = "inspection_sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("organisations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    client_session_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Offline mobile client session UUID for offline sync reconciliation",
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="package",
        index=True,
        doc="Channel: package, batch, ecommerce, consumer",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
        doc="Status: draft, queued, processing, partial_failure, complete, review_required, failed",
    )
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        doc="Deterministic key preventing duplicate sessions on client retry",
    )

    # Relationships
    organisation: Mapped["Organisation"] = relationship("Organisation")
    creator: Mapped["User | None"] = relationship("User")
    batch_images: Mapped[List["BatchImage"]] = relationship(
        "BatchImage",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    inspections: Mapped[List["Inspection"]] = relationship(
        "Inspection",
        back_populates="session",
    )

    __table_args__ = (
        Index("ix_inspection_sessions_org_status", "organisation_id", "status"),
        Index("ix_inspection_sessions_channel_captured", "channel", "captured_at"),
    )

    def __repr__(self) -> str:
        return f"<InspectionSession(id={self.id}, channel='{self.channel}', status='{self.status}')>"


class BatchImage(Base):
    """
    High-resolution shelf or multi-product image uploaded during a batch inspection session.
    The original image is stored immutably in object storage (MinIO/S3).
    """
    __tablename__ = "batch_images"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("inspection_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    object_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="MinIO/S3 object storage path, e.g. 'sessions/{session_id}/batches/{filename}.jpg'",
    )
    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="SHA-256 digest of original batch image bytes",
    )
    mime_type: Mapped[str | None] = mapped_column(String(50), nullable=True, default="image/jpeg")
    size_bytes: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer(), "sqlite"),
        nullable=True,
    )
    width_px: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_px: Mapped[int | None] = mapped_column(Integer, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Quality gates: blur_score, glare_ratio, lighting_ok, resolution_ok",
    )
    transform_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Perspective transforms and shelf rectification matrix",
    )
    calibration_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Calibration fiducial mode, px_per_mm, scale confidence",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="uploaded",
        index=True,
        doc="Status: uploaded, processing, valid, needs_recapture, rejected",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    session: Mapped["InspectionSession"] = relationship("InspectionSession", back_populates="batch_images")
    detections: Mapped[List["ProductDetection"]] = relationship(
        "ProductDetection",
        back_populates="batch_image",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<BatchImage(id={self.id}, sha256='{self.sha256[:8]}...', status='{self.status}')>"


class ProductDetection(Base):
    """
    Individual commodity package detected within a batch/shelf image.
    Can be linked to a discrete individual Inspection case.
    """
    __tablename__ = "product_detections"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    batch_image_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("batch_images.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inspection_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("inspections.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
        index=True,
        doc="Linked individual inspection record spawned from this detection",
    )
    detection_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Zero-based detection index inside the parent batch image",
    )
    bbox_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        doc="Normalized bounding box: {x: float, y: float, w: float, h: float}",
    )
    polygon_jsonb: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        doc="Optional segmentation mask polygon vertices",
    )
    crop_object_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="MinIO/S3 object storage path for cropped package image",
    )
    detection_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        doc="YOLO / detection model confidence score",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="detected",
        index=True,
        doc="Status: detected, processing, complete, review_required, needs_recapture, failed",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    batch_image: Mapped["BatchImage"] = relationship("BatchImage", back_populates="detections")
    inspection: Mapped["Inspection | None"] = relationship(
        "Inspection",
        foreign_keys=[inspection_id],
    )

    __table_args__ = (
        Index("ix_product_detections_batch_status", "batch_image_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<ProductDetection(id={self.id}, index={self.detection_index}, confidence={self.detection_confidence})>"
