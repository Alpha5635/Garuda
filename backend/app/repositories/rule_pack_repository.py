import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.rule_pack import RulePackVersion
from app.repositories.base import BaseRepository


class RulePackRepository(BaseRepository[RulePackVersion]):
    def __init__(self, session: AsyncSession):
        super().__init__(RulePackVersion, session)

    async def get_by_version(self, version: str) -> RulePackVersion | None:
        stmt = select(RulePackVersion).where(RulePackVersion.version == version)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active(self) -> RulePackVersion | None:
        stmt = select(RulePackVersion).where(RulePackVersion.is_active == True).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()
