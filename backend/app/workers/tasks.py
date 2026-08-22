import uuid
import asyncio
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from app.config import settings
from app.models.job import ProcessingJob, JobState
from app.models.inspection import Inspection, InspectionStatus
from app.models.image import Image
from app.models.normalization import NormalizedField
from app.models.calibration import CalibrationData
from app.models.violation import Violation
from app.services.storage_service import storage_service
from app.services.cv.quality_check_service import quality_check_service
from app.services.ocr.ocr_service import ocr_service
from app.services.normalization_service import normalization_service
from app.services.cv.calibration_service import calibration_service
from app.services.rules.rule_engine_service import rule_engine_service
from app.services.geometry.pdp_geometry_service import pdp_geometry_service
from app.services.evidence_service import evidence_service
from app.services.compliance_service import compliance_service
from app.schemas.ocr import OcrItemSchema, ExtractedFieldCandidate
from app.workers.celery_app import celery_app


def get_sync_session():
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
