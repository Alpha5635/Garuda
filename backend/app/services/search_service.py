import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.inspection import Inspection
from app.models.user import User, UserRole
from app.schemas.search import SearchQuery


class SearchService:
    async def search_inspections(
        self,
        session: AsyncSession,
        current_user: User,
        query: SearchQuery
    ) -> Sequence[Inspection]:
        stmt = select(Inspection)

        # 1. Organisation Isolation Guard
        if current_user.role == UserRole.MANUFACTURER.value and current_user.organisation_id:
            stmt = stmt.where(Inspection.organisation_id == current_user.organisation_id)
        elif current_user.role == UserRole.OFFICER.value:
            stmt = stmt.where(Inspection.officer_id == current_user.id)

        # 2. Text Search / Product Name
        if query.query:
            term = f"%{query.query}%"
            stmt = stmt.where(
                or_(
                    Inspection.product_name.ilike(term),
                    Inspection.brand_name.ilike(term),
                    Inspection.inspection_number.ilike(term)
                )
            )

        if query.product_name:
            stmt = stmt.where(Inspection.product_name.ilike(f"%{query.product_name}%"))

        if query.district:
            stmt = stmt.where(Inspection.district.ilike(f"%{query.district}%"))

        if query.status:
            stmt = stmt.where(Inspection.status == query.status)

        stmt = stmt.order_by(Inspection.created_at.desc()).offset(query.skip).limit(query.limit)
        result = await session.execute(stmt)
        return result.scalars().all()


search_service = SearchService()
