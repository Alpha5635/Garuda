import uuid
from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class RulePackVersion(Base, TimestampMixin):
    __tablename__ = "rule_pack_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    version: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. rp-2026.03
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="staged", nullable=False) # staged, active, archived
    rules_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
