import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class EcommerceListing(Base, TimestampMixin):
    __tablename__ = "ecommerce_listings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    inspection_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inspections.id", ondelete="SET NULL"),
        nullable=True
    )
    platform: Mapped[str] = mapped_column(String(100), nullable=False) # Amazon, Flipkart, Blinkit, etc.
    listing_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    seller_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    snapshot_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    declarations_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    inspection = relationship("Inspection")
