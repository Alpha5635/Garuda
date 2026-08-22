import hashlib
import uuid
from app.schemas.ecommerce import EcommerceListingRequest, EcommerceListingResponse
from app.schemas.rule_engine import RuleEvaluationResult
from app.services.rules.rule_engine_service import rule_engine_service
from app.services.normalization_service import normalization_service
from app.schemas.ocr import ExtractedFieldCandidate


class EcommerceService:
    def process_listing(self, data: EcommerceListingRequest) -> dict:
        content_hash = hashlib.sha256(f"{data.platform}:{data.listing_id}:{data.url}".encode("utf-8")).hexdigest()

        # Parse submitted online declarations
        raw_declarations = data.declarations or {}
        candidates: list[ExtractedFieldCandidate] = []
        for k, v in raw_declarations.items():
            candidates.append(ExtractedFieldCandidate(field_name=k, value=str(v), confidence=0.95))

        norm_fields = normalization_service.normalize_fields(candidates, [])

        # Evaluate rules under "E-commerce" channel (Rule 6(10) exemption active)
        from app.services.cv.calibration_service import CalibrationResult
        dummy_calib = CalibrationResult(
            is_valid=False,
            calibration_type="uncalibrated",
            reference_width_mm=0.0,
            reference_width_px=0.0,
            pixels_per_mm=0.0,
            measurement_error=0.0,
            calibration_confidence=0.0
        )

        rule_evals = rule_engine_service.evaluate_all_rules(
            normalized_fields=norm_fields,
            calibration_result=dummy_calib,
            channel="E-commerce"
        )

        return {
            "platform": data.platform,
            "listing_id": data.listing_id,
            "url": data.url,
            "seller_name": data.seller_name,
            "content_hash": content_hash,
            "rule_evaluations": [r.model_dump() for r in rule_evals]
        }


ecommerce_service = EcommerceService()
