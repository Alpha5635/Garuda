import uuid
from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.inspection import InspectionCreate, InspectionResponse, InspectionDetailResponse
from app.schemas.image import ImageResponse
from app.schemas.job import JobResponse
from app.services.inspection.inspection_service import InspectionService
from app.repositories.inspection_repository import InspectionRepository
from app.repositories.job_repository import JobRepository

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    data: InspectionCreate,
    current_user: User = Depends(require_roles(UserRole.OFFICER, UserRole.SUPER_ADMIN)),
    session: AsyncSession = Depends(get_db)
):
    service = InspectionService(session)
    inspection = await service.create_inspection(officer_id=current_user.id, data=data)
    return inspection


@router.get("", response_model=list[InspectionResponse])
async def list_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    repo = InspectionRepository(session)
    if current_user.role == UserRole.OFFICER.value:
        inspections = await repo.get_by_officer(officer_id=current_user.id, skip=skip, limit=limit)
    else:
        inspections = await repo.get_all(skip=skip, limit=limit)
    return inspections


@router.get("/{id}", response_model=InspectionDetailResponse)
async def get_inspection_detail(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    repo = InspectionRepository(session)
    job_repo = JobRepository(session)

    inspection = await repo.get_with_details(id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")

    latest_job = await job_repo.get_latest_for_inspection(id)

    images_data = [ImageResponse.model_validate(img) for img in inspection.images]
    latest_job_data = JobResponse.model_validate(latest_job) if latest_job else None

    return InspectionDetailResponse(
        id=inspection.id,
        inspection_number=inspection.inspection_number,
        officer_id=inspection.officer_id,
        organisation_id=inspection.organisation_id,
        status=inspection.status,
        channel=inspection.channel,
        state=inspection.state,
        district=inspection.district,
        product_name=inspection.product_name,
        brand_name=inspection.brand_name,
        created_at=inspection.created_at,
        updated_at=inspection.updated_at,
        images=images_data,
        latest_job=latest_job_data
    )
