import io
import uuid
import pytest
from httpx import AsyncClient
from app.services.inspection.risk_prioritization_service import risk_prioritization_service
from app.schemas.rule_engine import RuleEvaluationResult
from app.services.cv.calibration_service import CalibrationResult
from app.services.cv.product_detection_service import product_detection_service
from tests.test_stage4a_batch import generate_shelf_image_bytes


# --- 1. Risk Prioritization Tests ---

def test_risk_prioritization_high_rule_violation():
    """Verify confirmed rule violations receive HIGH risk priority."""
    rule_results = [
        RuleEvaluationResult(
            rule_id="LM-6-1-E-01",
            rule_version="2011.1",
            clause="Rule 6(1)(e)",
            result="violation",
            severity="critical",
            explanation="MRP declaration is missing",
            confidence=0.95
        )
    ]
    score_data = {"overall_status": "violation", "provisional_score": 78.0}
    res = risk_prioritization_service.evaluate_priority(
        rule_results=rule_results,
        compliance_score_data=score_data,
        job_status="complete"
    )
    assert res.priority == "high"
    assert res.reason == "rule_violation"
    assert res.underlying_rule_result == "violation"
    assert res.review_required is True


def test_risk_prioritization_high_multiple_violations():
    """Verify multiple violations trigger multiple_violations reason."""
    rule_results = [
        RuleEvaluationResult(
            rule_id="LM-6-1-A-01",
            rule_version="2011.1",
            clause="Rule 6(1)(a)",
            result="violation",
            severity="major",
            explanation="Manufacturer name absent",
            confidence=0.90
        ),
        RuleEvaluationResult(
            rule_id="LM-6-1-C-01",
            rule_version="2011.1",
            clause="Rule 6(1)(c)",
            result="violation",
            severity="major",
            explanation="Net weight absent",
            confidence=0.92
        )
    ]
    score_data = {"overall_status": "violation", "provisional_score": 60.0}
    res = risk_prioritization_service.evaluate_priority(
        rule_results=rule_results,
        compliance_score_data=score_data,
        job_status="complete"
    )
    assert res.priority == "high"
    assert res.reason == "multiple_violations"
    assert res.details["total_violations"] == 2


def test_risk_prioritization_medium_low_ocr():
    """Verify low OCR confidence triggers MEDIUM risk priority."""
    rule_results = []
    score_data = {"overall_status": "compliant", "provisional_score": 100.0}
    res = risk_prioritization_service.evaluate_priority(
        rule_results=rule_results,
        compliance_score_data=score_data,
        avg_ocr_confidence=0.62,
        job_status="complete"
    )
    assert res.priority == "medium"
    assert res.reason == "low_ocr_confidence"
    assert res.review_required is True


def test_risk_prioritization_medium_invalid_calibration():
    """Verify uncalibrated / invalid calibration triggers MEDIUM risk priority."""
    rule_results = []
    score_data = {"overall_status": "review_required", "provisional_score": 100.0}
    calib = CalibrationResult(is_valid=False, calibration_type="none", pixels_per_mm=0.0, reference_width_mm=0.0, reference_width_px=0.0, measurement_error=0.0, calibration_confidence=0.0)
    res = risk_prioritization_service.evaluate_priority(
        rule_results=rule_results,
        compliance_score_data=score_data,
        calibration_result=calib,
        avg_ocr_confidence=0.95,
        job_status="complete"
    )
    assert res.priority == "medium"
    assert res.reason == "invalid_calibration"
    assert res.review_required is True


def test_risk_prioritization_low_clean_compliant():
    """Verify compliant product with valid calibration and high OCR gets LOW priority."""
    rule_results = [
        RuleEvaluationResult(
            rule_id="LM-6-1-E-01",
            rule_version="2011.1",
            clause="Rule 6(1)(e)",
            result="pass",
            severity="critical",
            explanation="MRP declared clearly",
            confidence=0.98
        )
    ]
    score_data = {"overall_status": "compliant", "provisional_score": 100.0}
    calib = CalibrationResult(is_valid=True, calibration_type="aruco", pixels_per_mm=3.78, reference_width_mm=50.0, reference_width_px=189.0, measurement_error=0.2, calibration_confidence=0.99)
    res = risk_prioritization_service.evaluate_priority(
        rule_results=rule_results,
        compliance_score_data=score_data,
        calibration_result=calib,
        avg_ocr_confidence=0.96,
        detection_confidence=0.92,
        job_status="complete"
    )
    assert res.priority == "low"
    assert res.reason == "compliant"
    assert res.review_required is False


# --- 2. Smart Recapture & Session Summary Integration Tests ---

