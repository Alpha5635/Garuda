import uuid
from enum import Enum
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class UserRole(str, Enum):
    OFFICER = "officer"
    REVIEWER = "reviewer"
    MANUFACTURER = "manufacturer"
    CONSUMER = "consumer"
    ANALYST = "analyst"
    RULE_ADMIN = "rule_admin"
    SUPER_ADMIN = "super_admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=UserRole.OFFICER.value, nullable=False)
    organisation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="SET NULL"),
        nullable=True
    )

    organisation = relationship("Organisation", back_populates="users")
    inspections = relationship("Inspection", back_populates="officer")
    inspection_sessions = relationship("InspectionSession", back_populates="inspector")
