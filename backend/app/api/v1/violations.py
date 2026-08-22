import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.violation import ViolationSchema
from app.repositories.violation_repository import ViolationRepository

router = APIRouter(prefix="/violations", tags=["Violations"])


@router.get("/inspections/{id}", response_model=list[ViolationSchema])
async def get_inspection_violations(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    repo = ViolationRepository(session)
    violations = await repo.get_by_inspection_id(id)
    return [ViolationSchema.model_validate(v) for v in violations]
