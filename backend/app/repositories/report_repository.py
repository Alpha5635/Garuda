import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.report import ReportMetadata
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[ReportMetadata]):
    def __init__(self, session: AsyncSession):
        super().__init__(ReportMetadata, session)

    async def get_by_inspection_id(self, inspection_id: uuid.UUID) -> Sequence[ReportMetadata]:
        stmt = (
            select(ReportMetadata)
            .where(ReportMetadata.inspection_id == inspection_id)
            .order_by(ReportMetadata.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
