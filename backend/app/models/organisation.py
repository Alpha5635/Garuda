"""Organisation model for multi-tenant isolation and administrative jurisdiction."""

import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from backend.app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.catalog import Brand
    from backend.app.models.inspection import Inspection
    from backend.app.models.session import InspectionSession
    from backend.app.models.audit import AuditLog


class Organisation(Base, TimestampMixin):
    """
    Organisation entity representing DoCA, State Enforcement Authorities,
    Manufacturers, E-Commerce Platforms, or Demo tenants.
    """
    __tablename__ = "organisations"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Organisation type: DoCA, state, manufacturer, platform, demo",
    )
    state_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
        doc="ISO 3166-2:IN state code, e.g., 'DL', 'MH', 'KA', 'UP'",
    )
    code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
        doc="Unique organisation code, e.g. 'DOCA_CENTRAL', 'DL_METRO'",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True,
        doc="Status: active, inactive, suspended",
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    brands: Mapped[List["Brand"]] = relationship(
        "Brand",
        back_populates="manufacturer_org",
        foreign_keys="[Brand.manufacturer_org_id]",
    )
    inspections: Mapped[List["Inspection"]] = relationship(
        "Inspection",
        back_populates="organisation",
    )
    inspection_sessions: Mapped[List["InspectionSession"]] = relationship(
        "InspectionSession",
        back_populates="organisation",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="organisation",
    )

    __table_args__ = (
        Index("ix_organisations_type_state", "type", "state_code"),
    )

    def __repr__(self) -> str:
        return f"<Organisation(id={self.id}, name='{self.name}', type='{self.type}', status='{self.status}')>"
