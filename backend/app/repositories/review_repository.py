import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.human_review import FieldCorrection, ViolationReview
from app.repositories.base import BaseRepository


class FieldCorrectionRepository(BaseRepository[FieldCorrection]):
    def __init__(self, session: AsyncSession):
        super().__init__(FieldCorrection, session)

    async def get_by_inspection_id(self, inspection_id: uuid.UUID) -> Sequence[FieldCorrection]:
        stmt = select(FieldCorrection).where(FieldCorrection.inspection_id == inspection_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class ViolationReviewRepository(BaseRepository[ViolationReview]):
    def __init__(self, session: AsyncSession):
        super().__init__(ViolationReview, session)

    async def get_by_violation_id(self, violation_id: uuid.UUID) -> Sequence[ViolationReview]:
        stmt = select(ViolationReview).where(ViolationReview.violation_id == violation_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
