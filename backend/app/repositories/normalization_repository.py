import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.normalization import NormalizedField
from app.repositories.base import BaseRepository


class NormalizedFieldRepository(BaseRepository[NormalizedField]):
    def __init__(self, session: AsyncSession):
        super().__init__(NormalizedField, session)

    async def get_by_inspection_id(self, inspection_id: uuid.UUID) -> Sequence[NormalizedField]:
        stmt = select(NormalizedField).where(NormalizedField.inspection_id == inspection_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
