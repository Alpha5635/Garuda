"""Brand and Product catalog models."""

import uuid
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from backend.app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.organisation import Organisation
    from backend.app.models.inspection import Inspection
    from backend.app.models.intelligence import Offender, EcommerceListing


class Brand(Base, TimestampMixin):
    """
    Brand entity serving as normalization target for repeat-offender intelligence.
    Supports pg_trgm fuzzy matching for OCR tolerance.
    """
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Official registered brand name, e.g. 'Aashirvaad', 'Fortune', 'Tata Sampann'",
    )
    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        doc="Brand name / display name",
    )
    normalized_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        doc="Lowercased / stripped brand name for fast normalized lookups",
    )
    organisation_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("organisations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    aliases_jsonb: Mapped[List[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=list,
        doc="Common OCR variants, misspellings, and multilingual transliterations",
    )
    manufacturer_org_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID,
        ForeignKey("organisations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    manufacturer_org: Mapped["Organisation | None"] = relationship(
        "Organisation",
        back_populates="brands",
        foreign_keys=[manufacturer_org_id],
    )
    organisation: Mapped["Organisation | None"] = relationship(
        "Organisation",
        foreign_keys=[organisation_id],
    )
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="brand",
        cascade="all, delete-orphan",
    )
    offenders_history: Mapped[List["Offender"]] = relationship(
        "Offender",
        back_populates="brand",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_brands_canonical_name_trgm",
            "canonical_name",
            postgresql_using="gin",
            postgresql_ops={"canonical_name": "gin_trgm_ops"},
        ),
    )

    def __repr__(self) -> str:
        return f"<Brand(id={self.id}, canonical_name='{self.canonical_name}')>"


class Product(Base, TimestampMixin):
    """
    Product entity cataloging packaged commodities subject to LMPC Rules, 2011.
    """
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("brands.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        doc="Product name / commercial title",
    )
    generic_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Generic commodity name required under Rule 6(1)(b), e.g. 'Atta', 'Refined Sunflower Oil'",
    )
    sku: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Category: food_staples, edible_oil, cosmetics, cleaning_products, textiles, electronics, etc.",
    )
    is_imported: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Flag indicating if commodity is imported (triggers country-of-origin rule under Rule 6(1))",
    )
    metadata_jsonb: Mapped[Dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="Product metadata: HSN codes, default target quantity, standard dimensions",
    )

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    inspections: Mapped[List["Inspection"]] = relationship(
        "Inspection",
        back_populates="product",
    )
    ecommerce_listings: Mapped[List["EcommerceListing"]] = relationship(
        "EcommerceListing",
        back_populates="product",
    )

    __table_args__ = (
        Index("ix_products_category_imported", "category", "is_imported"),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, generic_name='{self.generic_name}', category='{self.category}')>"
