import pytest
from app.schemas.normalization import NormalizedFieldSchema
from app.services.cv.calibration_service import CalibrationResult
from app.services.rules.rule_engine_service import RuleEngineService


def test_rule_engine_evaluation_pass():
    service = RuleEngineService()

    normalized_fields = [
        NormalizedFieldSchema(field_name="manufacturer", raw_value="GlowSoft Pvt Ltd", normalized_value="GlowSoft Pvt Ltd", confidence=0.95),
        NormalizedFieldSchema(field_name="net_quantity", raw_value="500 g", normalized_value="500 g", numeric_value=500.0, unit="g", confidence=0.96, bounding_box=[10, 10, 50, 10]),
        NormalizedFieldSchema(field_name="mrp", raw_value="MRP Rs 249 (Incl of all taxes)", normalized_value="₹ 249.00", numeric_value=249.0, unit="INR", confidence=0.94),
        NormalizedFieldSchema(field_name="month_year", raw_value="05/2026", normalized_value="2026-05", confidence=0.92),
        NormalizedFieldSchema(field_name="consumer_care", raw_value="1800-111-222", normalized_value="1800-111-222", confidence=0.93),
    ]

    # Valid calibration 5 px/mm (10 px = 2.0 mm height)
    calib = CalibrationResult(
        is_valid=True,
        calibration_type="aruco_50mm",
        reference_width_mm=50.0,
        reference_width_px=250.0,
        pixels_per_mm=5.0,
        measurement_error=0.20,
        calibration_confidence=0.98
    )

    results = service.evaluate_all_rules(normalized_fields, calib)
    res_map = {r.rule_id: r for r in results}

    assert res_map["LM-6-1-A-01"].result == "pass"
    assert res_map["LM-6-1-C-01"].result == "pass"
    assert res_map["LM-6-1-E-01"].result == "pass"
    assert res_map["LM-6-1-D-01"].result == "pass"
    assert res_map["LM-6-2-01"].result == "pass"
    # Rule 7 for 500g requires 2.0 mm height. Measured height is 10 px / 5 = 2.0 mm. Error = 0.2 mm (overlaps threshold 2.0) -> review_required
    assert res_map["LM-7-2-01"].result in ["pass", "review_required"]


def test_rule_engine_uncalibrated_rule7_not_evaluable():
    service = RuleEngineService()

    normalized_fields = [
        NormalizedFieldSchema(field_name="net_quantity", raw_value="500 g", normalized_value="500 g", numeric_value=500.0, unit="g", confidence=0.96, bounding_box=[10, 10, 50, 10]),
    ]

    calib = CalibrationResult(
        is_valid=False,
        calibration_type="uncalibrated",
        reference_width_mm=0.0,
        reference_width_px=0.0,
        pixels_per_mm=0.0,
        measurement_error=0.0,
        calibration_confidence=0.0
    )

    results = service.evaluate_all_rules(normalized_fields, calib)
    res_map = {r.rule_id: r for r in results}

    assert res_map["LM-7-2-01"].result == "not_evaluable"
