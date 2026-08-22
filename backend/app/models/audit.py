"""Tamper-evident, append-only audit log model with cryptographic hash chaining."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from backend.app.db.base import Base, GUID

if TYPE_CHECKING:
    from backend.app.models.organisation import Organisation
    from backend.app.models.user import User


class AuditLog(Base):
    """
    Append-only tamper-evident audit log entity.
    Every operational event is cryptographically linked to the previous event hash:
    canonical_event = timestamp | actor | action | entity_type | entity_id | canonical(before) | canonical(after) | prev_hash
    event_hash = SHA-256(canonical_event)
    """
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("organisations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Organisation scope of the audit event",
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="User ID who initiated the event (null for system automated tasks)",
    )
    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Target entity: 'inspection', 'extracted_field', 'violation', 'review_action', 'report', 'user', 'rule_version'",
    )
    entity_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="String identifier or UUID of the affected entity",
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Action: CREATE, UPDATE, DELETE, REVIEW_ACCEPT, REVIEW_CORRECT, APPROVE_REPORT, SYNC_INGEST",
    )
    before_jsonb: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        doc="Previous state snapshot prior to mutation",
    )
    after_jsonb: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        doc="New state snapshot after mutation",
    )
    event_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    prev_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="SHA-256 hash of the immediately preceding event record (prev_hash chain)",
    )
    event_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        doc="SHA-256 hash over canonical representation of this event",
    )
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="HTTP request ID or Celery task ID for traceability",
    )

    # Relationships
    organisation: Mapped["Organisation | None"] = relationship("Organisation", back_populates="audit_logs")
    actor: Mapped["User | None"] = relationship("User")

    __table_args__ = (
        Index("ix_audit_log_entity_lookup", "entity_type", "entity_id"),
        Index("ix_audit_log_actor_time", "actor_id", "event_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', entity='{self.entity_type}:{self.entity_id}', hash='{self.event_hash[:8]}...')>"
