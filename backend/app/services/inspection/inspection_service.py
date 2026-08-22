import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inspection import Inspection, InspectionStatus
from app.models.image import Image
from app.models.job import ProcessingJob, JobState
from app.repositories.inspection_repository import InspectionRepository
from app.repositories.image_repository import ImageRepository
from app.repositories.job_repository import JobRepository
from app.schemas.inspection import InspectionCreate


class InspectionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.inspection_repo = InspectionRepository(session)
        self.image_repo = ImageRepository(session)
        self.job_repo = JobRepository(session)

    async def create_inspection(self, officer_id: uuid.UUID, data: InspectionCreate) -> Inspection:
        count = await self.inspection_repo.count_all()
        year = datetime.now(timezone.utc).year
        inspection_number = f"LM/{year}/{(count + 1):05d}"

        inspection = Inspection(
            inspection_number=inspection_number,
            officer_id=officer_id,
            organisation_id=data.organisation_id,
            status=InspectionStatus.DRAFT.value,
            channel=data.channel,
            state=data.state,
            district=data.district,
            product_name=data.product_name,
            brand_name=data.brand_name,
            metadata_json=data.metadata_json or {}
        )
        return await self.inspection_repo.create(inspection)

    async def create_image_metadata(
        self,
        inspection_id: uuid.UUID,
        object_key: str,
        filename: str,
        sha256_hash: str,
        mime_type: str,
        file_size: int,
        width: int | None = None,
        height: int | None = None,
        capture_timestamp: datetime | None = None,
        gps_latitude: float | None = None,
        gps_longitude: float | None = None,
    ) -> Image:
        image = Image(
            inspection_id=inspection_id,
            object_key=object_key,
            original_filename=filename,
            sha256_hash=sha256_hash,
            mime_type=mime_type,
            file_size=file_size,
            width=width,
            height=height,
            capture_timestamp=capture_timestamp,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude
        )
        return await self.image_repo.create(image)

    async def create_processing_job(self, inspection_id: uuid.UUID, image_id: uuid.UUID) -> ProcessingJob:
        job = ProcessingJob(
            inspection_id=inspection_id,
            image_id=image_id,
            status=JobState.QUEUED.value
        )
        job = await self.job_repo.create(job)

        # Update inspection status to queued
        inspection = await self.inspection_repo.get_by_id(inspection_id)
        if inspection:
            inspection.status = InspectionStatus.PROCESSING.value
            await self.inspection_repo.update(inspection)

        return job
