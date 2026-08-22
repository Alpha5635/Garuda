"""Offline Mobile Sync Ingestion Service with Idempotent Outbox Processing."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.inspection import (
    Inspection,
    ProductImage,
    ExtractedField,
    Violation,
)
from backend.app.models.intelligence import SyncQueue
from backend.app.services.audit import AuditService


class SyncService:
    """
    Handles atomic ingestion and reconciliation of offline field capture records.
    Guarantees idempotency via device_id + local_event_id deterministic keys.
    """

    @classmethod
    def ingest_offline_event(
        cls,
        session: Session,
        device_id: str,
        local_event_id: str,
        entity_type: str,
        payload_jsonb: Dict[str, Any],
        auto_process: bool = True,
    ) -> Tuple[SyncQueue, bool]:
        """
        Register and optionally process an offline synchronization event.
        Returns:
            (SyncQueue, is_new: bool)
        """
        idempotency_key = f"{device_id}_{local_event_id}"

        # 1. Check for existing idempotency key
        existing = session.execute(
            select(SyncQueue).filter_by(idempotency_key=idempotency_key)
        ).scalar_one_or_none()

        if existing:
            if existing.status == "synced":
                # Already processed successfully — no-op idempotent return
                return existing, False
            elif auto_process:
                # Retry processing of pending or failed record
                cls.process_sync_record(session, existing)
                return existing, False
            return existing, False

        # 2. Create new queue entry
        sync_item = SyncQueue(
            id=uuid.uuid4(),
            device_id=device_id,
            local_event_id=local_event_id,
            entity_type=entity_type,
            payload_jsonb=payload_jsonb,
            status="pending",
            attempts=0,
            idempotency_key=idempotency_key,
            received_at=datetime.now(timezone.utc),
        )
        session.add(sync_item)
        session.flush()

        if auto_process:
            cls.process_sync_record(session, sync_item)

        return sync_item, True

    @classmethod
    def process_sync_record(cls, session: Session, sync_item: SyncQueue) -> bool:
        """
        Atomically process a single SyncQueue item, creating or updating inspection records,
        images, extracted fields, violations, and hash-chained audit logs.
        """
        sync_item.attempts += 1
        payload = sync_item.payload_jsonb or {}

        try:
            with session.begin_nested():
                insp_data = payload.get("inspection", {})
                if not insp_data:
                    raise ValueError("Sync payload missing 'inspection' block.")

                raw_insp_id = insp_data.get("id")
                insp_id = uuid.UUID(str(raw_insp_id)) if raw_insp_id else uuid.uuid4()
                raw_org_id = insp_data.get("organisation_id")
                if not raw_org_id:
                    raise ValueError("Inspection payload missing mandatory 'organisation_id'.")
                org_id = uuid.UUID(str(raw_org_id))

                raw_rule_ver_id = insp_data.get("rule_version_id")
                if not raw_rule_ver_id:
                    raise ValueError("Inspection payload missing mandatory pinned 'rule_version_id'.")
                rule_ver_id = uuid.UUID(str(raw_rule_ver_id))

                raw_prod_id = insp_data.get("product_id")
                product_id = uuid.UUID(str(raw_prod_id)) if raw_prod_id else None

                raw_creator_id = insp_data.get("created_by")
                creator_id = uuid.UUID(str(raw_creator_id)) if raw_creator_id else None

                captured_at_val = insp_data.get("captured_at")
                if isinstance(captured_at_val, str):
                    try:
                        captured_at = datetime.fromisoformat(captured_at_val.replace("Z", "+00:00"))
                    except Exception:
                        captured_at = datetime.now(timezone.utc)
                elif isinstance(captured_at_val, datetime):
                    captured_at = captured_at_val
                else:
                    captured_at = datetime.now(timezone.utc)

                # Find or create Inspection
                inspection = session.execute(
                    select(Inspection).filter_by(id=insp_id)
                ).scalar_one_or_none()

                if not inspection:
                    inspection = Inspection(
                        id=insp_id,
                        organisation_id=org_id,
                        product_id=product_id,
                        channel=insp_data.get("channel", "package"),
                        status=insp_data.get("status", "draft"),
                        rule_version_id=rule_ver_id,
                        score=insp_data.get("score"),
                        score_status=insp_data.get("score_status", "provisional"),
                        latitude=insp_data.get("latitude"),
                        longitude=insp_data.get("longitude"),
                        district=insp_data.get("district"),
                        state_code=insp_data.get("state_code"),
                        officer_notes=insp_data.get("officer_notes"),
                        captured_at=captured_at,
                        created_by=creator_id,
                    )
                    session.add(inspection)
                    session.flush()
                else:
                    # Update status and scores if provided
                    if "status" in insp_data:
                        inspection.status = insp_data["status"]
                    if "score" in insp_data:
                        inspection.score = insp_data["score"]
                    if "officer_notes" in insp_data:
                        inspection.officer_notes = insp_data["officer_notes"]

                # Process Evidence Images
                images_data = payload.get("images", [])
                for img_item in images_data:
                    raw_img_id = img_item.get("id")
                    img_id = uuid.UUID(str(raw_img_id)) if raw_img_id else uuid.uuid4()
                    existing_img = session.execute(
                        select(ProductImage).filter_by(id=img_id)
                    ).scalar_one_or_none()

                    if not existing_img:
                        img_obj = ProductImage(
                            id=img_id,
                            inspection_id=inspection.id,
                            object_key=img_item.get("object_key", f"inspections/{inspection.id}/originals/{img_id}.jpg"),
                            sha256=img_item.get("sha256", "0" * 64),
                            captured_at=captured_at,
                            quality_jsonb=img_item.get("quality_jsonb", {}),
                            transform_jsonb=img_item.get("transform_jsonb", {}),
                            calibration_jsonb=img_item.get("calibration_jsonb", {}),
                            status=img_item.get("status", "uploaded"),
                        )
                        session.add(img_obj)

                # Process Extracted Fields (preserving raw text)
                fields_data = payload.get("extracted_fields", [])
                for fld_item in fields_data:
                    raw_fld_id = fld_item.get("id")
                    fld_id = uuid.UUID(str(raw_fld_id)) if raw_fld_id else uuid.uuid4()
                    raw_fld_img_id = fld_item.get("image_id")
                    fld_img_id = uuid.UUID(str(raw_fld_img_id)) if raw_fld_img_id else None

                    existing_fld = session.execute(
                        select(ExtractedField).filter_by(id=fld_id)
                    ).scalar_one_or_none()

                    if not existing_fld:
                        field_obj = ExtractedField(
                            id=fld_id,
                            inspection_id=inspection.id,
                            image_id=fld_img_id,
                            field_type=fld_item.get("field_type", "unknown"),
                            raw_text=fld_item.get("raw_text", ""),
                            normalized_jsonb=fld_item.get("normalized_jsonb", {}),
                            bbox_jsonb=fld_item.get("bbox_jsonb", {}),
                            polygon_jsonb=fld_item.get("polygon_jsonb", {}),
                            confidence=float(fld_item.get("confidence", 1.0)),
                            language=fld_item.get("language", "eng"),
                            model_version_id=uuid.UUID(str(fld_item["model_version_id"])) if fld_item.get("model_version_id") else None,
                            review_status=fld_item.get("review_status", "unreviewed"),
                        )
                        session.add(field_obj)

                # Process Violations
                violations_data = payload.get("violations", [])
                for viol_item in violations_data:
                    raw_viol_id = viol_item.get("id")
                    viol_id = uuid.UUID(str(raw_viol_id)) if raw_viol_id else uuid.uuid4()

                    existing_viol = session.execute(
                        select(Violation).filter_by(id=viol_id)
                    ).scalar_one_or_none()

                    if not existing_viol:
                        viol_obj = Violation(
                            id=viol_id,
                            inspection_id=inspection.id,
                            rule_version_id=rule_ver_id,
                            rule_id=viol_item.get("rule_id", "LMPC-UNKNOWN"),
                            clause=viol_item.get("clause"),
                            status=viol_item.get("status", "detected"),
                            severity=viol_item.get("severity", "Major"),
                            message=viol_item.get("message", "Rule contravention detected."),
                            evidence_jsonb=viol_item.get("evidence_jsonb", {}),
                            confidence=float(viol_item.get("confidence", 1.0)),
                            officer_disposition=viol_item.get("officer_disposition"),
                        )
                        session.add(viol_obj)

                # Cryptographic Hash-Chained Audit Trail Logging
                AuditService.log_event(
                    session=session,
                    action="SYNC_INGEST",
                    entity_type="inspection",
                    entity_id=inspection.id,
                    actor_id=creator_id,
                    organisation_id=org_id,
                    after_state={
                        "sync_id": str(sync_item.id),
                        "idempotency_key": sync_item.idempotency_key,
                        "device_id": sync_item.device_id,
                        "channel": inspection.channel,
                        "status": inspection.status,
                    },
                    request_id=f"sync:{sync_item.idempotency_key}",
                )

                sync_item.status = "synced"
                sync_item.processed_at = datetime.now(timezone.utc)
                sync_item.error_message = None
                return True

        except Exception as e:
            sync_item.status = "failed"
            sync_item.error_message = f"Sync processing error: {str(e)}"
            return False

    @classmethod
    def process_all_pending(cls, session: Session) -> Tuple[int, int]:
        """
        Process all pending records in the sync queue.
        Returns (success_count, failed_count).
        """
        stmt = select(SyncQueue).filter_by(status="pending").order_by(SyncQueue.received_at.asc())
        pending_items = session.execute(stmt).scalars().all()

        success_count = 0
        failed_count = 0
        for item in pending_items:
            ok = cls.process_sync_record(session, item)
            if ok:
                success_count += 1
            else:
                failed_count += 1
            session.flush()

        return success_count, failed_count
