"""Inspection, ProductImage, ExtractedField, Violation, Report, and ReviewAction models."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, TYPE_CHECKING
from geoalchemy2 import Geography
from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from backend.app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.organisation import Organisation
    from backend.app.models.user import User
    from backend.app.models.catalog import Product
    from backend.app.models.rule import RuleVersion
    from backend.app.models.session import InspectionSession, ProductDetection
    from backend.app.models.intelligence import ModelVersion


class Inspection(Base, TimestampMixin):
    """
    Core inspection case record tracking package/listing/consumer compliance audits.
    Supports both standalone single-product captures and multi-product batch sessions.
    """
    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("organisations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    inspection_session_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("inspection_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Parent batch inspection session (NULL for standalone single inspections)",
    )
    product_detection_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("product_detections.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
        index=True,
        doc="Reference to detected product item in batch image",
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Inspection channel: 'package', 'batch', 'ecommerce', 'consumer'",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
        doc="Status: draft, queued, processing, review_required, completed, needs_recapture, failed, archived",
    )
    rule_version_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("rule_versions.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        doc="Pinned exact rule version used during this inspection",
    )
    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Computed compliance score (0-100) per severity deduction model",
    )
    score_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="provisional",
        doc="'provisional' (automated) or 'verified' (officer approved)",
    )
    
    # PostGIS Location Support (Point with WGS84 SRID 4326)
    location: Mapped[Any | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False).with_variant(
            String(100), "sqlite"
        ),
        nullable=True,
        doc="Geographic coordinates of inspection capture",
    )
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    state_code: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    officer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Full-Text Search tsvector (PostgreSQL only)
    search_vector: Mapped[Any | None] = mapped_column(
        TSVECTOR().with_variant(Text(), "sqlite"),
        nullable=True,
        doc="Materialized tsvector for multi-field full text search",
    )
    
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    client_inspection_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Mobile client inspection UUID for offline sync reconciliation",
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        doc="Deterministic idempotency key for safe client retry",
    )

    # Relationships
    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="inspections")
    session: Mapped["InspectionSession | None"] = relationship(
        "InspectionSession",
        back_populates="inspections",
        foreign_keys=[inspection_session_id],
    )
    product_detection: Mapped["ProductDetection | None"] = relationship(
        "ProductDetection",
        foreign_keys=[product_detection_id],
    )
    product: Mapped["Product | None"] = relationship("Product", back_populates="inspections")
    rule_version: Mapped["RuleVersion | None"] = relationship("RuleVersion", back_populates="inspections")
    creator: Mapped["User | None"] = relationship("User", back_populates="inspections_created", foreign_keys=[created_by])
    
    images: Mapped[List["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="inspection",
        cascade="all, delete-orphan",
    )
    extracted_fields: Mapped[List["ExtractedField"]] = relationship(
        "ExtractedField",
        back_populates="inspection",
        cascade="all, delete-orphan",
    )
    violations: Mapped[List["Violation"]] = relationship(
        "Violation",
        back_populates="inspection",
        cascade="all, delete-orphan",
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="inspection",
        cascade="all, delete-orphan",
    )
    review_actions: Mapped[List["ReviewAction"]] = relationship(
        "ReviewAction",
        back_populates="inspection",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_inspections_org_status_channel", "organisation_id", "status", "channel"),
        Index("ix_inspections_district_captured", "district", "captured_at"),
        Index("ix_inspections_search_vector", "search_vector", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Inspection(id={self.id}, channel='{self.channel}', status='{self.status}', score={self.score})>"


class ProductImage(Base, TimestampMixin):
    """
    Evidence image metadata record. Original images and derived crops are stored in MinIO.
    Stores cryptographic SHA-256, quality gate analysis, homography transforms, and mm calibration.
    """
    __tablename__ = "product_images"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    object_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="MinIO/S3 object storage path, e.g. 'inspections/{id}/originals/{filename}.jpg'",
    )
    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="SHA-256 hash of original uploaded image bytes",
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
    location: Mapped[Any | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False).with_variant(
            String(100), "sqlite"
        ),
        nullable=True,
    )
    gps_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Quality Gates (Laplacian blur variance, glare saturation, resolution)
    quality_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Quality gates: blur_score, glare_ratio, resolution_ok, is_recapture_needed",
    )
    # Perspective correction & crop transforms
    transform_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Dewarp transform matrix, source coordinates, derived crop metadata",
    )
    # Millimetre calibration data (Fiducial, QR, Card, Coin, Dimensions)
    calibration_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Calibration mode (aruco/qr/card/coin/manual), px_per_mm scale, confidence, residual error",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="uploaded",
        index=True,
        doc="Status: uploaded, processing, valid, needs_recapture, rejected",
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="images")
    extracted_fields: Mapped[List["ExtractedField"]] = relationship(
        "ExtractedField",
        back_populates="image",
    )

    def __repr__(self) -> str:
        return f"<ProductImage(id={self.id}, sha256='{self.sha256[:8]}...', status='{self.status}')>"


class ExtractedField(Base, TimestampMixin):
    """
    Extracted label field metadata. Raw OCR extraction is NEVER overwritten when corrected.
    Officer corrections are recorded as review_actions, preserving original model outputs for active learning.
    """
    __tablename__ = "extracted_fields"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("product_images.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    field_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Field type: mrp, net_quantity, mfg_date, consumer_care, address, origin, generic_name, dimensions",
    )
    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Immutable raw OCR text from model extraction",
    )
    normalized_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Canonical parsed values: {amount: 90.0, currency: 'INR', unit: 'g', value: 500, month: 3, year: 2026}",
    )
    bbox_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Bounding box [x, y, w, h] normalized coordinates",
    )
    polygon_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Segmentation boundary polygon coordinates",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        doc="Model detection/recognition confidence score (0.0 - 1.0)",
    )
    language: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="eng",
        doc="Detected script/language: 'eng', 'hin', 'tam', etc.",
    )
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("model_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    review_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unreviewed",
        index=True,
        doc="Status: unreviewed, confirmed, corrected, dismissed",
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="extracted_fields")
    image: Mapped["ProductImage | None"] = relationship("ProductImage", back_populates="extracted_fields")
    model_version_rel: Mapped["ModelVersion | None"] = relationship("ModelVersion")
    review_actions: Mapped[List["ReviewAction"]] = relationship("ReviewAction", back_populates="field")

    __table_args__ = (
        Index("ix_extracted_fields_inspection_type", "inspection_id", "field_type"),
    )

    def __repr__(self) -> str:
        return f"<ExtractedField(id={self.id}, field_type='{self.field_type}', confidence={self.confidence})>"


class Violation(Base, TimestampMixin):
    """
    Specific rule contravention finding citing exact LMPC clauses and statutory references.
    """
    __tablename__ = "violations"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("rule_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Rule identifier, e.g. 'LMPC-6-1-E-MRP-001', 'LMPC-7-NUMERAL-HEIGHT-006'",
    )
    clause: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Legal clause citation, e.g. 'Rule 6(1)(e)', 'Rule 7(2)(i) Table I'",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="detected",
        index=True,
        doc="Status: detected, confirmed, dismissed, waived, resolved",
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Severity tier: 'Critical', 'Major', 'Minor', 'Review required'",
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Evidence crop object_key, crop_sha256, bbox, snippet, formula trace, logic result",
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    officer_disposition: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Officer disposition: 'confirmed', 'dismissed', 'waived'",
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="violations")
    rule_version: Mapped["RuleVersion"] = relationship("RuleVersion", back_populates="violations")
    review_actions: Mapped[List["ReviewAction"]] = relationship("ReviewAction", back_populates="violation")

    __table_args__ = (
        Index("ix_violations_severity_status", "severity", "status"),
    )

    def __repr__(self) -> str:
        return f"<Violation(id={self.id}, rule_id='{self.rule_id}', severity='{self.severity}', status='{self.status}')>"


class Report(Base):
    """
    Statutory inspection report artifacts (PDF, DOCX, CSV).
    Stores object storage keys, cryptographic hashes, and signing officer metadata.
    """
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        doc="Report format: 'PDF', 'DOCX', 'CSV'",
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    object_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="MinIO/S3 object storage path, e.g. 'reports/{inspection_id}/statutory_report_v1.pdf'",
    )
    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="SHA-256 digest of generated report file",
    )
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="reports")
    generator: Mapped["User | None"] = relationship("User", foreign_keys=[generated_by], back_populates="reports_generated")
    approver: Mapped["User | None"] = relationship("User", foreign_keys=[approved_by], back_populates="reports_approved")

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, type='{self.type}', sha256='{self.sha256[:8]}...')>"


class ReviewAction(Base):
    """
    Human-in-the-loop review actions recording officer approvals, field corrections, and dismissals.
    Decouples manual human decisions from automated model extractions.
    """
    __tablename__ = "review_actions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    field_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("extracted_fields.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    violation_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("violations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Action: accept_ocr, correct_ocr, accept_violation, reject_violation, waive_violation, request_recapture, accept, correct, dismiss, waive",
    )
    original_value_jsonb: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        doc="Original value snapshot extracted by model prior to review",
    )
    corrected_value_jsonb: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        doc="Corrected value payload supplied by the reviewing officer",
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="review_actions")
    field: Mapped["ExtractedField | None"] = relationship("ExtractedField", back_populates="review_actions")
    violation: Mapped["Violation | None"] = relationship("Violation", back_populates="review_actions")
    reviewer: Mapped["User"] = relationship("User", back_populates="review_actions")

    def __repr__(self) -> str:
        return f"<ReviewAction(id={self.id}, action='{self.action}', reviewer_id={self.reviewer_id})>"


from sqlalchemy import event


@event.listens_for(Inspection, "before_insert")
@event.listens_for(Inspection, "before_update")
def _populate_inspection_search_vector_fallback(mapper, connection, target):
    """
    Application-level search vector populator for non-PostgreSQL dialects (e.g. SQLite tests).
    In PostgreSQL, the database trigger trg_inspections_search_vector will overwrite with native weighted tsvector.
    """
    if target.search_vector is None:
        parts = [
            target.district or "",
            target.state_code or "",
            target.channel or "",
            target.status or "",
            target.officer_notes or "",
        ]
        target.search_vector = " ".join(p for p in parts if p.strip())

