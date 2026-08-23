from dataclasses import dataclass, field
from typing import Any
from app.schemas.rule_engine import RuleEvaluationResult
from app.services.cv.calibration_service import CalibrationResult


@dataclass
class RiskPriorityResult:
    """
    Deterministic risk prioritization for batch inspection review triage.
    IMPORTANT: Risk priority is an operational triage heuristic and NOT a legal determination
    of guilt or statutory liability. Authoritative versioned rule evaluations and authorized
    officer human review govern enforcement.
    """
    priority: str  # "high" | "medium" | "low"
    reason: str    # "rule_violation" | "multiple_violations" | "low_ocr_confidence" | "invalid_calibration" | "review_required" | "needs_recapture" | "compliant"
    confidence: float
    underlying_rule_result: str  # "violation" | "review_required" | "not_evaluable" | "compliant" | "needs_recapture"
    review_required: bool
    details: dict[str, Any] = field(default_factory=dict)


class RiskPrioritizationService:
    """
    Deterministic rule-based prioritization service to direct officer attention
    towards products requiring human verification.
    """

    def evaluate_priority(
        self,
        rule_results: list[RuleEvaluationResult] | None,
        compliance_score_data: dict[str, Any] | None,
        calibration_result: CalibrationResult | None = None,
        avg_ocr_confidence: float = 1.0,
        detection_confidence: float = 1.0,
        job_status: str = "complete",
        qc_reason: str | None = None
    ) -> RiskPriorityResult:
        rule_results = rule_results or []
        compliance_data = compliance_score_data or {}
        overall_status = compliance_data.get("overall_status", "compliant")

        # 1. Quality Check Failure / Needs Recapture
        if job_status in ("needs_recapture", "failed") or overall_status == "needs_recapture":
            return RiskPriorityResult(
                priority="medium",
                reason="needs_recapture",
                confidence=round(detection_confidence, 2),
                underlying_rule_result="needs_recapture",
                review_required=True,
                details={
                    "qc_reason": qc_reason or "evidence_unusable",
                    "triage_guidance": "Image quality issue detected. Product requires smart recapture before conclusive legal assessment."
                }
            )

        violations = [r for r in rule_results if r.result == "violation"]
        critical_violations = [r for r in violations if r.severity == "critical"]
        major_violations = [r for r in violations if r.severity == "major"]
        reviews_required = [r for r in rule_results if r.result == "review_required"]
        not_evaluables = [r for r in rule_results if r.result == "not_evaluable"]

        # 2. HIGH PRIORITY: Confirmed critical/major violations or multiple violations
        if len(violations) >= 2 or len(critical_violations) > 0 or len(major_violations) > 0 or overall_status == "violation":
            reason = "multiple_violations" if len(violations) >= 2 else "rule_violation"
            return RiskPriorityResult(
                priority="high",
                reason=reason,
                confidence=round(min(avg_ocr_confidence, detection_confidence), 2),
                underlying_rule_result="violation",
                review_required=True,
                details={
                    "total_violations": len(violations),
                    "critical_count": len(critical_violations),
                    "major_count": len(major_violations),
                    "triage_guidance": f"High attention required: {len(violations)} rule violation(s) detected under Legal Metrology Rules 2011."
                }
            )

        # 3. MEDIUM PRIORITY: Review required, uncalibrated dimensions, low OCR, or uncertain detection
        is_calibrated = calibration_result.is_valid if calibration_result else True
        if (
            reviews_required
            or not_evaluables
            or overall_status in ("review_required", "not_evaluable")
            or not is_calibrated
            or avg_ocr_confidence < 0.75
            or detection_confidence < 0.65
        ):
            if not is_calibrated:
                reason = "invalid_calibration"
            elif avg_ocr_confidence < 0.75:
                reason = "low_ocr_confidence"
            elif detection_confidence < 0.65:
                reason = "uncertain_detection"
            else:
                reason = "review_required"

            return RiskPriorityResult(
                priority="medium",
                reason=reason,
                confidence=round(min(avg_ocr_confidence, detection_confidence), 2),
                underlying_rule_result=overall_status if overall_status in ("review_required", "not_evaluable") else "review_required",
                review_required=True,
                details={
                    "calibrated": is_calibrated,
                    "avg_ocr_confidence": round(avg_ocr_confidence, 2),
                    "detection_confidence": round(detection_confidence, 2),
                    "reviews_required_count": len(reviews_required),
                    "triage_guidance": "Medium priority: Automated extraction has ambiguities or uncalibrated dimensional rules requiring human verification."
                }
            )

        # 4. LOW PRIORITY: Clean extraction, valid calibration, zero violations
        return RiskPriorityResult(
            priority="low",
            reason="compliant",
            confidence=round(min(avg_ocr_confidence, detection_confidence), 2),
            underlying_rule_result="compliant",
            review_required=False,
            details={
                "calibrated": is_calibrated,
                "avg_ocr_confidence": round(avg_ocr_confidence, 2),
                "triage_guidance": "Low priority: Mandatory declarations detected with high confidence; compliant with LMPC 2011 standard requirements."
            }
        )


risk_prioritization_service = RiskPrioritizationService()
