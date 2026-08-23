import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.report import ReportMetadata
from app.schemas.inspection_session import (
    SessionCreateRequest,
    SessionResponse,
    SessionStatusResponse,
    BatchImageUploadRequest,
    BatchImageUploadResponse,
    SessionProductListResponse,
    RecaptureProductListResponse,
    RecaptureUploadResponse
)
from app.schemas.session_report import (
    SessionReportGenerateRequest,
    SessionReportResponse
)
from app.services.inspection.batch_inspection_service import BatchInspectionService
from app.services.report_service import report_service
from app.services.storage_service import storage_service
from app.services.audit_service import AuditService
from app.workers.tasks import process_batch_shelf_image_task, reprocess_product_recapture_task

router = APIRouter(prefix="/inspection-sessions", tags=["Inspection Sessions"])


def _check_session_access(session_obj, current_user: User):
    """Enforces organisation isolation & access control."""
    if current_user.role == UserRole.SUPER_ADMIN.value:
        return
    if session_obj.organisation_id and current_user.organisation_id:
        if session_obj.organisation_id != current_user.organisation_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden: different organisation")
    elif session_obj.inspector_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden: not the assigned inspector")


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection_session(
    data: SessionCreateRequest,
    current_user: User = Depends(require_roles(UserRole.OFFICER, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    service = BatchInspectionService(db)
    session_obj = await service.create_session(
        inspector_id=current_user.id,
        organisation_id=current_user.organisation_id,
        data=data
    )
    metrics = await service.get_session_summary_metrics(session_obj.id)
    
    resp_dict = {c.name: getattr(session_obj, c.name) for c in session_obj.__table__.columns}
    resp_dict.update(metrics)
    return resp_dict


@router.get("", response_model=list[SessionResponse])
async def list_inspection_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BatchInspectionService(db)
    is_super = current_user.role == UserRole.SUPER_ADMIN.value
    sessions = await service.list_sessions(
        inspector_id=current_user.id,
        organisation_id=current_user.organisation_id,
        is_super_admin=is_super,
        skip=skip,
        limit=limit
    )
    
    results = []
    for s in sessions:
        metrics = await service.get_session_summary_metrics(s.id)
        d = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        d.update(metrics)
        results.append(d)
    return results


@router.get("/{session_id}", response_model=SessionResponse)
async def get_inspection_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    metrics = await service.get_session_summary_metrics(session_id)
    d = {c.name: getattr(session_obj, c.name) for c in session_obj.__table__.columns}
    d.update(metrics)
    return d


@router.post("/{session_id}/images/upload-url", response_model=BatchImageUploadResponse)
async def generate_batch_image_upload_urls(
    session_id: uuid.UUID,
    data: BatchImageUploadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    result = await service.generate_batch_upload_urls(session_id=session_id, data=data)
    await db.commit()

    # Queue detection tasks for each image
    for item in result.uploads:
        process_batch_shelf_image_task.delay(str(session_id), str(item.image_id))

    return result


@router.post("/{session_id}/images/direct-upload")
async def direct_upload_shelf_image(
    session_id: uuid.UUID,
    file: UploadFile = File(...),
    gps_latitude: float | None = Form(None),
    gps_longitude: float | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    file_bytes = await file.read()
    image = await service.direct_upload_shelf_image(
        session_id=session_id,
        file_bytes=file_bytes,
        filename=file.filename or "shelf.jpg",
        content_type=file.content_type or "image/jpeg",
        gps_latitude=gps_latitude,
        gps_longitude=gps_longitude
    )
    await db.commit()

    # Trigger product detection task
    process_batch_shelf_image_task.delay(str(session_id), str(image.id))

    return {
        "session_id": session_id,
        "image_id": image.id,
        "status": "detecting_products",
        "message": "Shelf image uploaded successfully, product detection started"
    }


@router.get("/{session_id}/products", response_model=SessionProductListResponse)
async def list_session_products(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    return await service.get_session_products(session_id)


# --- Smart Recapture Endpoints ---

@router.get("/{session_id}/recapture", response_model=RecaptureProductListResponse)
async def get_session_recapture_products(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns only the specific products in this session requiring smart recapture
    along with root-cause diagnostic reasons (blur, glare, low_resolution, bad_orientation, etc.).
    """
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    return await service.get_recapture_products(session_id)


@router.post("/{session_id}/products/{product_id}/recapture", response_model=RecaptureUploadResponse)
async def direct_upload_product_recapture(
    session_id: uuid.UUID,
    product_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Non-destructively replaces evidence for a single problematic product.
    Maintains full audit chain and triggers pipeline re-processing.
    """
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    file_bytes = await file.read()
    new_image = await service.direct_upload_product_recapture(
        session_id=session_id,
        product_id=product_id,
        file_bytes=file_bytes,
        filename=file.filename or "recapture.jpg",
        content_type=file.content_type or "image/jpeg",
        actor_id=current_user.id
    )
    await db.commit()

    # Trigger re-processing task
    reprocess_product_recapture_task.delay(str(session_id), str(product_id), str(new_image.id))

    return RecaptureUploadResponse(
        session_id=session_id,
        product_id=product_id,
        image_id=new_image.id,
        status="processing",
        message="Replacement evidence uploaded non-destructively. Product re-processing initiated."
    )


# --- Session Report Endpoints ---

@router.post("/{session_id}/reports", response_model=SessionReportResponse)
async def generate_session_report(
    session_id: uuid.UUID,
    data: SessionReportGenerateRequest,
    current_user: User = Depends(require_roles(UserRole.OFFICER, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Generates an official session-level inspection PDF, CSV, or DOCX report."""
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    products_res = await service.get_session_products(session_id)
    metrics = await service.get_session_summary_metrics(session_id)

    session_data = {
        "session_id": str(session_obj.id),
        "location": session_obj.location,
        "latitude": session_obj.latitude,
        "longitude": session_obj.longitude,
        "inspector_id": str(session_obj.inspector_id),
        "status": session_obj.status,
        "total_images": session_obj.total_images,
        "total_products": session_obj.total_products,
        "started_at": session_obj.started_at.isoformat() if session_obj.started_at else "",
        "metrics": metrics,
        "products": [
            {
                "product_id": str(p.product_id),
                "inspection_id": str(p.inspection_id) if p.inspection_id else "",
                "priority": p.priority or "low",
                "status": p.inspection_status or "compliant",
                "reason": p.priority_reason or "compliant",
                "confidence": p.priority_confidence,
                "rule_evaluations": []
            }
            for p in products_res.products
        ]
    }

    report_fmt = data.format.lower()
    if report_fmt == "pdf":
        file_bytes = report_service.generate_session_pdf_bytes(session_data)
        mime = "application/pdf"
    elif report_fmt == "docx":
        file_bytes = report_service.generate_session_docx_bytes(session_data)
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        file_bytes = report_service.generate_session_csv_bytes(session_data)
        mime = "text/csv"

    sha256 = storage_service.compute_sha256(file_bytes)
    report_id = uuid.uuid4()
    object_key = f"sessions/{session_id}/reports/{report_id}.{report_fmt}"
    storage_service.upload_file_bytes(object_key, file_bytes, content_type=mime)

    report_meta = ReportMetadata(
        id=report_id,
        session_id=session_id,
        inspection_id=None,
        format=report_fmt,
        object_key=object_key,
        file_size=len(file_bytes),
        sha256_hash=sha256
    )
    db.add(report_meta)
    await db.commit()
    await db.refresh(report_meta)

    # Log audit event
    audit_service = AuditService()
    await audit_service.log_event(
        session=db,
        action="report_generated",
        entity_type="report",
        entity_id=str(report_id),
        actor_id=current_user.id,
        after_state={"session_id": str(session_id), "format": report_fmt, "sha256": sha256}
    )

    return report_meta


@router.get("/{session_id}/reports", response_model=list[SessionReportResponse])
async def list_session_reports(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    result = await db.execute(select(ReportMetadata).where(ReportMetadata.session_id == session_id).order_by(ReportMetadata.created_at.desc()))
    return result.scalars().all()


@router.get("/{session_id}/reports/{report_id}/download")
async def download_session_report(
    session_id: uuid.UUID,
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BatchInspectionService(db)
    session_obj = await service.get_session(session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection session not found")
    _check_session_access(session_obj, current_user)

    result = await db.execute(select(ReportMetadata).where(ReportMetadata.id == report_id, ReportMetadata.session_id == session_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    file_bytes = storage_service.download_file_bytes(report.object_key)
    media_type = "application/pdf" if report.format == "pdf" else ("application/vnd.openxmlformats-officedocument.wordprocessingml.document" if report.format == "docx" else "text/csv")
    
    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="session_report_{session_id}_{report_id}.{report.format}"'}
    )
