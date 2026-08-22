import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.calibration import CalibrationData
from app.repositories.base import BaseRepository


class CalibrationRepository(BaseRepository[CalibrationData]):
    def __init__(self, session: AsyncSession):
        super().__init__(CalibrationData, session)

    async def get_by_inspection_id(self, inspection_id: uuid.UUID) -> CalibrationData | None:
        stmt = (
            select(CalibrationData)
            .where(CalibrationData.inspection_id == inspection_id)
            .order_by(CalibrationData.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
