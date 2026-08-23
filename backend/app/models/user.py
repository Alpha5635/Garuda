"""User identity and authentication model."""

import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.organisation import Organisation
    from backend.app.models.role import UserRole
    from backend.app.models.inspection import Inspection, ReviewAction, Report


class User(Base, TimestampMixin):
    """
    User entity representing officers, reviewers, administrators, manufacturers, or analysts.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("organisations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True,
        doc="Status: active, inactive, pending, suspended",
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organisation: Mapped["Organisation"] = relationship(
        "Organisation",
        back_populates="users",
    )
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    inspections_created: Mapped[List["Inspection"]] = relationship(
        "Inspection",
        back_populates="creator",
        foreign_keys="Inspection.created_by",
    )
    review_actions: Mapped[List["ReviewAction"]] = relationship(
        "ReviewAction",
        back_populates="reviewer",
    )
    reports_generated: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="generator",
        foreign_keys="Report.generated_by",
    )
    reports_approved: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="approver",
        foreign_keys="Report.approved_by",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', status='{self.status}')>"
