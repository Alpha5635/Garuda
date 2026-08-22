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
from app.models.image import Image
from app.models.report import ReportMetadata
from app.services.storage_service import storage_service


class ReportService:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "../templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def generate_pdf_bytes(self, inspection_data: dict) -> bytes:
        # Generate simple PDF using ReportLab canvas
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


report_service = ReportService()
