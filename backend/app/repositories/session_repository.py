import uuid
from typing import Sequence
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inspection_session import InspectionSession
from app.models.product_detection import ProductDetection


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, item: InspectionSession) -> InspectionSession:
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, session_id: uuid.UUID) -> InspectionSession | None:
        result = await self.session.execute(
            select(InspectionSession).where(InspectionSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_with_details(self, session_id: uuid.UUID) -> InspectionSession | None:
        result = await self.session.execute(
            select(InspectionSession)
            .options(
                selectinload(InspectionSession.images),
                selectinload(InspectionSession.detections),
                selectinload(InspectionSession.inspections)
            )
            .where(InspectionSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, idempotency_key: str) -> InspectionSession | None:
        result = await self.session.execute(
            select(InspectionSession).where(InspectionSession.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def get_by_client_session_id(self, client_session_id: str, inspector_id: uuid.UUID) -> InspectionSession | None:
        result = await self.session.execute(
            select(InspectionSession).where(
                and_(
                    InspectionSession.client_session_id == client_session_id,
                    InspectionSession.inspector_id == inspector_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_sessions(
        self,
        inspector_id: uuid.UUID | None = None,
        organisation_id: uuid.UUID | None = None,
        is_super_admin: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> Sequence[InspectionSession]:
        query = select(InspectionSession)

        if not is_super_admin:
            if organisation_id:
                query = query.where(InspectionSession.organisation_id == organisation_id)
            elif inspector_id:
                query = query.where(InspectionSession.inspector_id == inspector_id)

        query = query.order_by(InspectionSession.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, item: InspectionSession) -> InspectionSession:
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def create_detection(self, detection: ProductDetection) -> ProductDetection:
        self.session.add(detection)
        await self.session.commit()
        await self.session.refresh(detection)
        return detection

    async def get_detections_for_session(self, session_id: uuid.UUID) -> Sequence[ProductDetection]:
        result = await self.session.execute(
            select(ProductDetection)
            .where(ProductDetection.session_id == session_id)
            .options(
                selectinload(ProductDetection.inspection),
                selectinload(ProductDetection.image)
            )
            .order_by(ProductDetection.created_at.asc())
        )
        return result.scalars().all()

    async def get_detection_by_id(self, detection_id: uuid.UUID) -> ProductDetection | None:
        result = await self.session.execute(
            select(ProductDetection)
            .where(ProductDetection.id == detection_id)
            .options(
                selectinload(ProductDetection.inspection),
                selectinload(ProductDetection.session)
            )
        )
        return result.scalar_one_or_none()
