import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.image import ImageUploadUrlRequest, ImageUploadUrlResponse, ImageResponse
from app.schemas.job import JobResponse
from app.services.storage_service import storage_service
from app.services.inspection.inspection_service import InspectionService
from app.repositories.inspection_repository import InspectionRepository
from app.workers.tasks import process_inspection_image_task

router = APIRouter(tags=["Images"])


@router.post("/inspections/{id}/images/upload-url", response_model=ImageUploadUrlResponse)
async def generate_image_upload_url(
    id: uuid.UUID,
    data: ImageUploadUrlRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    insp_repo = InspectionRepository(session)
    inspection = await insp_repo.get_by_id(id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")

    ext = os.path.splitext(data.filename)[1] or ".jpg"
    unique_filename = f"{uuid.uuid4()}{ext}"
    object_key = f"inspections/{id}/{unique_filename}"

    service = InspectionService(session)
    image = await service.create_image_metadata(
        inspection_id=id,
        object_key=object_key,
        filename=data.filename,
        sha256_hash=data.sha256_hash,
        mime_type=data.mime_type,
        file_size=data.file_size,
        width=data.width,
        height=data.height,
        capture_timestamp=data.capture_timestamp,
        gps_latitude=data.gps_latitude,
        gps_longitude=data.gps_longitude
    )

    job = await service.create_processing_job(inspection_id=id, image_id=image.id)
    await session.commit()

    # Trigger Celery job
    process_inspection_image_task.delay(str(job.id))

    upload_url = storage_service.generate_upload_url(object_key)

    return ImageUploadUrlResponse(
        image_id=image.id,
        upload_url=upload_url,
        object_key=object_key
    )


@router.post("/inspections/{id}/images/direct-upload", response_model=JobResponse)
async def direct_image_upload(
    id: uuid.UUID,
    file: UploadFile = File(...),
    gps_latitude: float | None = Form(None),
    gps_longitude: float | None = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    insp_repo = InspectionRepository(session)
    inspection = await insp_repo.get_by_id(id)
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")

    file_bytes = await file.read()
    sha256_hash = storage_service.compute_sha256(file_bytes)

    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    object_key = f"inspections/{id}/{uuid.uuid4()}{ext}"

    storage_service.upload_file_bytes(object_key, file_bytes, content_type=file.content_type or "image/jpeg")

    service = InspectionService(session)
    image = await service.create_image_metadata(
        inspection_id=id,
        object_key=object_key,
        filename=file.filename or "uploaded.jpg",
        sha256_hash=sha256_hash,
        mime_type=file.content_type or "image/jpeg",
        file_size=len(file_bytes),
        gps_latitude=gps_latitude,
        gps_longitude=gps_longitude
    )

    job = await service.create_processing_job(inspection_id=id, image_id=image.id)
    await session.commit()

    # Launch Celery background task
    process_inspection_image_task.delay(str(job.id))

    return JobResponse.model_validate(job)
