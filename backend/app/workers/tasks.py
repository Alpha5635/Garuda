import uuid
import asyncio
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from datetime import datetime, timezone
from app.config import settings
from app.models.job import ProcessingJob, JobState
from app.models.inspection import Inspection, InspectionStatus
from app.models.inspection_session import InspectionSession, SessionStatus
from app.models.product_detection import ProductDetection, DetectionStatus
from app.models.image import Image
from app.models.normalization import NormalizedField
from app.models.calibration import CalibrationData
from app.models.violation import Violation
from app.services.storage_service import storage_service
from app.services.cv.quality_check_service import quality_check_service
from app.services.cv.product_detection_service import product_detection_service
from app.services.ocr.ocr_service import ocr_service
from app.services.normalization_service import normalization_service
from app.services.cv.calibration_service import calibration_service
from app.services.rules.rule_engine_service import rule_engine_service
from app.services.geometry.pdp_geometry_service import pdp_geometry_service
from app.services.evidence_service import evidence_service
from app.services.compliance_service import compliance_service
from app.schemas.ocr import OcrItemSchema, ExtractedFieldCandidate
from app.workers.celery_app import celery_app


sync_session_factory = None


def get_sync_session():
    global sync_session_factory
    if sync_session_factory is not None:
        return sync_session_factory()
    try:
        engine = create_engine(settings.get_sync_database_url(), pool_pre_ping=True)
        Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        session = Session()
        session.execute(sqlalchemy.text("SELECT 1"))
        return session
    except Exception as e:
        print(f"[CeleryTask] Warning: Could not connect to sync database ({e}). Using mock task runner session.")
        return None


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_inspection_image_task(self, job_id_str: str):
    job_id = uuid.UUID(job_id_str)
    session = get_sync_session()
    if not session:
        return {"status": "failed", "error": "Database unavailable"}

    try:
        job = session.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return {"status": "failed", "error": "Job not found"}

        inspection = session.query(Inspection).filter(Inspection.id == job.inspection_id).first()
        image = session.query(Image).filter(Image.id == job.image_id).first() if job.image_id else None

        if not inspection or not image:
            job.status = JobState.FAILED.value
            job.error_reason = "Missing inspection or image record"
            session.commit()
            return {"status": "failed", "error": "Missing record"}

        # 1. Quality Check Phase
        job.status = JobState.QUALITY_CHECK.value
        session.commit()

        image_bytes = storage_service.download_file_bytes(image.object_key)
        qc_res = quality_check_service.evaluate_image(image_bytes)
        job.quality_metrics_json = qc_res.metrics

        if not qc_res.is_usable:
            job.status = JobState.NEEDS_RECAPTURE.value
            job.error_reason = qc_res.reason
            inspection.status = InspectionStatus.NEEDS_RECAPTURE.value
            session.commit()
            return {
                "status": "needs_recapture",
                "reason": qc_res.reason,
                "job_id": str(job_id)
            }

        # 2. OCR Phase
        job.status = JobState.OCR.value
        session.commit()

        ocr_container = ocr_service.run_ocr(image_bytes)
        raw_candidates = ocr_service.extract_fields(ocr_container.items)

        # 3. Field Normalization
        normalized_fields = normalization_service.normalize_fields(raw_candidates, ocr_container.items)
        for nf in normalized_fields:
            db_norm = NormalizedField(
                inspection_id=inspection.id,
                field_name=nf.field_name,
                raw_value=nf.raw_value,
                normalized_value=nf.normalized_value,
                numeric_value=nf.numeric_value,
                unit=nf.unit,
                confidence=nf.confidence,
                bounding_box=nf.bounding_box
            )
            session.add(db_norm)

        # 4. Calibration Check
        calib_res = calibration_service.calibrate_image(image_bytes)
        if calib_res.is_valid:
            db_calib = CalibrationData(
                inspection_id=inspection.id,
                image_id=image.id,
                calibration_type=calib_res.calibration_type,
                reference_width_mm=calib_res.reference_width_mm,
                reference_width_px=calib_res.reference_width_px,
                pixels_per_mm=calib_res.pixels_per_mm,
                measurement_error=calib_res.measurement_error,
                calibration_confidence=calib_res.calibration_confidence
            )
            session.add(db_calib)

        # 5. LMPC Rule Engine Evaluation
        rule_eval_results = rule_engine_service.evaluate_all_rules(
            normalized_fields=normalized_fields,
            calibration_result=calib_res,
            channel=inspection.channel or "Retail store"
        )

        # 6. Violation & Evidence Crops Generation
        violations_count = 0
        for r_res in rule_eval_results:
            if r_res.result == "violation":
                violations_count += 1
                # Find matching field bbox for evidence crop
                matching_field = next((f for f in normalized_fields if f.field_name in r_res.rule_id.lower() or f.field_name in r_res.clause.lower()), None)
                bbox = matching_field.bounding_box if matching_field else None
                crop_key = evidence_service.crop_and_store_evidence(
                    original_image_bytes=image_bytes,
                    inspection_id=inspection.id,
                    rule_id=r_res.rule_id,
                    bbox=bbox
                )

                db_violation = Violation(
                    inspection_id=inspection.id,
                    image_id=image.id,
                    rule_id=r_res.rule_id,
                    rule_version=r_res.rule_version,
                    clause=r_res.clause,
                    severity=r_res.severity,
                    message=r_res.explanation,
                    evidence_bbox=bbox,
                    evidence_crop_key=crop_key,
                    ocr_text=matching_field.raw_value if matching_field else None,
                    normalized_value=matching_field.normalized_value if matching_field else None,
                    confidence=r_res.confidence
                )
                session.add(db_violation)

        # 7. PDP Geometry Overlay
        pdp_geom = pdp_geometry_service.calculate_geometry(
            ocr_items=ocr_container.items,
            normalized_fields=normalized_fields,
            calibration_result=calib_res,
            image_width=image.width or 1920,
            image_height=image.height or 1080
        )

        # 8. Compliance Score Calculation
        score_res = compliance_service.calculate_compliance_score(
            rule_results=rule_eval_results,
            calibration_result=calib_res,
            job_status="complete"
        )

        # Save to job and inspection
        job.ocr_data_json = ocr_container.model_dump()
        job.extracted_fields_json = [f.model_dump() for f in raw_candidates]
        job.status = JobState.COMPLETE.value
        job.error_reason = None

        inspection.status = score_res["overall_status"]
        inspection.metadata_json = {
            "pdp_geometry": pdp_geom.model_dump(),
            "compliance_score": score_res,
            "rule_evaluations": [r.model_dump() for r in rule_eval_results]
        }

        session.commit()
        return {
            "status": "complete",
            "job_id": str(job_id),
            "ocr_confidence": ocr_container.confidence,
            "overall_status": score_res["overall_status"],
            "score_status": score_res["score_status"],
            "violations_found": violations_count
        }

    except Exception as exc:
        session.rollback()
        print(f"[CeleryTask] Exception processing job {job_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        return {"status": "failed", "error": str(exc)}
    finally:
        session.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_batch_shelf_image_task(self, session_id_str: str, image_id_str: str):
    """
    Stage 4A: Detect products on shelf image, create crops and individual product inspections.
    """
    session_id = uuid.UUID(session_id_str)
    image_id = uuid.UUID(image_id_str)
    db_session = get_sync_session()
    if not db_session:
        return {"status": "failed", "error": "Database unavailable"}

    try:
        insp_session = db_session.query(InspectionSession).filter(InspectionSession.id == session_id).first()
        image = db_session.query(Image).filter(Image.id == image_id).first()

        if not insp_session or not image:
            return {"status": "failed", "error": "Missing inspection session or image record"}

        # 1. Product Detection Phase
        insp_session.status = SessionStatus.DETECTING_PRODUCTS.value
        db_session.commit()

        image_bytes = storage_service.download_file_bytes(image.object_key)
        candidates = product_detection_service.detect_products(image_bytes)

        if not candidates:
            insp_session.status = SessionStatus.COMPLETE.value
            insp_session.total_products = 0
            insp_session.processed_products = 0
            insp_session.completed_at = datetime.now(timezone.utc)
            db_session.commit()
            return {
                "status": "complete",
                "session_id": str(session_id),
                "total_products": 0,
                "message": "No products detected on shelf image"
            }

        # Count total existing inspections to generate sequential inspection numbers
        count = db_session.query(Inspection).count()
        year = datetime.now(timezone.utc).year

        created_job_ids: list[str] = []

        for idx, cand in enumerate(candidates):
            detection_id = uuid.uuid4()
            crop_key = f"sessions/{session_id}/crops/{detection_id}.jpg"

            # 2. Derive Evidence Crop
            crop_bytes = product_detection_service.crop_product(
                image_bytes=image_bytes,
                bbox_x=cand.bbox_x,
                bbox_y=cand.bbox_y,
                bbox_width=cand.bbox_width,
                bbox_height=cand.bbox_height
            )
            crop_sha256 = storage_service.compute_sha256(crop_bytes)
            storage_service.upload_file_bytes(crop_key, crop_bytes, content_type="image/jpeg")

            # 3. Create ProductDetection record
            db_detection = ProductDetection(
                id=detection_id,
                session_id=session_id,
                image_id=image.id,
                bbox_x=cand.bbox_x,
                bbox_y=cand.bbox_y,
                bbox_width=cand.bbox_width,
                bbox_height=cand.bbox_height,
                confidence=cand.confidence,
                crop_object_key=crop_key,
                status=DetectionStatus.CROPPED.value
            )
            db_session.add(db_detection)

            # 4. Create Individual Product Inspection
            product_inspection_id = uuid.uuid4()
            insp_num = f"LM/{year}/{(count + idx + 1):05d}"
            db_inspection = Inspection(
                id=product_inspection_id,
                inspection_number=insp_num,
                officer_id=insp_session.inspector_id,
                organisation_id=insp_session.organisation_id,
                status=InspectionStatus.PROCESSING.value,
                channel=insp_session.location or "Retail store",
                session_id=session_id,
                detection_id=detection_id,
                idempotency_key=f"session-{session_id}-det-{detection_id}",
                client_inspection_id=f"shelf-crop-{idx + 1}"
            )
            db_session.add(db_inspection)

            # 5. Create Crop Image Record
            crop_image = Image(
                id=uuid.uuid4(),
                inspection_id=product_inspection_id,
                session_id=session_id,
                object_key=crop_key,
                original_filename=f"product_crop_{idx + 1}.jpg",
                sha256_hash=crop_sha256,
                mime_type="image/jpeg",
                file_size=len(crop_bytes),
                width=int(cand.bbox_width),
                height=int(cand.bbox_height),
                capture_timestamp=image.capture_timestamp or datetime.now(timezone.utc),
                gps_latitude=image.gps_latitude,
                gps_longitude=image.gps_longitude
            )
            db_session.add(crop_image)

            # 6. Create Processing Job
            job_id = uuid.uuid4()
            db_job = ProcessingJob(
                id=job_id,
                inspection_id=product_inspection_id,
                image_id=crop_image.id,
                status=JobState.QUEUED.value
            )
            db_session.add(db_job)
            created_job_ids.append(str(job_id))

        insp_session.total_products = len(candidates)
        insp_session.status = SessionStatus.PROCESSING_PRODUCTS.value
        db_session.commit()
        db_session.close()
        db_session = None

        # 7. Queue individual product jobs
        for job_id_str in created_job_ids:
            process_batch_product_task.delay(job_id_str, str(session_id))

        return {
            "status": "processing_products",
            "session_id": str(session_id),
            "total_products": len(candidates),
            "jobs_queued": len(created_job_ids)
        }

    except Exception as exc:
        if db_session:
            db_session.rollback()
        print(f"[CeleryBatchTask] Exception detecting products in session {session_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        return {"status": "failed", "error": str(exc)}
    finally:
        if db_session:
            db_session.close()


from app.models.audit import AuditChain
from app.services.inspection.risk_prioritization_service import risk_prioritization_service


def _log_audit_sync(
    db_session,
    action: str,
    entity_type: str,
    entity_id: str,
    actor_email: str = "system",
    inspection_id: uuid.UUID | None = None,
    session_id: uuid.UUID | None = None,
    before_state: dict | None = None,
    after_state: dict | None = None
):
    try:
        latest = db_session.query(AuditChain).order_by(AuditChain.created_at.desc()).first()
        prev_hash = latest.current_hash if latest else "GENESIS_HASH_00000000000000000000000000000000000000000000000000000000"
        payload = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "actor": actor_email,
            "before": before_state,
            "after": after_state
        }
        import json
        import hashlib
        payload_str = json.dumps(payload, sort_keys=True)
        raw_str = f"{prev_hash}:{payload_str}"
        current_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        event = AuditChain(
            session_id=session_id,
            inspection_id=inspection_id,
            actor_email=actor_email,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            before_state=before_state,
            after_state=after_state,
            previous_hash=prev_hash,
            current_hash=current_hash
        )
        db_session.add(event)
        db_session.commit()
    except Exception as e:
        print(f"[CeleryAudit] Warning: Failed to log sync audit event ({e})")


@shared_task(bind=True, name="app.workers.tasks.process_batch_product_task", max_retries=3, default_retry_delay=10)
def process_batch_product_task(self, job_id_str: str, session_id_str: str):
    job_id = uuid.UUID(job_id_str)
    session_id = uuid.UUID(session_id_str)
    db_session = get_sync_session()

    try:
        job = db_session.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return {"status": "failed", "error": f"Job {job_id} not found"}

        image = db_session.query(Image).filter(Image.id == job.image_id).first() if job.image_id else None
        inspection = db_session.query(Inspection).filter(Inspection.id == job.inspection_id).first()
        detection = db_session.query(ProductDetection).filter(ProductDetection.id == inspection.detection_id).first() if inspection and inspection.detection_id else None

        if not inspection or not image:
            job.status = JobState.FAILED.value
            job.error_reason = "Missing inspection or image record"
            db_session.commit()
            return {"status": "failed", "error": "Missing record"}

        # 1. Quality Check Phase
        job.status = JobState.QUALITY_CHECK.value
        db_session.commit()

        image_bytes = storage_service.download_file_bytes(image.object_key)
        qc_res = quality_check_service.evaluate_image(image_bytes, is_crop=True)
        job.quality_metrics_json = qc_res.metrics

        if not qc_res.is_usable:
            job.status = JobState.NEEDS_RECAPTURE.value
            job.error_reason = qc_res.reason
            inspection.status = InspectionStatus.NEEDS_RECAPTURE.value
            if detection:
                detection.status = DetectionStatus.FAILED.value

            risk_res = risk_prioritization_service.evaluate_priority(
                rule_results=[],
                compliance_score_data={"overall_status": "needs_recapture"},
                job_status="needs_recapture",
                qc_reason=qc_res.reason,
                detection_confidence=detection.confidence if detection else 1.0
            )
            inspection.metadata_json = {
                "risk_priority": {
                    "priority": risk_res.priority,
                    "reason": risk_res.reason,
                    "confidence": risk_res.confidence,
                    "underlying_rule_result": risk_res.underlying_rule_result,
                    "review_required": risk_res.review_required,
                    "details": risk_res.details
                }
            }

            db_session.commit()
            _log_audit_sync(
                db_session,
                action="priority_assigned",
                entity_type="inspection",
                entity_id=str(inspection.id),
                inspection_id=inspection.id,
                session_id=session_id,
                after_state={"priority": risk_res.priority, "reason": risk_res.reason}
            )
            _aggregate_session_progress(db_session, session_id)
            return {
                "status": "needs_recapture",
                "reason": qc_res.reason,
                "job_id": str(job_id)
            }

        # 2. OCR Phase
        job.status = JobState.OCR.value
        db_session.commit()

        ocr_container = ocr_service.run_ocr(image_bytes)
        raw_candidates = ocr_service.extract_fields(ocr_container.items)

        # 3. Field Normalization
        normalized_fields = normalization_service.normalize_fields(raw_candidates, ocr_container.items)
        for nf in normalized_fields:
            db_norm = NormalizedField(
                inspection_id=inspection.id,
                field_name=nf.field_name,
                raw_value=nf.raw_value,
                normalized_value=nf.normalized_value,
                numeric_value=nf.numeric_value,
                unit=nf.unit,
                confidence=nf.confidence,
                bounding_box=nf.bounding_box
            )
            db_session.add(db_norm)

        # 4. Calibration Check
        calib_res = calibration_service.calibrate_image(image_bytes)
        if calib_res.is_valid:
            db_calib = CalibrationData(
                inspection_id=inspection.id,
                image_id=image.id,
                calibration_type=calib_res.calibration_type,
                reference_width_mm=calib_res.reference_width_mm,
                reference_width_px=calib_res.reference_width_px,
                pixels_per_mm=calib_res.pixels_per_mm,
                measurement_error=calib_res.measurement_error,
                calibration_confidence=calib_res.calibration_confidence
            )
            db_session.add(db_calib)

        # 5. Rule Evaluation
        rule_eval_results = rule_engine_service.evaluate_all_rules(
            normalized_fields=normalized_fields,
            calibration_result=calib_res,
            channel=inspection.channel or "Retail store"
        )

        # 6. Violation Crops
        violations_count = 0
        for r_res in rule_eval_results:
            if r_res.result == "violation":
                violations_count += 1
                matching_field = next((f for f in normalized_fields if f.field_name in r_res.rule_id.lower() or f.field_name in r_res.clause.lower()), None)
                bbox = matching_field.bounding_box if matching_field else None
                crop_key = evidence_service.crop_and_store_evidence(
                    original_image_bytes=image_bytes,
                    inspection_id=inspection.id,
                    rule_id=r_res.rule_id,
                    bbox=bbox
                )
                db_violation = Violation(
                    inspection_id=inspection.id,
                    image_id=image.id,
                    rule_id=r_res.rule_id,
                    rule_version=r_res.rule_version,
                    clause=r_res.clause,
                    severity=r_res.severity,
                    message=r_res.explanation,
                    evidence_bbox=bbox,
                    evidence_crop_key=crop_key,
                    ocr_text=matching_field.raw_value if matching_field else None,
                    normalized_value=matching_field.normalized_value if matching_field else None,
                    confidence=r_res.confidence
                )
                db_session.add(db_violation)

        # 7. PDP Geometry
        pdp_geom = pdp_geometry_service.calculate_geometry(
            ocr_items=ocr_container.items,
            normalized_fields=normalized_fields,
            calibration_result=calib_res,
            image_width=image.width or 800,
            image_height=image.height or 800
        )

        # 8. Score Calculation
        score_res = compliance_service.calculate_compliance_score(
            rule_results=rule_eval_results,
            calibration_result=calib_res,
            job_status="complete"
        )

        # 9. Risk Prioritization
        risk_res = risk_prioritization_service.evaluate_priority(
            rule_results=rule_eval_results,
            compliance_score_data=score_res,
            calibration_result=calib_res,
            avg_ocr_confidence=ocr_container.confidence,
            detection_confidence=detection.confidence if detection else 1.0,
            job_status="complete"
        )

        job.ocr_data_json = ocr_container.model_dump()
        job.extracted_fields_json = [f.model_dump() for f in raw_candidates]
        job.status = JobState.COMPLETE.value
        job.error_reason = None

        inspection.status = score_res["overall_status"]
        inspection.metadata_json = {
            "pdp_geometry": pdp_geom.model_dump(),
            "compliance_score": score_res,
            "rule_evaluations": [r.model_dump() for r in rule_eval_results],
            "risk_priority": {
                "priority": risk_res.priority,
                "reason": risk_res.reason,
                "confidence": risk_res.confidence,
                "underlying_rule_result": risk_res.underlying_rule_result,
                "review_required": risk_res.review_required,
                "details": risk_res.details
            }
        }

        if detection:
            detection.status = DetectionStatus.INSPECTED.value

        db_session.commit()

        _log_audit_sync(
            db_session,
            action="priority_assigned",
            entity_type="inspection",
            entity_id=str(inspection.id),
            inspection_id=inspection.id,
            session_id=session_id,
            after_state={"priority": risk_res.priority, "reason": risk_res.reason, "score": score_res.get("provisional_score")}
        )

        # Update and aggregate session progress
        _aggregate_session_progress(db_session, session_id)

        return {
            "status": "complete",
            "job_id": str(job_id),
            "session_id": str(session_id),
            "overall_status": score_res["overall_status"],
            "priority": risk_res.priority,
            "violations_found": violations_count
        }

    except Exception as exc:
        db_session.rollback()
        print(f"[CeleryBatchProductTask] Exception processing product job {job_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        # On permanent failure, update progress so session doesn't hang
        _aggregate_session_progress(db_session, session_id)
        return {"status": "failed", "error": str(exc)}
    finally:
        db_session.close()


@shared_task(bind=True, name="app.workers.tasks.reprocess_product_recapture_task", max_retries=3, default_retry_delay=10)
def reprocess_product_recapture_task(self, session_id_str: str, product_id_str: str, new_image_id_str: str):
    """
    Re-executes the complete inspection pipeline for a single product using new recapture evidence.
    """
    session_id = uuid.UUID(session_id_str)
    product_id = uuid.UUID(product_id_str)
    new_image_id = uuid.UUID(new_image_id_str)
    db_session = get_sync_session()

    try:
        detection = db_session.query(ProductDetection).filter(ProductDetection.id == product_id).first()
        if not detection:
            return {"status": "failed", "error": f"Product detection {product_id} not found"}

        inspection = db_session.query(Inspection).filter(Inspection.id == detection.inspection.id).first() if detection.inspection else None
        image = db_session.query(Image).filter(Image.id == new_image_id).first()

        if not inspection or not image:
            return {"status": "failed", "error": "Missing inspection or image record"}

        # Clear prior normalized fields, calibration, and violations for clean re-evaluation
        db_session.query(NormalizedField).filter(NormalizedField.inspection_id == inspection.id).delete()
        db_session.query(CalibrationData).filter(CalibrationData.inspection_id == inspection.id).delete()
        db_session.query(Violation).filter(Violation.inspection_id == inspection.id).delete()
        db_session.commit()

        # Update inspection and job status
        inspection.status = InspectionStatus.PROCESSING.value
        db_session.commit()

        image_bytes = storage_service.download_file_bytes(image.object_key)
        qc_res = quality_check_service.evaluate_image(image_bytes, is_crop=True)

        if not qc_res.is_usable:
            inspection.status = InspectionStatus.NEEDS_RECAPTURE.value
            detection.status = DetectionStatus.FAILED.value
            risk_res = risk_prioritization_service.evaluate_priority(
                rule_results=[],
                compliance_score_data={"overall_status": "needs_recapture"},
                job_status="needs_recapture",
                qc_reason=qc_res.reason,
                detection_confidence=detection.confidence
            )
            inspection.metadata_json = {
                "risk_priority": {
                    "priority": risk_res.priority,
                    "reason": risk_res.reason,
                    "confidence": risk_res.confidence,
                    "underlying_rule_result": risk_res.underlying_rule_result,
                    "review_required": risk_res.review_required,
                    "details": risk_res.details
                }
            }
            db_session.commit()
            _aggregate_session_progress(db_session, session_id)
            return {"status": "needs_recapture", "reason": qc_res.reason}

        # OCR & Normalization
        ocr_container = ocr_service.run_ocr(image_bytes)
        raw_candidates = ocr_service.extract_fields(ocr_container.items)
        normalized_fields = normalization_service.normalize_fields(raw_candidates, ocr_container.items)

        for nf in normalized_fields:
            db_norm = NormalizedField(
                inspection_id=inspection.id,
                field_name=nf.field_name,
                raw_value=nf.raw_value,
                normalized_value=nf.normalized_value,
                numeric_value=nf.numeric_value,
                unit=nf.unit,
                confidence=nf.confidence,
                bounding_box=nf.bounding_box
            )
            db_session.add(db_norm)

        # Calibration
        calib_res = calibration_service.calibrate_image(image_bytes)
        if calib_res.is_valid:
            db_calib = CalibrationData(
                inspection_id=inspection.id,
                image_id=image.id,
                calibration_type=calib_res.calibration_type,
                reference_width_mm=calib_res.reference_width_mm,
                reference_width_px=calib_res.reference_width_px,
                pixels_per_mm=calib_res.pixels_per_mm,
                measurement_error=calib_res.measurement_error,
                calibration_confidence=calib_res.calibration_confidence
            )
            db_session.add(db_calib)

        # Rule Evaluations
        rule_eval_results = rule_engine_service.evaluate_all_rules(
            normalized_fields=normalized_fields,
            calibration_result=calib_res,
            channel=inspection.channel or "Retail store"
        )

        # Violation Crops
        for r_res in rule_eval_results:
            if r_res.result == "violation":
                matching_field = next((f for f in normalized_fields if f.field_name in r_res.rule_id.lower() or f.field_name in r_res.clause.lower()), None)
                bbox = matching_field.bounding_box if matching_field else None
                crop_key = evidence_service.crop_and_store_evidence(
                    original_image_bytes=image_bytes,
                    inspection_id=inspection.id,
                    rule_id=r_res.rule_id,
                    bbox=bbox
                )
                db_violation = Violation(
                    inspection_id=inspection.id,
                    image_id=image.id,
                    rule_id=r_res.rule_id,
                    rule_version=r_res.rule_version,
                    clause=r_res.clause,
                    severity=r_res.severity,
                    message=r_res.explanation,
                    evidence_bbox=bbox,
                    evidence_crop_key=crop_key,
                    ocr_text=matching_field.raw_value if matching_field else None,
                    normalized_value=matching_field.normalized_value if matching_field else None,
                    confidence=r_res.confidence
                )
                db_session.add(db_violation)

        # PDP Geometry & Score
        pdp_geom = pdp_geometry_service.calculate_geometry(
            ocr_items=ocr_container.items,
            normalized_fields=normalized_fields,
            calibration_result=calib_res,
            image_width=image.width or 800,
            image_height=image.height or 800
        )
        score_res = compliance_service.calculate_compliance_score(
            rule_results=rule_eval_results,
            calibration_result=calib_res,
            job_status="complete"
        )
        risk_res = risk_prioritization_service.evaluate_priority(
            rule_results=rule_eval_results,
            compliance_score_data=score_res,
            calibration_result=calib_res,
            avg_ocr_confidence=ocr_container.confidence,
            detection_confidence=detection.confidence,
            job_status="complete"
        )

        inspection.status = score_res["overall_status"]
        inspection.metadata_json = {
            "pdp_geometry": pdp_geom.model_dump(),
            "compliance_score": score_res,
            "rule_evaluations": [r.model_dump() for r in rule_eval_results],
            "risk_priority": {
                "priority": risk_res.priority,
                "reason": risk_res.reason,
                "confidence": risk_res.confidence,
                "underlying_rule_result": risk_res.underlying_rule_result,
                "review_required": risk_res.review_required,
                "details": risk_res.details
            }
        }
        detection.status = DetectionStatus.INSPECTED.value
        db_session.commit()

        _log_audit_sync(
            db_session,
            action="product_processed",
            entity_type="product_detection",
            entity_id=str(product_id),
            inspection_id=inspection.id,
            session_id=session_id,
            after_state={"priority": risk_res.priority, "status": inspection.status}
        )

        _aggregate_session_progress(db_session, session_id)
        return {
            "status": "complete",
            "session_id": str(session_id),
            "product_id": str(product_id),
            "overall_status": score_res["overall_status"],
            "priority": risk_res.priority
        }

    except Exception as exc:
        db_session.rollback()
        print(f"[CeleryRecaptureTask] Exception reprocessing product {product_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        _aggregate_session_progress(db_session, session_id)
        return {"status": "failed", "error": str(exc)}
    finally:
        db_session.close()


def _aggregate_session_progress(db_session, session_id: uuid.UUID):
    """Helper to update session processed_products count and aggregate final status."""
    try:
        insp_session = db_session.query(InspectionSession).filter(InspectionSession.id == session_id).first()
        if not insp_session:
            return

        session_inspections = db_session.query(Inspection).filter(Inspection.session_id == session_id).all()
        total_products = len(session_inspections)
        insp_session.total_products = total_products

        terminal_statuses = {
            InspectionStatus.COMPLETE.value,
            "compliant",
            "non_compliant",
            "violation",
            "review_required",
            "not_evaluable",
            InspectionStatus.FAILED.value,
            InspectionStatus.NEEDS_RECAPTURE.value
        }
        completed_count = sum(1 for i in session_inspections if i.status in terminal_statuses)
        insp_session.processed_products = completed_count

        if completed_count >= total_products and total_products > 0:
            failed_count = sum(
                1 for i in session_inspections
                if i.status in (InspectionStatus.FAILED.value, InspectionStatus.NEEDS_RECAPTURE.value)
            )
            if failed_count == 0:
                insp_session.status = SessionStatus.COMPLETE.value
            elif failed_count < total_products:
                insp_session.status = SessionStatus.PARTIAL_FAILURE.value
            else:
                insp_session.status = SessionStatus.FAILED.value

            insp_session.completed_at = datetime.now(timezone.utc)

        db_session.commit()
    except Exception as e:
        print(f"[CeleryBatchTask] Error aggregating session progress: {e}")
        db_session.rollback()