@pytest.mark.asyncio
async def test_session_summary_and_product_priorities(async_client: AsyncClient, auth_headers: dict):
    # 1. Create Session
    session_res = await async_client.post(
        "/api/v1/inspection-sessions",
        json={"location": "Spencer's Hypermarket, Kolkata", "client_session_id": "SPENCER-KOL-01"},
        headers=auth_headers
    )
    assert session_res.status_code == 201
    session_id = session_res.json()["id"]

    # 2. Upload shelf display image with 2 products
    shelf_bytes = generate_shelf_image_bytes(num_products=2)
    upload_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/images/direct-upload",
        files={"file": ("shelf_display.jpg", shelf_bytes, "image/jpeg")},
        headers=auth_headers
    )
    assert upload_res.status_code == 200

    # 3. Check Session Summary live metrics
    summary_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}", headers=auth_headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_products"] >= 1
    assert "high_priority" in summary
    assert "medium_priority" in summary
    assert "low_priority" in summary
    assert "needs_recapture" in summary
    assert "review_required" in summary
    assert "violations" in summary

    # 4. Check Products List includes priority fields
    products_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/products", headers=auth_headers)
    assert products_res.status_code == 200
    prods = products_res.json()["products"]
    assert len(prods) >= 1
    for p in prods:
        assert p["priority"] in ("high", "medium", "low")
        assert p["priority_reason"] is not None
        assert p["underlying_rule_result"] is not None


@pytest.mark.asyncio
async def test_smart_recapture_api_and_upload(async_client: AsyncClient, auth_headers: dict):
    # 1. Create Session
    session_res = await async_client.post(
        "/api/v1/inspection-sessions",
        json={"location": "Smart Bazaar, Bengaluru"},
        headers=auth_headers
    )
    session_id = session_res.json()["id"]

    # 2. Upload shelf image
    shelf_bytes = generate_shelf_image_bytes(num_products=2)
    await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/images/direct-upload",
        files={"file": ("shelf.jpg", shelf_bytes, "image/jpeg")},
        headers=auth_headers
    )

    # 3. Query Smart Recapture Endpoint
    recap_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/recapture", headers=auth_headers)
    assert recap_res.status_code == 200
    recap_data = recap_res.json()
    assert "total_recapture_needed" in recap_data
    assert "items" in recap_data

    # 4. Upload replacement evidence for product 1
    products_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/products", headers=auth_headers)
    first_product = products_res.json()["products"][0]
    prod_id = first_product["product_id"]

    replacement_bytes = generate_shelf_image_bytes(num_products=1, width=400, height=400)
    recap_upload_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/products/{prod_id}/recapture",
        files={"file": ("recapture_crisp.jpg", replacement_bytes, "image/jpeg")},
        headers=auth_headers
    )
    assert recap_upload_res.status_code == 200
    recap_upload_data = recap_upload_res.json()
    assert recap_upload_data["product_id"] == prod_id
    assert recap_upload_data["status"] == "processing"


# --- 3. Session PDF Report & Audit Tests ---

@pytest.mark.asyncio
async def test_session_pdf_and_csv_report_generation(async_client: AsyncClient, auth_headers: dict):
    # 1. Create Session
    session_res = await async_client.post(
        "/api/v1/inspection-sessions",
        json={"location": "Nature's Basket, Mumbai"},
        headers=auth_headers
    )
    session_id = session_res.json()["id"]

    shelf_bytes = generate_shelf_image_bytes(num_products=2)
    await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/images/direct-upload",
        files={"file": ("shelf.jpg", shelf_bytes, "image/jpeg")},
        headers=auth_headers
    )

    # 2. Generate Session PDF Report
    pdf_gen_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/reports",
        json={"format": "pdf"},
        headers=auth_headers
    )
    assert pdf_gen_res.status_code == 200
    pdf_report = pdf_gen_res.json()
    assert pdf_report["format"] == "pdf"
    assert pdf_report["file_size"] > 0
    assert len(pdf_report["sha256_hash"]) == 64

    # 3. Generate Session CSV Report
    csv_gen_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/reports",
        json={"format": "csv"},
        headers=auth_headers
    )
    assert csv_gen_res.status_code == 200
    csv_report = csv_gen_res.json()
    assert csv_report["format"] == "csv"

    # 4. List Session Reports
    list_reports_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/reports", headers=auth_headers)
    assert list_reports_res.status_code == 200
    reports_list = list_reports_res.json()
    assert len(reports_list) >= 2

    # 5. Download Session PDF Report
    dl_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/reports/{pdf_report['id']}/download", headers=auth_headers)
    assert dl_res.status_code == 200
    assert len(dl_res.content) == pdf_report["file_size"]
    assert dl_res.headers["content-type"] == "application/pdf"
