import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.rule_pack import RulePackVersionRequest, RulePackVersionResponse
from app.services.rule_admin_service import rule_admin_service
from app.repositories.rule_pack_repository import RulePackRepository

router = APIRouter(prefix="/rule-packs", tags=["Rule Pack Administration"])


@router.get("", response_model=list[RulePackVersionResponse])
async def list_rule_packs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    repo = RulePackRepository(session)
    packs = await repo.get_all()
    return [RulePackVersionResponse.model_validate(p) for p in packs]


@router.post("", response_model=RulePackVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_staged_rule_pack(
    data: RulePackVersionRequest,
    current_user: User = Depends(require_roles(UserRole.RULE_ADMIN, UserRole.SUPER_ADMIN)),
    session: AsyncSession = Depends(get_db)
):
    pack = await rule_admin_service.create_staged_rule_pack(session, data)
    await session.commit()
    return RulePackVersionResponse.model_validate(pack)


@router.post("/{id}/approve", response_model=RulePackVersionResponse)
async def approve_rule_pack_version(
    id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.RULE_ADMIN, UserRole.SUPER_ADMIN)),
    session: AsyncSession = Depends(get_db)
):
    pack = await rule_admin_service.approve_rule_pack(session, id)
    if not pack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule pack version not found")
    await session.commit()
    return RulePackVersionResponse.model_validate(pack)
