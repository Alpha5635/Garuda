import pytest
from app.schemas.calibration import CalibrationRequest
from app.services.cv.calibration_service import CalibrationService, CalibrationResult


def test_manual_calibration_request():
    service = CalibrationService()
    req = CalibrationRequest(
        calibration_type="aruco_50mm",
        reference_width_mm=50.0,
        reference_width_px=250.0 # 5 px per mm
    )

    res = service.calibrate_image(b"dummy_bytes", req)
    assert res.is_valid is True
    assert res.pixels_per_mm == 5.0
    assert res.measurement_error == 0.20 # 1 / 5 = 0.2 mm

    # Measure 10 px height numeral -> 2.0 mm
    bbox = [10, 10, 50, 10] # rect height 10 px
    height_mm = service.measure_numeral_height_mm(bbox, res.pixels_per_mm)
    assert height_mm == 2.0


def test_uncalibrated_rejection():
    service = CalibrationService()
    res = service.calibrate_image(b"dummy_bytes", None)
    assert res.is_valid is False
    assert res.status == "not_evaluable"
    assert res.pixels_per_mm == 0.0
