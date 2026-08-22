import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit import AuditChain
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditChain]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuditChain, session)

    async def get_by_inspection_id(self, inspection_id: uuid.UUID) -> Sequence[AuditChain]:
        stmt = (
            select(AuditChain)
            .where(AuditChain.inspection_id == inspection_id)
            .order_by(AuditChain.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_latest_event(self) -> AuditChain | None:
        stmt = (
            select(AuditChain)
            .order_by(AuditChain.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
