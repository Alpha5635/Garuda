import uuid
import os
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.inspection_session import InspectionSession, SessionStatus
from app.models.product_detection import ProductDetection, DetectionStatus
from app.models.inspection import Inspection, InspectionStatus
from app.models.image import Image
from app.models.job import ProcessingJob, JobState
from app.repositories.session_repository import SessionRepository
from app.repositories.image_repository import ImageRepository
from app.repositories.inspection_repository import InspectionRepository
from app.services.storage_service import storage_service
from app.services.audit_service import AuditService
from app.services.inspection.risk_prioritization_service import risk_prioritization_service
from app.schemas.inspection_session import (
    SessionCreateRequest,
    BatchImageUploadRequest,
    BatchImageUploadResponse,
    BatchImageUploadItemResponse,
    SessionProductItemResponse,
    SessionProductListResponse,
    RecaptureProductItem,
    RecaptureProductListResponse,
    RecaptureUploadResponse,
    SessionStatusResponse
)


class BatchInspectionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_repo = SessionRepository(session)
        self.image_repo = ImageRepository(session)
        self.inspection_repo = InspectionRepository(session)
        self.audit_service = AuditService()

    async def create_session(
        self,
        inspector_id: uuid.UUID,
        organisation_id: uuid.UUID | None,
        data: SessionCreateRequest
    ) -> InspectionSession:
        # 1. Idempotency Check
        if data.idempotency_key:
            existing = await self.session_repo.get_by_idempotency_key(data.idempotency_key)
            if existing:
                return existing

        if data.client_session_id:
            existing_client = await self.session_repo.get_by_client_session_id(
                data.client_session_id, inspector_id
            )
            if existing_client:
                return existing_client

        # 2. Create Session
        new_session = InspectionSession(
            organisation_id=data.organisation_id or organisation_id,
            inspector_id=inspector_id,
            client_session_id=data.client_session_id,
            idempotency_key=data.idempotency_key,
            location=data.location,
            latitude=data.latitude,
            longitude=data.longitude,
            gps_accuracy=data.gps_accuracy,
            started_at=datetime.now(timezone.utc),
            status=SessionStatus.QUEUED.value,
            total_images=0,
            total_products=0,
            processed_products=0,
            metadata_json=data.metadata_json or {}
        )
        session_obj = await self.session_repo.create_session(new_session)

        # 3. Log Audit Event
        await self.audit_service.log_event(
            session=self.session,
            action="session_created",
            entity_type="session",
            entity_id=str(session_obj.id),
            actor_id=inspector_id,
            after_state={
                "session_id": str(session_obj.id),
                "location": session_obj.location,
                "client_session_id": session_obj.client_session_id
            }
        )
        return session_obj

    async def get_session(self, session_id: uuid.UUID) -> InspectionSession | None:
        return await self.session_repo.get_by_id(session_id)

    async def get_session_with_details(self, session_id: uuid.UUID) -> InspectionSession | None:
        return await self.session_repo.get_with_details(session_id)

    async def get_session_summary_metrics(self, session_id: uuid.UUID) -> dict[str, int]:
        """Calculates live summary breakdown from database child records."""
        detections = await self.session_repo.get_detections_for_session(session_id)
        
        high_p = 0
        med_p = 0
        low_p = 0
        needs_recap = 0
        review_req = 0
        violations_count = 0

        for det in detections:
            insp = det.inspection
            if not insp:
                continue

            meta = insp.metadata_json or {}
            risk = meta.get("risk_priority") or {}
            priority = risk.get("priority")
            underlying = risk.get("underlying_rule_result")

            if insp.status == InspectionStatus.NEEDS_RECAPTURE.value or det.status == DetectionStatus.FAILED.value:
                needs_recap += 1
            if underlying == "violation" or insp.status in ("violation", "non_compliant"):
                violations_count += 1
            if risk.get("review_required") or underlying == "review_required" or insp.status == "review_required":
                review_req += 1

            if priority == "high":
                high_p += 1
            elif priority == "medium":
                med_p += 1
            elif priority == "low":
                low_p += 1
            else:
                # Default bucket if pending or needs recapture
                if insp.status == InspectionStatus.NEEDS_RECAPTURE.value:
                    med_p += 1
                elif insp.status in ("violation", "non_compliant"):
                    high_p += 1
                elif insp.status in ("compliant", InspectionStatus.COMPLETE.value):
                    low_p += 1
                else:
                    med_p += 1

        return {
            "high_priority": high_p,
            "medium_priority": med_p,
            "low_priority": low_p,
            "needs_recapture": needs_recap,
            "review_required": review_req,
            "violations": violations_count
        }

    async def list_sessions(
        self,
        inspector_id: uuid.UUID | None = None,
        organisation_id: uuid.UUID | None = None,
        is_super_admin: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> list[InspectionSession]:
        sessions = await self.session_repo.list_sessions(
            inspector_id=inspector_id,
            organisation_id=organisation_id,
            is_super_admin=is_super_admin,
            skip=skip,
            limit=limit
        )
        return list(sessions)

    async def generate_batch_upload_urls(
        self,
        session_id: uuid.UUID,
        data: BatchImageUploadRequest
    ) -> BatchImageUploadResponse:
        session_obj = await self.session_repo.get_by_id(session_id)
        if not session_obj:
            raise ValueError("Inspection session not found")

        responses: list[BatchImageUploadItemResponse] = []

        for item in data.images:
            ext = os.path.splitext(item.filename)[1] or ".jpg"
            image_id = uuid.uuid4()
            object_key = f"sessions/{session_id}/images/{image_id}{ext}"

            # Create image record in DB
            img = Image(
                id=image_id,
                session_id=session_id,
                inspection_id=None,
                object_key=object_key,
                original_filename=item.filename,
                sha256_hash=item.sha256_hash,
                mime_type=item.mime_type,
                file_size=item.file_size,
                width=item.width,
                height=item.height,
                capture_timestamp=item.capture_timestamp or datetime.now(timezone.utc),
                gps_latitude=item.gps_latitude,
                gps_longitude=item.gps_longitude
            )
            await self.image_repo.create(img)

            # Generate presigned upload URL
            upload_url = storage_service.generate_upload_url(object_key, expires_in=3600)
            responses.append(
                BatchImageUploadItemResponse(
                    image_id=img.id,
                    upload_url=upload_url,
                    object_key=object_key,
                    expiration=3600
                )
            )

        session_obj.total_images += len(data.images)
        await self.session_repo.update(session_obj)

        await self.audit_service.log_event(
            session=self.session,
            action="image_uploaded",
            entity_type="session",
            entity_id=str(session_id),
            after_state={"images_count": len(data.images)}
        )

        return BatchImageUploadResponse(
            session_id=session_id,
            uploads=responses
        )

    async def direct_upload_shelf_image(
        self,
        session_id: uuid.UUID,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        gps_latitude: float | None = None,
        gps_longitude: float | None = None
    ) -> Image:
        session_obj = await self.session_repo.get_by_id(session_id)
        if not session_obj:
            raise ValueError("Inspection session not found")

        sha256_hash = storage_service.compute_sha256(file_bytes)
        ext = os.path.splitext(filename or "shelf.jpg")[1] or ".jpg"
        image_id = uuid.uuid4()
        object_key = f"sessions/{session_id}/images/{image_id}{ext}"

        storage_service.upload_file_bytes(object_key, file_bytes, content_type=content_type or "image/jpeg")

        img = Image(
            id=image_id,
            session_id=session_id,
            inspection_id=None,
            object_key=object_key,
            original_filename=filename,
            sha256_hash=sha256_hash,
            mime_type=content_type or "image/jpeg",
            file_size=len(file_bytes),
            capture_timestamp=datetime.now(timezone.utc),
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude
        )
        await self.image_repo.create(img)

        session_obj.total_images += 1
        await self.session_repo.update(session_obj)

        await self.audit_service.log_event(
            session=self.session,
            action="image_uploaded",
            entity_type="session",
            entity_id=str(session_id),
            after_state={"image_id": str(image_id), "sha256": sha256_hash}
        )
        return img

    async def get_session_products(self, session_id: uuid.UUID) -> SessionProductListResponse:
        detections = await self.session_repo.get_detections_for_session(session_id)
        
        products: list[SessionProductItemResponse] = []
        for det in detections:
            bbox = {
                "bbox_x": det.bbox_x,
                "bbox_y": det.bbox_y,
                "bbox_width": det.bbox_width,
                "bbox_height": det.bbox_height
            }
            insp_id = det.inspection.id if det.inspection else None
            insp_status = det.inspection.status if det.inspection else None

            # Retrieve stored risk priority or compute deterministic fallback
            meta = (det.inspection.metadata_json or {}) if det.inspection else {}
            risk_data = meta.get("risk_priority") or {}

            priority = risk_data.get("priority")
            priority_reason = risk_data.get("reason")
            priority_conf = risk_data.get("confidence") or det.confidence
            underlying = risk_data.get("underlying_rule_result") or insp_status
            review_req = risk_data.get("review_required", False)

            products.append(
                SessionProductItemResponse(
                    product_id=det.id,
                    detection_id=det.id,
                    inspection_id=insp_id,
                    image_id=det.image_id,
                    bounding_box=bbox,
                    confidence=det.confidence,
                    crop_reference=det.crop_object_key,
                    processing_status=det.status,
                    inspection_status=insp_status,
                    priority=priority,
                    priority_reason=priority_reason,
                    priority_confidence=priority_conf,
                    underlying_rule_result=underlying,
                    review_required=review_req
                )
            )

        return SessionProductListResponse(
            session_id=session_id,
            total_products=len(products),
            products=products
        )

    # --- Smart Recapture APIs ---

    async def get_recapture_products(self, session_id: uuid.UUID) -> RecaptureProductListResponse:
        """Finds all products in the session flagged for recapture with specific root cause reasons."""
        detections = await self.session_repo.get_detections_for_session(session_id)
        items: list[RecaptureProductItem] = []

        for det in detections:
            insp = det.inspection
            if not insp:
                continue

            meta = insp.metadata_json or {}
            risk = meta.get("risk_priority") or {}
            is_recap_needed = (
                insp.status == InspectionStatus.NEEDS_RECAPTURE.value
                or det.status == DetectionStatus.FAILED.value
                or risk.get("reason") == "needs_recapture"
                or risk.get("reason") == "invalid_calibration"
            )

            if is_recap_needed:
                qc_reason = risk.get("details", {}).get("qc_reason") or "needs_recapture"
                bbox = {
                    "bbox_x": det.bbox_x,
                    "bbox_y": det.bbox_y,
                    "bbox_width": det.bbox_width,
                    "bbox_height": det.bbox_height
                }
                items.append(
                    RecaptureProductItem(
                        product_id=det.id,
                        detection_id=det.id,
                        inspection_id=insp.id,
                        image_id=det.image_id,
                        reason=qc_reason,
                        bounding_box=bbox,
                        current_status=insp.status
                    )
                )

        return RecaptureProductListResponse(
            session_id=session_id,
            total_recapture_needed=len(items),
            items=items
        )

    async def direct_upload_product_recapture(
        self,
        session_id: uuid.UUID,
        product_id: uuid.UUID,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        actor_id: uuid.UUID | None = None
    ) -> Image:
        """
        Non-destructive single-product recapture upload.
        Never overwrites original evidence; stores as a new version linked to the inspection.
        """
        det = await self.session_repo.get_detection_by_id(product_id)
        if not det:
            raise ValueError("Product detection not found")

        insp = det.inspection
        if not insp:
            raise ValueError("Associated inspection record not found")

        sha256_hash = storage_service.compute_sha256(file_bytes)
        ext = os.path.splitext(filename or "recapture.jpg")[1] or ".jpg"
        new_image_id = uuid.uuid4()
        object_key = f"sessions/{session_id}/recaptures/{new_image_id}{ext}"

        # Upload new evidence image
        storage_service.upload_file_bytes(object_key, file_bytes, content_type=content_type or "image/jpeg")

        # Create new Image version record
        new_img = Image(
            id=new_image_id,
            session_id=session_id,
            inspection_id=insp.id,
            object_key=object_key,
            original_filename=filename,
            sha256_hash=sha256_hash,
            mime_type=content_type or "image/jpeg",
            file_size=len(file_bytes),
            capture_timestamp=datetime.now(timezone.utc)
        )
        await self.image_repo.create(new_img)

        # Update detection crop reference
        old_crop_key = det.crop_object_key
        det.crop_object_key = object_key
        det.status = DetectionStatus.CROPPED.value
        await self.session_repo.session.commit()

        # Log audit event
        await self.audit_service.log_event(
            session=self.session,
            action="recapture_uploaded",
            entity_type="product_detection",
            entity_id=str(product_id),
            inspection_id=insp.id,
            actor_id=actor_id,
            before_state={"old_crop_key": old_crop_key, "old_status": det.status},
            after_state={"new_image_id": str(new_image_id), "new_crop_key": object_key, "sha256": sha256_hash}
        )

        return new_img
