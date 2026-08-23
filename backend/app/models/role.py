"""Role and UserRole models for Role-Based Access Control (RBAC)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from backend.app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.organisation import Organisation


class Role(Base, TimestampMixin):
    """
    System role entity defining authority levels:
    - super_admin: System-wide governance and cryptographic audit verification
    - rule_admin: Authoring, validating, and approving LMPC rule packs
    - officer: Field inspections, violation acceptance/dismissal, statutory signing
    - reviewer: Human-in-the-loop OCR verification and correction queue
    - manufacturer: Pre-launch self-check and label compliance verification
    - consumer: Scan-and-report citizen interface
    - analyst: Aggregate dashboard analytics and heatmaps
    """
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique role code: super_admin, rule_admin, officer, reviewer, manufacturer, consumer, analyst",
    )
    name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        doc="Human-readable role name / alias for code",
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    permissions_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Granular permission flags and scoped action grants",
    )

    # Relationships
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, code='{self.code}')>"


class UserRole(Base):
    """
    Join table linking Users to Roles, optionally scoped within an Organisation context.
    Allows an officer to act as a reviewer without role sprawl.
    """
    __tablename__ = "user_roles"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organisation_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")
    organisation: Mapped["Organisation | None"] = relationship("Organisation")

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "organisation_id", name="uq_user_role_org"),
    )

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}, organisation_id={self.organisation_id})>"
