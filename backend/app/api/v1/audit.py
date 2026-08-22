import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.audit import AuditVerificationResponse, AuditEventSchema
from app.services.audit_service import audit_service
from app.repositories.audit_repository import AuditRepository

router = APIRouter(prefix="/audit", tags=["Audit Chain"])


@router.get("/verify/{inspection_id}", response_model=AuditVerificationResponse)
async def verify_audit_chain(
    inspection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    return await audit_service.verify_inspection_chain(session, inspection_id)


@router.get("/inspections/{id}", response_model=list[AuditEventSchema])
async def get_inspection_audit_events(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    repo = AuditRepository(session)
    events = await repo.get_by_inspection_id(id)
    return [AuditEventSchema.model_validate(e) for e in events]
