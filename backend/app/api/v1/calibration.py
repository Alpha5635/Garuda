import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.calibration import CalibrationData
from app.schemas.calibration import CalibrationRequest, CalibrationResponse
from app.repositories.inspection_repository import InspectionRepository
from app.repositories.calibration_repository import CalibrationRepository
from app.repositories.image_repository import ImageRepository
from app.services.cv.calibration_service import calibration_service
from app.services.storage_service import storage_service

router = APIRouter(tags=["Calibration"])


@router.post("/inspections/{id}/calibration", response_model=CalibrationResponse)
async def set_calibration(
    id: uuid.UUID,
    data: CalibrationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    insp_repo = InspectionRepository(session)
    inspection = await insp_repo.get_by_id(id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")

    img_repo = ImageRepository(session)
    images = await img_repo.get_by_inspection_id(id)
    image = images[0] if images else None

    px_per_mm = 0.0
    if data.reference_width_px and data.reference_width_mm > 0:
        px_per_mm = data.reference_width_px / data.reference_width_mm

    calib = CalibrationData(
        inspection_id=id,
        image_id=image.id if image else None,
        calibration_type=data.calibration_type,
        reference_width_mm=data.reference_width_mm,
        reference_width_px=data.reference_width_px or 0.0,
        pixels_per_mm=px_per_mm,
        measurement_error=round(1.0 / px_per_mm, 3) if px_per_mm > 0 else 0.0,
        calibration_confidence=0.95
    )

    calib_repo = CalibrationRepository(session)
    calib = await calib_repo.create(calib)
    await session.commit()

    return CalibrationResponse.model_validate(calib)


@router.get("/inspections/{id}/calibration", response_model=CalibrationResponse)
async def get_calibration(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    calib_repo = CalibrationRepository(session)
    calib = await calib_repo.get_by_inspection_id(id)
    if not calib:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calibration data not found for this inspection")
    return CalibrationResponse.model_validate(calib)
