import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.job import JobResponse
from app.schemas.ocr import InspectionAnalysisResponse, OcrResultContainer, ExtractedFieldCandidate
from app.repositories.job_repository import JobRepository

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{id}", response_model=InspectionAnalysisResponse)
async def get_job_status(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    repo = JobRepository(session)
    job = await repo.get_by_id(id)

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    ocr_data = job.ocr_data_json or {}
    items = ocr_data.get("items", [])
    text = ocr_data.get("text", [])
    confidence = ocr_data.get("confidence", 0.0)

    ocr_container = OcrResultContainer(items=items, text=text, confidence=confidence)

    raw_fields = job.extracted_fields_json or []
    extracted_fields = [ExtractedFieldCandidate(**f) for f in raw_fields]

    return InspectionAnalysisResponse(
        inspection_id=str(job.inspection_id),
        status=job.status,
        ocr=ocr_container,
        fields=extracted_fields,
        job_id=str(job.id),
        error_reason=job.error_reason
    )
