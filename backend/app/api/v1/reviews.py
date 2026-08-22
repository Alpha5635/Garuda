import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.human_review import FieldCorrection, ViolationReview
from app.schemas.human_review import FieldCorrectionRequest, ViolationReviewRequest, HumanReviewResponse
from app.repositories.review_repository import FieldCorrectionRepository, ViolationReviewRepository
from app.repositories.violation_repository import ViolationRepository

router = APIRouter(prefix="/reviews", tags=["Human Reviews"])


@router.post("/inspections/{id}/ocr-correction", response_model=HumanReviewResponse)
async def submit_ocr_correction(
    id: uuid.UUID,
    data: FieldCorrectionRequest,
    current_user: User = Depends(require_roles(UserRole.OFFICER, UserRole.REVIEWER, UserRole.SUPER_ADMIN)),
    session: AsyncSession = Depends(get_db)
):
    repo = FieldCorrectionRepository(session)
    correction = FieldCorrection(
        inspection_id=id,
        reviewer_id=current_user.id,
        field_name=data.field_name,
        original_ocr_value=data.original_ocr_value,
        corrected_value=data.corrected_value,
        reason=data.reason
    )
    correction = await repo.create(correction)
    await session.commit()

    return HumanReviewResponse(
        status="success",
        message=f"OCR correction recorded for field '{data.field_name}'",
        updated_record_id=correction.id
    )


@router.post("/violation-decision", response_model=HumanReviewResponse)
async def submit_violation_review(
    data: ViolationReviewRequest,
    current_user: User = Depends(require_roles(UserRole.OFFICER, UserRole.REVIEWER, UserRole.SUPER_ADMIN)),
    session: AsyncSession = Depends(get_db)
):
    v_repo = ViolationRepository(session)
    violation = await v_repo.get_by_id(data.violation_id)
    if not violation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation record not found")

    if data.decision not in ["accepted", "rejected", "waived"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Decision must be 'accepted', 'rejected', or 'waived'")

    if data.decision == "waived" and not data.justification_reason:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Waiving a violation requires a justification reason")

    rev_repo = ViolationReviewRepository(session)
    review = ViolationReview(
        violation_id=data.violation_id,
        reviewer_id=current_user.id,
        decision=data.decision,
        justification_reason=data.justification_reason
    )
    review = await rev_repo.create(review)
    await session.commit()

    return HumanReviewResponse(
        status="success",
        message=f"Violation decision '{data.decision}' recorded successfully.",
        updated_record_id=review.id
    )
