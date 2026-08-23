"""Enforcement Intelligence and Repeat Offender Analytics Service.

IMPORTANT COMPLIANCE NOTICE:
This module computes internal operational enforcement analytics and risk trends.
It is NOT a public blacklist or permanent legal determination.
"""

import uuid
from datetime import date, datetime, time, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session

from backend.app.models.catalog import Brand, Product
from backend.app.models.inspection import Inspection, Violation
from backend.app.models.intelligence import Offender
from backend.app.models.session import InspectionSession, BatchImage, ProductDetection


class IntelligenceService:
    """
    Computes scheduled brand compliance intelligence, risk metrics,
    and regional compliance distribution.
    """

    SEVERITY_WEIGHTS = {
        "Critical": 25.0,
        "Major": 12.0,
        "Minor": 4.0,
        "Review required": 2.0,
    }

    @classmethod
    def aggregate_brand_offenders(
        cls,
        session: Session,
        period_start: date,
        period_end: date,
    ) -> List[Offender]:
        """
        Aggregate compliance performance per brand over a defined quarterly or monthly reporting period.
        Extracts confirmed non-compliance cases to build actionable enforcement risk scores.
        """
        results: List[Offender] = []

        # 1. Query all brands active in this window
        start_dt = datetime.combine(period_start, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(period_end, time.max, tzinfo=timezone.utc)

        brands = session.execute(select(Brand)).scalars().all()

        for brand in brands:
            # 1. Fetch inspections for this brand in the period
            stmt_insp = (
                select(Inspection)
                .join(Product, Inspection.product_id == Product.id)
                .where(
                    Product.brand_id == brand.id,
                    Inspection.captured_at >= start_dt,
                    Inspection.captured_at <= end_dt,
                )
                .order_by(Inspection.captured_at.desc())
            )
            inspections = session.execute(stmt_insp).scalars().all()
            inspection_count = len(inspections)

            if inspection_count == 0:
                continue

            last_seen_at = inspections[0].captured_at
            insp_ids = [insp.id for insp in inspections]

            # 2. Fetch violations across these inspections
            stmt_viol = (
                select(Violation)
                .where(
                    Violation.inspection_id.in_(insp_ids),
                    Violation.status.in_(["confirmed", "detected"]),
                )
            )
            violations = session.execute(stmt_viol).scalars().all()

            confirmed_count = len([
                v for v in violations
                if v.status == "confirmed" or v.officer_disposition == "confirmed" or v.status == "detected"
            ])

            # 3. Calculate weighted severity score
            cumulative_severity = 0.0
            for v in violations:
                weight = cls.SEVERITY_WEIGHTS.get(v.severity, 5.0)
                cumulative_severity += weight

            # 4. Upsert or update Offender record
            stmt_offender = select(Offender).where(
                Offender.brand_id == brand.id,
                Offender.period_start == period_start,
                Offender.period_end == period_end,
            )
            offender_rec = session.execute(stmt_offender).scalar_one_or_none()

            if not offender_rec:
                offender_rec = Offender(
                    id=uuid.uuid4(),
                    brand_id=brand.id,
                    period_start=period_start,
                    period_end=period_end,
                    inspection_count=inspection_count,
                    confirmed_count=confirmed_count,
                    severity_score=round(cumulative_severity, 2),
                    last_seen_at=last_seen_at,
                )
                session.add(offender_rec)
            else:
                offender_rec.inspection_count = inspection_count
                offender_rec.confirmed_count = confirmed_count
                offender_rec.severity_score = round(cumulative_severity, 2)
                offender_rec.last_seen_at = last_seen_at

            results.append(offender_rec)

        session.flush()
        return results

    @classmethod
    def get_brand_intelligence_summary(
        cls,
        session: Session,
        brand_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        Produce historical compliance score summary and repeat-offender intelligence.
        """
        brand = session.execute(select(Brand).filter_by(id=brand_id)).scalar_one_or_none()
        if not brand:
            return {"error": "Brand not found"}

        history = session.execute(
            select(Offender)
            .filter_by(brand_id=brand_id)
            .order_by(Offender.period_end.desc())
        ).scalars().all()

        total_inspections = sum(h.inspection_count for h in history)
        total_confirmed = sum(h.confirmed_count for h in history)
        avg_severity = (sum(h.severity_score for h in history) / len(history)) if history else 0.0

        return {
            "brand_id": str(brand.id),
            "canonical_name": brand.canonical_name,
            "total_inspections": total_inspections,
            "total_confirmed_violations": total_confirmed,
            "average_severity_score": round(avg_severity, 2),
            "non_compliance_rate_pct": round((total_confirmed / total_inspections * 100), 1) if total_inspections > 0 else 0.0,
            "periods_tracked": len(history),
            "history": [
                {
                    "period_start": str(h.period_start),
                    "period_end": str(h.period_end),
                    "inspections": h.inspection_count,
                    "confirmed": h.confirmed_count,
                    "severity": h.severity_score,
                    "last_seen": h.last_seen_at.isoformat() if h.last_seen_at else None,
                }
                for h in history
            ],
        }

    @classmethod
    def get_district_compliance_heatmap(
        cls,
        session: Session,
        state_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Aggregate compliance averages and case volumes by district.
        """
        stmt = (
            select(
                Inspection.district,
                Inspection.state_code,
                func.count(Inspection.id).label("total_inspections"),
                func.avg(Inspection.score).label("avg_score"),
                func.count(
                    Inspection.id
                ).filter(Inspection.status == "review_required").label("pending_reviews"),
            )
            .where(Inspection.district.is_not(None))
            .group_by(Inspection.district, Inspection.state_code)
            .order_by(func.count(Inspection.id).desc())
        )

        if state_code:
            stmt = stmt.where(Inspection.state_code == state_code)

        rows = session.execute(stmt).all()
        return [
            {
                "district": row.district,
                "state_code": row.state_code,
                "total_inspections": row.total_inspections,
                "average_score": round(float(row.avg_score or 0.0), 2),
                "pending_reviews": row.pending_reviews,
            }
            for row in rows
        ]

    @classmethod
    def get_batch_inspection_intelligence(
        cls,
        session: Session,
        session_id: Optional[uuid.UUID] = None,
        organisation_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """
        Compute dynamic aggregation metrics across batch inspection sessions.
        """
        # 1. Total sessions
        sess_stmt = select(func.count(InspectionSession.id))
        if organisation_id:
            sess_stmt = sess_stmt.where(InspectionSession.organisation_id == organisation_id)
        if session_id:
            sess_stmt = sess_stmt.where(InspectionSession.id == session_id)
        total_sessions = session.execute(sess_stmt).scalar() or 0

        # 2. Total products screened & status counts
        det_stmt = (
            select(
                func.count(ProductDetection.id).label("total_screened"),
                func.count(ProductDetection.id).filter(ProductDetection.status == "review_required").label("review_required"),
                func.count(ProductDetection.id).filter(ProductDetection.status == "needs_recapture").label("needs_recapture"),
            )
            .select_from(ProductDetection)
            .join(BatchImage, ProductDetection.batch_image_id == BatchImage.id)
            .join(InspectionSession, BatchImage.session_id == InspectionSession.id)
        )

        if organisation_id:
            det_stmt = det_stmt.where(InspectionSession.organisation_id == organisation_id)
        if session_id:
            det_stmt = det_stmt.where(InspectionSession.id == session_id)

        det_row = session.execute(det_stmt).first()
        total_screened = det_row.total_screened if det_row else 0
        det_review_req = det_row.review_required if det_row else 0
        det_recapture = det_row.needs_recapture if det_row else 0

        # 3. Violation priorities
        viol_stmt = (
            select(
                func.count(Violation.id).label("total_violations"),
                func.count(Violation.id).filter(Violation.severity == "Critical").label("high_priority"),
                func.count(Violation.id).filter(Violation.severity == "Major").label("medium_priority"),
                func.count(Violation.id).filter(Violation.severity == "Minor").label("low_priority"),
                func.count(Violation.id).filter(Violation.status == "confirmed").label("confirmed_violations"),
            )
            .select_from(Violation)
            .join(Inspection, Violation.inspection_id == Inspection.id)
        )

        if organisation_id:
            viol_stmt = viol_stmt.where(Inspection.organisation_id == organisation_id)
        if session_id:
            viol_stmt = viol_stmt.where(Inspection.inspection_session_id == session_id)

        viol_row = session.execute(viol_stmt).first()

        return {
            "total_sessions": total_sessions,
            "total_products_screened": total_screened,
            "high_priority_products": viol_row.high_priority if viol_row else 0,
            "medium_priority_products": viol_row.medium_priority if viol_row else 0,
            "low_priority_products": viol_row.low_priority if viol_row else 0,
            "review_required": det_review_req,
            "needs_recapture": det_recapture,
            "confirmed_violations": viol_row.confirmed_violations if viol_row else 0,
        }
