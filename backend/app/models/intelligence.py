"""Offenders, SyncQueue, EcommerceListing, and ModelVersion intelligence models."""

import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, TYPE_CHECKING
from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from backend.app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.catalog import Brand, Product


class Offender(Base, TimestampMixin):
    """
    Intelligence aggregation model tracking repeat non-compliance trends per brand/period.
    NOTE: This is operational enforcement intelligence, NOT a public legal blacklist.
    """
    __tablename__ = "offenders"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    inspection_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confirmed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    severity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="offenders_history")

    __table_args__ = (
        Index("ix_offenders_brand_period", "brand_id", "period_start", "period_end"),
    )

    def __repr__(self) -> str:
        return f"<Offender(brand_id={self.brand_id}, confirmed={self.confirmed_count}, severity={self.severity_score})>"


class SyncQueue(Base, TimestampMixin):
    """
    Offline mobile synchronization queue supporting idempotent outbox reconciliation.
    Ensures that retried synchronization events from field officers never duplicate case data.
    """
    __tablename__ = "sync_queue"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    local_event_id: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        doc="Offline mobile capture payload (metadata, timestamps, calibration, GPS)",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        doc="Status: pending, processing, synced, failed, conflict",
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Deterministic idempotency key generated on client (device_id + local_uuid)",
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_sync_queue_device_status", "device_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<SyncQueue(id={self.id}, idempotency_key='{self.idempotency_key}', status='{self.status}')>"


class EcommerceListing(Base, TimestampMixin):
    """
    E-Commerce marketplace listing record (Rule 6(10) enforcement surface).
    Stores listing URLs, snapshot evidence, seller metadata, and raw JSON payloads.
    """
    __tablename__ = "ecommerce_listings"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Platform name: 'Amazon', 'Flipkart', 'Blinkit', 'Zepto', 'Swiggy Instamart', 'JioMart'",
    )
    external_listing_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="ASIN, FSN, or marketplace SKU ID",
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    snapshot_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="MinIO object key for listing HTML/rendered screenshot evidence",
    )
    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="SHA-256 hash of scraped HTML/payload for tamper evidence",
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    seller_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    availability: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Raw marketplace JSON payload/scraped attributes",
    )

    # Relationships
    product: Mapped["Product | None"] = relationship("Product", back_populates="ecommerce_listings")

    __table_args__ = (
        UniqueConstraint("platform", "external_listing_id", name="uq_platform_external_listing"),
        Index("ix_ecommerce_platform_seller", "platform", "seller_name"),
    )

    def __repr__(self) -> str:
        return f"<EcommerceListing(id={self.id}, platform='{self.platform}', external_id='{self.external_listing_id}')>"


class ModelVersion(Base, TimestampMixin):
    """
    CV and OCR model evaluation registry linking extractions to specific model releases.
    """
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Model name, e.g. 'PaddleOCR-PP-OCRv5', 'YOLOv8-PDP-seg', 'LayoutLMv3-LMPC'",
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    artifact_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    metrics_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Held-out evaluation metrics: {precision: 0.96, recall: 0.93, iou: 0.88, font_mae_mm: 0.22}",
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_model_name_version"),
    )

    def __repr__(self) -> str:
        return f"<ModelVersion(id={self.id}, name='{self.name}', version='{self.version}')>"
