import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ecommerce import EcommerceListing
from app.repositories.base import BaseRepository


class EcommerceRepository(BaseRepository[EcommerceListing]):
    def __init__(self, session: AsyncSession):
        super().__init__(EcommerceListing, session)

    async def get_by_listing_id(self, listing_id: str) -> EcommerceListing | None:
        stmt = select(EcommerceListing).where(EcommerceListing.listing_id == listing_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
