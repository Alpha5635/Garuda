from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organisation import Organisation
from app.repositories.base import BaseRepository


class OrganisationRepository(BaseRepository[Organisation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Organisation, session)
