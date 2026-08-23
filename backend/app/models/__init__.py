"""LabelSetu Database Models module exporting all 19 relational entities and Base."""

from backend.app.db.base import Base, GUID, TimestampMixin
from backend.app.models.organisation import Organisation
from backend.app.models.role import Role, UserRole
from backend.app.models.user import User
from backend.app.models.catalog import Brand, Product
from backend.app.models.rule import RulePack, RuleVersion
from backend.app.models.inspection import (
    Inspection,
    ProductImage,
    ExtractedField,
    Violation,
    Report,
    ReviewAction,
)
from backend.app.models.session import (
    InspectionSession,
    BatchImage,
    ProductDetection,
)
from backend.app.models.audit import AuditLog
from backend.app.models.intelligence import (
    Offender,
    SyncQueue,
    EcommerceListing,
    ModelVersion,
)

__all__ = [
    "Base",
    "GUID",
    "TimestampMixin",
    "Organisation",
    "Role",
    "UserRole",
    "User",
    "Brand",
    "Product",
    "RulePack",
    "RuleVersion",
    "InspectionSession",
    "BatchImage",
    "ProductDetection",
    "Inspection",
    "ProductImage",
    "ExtractedField",
    "Violation",
    "Report",
    "ReviewAction",
    "AuditLog",
    "Offender",
    "SyncQueue",
    "EcommerceListing",
    "ModelVersion",
]
