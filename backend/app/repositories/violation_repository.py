import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.violation import Violation
from app.repositories.base import BaseRepository


class ViolationRepository(BaseRepository[Violation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Violation, session)

    async def get_by_inspection_id(self, inspection_id: uuid.UUID) -> Sequence[Violation]:
        stmt = select(Violation).where(Violation.inspection_id == inspection_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
