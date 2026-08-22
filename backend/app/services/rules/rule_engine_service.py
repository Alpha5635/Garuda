import os
import json
from typing import Sequence
from app.schemas.normalization import NormalizedFieldSchema
from app.schemas.calibration import CalibrationResponse
from app.schemas.rule_engine import RuleEvaluationResult, RuleDefinition
from app.services.cv.calibration_service import CalibrationResult


class RuleEngineService:
    def __init__(self):
        self.rulepack_version = "LMPC-2011/v1.0.0"
        self.rules: list[dict] = []
        self.table_i_config: dict = {}
        self._load_rules()

    def _load_rules(self):
        rules_path = os.path.join(os.path.dirname(__file__), "../../rules/lmpc_rules_v1.json")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.rulepack_version = data.get("rulepack_version", "LMPC-2011/v1.0.0")
                self.rules = data.get("rules", [])
                self.table_i_config = data.get("rule7_table_i", {})

    def evaluate_all_rules(
        self,
        normalized_fields: list[NormalizedFieldSchema],
        calibration_result: CalibrationResult,
        channel: str = "Retail store",
        is_embossed: bool = False
    ) -> list[RuleEvaluationResult]:
        field_map = {f.field_name: f for f in normalized_fields}
        results: list[RuleEvaluationResult] = []

        for rule in self.rules:
            rule_id = rule["rule_id"]
            clause = rule["clause"]
            field_key = rule["field"]
            severity = rule["severity"]
            applicability = rule.get("applicability", [])

            # Check Channel Applicability (e.g. Month/Year is exempt for E-commerce under Rule 6(10))
            if channel not in applicability and "All" not in applicability:
                results.append(
                    RuleEvaluationResult(
                        rule_id=rule_id,
                        rule_version=self.rulepack_version,
                        clause=clause,
                        result="not_applicable",
                        severity=severity,
                        confidence=1.0,
                        explanation=f"Rule {clause} is not applicable for channel '{channel}'."
                    )
                )
                continue

            # 1. Manufacturer / Address Check
            if rule_id == "LM-6-1-A-01":
                field = field_map.get("manufacturer")
                if not field or not field.normalized_value:
                    results.append(self._make_violation(rule, "Missing name and address of manufacturer/packer/importer."))
                else:
                    results.append(self._make_pass(rule, f"Manufacturer declared: '{field.normalized_value}'"))

            # 2. Net Quantity Check
            elif rule_id == "LM-6-1-C-01":
                field = field_map.get("net_quantity")
                if not field or not field.normalized_value:
                    results.append(self._make_violation(rule, "Missing net quantity declaration."))
                else:
                    results.append(self._make_pass(rule, f"Net quantity declared: '{field.normalized_value}'"))

            # 3. MRP Check
            elif rule_id == "LM-6-1-E-01":
                field = field_map.get("mrp")
                if not field or not field.normalized_value:
                    results.append(self._make_violation(rule, "Missing MRP declaration."))
                else:
                    raw_lower = field.raw_value.lower()
                    if "incl" not in raw_lower and "taxes" not in raw_lower:
                        results.append(self._make_violation(rule, "MRP declaration lacks mandatory 'inclusive of all taxes' wording."))
                    else:
                        results.append(self._make_pass(rule, f"MRP declared: '{field.normalized_value}' (inclusive of all taxes)"))

            # 4. Month/Year Check
            elif rule_id == "LM-6-1-D-01":
                field = field_map.get("month_year")
                if not field or not field.normalized_value:
                    results.append(self._make_violation(rule, "Missing month and year of manufacture/packing."))
                else:
                    results.append(self._make_pass(rule, f"Month/Year declared: '{field.normalized_value}'"))

            # 5. Consumer Care Check
            elif rule_id == "LM-6-2-01":
                field = field_map.get("consumer_care")
                if not field or not field.normalized_value:
                    results.append(self._make_violation(rule, "Missing consumer care helpline/email/address."))
                else:
                    results.append(self._make_pass(rule, f"Consumer care declared: '{field.normalized_value}'"))

            # 6. Country of Origin Check
            elif rule_id == "LM-6-1-AA-01":
                field = field_map.get("country_of_origin")
                if not field or not field.normalized_value:
                    results.append(self._make_pass(rule, "Domestic package (Country of origin not declared / optional for domestic)."))
                else:
                    results.append(self._make_pass(rule, f"Country of origin declared: '{field.normalized_value}'"))

            # 7. Rule 7 Table I Calibrated Numeral Height Check
            elif rule_id == "LM-7-2-01":
                if not calibration_result.is_valid or calibration_result.pixels_per_mm <= 0:
                    results.append(
                        RuleEvaluationResult(
                            rule_id=rule_id,
                            rule_version=self.rulepack_version,
                            clause=clause,
                            result="not_evaluable",
                            severity=severity,
                            confidence=0.0,
                            explanation="Camera scale is uncalibrated. Legal Metrology numeral height cannot be measured without physical scale calibration."
                        )
                    )
                else:
                    net_qty_field = field_map.get("net_quantity")
                    if not net_qty_field or not net_qty_field.bounding_box or not net_qty_field.numeric_value:
                        results.append(
                            RuleEvaluationResult(
                                rule_id=rule_id,
                                rule_version=self.rulepack_version,
                                clause=clause,
                                result="not_evaluable",
                                severity=severity,
                                confidence=0.0,
                                explanation="Net quantity bounding box or numeric weight/volume unavailable for Rule 7 Table I height check."
                            )
                        )
                    else:
                        qty = net_qty_field.numeric_value
                        req_height_mm = self._get_required_numeral_height(qty, is_embossed)
                        
                        # Calculate height in mm
                        height_px = float(net_qty_field.bounding_box[3]) if isinstance(net_qty_field.bounding_box[0], (int, float)) else float(net_qty_field.bounding_box[3][1] - net_qty_field.bounding_box[0][1])
                        measured_height_mm = round(height_px / calibration_result.pixels_per_mm, 2)
                        error_mm = calibration_result.measurement_error

                        # Check error boundary overlap
                        if abs(measured_height_mm - req_height_mm) <= error_mm:
                            results.append(
                                RuleEvaluationResult(
                                    rule_id=rule_id,
                                    rule_version=self.rulepack_version,
                                    clause=clause,
                                    result="review_required",
                                    severity=severity,
                                    confidence=0.75,
                                    explanation=f"Numeral height measured at {measured_height_mm} mm (±{error_mm} mm). Uncertainty overlaps regulatory requirement threshold of {req_height_mm} mm."
                                )
                            )
                        elif measured_height_mm < req_height_mm:
                            results.append(
                                RuleEvaluationResult(
                                    rule_id=rule_id,
                                    rule_version=self.rulepack_version,
                                    clause=clause,
                                    result="violation",
                                    severity=severity,
                                    confidence=0.92,
                                    explanation=f"Contravention of Rule 7(2) Table I: Net quantity numeral height measured at {measured_height_mm} mm, which is below mandatory minimum height of {req_height_mm} mm for a {qty} g/ml package."
                                )
                            )
                        else:
                            results.append(
                                RuleEvaluationResult(
                                    rule_id=rule_id,
                                    rule_version=self.rulepack_version,
                                    clause=clause,
                                    result="pass",
                                    severity=severity,
                                    confidence=0.95,
                                    explanation=f"Rule 7(2) Table I compliant: Net quantity numeral height measured at {measured_height_mm} mm (mandatory minimum: {req_height_mm} mm)."
                                )
                            )

        return results

    def _get_required_numeral_height(self, qty_g_ml: float, is_embossed: bool = False) -> float:
        table_key = "embossed" if is_embossed else "normal"
        entries = self.table_i_config.get(table_key, [])
        for entry in entries:
            max_q = entry.get("max_qty_g_ml")
            if max_q is None or qty_g_ml <= max_q:
                return float(entry.get("min_height_mm", 1.0))
        return 4.0

    def _make_pass(self, rule: dict, explanation: str) -> RuleEvaluationResult:
        return RuleEvaluationResult(
            rule_id=rule["rule_id"],
            rule_version=self.rulepack_version,
            clause=rule["clause"],
            result="pass",
            severity=rule["severity"],
            confidence=0.95,
            explanation=explanation
        )

    def _make_violation(self, rule: dict, explanation: str) -> RuleEvaluationResult:
        return RuleEvaluationResult(
            rule_id=rule["rule_id"],
            rule_version=self.rulepack_version,
            clause=rule["clause"],
            result="violation",
            severity=rule["severity"],
            confidence=0.90,
            explanation=explanation
        )


rule_engine_service = RuleEngineService()
