from app.schemas.rule_engine import RuleEvaluationResult
from app.services.cv.calibration_service import CalibrationResult


class ComplianceService:
    def calculate_compliance_score(
        self,
        rule_results: list[RuleEvaluationResult],
        calibration_result: CalibrationResult,
        job_status: str
    ) -> dict:
        if job_status == "needs_recapture":
            return {
                "overall_status": "needs_recapture",
                "score_status": "final",
                "provisional_score": 0.0,
                "critical_violations_count": 0,
                "major_violations_count": 0,
                "review_required_count": 0,
                "explanation": "Image quality check failed. Evidence unusable; needs recapture."
            }

        critical_violations = [r for r in rule_results if r.result == "violation" and r.severity == "critical"]
        major_violations = [r for r in rule_results if r.result == "violation" and r.severity == "major"]
        minor_violations = [r for r in rule_results if r.result == "violation" and r.severity == "minor"]
        reviews_required = [r for r in rule_results if r.result == "review_required"]
        not_evaluables = [r for r in rule_results if r.result == "not_evaluable"]

        total_penalty = (len(critical_violations) * 22) + (len(major_violations) * 9) + (len(minor_violations) * 3)
        base_score = max(0.0, round(100.0 - total_penalty, 2))

        score_status = "final"
        if not calibration_result.is_valid or not_evaluables or reviews_required:
            score_status = "provisional"

        if critical_violations or major_violations or minor_violations:
            overall_status = "violation"
        elif reviews_required:
            overall_status = "review_required"
        elif not_evaluables:
            overall_status = "not_evaluable"
        else:
            overall_status = "compliant"

        return {
            "overall_status": overall_status,
            "score_status": score_status,
            "provisional_score": base_score,
            "critical_violations_count": len(critical_violations),
            "major_violations_count": len(major_violations),
            "review_required_count": len(reviews_required),
            "explanation": f"Evaluation complete. Score: {base_score}/100. Status: {overall_status} ({score_status})."
        }


compliance_service = ComplianceService()
