import os
import io
import csv
import uuid
import hashlib
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.models.inspection import Inspection
from app.models.inspection_session import InspectionSession
from app.models.image import Image
from app.models.report import ReportMetadata
from app.services.storage_service import storage_service


class ReportService:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "../templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    # --- Single Inspection Reports ---

    def generate_pdf_bytes(self, inspection_data: dict) -> bytes:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, "DEPARTMENT OF CONSUMER AFFAIRS, GOVT OF INDIA")
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 730, "LEGAL METROLOGY COMPLIANCE INSPECTION REPORT")
        
        p.setFont("Helvetica", 10)
        p.drawString(50, 700, f"Inspection ID: {inspection_data.get('inspection_number')}")
        p.drawString(50, 685, f"Product Name: {inspection_data.get('product_name', 'N/A')}")
        p.drawString(50, 670, f"Channel: {inspection_data.get('channel', 'Retail store')}")
        p.drawString(50, 655, f"Overall Status: {inspection_data.get('status', 'draft')}")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, 620, "Rule Evaluations (LMPC 2011)")

        y = 595
        p.setFont("Helvetica", 9)
        for r in inspection_data.get("rule_evaluations", []):
            if y < 100:
                p.showPage()
                y = 750
            p.drawString(50, y, f"[{r.get('rule_id')}] {r.get('clause')}: {r.get('result', '').upper()} - {r.get('explanation')}")
            y -= 18

        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, 40, f"Generated on: {datetime.now(timezone.utc).isoformat()} | Platform: LabelSetu")
        p.showPage()
        p.save()

        buffer.seek(0)
        return buffer.getvalue()

    def generate_docx_bytes(self, inspection_data: dict) -> bytes:
        doc = Document()
        doc.add_heading("Legal Metrology Compliance Inspection Report", level=0)
        doc.add_paragraph(f"Inspection Number: {inspection_data.get('inspection_number')}")
        doc.add_paragraph(f"Product Name: {inspection_data.get('product_name')}")
        doc.add_paragraph(f"Status: {inspection_data.get('status')}")

        doc.add_heading("Rule Evaluation Findings", level=1)
        for r in inspection_data.get("rule_evaluations", []):
            doc.add_paragraph(f"{r.get('rule_id')} ({r.get('clause')}): {r.get('result')} - {r.get('explanation')}")

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_csv_bytes(self, inspection_data: dict) -> bytes:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Inspection Number", "Product Name", "Channel", "Status"])
        writer.writerow([
            inspection_data.get("inspection_number"),
            inspection_data.get("product_name"),
            inspection_data.get("channel"),
            inspection_data.get("status")
        ])
        writer.writerow([])
        writer.writerow(["Rule ID", "Clause", "Result", "Severity", "Explanation"])
        for r in inspection_data.get("rule_evaluations", []):
            writer.writerow([r.get("rule_id"), r.get("clause"), r.get("result"), r.get("severity"), r.get("explanation")])

        return output.getvalue().encode("utf-8")

    def build_report_data(self, inspection: Inspection, image: Image | None, normalized_fields: list, violations: list) -> dict:
        meta = inspection.metadata_json or {}
        rule_evals = meta.get("rule_evaluations", [])

        return {
            "inspection_number": inspection.inspection_number,
            "product_name": inspection.product_name or "N/A",
            "brand_name": inspection.brand_name or "N/A",
            "channel": inspection.channel or "Retail store",
            "officer_id": str(inspection.officer_id),
            "status": inspection.status,
            "created_at": inspection.created_at.isoformat() if inspection.created_at else "",
            "image_hash": image.sha256_hash if image else "N/A",
            "rule_evaluations": rule_evals,
            "normalized_fields": [{"field_name": f.field_name, "raw_value": f.raw_value, "normalized_value": f.normalized_value, "confidence": f.confidence} for f in normalized_fields]
        }

    # --- Session-Level Reports (Stage 4B) ---

    def generate_session_pdf_bytes(self, session_data: dict) -> bytes:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Page 1: Header & Executive Triage Summary
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, "DEPARTMENT OF CONSUMER AFFAIRS, GOVT OF INDIA")
        p.setFont("Helvetica-Bold", 13)
        p.drawString(50, 730, "LEGAL METROLOGY BATCH / SHELF INSPECTION REPORT")

        p.setFont("Helvetica", 10)
        p.drawString(50, 695, f"Session ID: {session_data.get('session_id')}")
        p.drawString(50, 680, f"Location: {session_data.get('location', 'N/A')}")
        p.drawString(50, 665, f"GPS Coordinates: Lat {session_data.get('latitude', 'N/A')}, Lon {session_data.get('longitude', 'N/A')}")
        p.drawString(50, 650, f"Inspector ID: {session_data.get('inspector_id', 'N/A')}")
        p.drawString(50, 635, f"Session Status: {session_data.get('status', 'complete').upper()}")
        p.drawString(50, 620, f"Timestamp: {session_data.get('started_at', datetime.now(timezone.utc).isoformat())}")

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 585, "BATCH OPERATIONAL SUMMARY")
        p.setFont("Helvetica", 10)
        metrics = session_data.get("metrics", {})
        p.drawString(60, 565, f"• Total Shelf Images: {session_data.get('total_images', 1)}")
        p.drawString(60, 550, f"• Total Products Screened: {session_data.get('total_products', 0)}")
        p.drawString(60, 535, f"• High Priority (Violations / Critical): {metrics.get('high_priority', 0)}")
        p.drawString(60, 520, f"• Medium Priority (Ambiguities / Review): {metrics.get('medium_priority', 0)}")
        p.drawString(60, 505, f"• Low Priority (Compliant Standard): {metrics.get('low_priority', 0)}")
        p.drawString(60, 490, f"• Smart Recaptures Required: {metrics.get('needs_recapture', 0)}")
        p.drawString(60, 475, f"• Total Violations Flagged: {metrics.get('violations', 0)}")

        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 440, "SCREENED COMMODITY BREAKDOWN")

        y = 415
        p.setFont("Helvetica", 9)
        for idx, prod in enumerate(session_data.get("products", [])):
            if y < 100:
                p.showPage()
                y = 750
                p.setFont("Helvetica-Bold", 11)
                p.drawString(50, y, "SCREENED COMMODITY BREAKDOWN (Continued)")
                y -= 25
                p.setFont("Helvetica", 9)

            p.drawString(50, y, f"Product #{idx + 1} [{prod.get('product_id', '')[:8]}]: Priority={prod.get('priority', 'low').upper()} | Status={prod.get('status', 'compliant')} | Reason={prod.get('reason', 'N/A')}")
            y -= 14
            for r in prod.get("rule_evaluations", []):
                if y < 100:
                    p.showPage()
                    y = 750
                    p.setFont("Helvetica", 9)
                p.drawString(70, y, f"- [{r.get('rule_id')}] {r.get('clause')}: {r.get('result', '').upper()} (v{r.get('rule_version', '1.0')})")
                y -= 12
            y -= 6

        # Audit & Cryptographic Chain Signature
        if y < 80:
            p.showPage()
            y = 750
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, 40, f"Generated on: {datetime.now(timezone.utc).isoformat()} | Audit Chained | Platform: LabelSetu")
        p.showPage()
        p.save()

        buffer.seek(0)
        return buffer.getvalue()

    def generate_session_csv_bytes(self, session_data: dict) -> bytes:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Session ID", "Location", "Status", "Total Products", "High Priority", "Medium Priority", "Low Priority", "Violations"])
        metrics = session_data.get("metrics", {})
        writer.writerow([
            session_data.get("session_id"),
            session_data.get("location"),
            session_data.get("status"),
            session_data.get("total_products"),
            metrics.get("high_priority"),
            metrics.get("medium_priority"),
            metrics.get("low_priority"),
            metrics.get("violations")
        ])
        writer.writerow([])
        writer.writerow(["Product ID", "Inspection ID", "Priority", "Status", "Reason", "Confidence"])
        for prod in session_data.get("products", []):
            writer.writerow([
                prod.get("product_id"),
                prod.get("inspection_id"),
                prod.get("priority"),
                prod.get("status"),
                prod.get("reason"),
                prod.get("confidence")
            ])

        return output.getvalue().encode("utf-8")

    def generate_session_docx_bytes(self, session_data: dict) -> bytes:
        doc = Document()
        doc.add_heading("Legal Metrology Batch Inspection Session Report", level=0)
        doc.add_paragraph(f"Session ID: {session_data.get('session_id')}")
        doc.add_paragraph(f"Location: {session_data.get('location')}")
        doc.add_paragraph(f"Status: {session_data.get('status')}")

        doc.add_heading("Operational Summary", level=1)
        metrics = session_data.get("metrics", {})
        doc.add_paragraph(f"Total Products: {session_data.get('total_products')}")
        doc.add_paragraph(f"High Priority: {metrics.get('high_priority')}")
        doc.add_paragraph(f"Medium Priority: {metrics.get('medium_priority')}")
        doc.add_paragraph(f"Low Priority: {metrics.get('low_priority')}")

        doc.add_heading("Product Findings", level=1)
        for prod in session_data.get("products", []):
            doc.add_paragraph(f"Product ID: {prod.get('product_id')} | Priority: {prod.get('priority')} | Status: {prod.get('status')}")

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()


report_service = ReportService()
