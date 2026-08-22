import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.image import Image
from app.repositories.base import BaseRepository


class ImageRepository(BaseRepository[Image]):
    def __init__(self, session: AsyncSession):
        super().__init__(Image, session)

    async def get_by_inspection_id(self, inspection_id: uuid.UUID) -> Sequence[Image]:
        stmt = select(Image).where(Image.inspection_id == inspection_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_hash(self, sha256_hash: str) -> Image | None:
        stmt = select(Image).where(Image.sha256_hash == sha256_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()
