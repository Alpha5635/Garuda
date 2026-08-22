import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.report import ReportMetadata
from app.schemas.report import ReportRequest, ReportResponse
from app.repositories.inspection_repository import InspectionRepository
from app.repositories.image_repository import ImageRepository
from app.repositories.normalization_repository import NormalizedFieldRepository
from app.repositories.violation_repository import ViolationRepository
from app.repositories.report_repository import ReportRepository
from app.services.report_service import report_service
from app.services.storage_service import storage_service
from app.services.audit_service import audit_service

router = APIRouter(tags=["Reports"])


@router.post("/inspections/{id}/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_inspection_report(
    id: uuid.UUID,
    data: ReportRequest,
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

    norm_repo = NormalizedFieldRepository(session)
    normalized_fields = await norm_repo.get_by_inspection_id(id)

    viol_repo = ViolationRepository(session)
    violations = await viol_repo.get_by_inspection_id(id)

    report_payload = report_service.build_report_data(inspection, image, normalized_fields, violations)

    # Generate document bytes
    fmt = data.format.lower()
    if fmt == "pdf":
        file_bytes = report_service.generate_pdf_bytes(report_payload)
        ext = ".pdf"
    elif fmt == "docx":
        file_bytes = report_service.generate_docx_bytes(report_payload)
        ext = ".docx"
    elif fmt == "csv":
        file_bytes = report_service.generate_csv_bytes(report_payload)
        ext = ".csv"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported report format. Must be pdf, docx, or csv")

    report_sha256 = storage_service.compute_sha256(file_bytes)
    object_key = f"reports/inspections/{id}/report_{uuid.uuid4()}{ext}"

    storage_service.upload_file_bytes(object_key, file_bytes, content_type=f"application/{fmt}")

    rep_repo = ReportRepository(session)
    report_meta = ReportMetadata(
        inspection_id=id,
        format=fmt,
        object_key=object_key,
        file_size=len(file_bytes),
        sha256_hash=report_sha256
    )
    report_meta = await rep_repo.create(report_meta)

    # Log audit event
    await audit_service.log_event(
        session=session,
        action="REPORT_GENERATED",
        entity_type="report",
        entity_id=str(report_meta.id),
        actor_email=current_user.email,
        inspection_id=id,
        actor_id=current_user.id,
        after_state={"format": fmt, "sha256": report_sha256}
    )

    await session.commit()

    download_url = storage_service.generate_upload_url(object_key, expires_in=3600)

    return ReportResponse(
        id=report_meta.id,
        inspection_id=id,
        format=fmt,
        object_key=object_key,
        file_size=len(file_bytes),
        sha256_hash=report_sha256,
        download_url=download_url,
        expires_in_seconds=3600,
        created_at=report_meta.created_at
    )


@router.get("/reports/{id}/download")
async def download_report_url(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    rep_repo = ReportRepository(session)
    report_meta = await rep_repo.get_by_id(id)
    if not report_meta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report record not found")

    download_url = storage_service.generate_upload_url(report_meta.object_key, expires_in=3600)
    return {
        "report_id": str(report_meta.id),
        "download_url": download_url,
        "sha256_hash": report_meta.sha256_hash
    }
