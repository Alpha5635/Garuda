import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.job import ProcessingJob
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[ProcessingJob]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProcessingJob, session)

    async def get_by_inspection_id(self, inspection_id: uuid.UUID) -> Sequence[ProcessingJob]:
        stmt = (
            select(ProcessingJob)
            .where(ProcessingJob.inspection_id == inspection_id)
            .order_by(ProcessingJob.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_latest_for_inspection(self, inspection_id: uuid.UUID) -> ProcessingJob | None:
        stmt = (
            select(ProcessingJob)
            .where(ProcessingJob.inspection_id == inspection_id)
            .order_by(ProcessingJob.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
