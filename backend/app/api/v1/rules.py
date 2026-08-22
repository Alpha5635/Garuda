import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.rule_engine import RuleDefinition, RuleEvaluationResult
from app.services.rules.rule_engine_service import rule_engine_service
from app.services.cv.calibration_service import CalibrationResult
from app.repositories.inspection_repository import InspectionRepository
from app.repositories.job_repository import JobRepository
from app.repositories.calibration_repository import CalibrationRepository
from app.schemas.normalization import NormalizedFieldSchema

router = APIRouter(tags=["Rules & Evaluation"])


@router.get("/rules", response_model=list[RuleDefinition])
async def list_rules():
    return [RuleDefinition(**r) for r in rule_engine_service.rules]


@router.post("/inspections/{id}/evaluate", response_model=list[RuleEvaluationResult])
async def evaluate_inspection_rules(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    insp_repo = InspectionRepository(session)
    inspection = await insp_repo.get_by_id(id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")

    job_repo = JobRepository(session)
    job = await job_repo.get_latest_for_inspection(id)
    if not job or not job.extracted_fields_json:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No extracted fields available for evaluation")

    calib_repo = CalibrationRepository(session)
    calib = await calib_repo.get_by_inspection_id(id)

    calib_res = CalibrationResult(
        is_valid=calib is not None and calib.pixels_per_mm > 0,
        calibration_type=calib.calibration_type if calib else "uncalibrated",
        reference_width_mm=calib.reference_width_mm if calib else 0.0,
        reference_width_px=calib.reference_width_px if calib else 0.0,
        pixels_per_mm=calib.pixels_per_mm if calib else 0.0,
        measurement_error=calib.measurement_error if calib else 0.0,
        calibration_confidence=calib.calibration_confidence if calib else 0.0
    )

    # Re-normalize fields
    from app.services.normalization_service import normalization_service
    from app.schemas.ocr import ExtractedFieldCandidate, OcrItemSchema

    candidates = [ExtractedFieldCandidate(**f) for f in job.extracted_fields_json]
    ocr_items = [OcrItemSchema(**item) for item in (job.ocr_data_json or {}).get("items", [])]
    normalized_fields = normalization_service.normalize_fields(candidates, ocr_items)

    results = rule_engine_service.evaluate_all_rules(
        normalized_fields=normalized_fields,
        calibration_result=calib_res,
        channel=inspection.channel or "Retail store"
    )

    return results
