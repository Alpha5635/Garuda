"""Rule Pack and Rule Version models for versioned, declarative LMPC compliance governance."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from backend.app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.organisation import Organisation
    from backend.app.models.user import User
    from backend.app.models.inspection import Inspection, Violation


class RulePack(Base, TimestampMixin):
    """
    Logical container for Legal Metrology rule packs (e.g. 'lmpc-core', 'lmpc-state-amendments').
    """
    __tablename__ = "rule_packs"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        doc="Identifier code, e.g. 'lmpc-core', 'lmpc-ecom'",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="India",
        doc="Jurisdiction scope, e.g. 'India', 'India-Delhi', 'India-Maharashtra'",
    )
    owner_org_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("organisations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    owner_org: Mapped["Organisation | None"] = relationship("Organisation")
    versions: Mapped[List["RuleVersion"]] = relationship(
        "RuleVersion",
        back_populates="rule_pack",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<RulePack(id='{self.id}', name='{self.name}', jurisdiction='{self.jurisdiction}')>"


class RuleVersion(Base, TimestampMixin):
    """
    Immutable released rule version. Every inspection pins exactly one rule version.
    Contains declarative JSON schema, regex patterns, logic expressions, source citations,
    and statutory penalty references under Legal Metrology Act, 2009, Section 36(1).
    """
    __tablename__ = "rule_versions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    rule_pack_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("rule_packs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Semantic version or release code, e.g. '2026.0', '2026.03'",
    )
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Effective statutory date of this rule pack release",
    )
    content_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        doc="Full declarative rule definitions, clauses, regexes, validation logic, severity weights",
    )
    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="SHA-256 hash of canonical content_jsonb for immutability verification",
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="staged",
        index=True,
        doc="Status: draft, staged, active, deprecated, immutable",
    )

    # Relationships
    rule_pack: Mapped["RulePack"] = relationship("RulePack", back_populates="versions")
    approver: Mapped["User | None"] = relationship("User", foreign_keys=[approved_by])
    inspections: Mapped[List["Inspection"]] = relationship(
        "Inspection",
        back_populates="rule_version",
    )
    violations: Mapped[List["Violation"]] = relationship(
        "Violation",
        back_populates="rule_version",
    )

    __table_args__ = (
        UniqueConstraint("rule_pack_id", "version", name="uq_rule_pack_version"),
        Index("ix_rule_versions_status_effective", "status", "effective_from"),
    )

    def __repr__(self) -> str:
        return f"<RuleVersion(id={self.id}, pack='{self.rule_pack_id}', version='{self.version}', status='{self.status}')>"
