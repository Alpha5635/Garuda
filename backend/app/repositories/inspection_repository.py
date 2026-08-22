import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.inspection import Inspection
from app.repositories.base import BaseRepository


class InspectionRepository(BaseRepository[Inspection]):
    def __init__(self, session: AsyncSession):
        super().__init__(Inspection, session)

    async def get_with_details(self, id: uuid.UUID) -> Inspection | None:
        stmt = (
            select(Inspection)
            .options(
                selectinload(Inspection.images),
                selectinload(Inspection.jobs)
            )
            .where(Inspection.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_officer(self, officer_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Inspection]:
        stmt = (
            select(Inspection)
            .where(Inspection.officer_id == officer_id)
            .order_by(Inspection.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Inspection))
        return result.scalar() or 0
