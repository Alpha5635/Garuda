import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class AuditChain(Base, TimestampMixin):
    __tablename__ = "audit_chain"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    inspection_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspections.id", ondelete="CASCADE", use_alter=True),
        nullable=True
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspection_sessions.id", ondelete="CASCADE", use_alter=True),
        nullable=True,
        index=True
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # INSPECTION_CREATED, OCR_PROCESSED, VIOLATION_DECLARED, HUMAN_REVIEW_SUBMITTED, REPORT_GENERATED
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False) # inspection, violation, report, review
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    before_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    inspection = relationship("Inspection")
    session = relationship("InspectionSession", back_populates="audit_events")
    actor = relationship("User")
