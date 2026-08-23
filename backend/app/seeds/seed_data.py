"""Seed script for LabelSetu: Inserts comprehensive demo corpus adhering to SIH 26034 Playbook."""

import hashlib
import json
import uuid
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash, canonical_json_dumps, compute_canonical_audit_hash
from backend.app.db.session import db_session
from backend.app.models.organisation import Organisation
from backend.app.models.role import Role, UserRole
from backend.app.models.user import User
from backend.app.models.catalog import Brand, Product
from backend.app.models.rule import RulePack, RuleVersion
from backend.app.models.session import (
    InspectionSession,
    BatchImage,
    ProductDetection,
)
from backend.app.models.inspection import (
    Inspection,
    ProductImage,
    ExtractedField,
    Violation,
    Report,
    ReviewAction,
)
from backend.app.models.audit import AuditLog
from backend.app.models.intelligence import (
    Offender,
    SyncQueue,
    EcommerceListing,
    ModelVersion,
)
from backend.app.services.audit import AuditService


import os
import sys

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

def seed_database(session: Session) -> None:
    """Populate database with complete production-aligned seed data."""
    print("[INFO] Starting LabelSetu Database Seeding...")

    # Check if already seeded
    existing_org = session.execute(select(Organisation).filter_by(name="DoCA Central Enforcement")).scalar_one_or_none()
    if existing_org:
        print("[INFO] Database already seeded. Skipping initial creation.")
        return

    # 1. Organisations
    doca_central = Organisation(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        name="DoCA Central Enforcement",
        code="DOCA_CENTRAL",
        type="DoCA",
        state_code=None,
        status="active",
    )
    delhi_dept = Organisation(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        name="Delhi Legal Metrology Department",
        code="DL_METRO",
        type="state",
        state_code="DL",
        status="active",
    )
    mh_dept = Organisation(
        id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        name="Maharashtra Legal Metrology Department",
        code="MH_METRO",
        type="state",
        state_code="MH",
        status="active",
    )
    itc_mfg = Organisation(
        id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
        name="ITC Limited - Foods Division",
        code="ITC_LTD",
        type="manufacturer",
        state_code="WB",
        status="active",
    )
    blinkit_platform = Organisation(
        id=uuid.UUID("55555555-5555-5555-5555-555555555555"),
        name="Blinkit QuickCommerce Pvt Ltd",
        code="BLINKIT",
        type="platform",
        state_code="DL",
        status="active",
    )
    demo_lab = Organisation(
        id=uuid.UUID("66666666-6666-6666-6666-666666666666"),
        name="SIH Evaluation Demonstration Lab",
        code="SIH_DEMO_LAB",
        type="demo",
        state_code="DL",
        status="active",
    )
    session.add_all([doca_central, delhi_dept, mh_dept, itc_mfg, blinkit_platform, demo_lab])
    session.flush()

    # 2. Roles
    roles_data = [
        ("super_admin", "Super Administrator", "System Governance & Audit Verifier", {"all": True, "audit_verify": True}),
        ("rule_admin", "Rule Administrator", "Legal Metrology Rule Pack Author", {"rule_author": True, "rule_approve": True}),
        ("officer", "Legal Metrology Officer", "Field Metrology Officer", {"inspect": True, "sign_report": True, "resolve_violation": True}),
        ("reviewer", "OCR Reviewer", "Human-in-the-Loop OCR Reviewer", {"review_queue": True, "correct_field": True}),
        ("manufacturer", "Manufacturer Self-Checker", "Manufacturer Self-Check Operator", {"self_check": True, "view_own_catalog": True}),
        ("consumer", "Citizen Consumer", "Citizen Scan & Lead Reporter", {"consumer_scan": True, "view_status": True}),
        ("analyst", "Enforcement Analyst", "Enforcement Intelligence Analyst", {"view_heatmaps": True, "view_offenders": True, "export_kpi": True}),
    ]
    roles_map = {}
    for code, name, desc, perms in roles_data:
        role = Role(
            id=uuid.uuid4(),
            code=code,
            name=name,
            description=desc,
            permissions_jsonb=perms,
        )
        session.add(role)
        roles_map[code] = role
    session.flush()

    # 3. Users
    pwd_hash = get_password_hash("DemoPass2026!")
    user_super = User(
        id=uuid.UUID("a1111111-1111-1111-1111-111111111111"),
        organisation_id=doca_central.id,
        email="superadmin@doca.gov.in",
        phone="+91-11-2338-0001",
        password_hash=pwd_hash,
        name="Dr. Rajesh Kumar",
        full_name="Dr. Rajesh Kumar (Super Admin)",
        is_active=True,
        status="active",
    )
    user_rule_admin = User(
        id=uuid.UUID("a2222222-2222-2222-2222-222222222222"),
        organisation_id=doca_central.id,
        email="ruleadmin@doca.gov.in",
        phone="+91-11-2338-0002",
        password_hash=pwd_hash,
        name="Adv. Meera Sen",
        full_name="Adv. Meera Sen (Legal Metrology Legal Counsel)",
        is_active=True,
        status="active",
    )
    user_officer = User(
        id=uuid.UUID("a3333333-3333-3333-3333-333333333333"),
        organisation_id=delhi_dept.id,
        email="officer.delhi@gov.in",
        phone="+91-98110-12345",
        password_hash=pwd_hash,
        name="Inspector Vikram Sharma",
        full_name="Inspector Vikram Sharma",
        is_active=True,
        status="active",
    )
    user_reviewer = User(
        id=uuid.UUID("a4444444-4444-4444-4444-444444444444"),
        organisation_id=delhi_dept.id,
        email="reviewer.delhi@gov.in",
        phone="+91-98110-54321",
        password_hash=pwd_hash,
        name="Ananya Verma",
        full_name="Ananya Verma (Verification Specialist)",
        is_active=True,
        status="active",
    )
    user_mfg = User(
        id=uuid.UUID("a5555555-5555-5555-5555-555555555555"),
        organisation_id=itc_mfg.id,
        email="compliance@itc.in",
        phone="+91-33-2288-0000",
        password_hash=pwd_hash,
        name="Sunil Natarajan",
        full_name="Sunil Natarajan (QA / Packaging Lead)",
        is_active=True,
        status="active",
    )
    user_analyst = User(
        id=uuid.UUID("a6666666-6666-6666-6666-666666666666"),
        organisation_id=doca_central.id,
        email="analyst@doca.gov.in",
        phone="+91-11-2338-0005",
        password_hash=pwd_hash,
        name="Pooja Deshmukh",
        full_name="Pooja Deshmukh (Data Analyst)",
        is_active=True,
        status="active",
    )
    user_consumer = User(
        id=uuid.UUID("a7777777-7777-7777-7777-777777777777"),
        organisation_id=demo_lab.id,
        email="citizen@gmail.com",
        phone="+91-99999-88888",
        password_hash=pwd_hash,
        name="Rohit Verma",
        full_name="Rohit Verma (Consumer Citizen)",
        is_active=True,
        status="active",
    )
    session.add_all([user_super, user_rule_admin, user_officer, user_reviewer, user_mfg, user_analyst, user_consumer])
    session.flush()

    # 4. User Roles Mapping
    user_roles_entries = [
        (user_super.id, roles_map["super_admin"].id, doca_central.id),
        (user_rule_admin.id, roles_map["rule_admin"].id, doca_central.id),
        (user_officer.id, roles_map["officer"].id, delhi_dept.id),
        (user_officer.id, roles_map["reviewer"].id, delhi_dept.id),  # Supports state officer acting as reviewer
        (user_reviewer.id, roles_map["reviewer"].id, delhi_dept.id),
        (user_mfg.id, roles_map["manufacturer"].id, itc_mfg.id),
        (user_analyst.id, roles_map["analyst"].id, doca_central.id),
        (user_consumer.id, roles_map["consumer"].id, demo_lab.id),
    ]
    for uid, rid, oid in user_roles_entries:
        session.add(UserRole(id=uuid.uuid4(), user_id=uid, role_id=rid, organisation_id=oid))
    session.flush()

    # 5. Brands
    brand_aashirvaad = Brand(
        id=uuid.UUID("b1111111-1111-1111-1111-111111111111"),
        canonical_name="Aashirvaad",
        name="Aashirvaad",
        normalized_name="aashirvaad",
        organisation_id=itc_mfg.id,
        aliases_jsonb=["Aashirvad", "Ashirwad", "Aashirvaad Atta", "आशीर्वाद"],
        manufacturer_org_id=itc_mfg.id,
    )
    brand_fortune = Brand(
        id=uuid.UUID("b2222222-2222-2222-2222-222222222222"),
        canonical_name="Fortune",
        name="Fortune",
        normalized_name="fortune",
        organisation_id=None,
        aliases_jsonb=["Fortune Oil", "Fortune Foods", "Fortun", "फॉर्च्यून"],
        manufacturer_org_id=None,
    )
    brand_tata = Brand(
        id=uuid.UUID("b3333333-3333-3333-3333-333333333333"),
        canonical_name="Tata Sampann",
        name="Tata Sampann",
        normalized_name="tata sampann",
        organisation_id=None,
        aliases_jsonb=["Tata Sampan", "Sampann", "Tata Dal", "टाटा सम्पन्न"],
        manufacturer_org_id=None,
    )
    brand_imported = Brand(
        id=uuid.UUID("b4444444-4444-4444-4444-444444444444"),
        canonical_name="Swiss Chocolatier Premium",
        name="Swiss Chocolatier Premium",
        normalized_name="swiss chocolatier premium",
        organisation_id=None,
        aliases_jsonb=["SwissChoc", "AlpenGold Swiss"],
        manufacturer_org_id=None,
    )
    brand_glow = Brand(
        id=uuid.UUID("b5555555-5555-5555-5555-555555555555"),
        canonical_name="Glow & Care Herbal",
        name="Glow & Care Herbal",
        normalized_name="glow & care herbal",
        organisation_id=None,
        aliases_jsonb=["GlowCare", "Glow Herbal"],
        manufacturer_org_id=None,
    )
    session.add_all([brand_aashirvaad, brand_fortune, brand_tata, brand_imported, brand_glow])
    session.flush()

    # 6. Products
    prod_atta = Product(
        id=uuid.UUID("c1111111-1111-1111-1111-111111111111"),
        brand_id=brand_aashirvaad.id,
        name="Aashirvaad Whole Wheat Atta 5kg",
        generic_name="Whole Wheat Atta (Chakki Fresh)",
        sku="AASH-WHEAT-5KG",
        category="food_staples",
        is_imported=False,
        metadata_jsonb={"standard_net_quantity": "5 kg", "hsn": "11010000"},
    )
    prod_oil = Product(
        id=uuid.UUID("c2222222-2222-2222-2222-222222222222"),
        brand_id=brand_fortune.id,
        name="Fortune Refined Sunflower Oil 1L",
        generic_name="Refined Sunflower Oil",
        sku="FORT-SUN-1L",
        category="edible_oil",
        is_imported=False,
        metadata_jsonb={"standard_net_quantity": "1 L", "density_g_per_ml": 0.91},
    )
    prod_dal = Product(
        id=uuid.UUID("c3333333-3333-3333-3333-333333333333"),
        brand_id=brand_tata.id,
        name="Tata Sampann Unpolished Toor Dal 1kg",
        generic_name="Unpolished Toor Dal",
        sku="TATA-TOOR-1KG",
        category="food_staples",
        is_imported=False,
        metadata_jsonb={"standard_net_quantity": "1 kg", "grade": "Grade A"},
    )
    prod_choc = Product(
        id=uuid.UUID("c4444444-4444-4444-4444-444444444444"),
        brand_id=brand_imported.id,
        name="Swiss Chocolatier Dark Chocolate 100g",
        generic_name="Dark Chocolate Bar 70% Cocoa",
        sku="SWISS-DARK-100G",
        category="food_staples",
        is_imported=True,
        metadata_jsonb={"standard_net_quantity": "100 g", "country_of_origin": "Switzerland"},
    )
    session.add_all([prod_atta, prod_oil, prod_dal, prod_choc])
    session.flush()

    # 7. Rule Pack & Rule Version (lmpc-core @ 2026.0)
    rule_pack_core = RulePack(
        id="lmpc-core",
        name="Legal Metrology (Packaged Commodities) Rules, 2011 - Core Standards",
        jurisdiction="India",
        owner_org_id=doca_central.id,
    )
    session.add(rule_pack_core)
    session.flush()

    rule_pack_content = {
        "pack_id": "lmpc-core",
        "version": "2026.0",
        "effective_from": "2026-01-01T00:00:00Z",
        "jurisdiction": "India",
        "rules": [
            {
                "rule_id": "LMPC-6-1-E-MRP-001",
                "clause": "Rule 6(1)(e)",
                "description": "Retail sale price must be expressed as MRP/Maximum Retail Price inclusive of all taxes with currency symbol and 2 decimals.",
                "applies_to": {"channel": ["package", "ecommerce"], "unless": ["bidi", "apm_lpg"]},
                "extraction_pattern": r"(?i)(maximum\s+retail\s+price|max\.?\s*retail\s*price|mrp)\s*[:\.\s]*([₹Rs\.\sINR]+)?\s*([0-9]+(?:\.[0-9]{2})?)",
                "validation_logic": "exists(mrp) AND currency_symbol(mrp) AND decimal_places(mrp, 2)",
                "severity": "Major",
                "penalty_reference": "Legal Metrology Act, 2009, Section 36(1)",
                "source_url": "https://consumeraffairs.nic.in/acts-and-rules/legal-metrology/packaged-commodities-rules-2011",
            },
            {
                "rule_id": "LMPC-6-1-C-NETQ-002",
                "clause": "Rule 6(1)(c)",
                "description": "Net quantity must be declared in permitted standard units (g, kg, ml, l, m, cm, pieces) without non-standard symbols.",
                "applies_to": {"channel": ["package", "ecommerce"]},
                "extraction_pattern": r"(?i)(net\s*(?:qty|quantity|wt|weight|vol(?:ume)?)?)\s*[:\.\s]*([0-9]+(?:\.[0-9]+)?)\s*(g|kg|gm|gms|ml|l|ltr|litres|m|cm|N|units|pieces)",
                "validation_logic": "exists(net_quantity) AND unit(net_quantity) IN ['g','kg','ml','l','m','cm','N']",
                "severity": "Critical",
                "penalty_reference": "Legal Metrology Act, 2009, Section 36(1)",
                "source_url": "https://consumeraffairs.nic.in/acts-and-rules/legal-metrology/packaged-commodities-rules-2011",
            },
            {
                "rule_id": "LMPC-6-1-D-DATE-003",
                "clause": "Rule 6(1)(d)",
                "description": "Month and year of manufacture, pre-packing or import are mandatory on physical package; exempted for e-commerce listings per Rule 6(10).",
                "applies_to": {"channel": ["package"], "exempt_categories": ["bidi", "incense_sticks"]},
                "extraction_pattern": r"(?i)(mfg|manufactured|packed|pre[- ]?packed|imported)\s*(?:date|on|pkd|mfd)?\s*[:\.\s]*([0-9]{1,2}[\/\-\.][0-9]{2,4}|[A-Za-z]{3,9}\s*[0-9]{2,4})",
                "validation_logic": "exists(month_year) AND valid_month_year(month_year)",
                "severity": "Major",
                "penalty_reference": "Legal Metrology Act, 2009, Section 36(1)",
                "source_url": "https://consumeraffairs.nic.in/acts-and-rules/legal-metrology/packaged-commodities-rules-2011",
            },
            {
                "rule_id": "LMPC-6-2-CARE-004",
                "clause": "Rule 6(2)",
                "description": "Consumer care declaration requires contact name/designation, physical address, email, and phone number.",
                "applies_to": {"channel": ["package", "ecommerce"]},
                "extraction_pattern": {
                    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                    "phone": r"(?:(?:\+91|0)?[ -]?)?[6-9]\d{9}|1800[- ]?\d{3}[- ]?\d{3,4}",
                },
                "validation_logic": "exists(consumer_care.name) AND exists(consumer_care.address) AND exists(consumer_care.email) AND exists(consumer_care.phone)",
                "severity": "Major",
                "penalty_reference": "Legal Metrology Act, 2009, Section 36(1)",
                "source_url": "https://consumeraffairs.nic.in/acts-and-rules/legal-metrology/packaged-commodities-rules-2011",
            },
            {
                "rule_id": "LMPC-6-1-A-ADDRESS-005",
                "clause": "Rule 6(1)(a)",
                "description": "Name and complete postal address of manufacturer, packer, or importer must be clearly declared on the PDP.",
                "applies_to": {"channel": ["package", "ecommerce"]},
                "extraction_pattern": r"(?i)(manufactured|packed|imported|marketed)\s+by\s*[:\.\s]*([^\n\r]+)",
                "validation_logic": "exists(responsible_entity.name) AND exists(responsible_entity.address)",
                "severity": "Critical",
                "penalty_reference": "Legal Metrology Act, 2009, Section 36(1)",
                "source_url": "https://consumeraffairs.nic.in/acts-and-rules/legal-metrology/packaged-commodities-rules-2011",
            },
            {
                "rule_id": "LMPC-7-NUMERAL-HEIGHT-006",
                "clause": "Rule 7(2)(i), Table I",
                "description": "Net quantity numeral height in millimetres must comply with Table I: <=200g -> 1mm; >200-500g -> 2mm; >500g -> 4mm (normal font).",
                "applies_to": {"channel": ["package"], "quantity_dimension": ["weight", "volume"]},
                "extraction_pattern": "calibrated_glyph_height_mm(extracted.net_quantity)",
                "validation_logic": "requires(calibration.confidence >= 0.90) AND check_table_1_height(quantity, height_mm)",
                "severity": "Major",
                "penalty_reference": "Legal Metrology Act, 2009, Section 36(1)",
                "source_url": "https://consumeraffairs.nic.in/acts-and-rules/legal-metrology/packaged-commodities-rules-2011",
            },
            {
                "rule_id": "LMPC-7-QUIET-ZONE-007",
                "clause": "Rule 7, Clearance Quiet Zone",
                "description": "Net quantity declaration requires 1x numeral height blank clearance above/below and 2x numeral height left/right.",
                "applies_to": {"channel": ["package"]},
                "validation_logic": "check_clearance(net_quantity_box, surrounding_boxes, h_top=1.0, h_bottom=1.0, w_left=2.0, w_right=2.0)",
                "severity": "Minor",
                "penalty_reference": "Legal Metrology Act, 2009, Section 36(1)",
                "source_url": "https://consumeraffairs.nic.in/acts-and-rules/legal-metrology/packaged-commodities-rules-2011",
            },
        ],
        "tables": {
            "table_1_weight_volume": [
                {"max_g_ml": 200, "min_height_normal_mm": 1.0, "min_height_formed_mm": 2.0},
                {"max_g_ml": 500, "min_height_normal_mm": 2.0, "min_height_formed_mm": 4.0},
                {"max_g_ml": None, "min_height_normal_mm": 4.0, "min_height_formed_mm": 6.0},
            ],
            "table_2_pdp_area": [
                {"max_area_cm2": 100, "min_height_normal_mm": 1.0, "min_height_formed_mm": 2.0},
                {"max_area_cm2": 500, "min_height_normal_mm": 2.0, "min_height_formed_mm": 4.0},
                {"max_area_cm2": 2500, "min_height_normal_mm": 4.0, "min_height_formed_mm": 6.0},
                {"max_area_cm2": None, "min_height_normal_mm": 6.0, "min_height_formed_mm": 6.0},
            ],
        },
        "severity_deductions": {
            "Critical": {"deduction": 25, "cap": 60},
            "Major": {"deduction": 12, "cap": 36},
            "Minor": {"deduction": 4, "cap": 12},
            "Review required": {"deduction": 0, "blocks_fully_verified": True},
        },
    }

    rule_pack_canonical = canonical_json_dumps(rule_pack_content)
    rule_pack_sha256 = hashlib.sha256(rule_pack_canonical.encode("utf-8")).hexdigest()

    rule_version_2026 = RuleVersion(
        id=uuid.UUID("d1111111-1111-1111-1111-111111111111"),
        rule_pack_id=rule_pack_core.id,
        version="2026.0",
        effective_from=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        content_jsonb=rule_pack_content,
        sha256=rule_pack_sha256,
        approved_by=user_rule_admin.id,
        approved_at=datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        status="immutable",
    )
    session.add(rule_version_2026)
    session.flush()

    # 8. Model Versions
    model_paddle = ModelVersion(
        id=uuid.UUID("e1111111-1111-1111-1111-111111111111"),
        name="PaddleOCR-PP-OCRv5-Multilingual",
        version="5.1.0",
        artifact_uri="s3://labelsetu-models/paddleocr/ppocrv5_en_hi_v5.1.onnx",
        metrics_jsonb={"precision": 0.962, "recall": 0.928, "hindi_recall": 0.884},
        approved_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )
    model_yolo = ModelVersion(
        id=uuid.UUID("e2222222-2222-2222-2222-222222222222"),
        name="YOLOv8-PDP-Seg",
        version="8.2.1",
        artifact_uri="s3://labelsetu-models/yolo/pdp_segmenter_v8.2.onnx",
        metrics_jsonb={"iou_pdp": 0.895, "contour_accuracy": 0.941},
        approved_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )
    session.add_all([model_paddle, model_yolo])
    session.flush()

    # 9. Inspections & Product Images & Violations
    
    # Case 1: Fully Compliant Wheat Atta (Package Channel)
    insp_compliant = Inspection(
        id=uuid.UUID("f1111111-1111-1111-1111-111111111111"),
        organisation_id=delhi_dept.id,
        product_id=prod_atta.id,
        channel="package",
        status="completed",
        rule_version_id=rule_version_2026.id,
        score=100.0,
        score_status="verified",
        latitude=28.6139,
        longitude=77.2090,
        district="New Delhi",
        state_code="DL",
        officer_notes="Routine supermarket inspection at Connaught Place. All Rule 6 and Rule 7 declarations conforming.",
        captured_at=datetime(2026, 2, 10, 11, 30, 0, tzinfo=timezone.utc),
        created_by=user_officer.id,
    )
    session.add(insp_compliant)
    session.flush()

    img_compliant = ProductImage(
        id=uuid.UUID("f1111111-aaaa-1111-1111-111111111111"),
        inspection_id=insp_compliant.id,
        object_key="inspections/f1111111-1111-1111-1111-111111111111/originals/aashirvaad_5kg_pdp.jpg",
        sha256="7a8f9c1b3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f2a",
        captured_at=datetime(2026, 2, 10, 11, 30, 0, tzinfo=timezone.utc),
        quality_jsonb={"blur_score": 320.5, "glare_ratio": 0.01, "resolution_ok": True, "needs_recapture": False},
        transform_jsonb={"homography_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
        calibration_jsonb={"mode": "aruco_50mm", "px_per_mm": 18.5, "confidence": 0.98, "residual_error": 0.04},
        status="valid",
    )
    session.add(img_compliant)
    session.flush()

    # Extracted fields for compliant pack
    field_mrp_1 = ExtractedField(
        id=uuid.uuid4(),
        inspection_id=insp_compliant.id,
        image_id=img_compliant.id,
        field_type="mrp",
        raw_text="MRP ₹ 245.00 (inclusive of all taxes)",
        normalized_jsonb={"amount": 245.00, "currency": "INR", "tax_inclusive": True},
        bbox_jsonb={"x": 0.12, "y": 0.75, "w": 0.35, "h": 0.06},
        polygon_jsonb={"vertices": [[120, 750], [470, 750], [470, 810], [120, 810]]},
        confidence=0.98,
        language="eng",
        model_version="PaddleOCR-PP-OCRv5-Multilingual",
        model_version_id=model_paddle.id,
        review_status="confirmed",
    )
    field_netq_1 = ExtractedField(
        id=uuid.uuid4(),
        inspection_id=insp_compliant.id,
        image_id=img_compliant.id,
        field_type="net_quantity",
        raw_text="Net Qty: 5 kg",
        normalized_jsonb={"value": 5.0, "unit": "kg", "height_mm": 5.2},
        bbox_jsonb={"x": 0.12, "y": 0.65, "w": 0.25, "h": 0.08},
        polygon_jsonb={"vertices": [[120, 650], [370, 650], [370, 730], [120, 730]]},
        confidence=0.99,
        language="eng",
        model_version="PaddleOCR-PP-OCRv5-Multilingual",
        model_version_id=model_paddle.id,
        review_status="confirmed",
    )
    session.add_all([field_mrp_1, field_netq_1])

    # Case 2: Deliberate Non-Compliant 500g Pack (Undersized Numeral & MRP Currency Missing)
    insp_noncompliant = Inspection(
        id=uuid.UUID("f2222222-2222-2222-2222-222222222222"),
        organisation_id=delhi_dept.id,
        product_id=prod_oil.id,
        channel="package",
        status="review_required",
        rule_version_id=rule_version_2026.id,
        score=64.0,  # 100 - 24 (two Major violations: Rule 7 height & Rule 6(1)(e) MRP) - 12
        score_status="provisional",
        latitude=28.6304,
        longitude=77.2177,
        district="Central Delhi",
        state_code="DL",
        officer_notes="Tested with 50mm ArUco calibration card. Measured 500g numeral is 3.1mm vs required 4.0mm.",
        captured_at=datetime(2026, 2, 12, 14, 15, 0, tzinfo=timezone.utc),
        created_by=user_officer.id,
    )
    session.add(insp_noncompliant)
    session.flush()

    img_noncompliant = ProductImage(
        id=uuid.UUID("f2222222-bbbb-2222-2222-222222222222"),
        inspection_id=insp_noncompliant.id,
        object_key="inspections/f2222222-2222-2222-2222-222222222222/originals/fortune_500g_test_pack.jpg",
        sha256="9b2e4f6a8c0d1e3f5a7b9c1d3e5f7a9b1c3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f",
        captured_at=datetime(2026, 2, 12, 14, 15, 0, tzinfo=timezone.utc),
        quality_jsonb={"blur_score": 280.0, "glare_ratio": 0.02, "resolution_ok": True, "needs_recapture": False},
        transform_jsonb={"homography_matrix": [[0.98, 0.02, 10.0], [-0.01, 0.99, 5.0], [0.0, 0.0, 1.0]]},
        calibration_jsonb={"mode": "aruco_50mm", "px_per_mm": 16.2, "confidence": 0.95, "residual_error": 0.08},
        status="valid",
    )
    session.add(img_noncompliant)
    session.flush()

    field_netq_bad = ExtractedField(
        id=uuid.UUID("f2222222-cccc-1111-1111-111111111111"),
        inspection_id=insp_noncompliant.id,
        image_id=img_noncompliant.id,
        field_type="net_quantity",
        raw_text="Net Qty: 500 g",
        normalized_jsonb={"value": 500, "unit": "g", "measured_height_mm": 3.10, "required_min_mm": 4.0},
        bbox_jsonb={"x": 0.15, "y": 0.70, "w": 0.20, "h": 0.04},
        polygon_jsonb={"vertices": [[150, 700], [350, 700], [350, 740], [150, 740]]},
        confidence=0.96,
        language="eng",
        model_version="PaddleOCR-PP-OCRv5-Multilingual",
        model_version_id=model_paddle.id,
        review_status="unreviewed",
    )
    session.add(field_netq_bad)

    # Violations for Case 2
    viol_height = Violation(
        id=uuid.uuid4(),
        inspection_id=insp_noncompliant.id,
        rule_version_id=rule_version_2026.id,
        rule_id="LMPC-7-NUMERAL-HEIGHT-006",
        clause="Rule 7(2)(i), Table I",
        status="detected",
        severity="Major",
        message="Net-quantity numeral height of 3.10 mm is below the mandatory 4.00 mm threshold for 500 g packages.",
        evidence_jsonb={
            "measured_height_mm": 3.10,
            "required_height_mm": 4.00,
            "scale_px_per_mm": 16.2,
            "crop_object_key": "inspections/f2222222-2222-2222-2222-222222222222/crops/net_quantity_numeral_crop.jpg",
            "crop_sha256": "4a7b9c1d3e5f7a9b1c3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f5a7b9c1d3e5f7a9b",
            "rule_version": "2026.0",
        },
        confidence=0.95,
        officer_disposition=None,
    )
    viol_mrp = Violation(
        id=uuid.uuid4(),
        inspection_id=insp_noncompliant.id,
        rule_version_id=rule_version_2026.id,
        rule_id="LMPC-6-1-E-MRP-001",
        clause="Rule 6(1)(e)",
        status="detected",
        severity="Major",
        message="MRP declaration '120.00' is missing mandatory Indian currency symbol (₹ or Rs.).",
        evidence_jsonb={
            "raw_text": "MRP 120.00",
            "missing_component": "currency_symbol",
            "crop_object_key": "inspections/f2222222-2222-2222-2222-222222222222/crops/mrp_defect_crop.jpg",
            "rule_version": "2026.0",
        },
        confidence=0.94,
        officer_disposition=None,
    )
    session.add_all([viol_height, viol_mrp])

    # Case 3: E-Commerce Listing Inspection (Blinkit - Rule 6(10))
    insp_ecom = Inspection(
        id=uuid.UUID("f3333333-3333-3333-3333-333333333333"),
        organisation_id=blinkit_platform.id,
        product_id=prod_dal.id,
        channel="ecommerce",
        status="completed",
        rule_version_id=rule_version_2026.id,
        score=100.0,
        score_status="verified",
        latitude=28.5355,
        longitude=77.3910,
        district="South Delhi",
        state_code="DL",
        officer_notes="Rule 6(10) online check. Month/year correctly exempted online. All required digital declarations present.",
        captured_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=timezone.utc),
        created_by=user_officer.id,
    )
    session.add(insp_ecom)
    session.flush()

    ecom_listing = EcommerceListing(
        id=uuid.UUID("e3333333-1111-1111-1111-111111111111"),
        platform="Blinkit",
        external_listing_id="BLK-TATA-DAL-1KG-994",
        url="https://blinkit.com/prn/tata-sampann-unpolished-toor-dal/prid/994123",
        product_id=prod_dal.id,
        snapshot_key="listings/blinkit/BLK-TATA-DAL-1KG-994_20260214.html",
        content_hash="3c5a7b9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f5a7b",
        captured_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=timezone.utc),
        seller_name="SuperFast Retail Delhi Hub",
        availability="in_stock",
        raw_jsonb={
            "title": "Tata Sampann Unpolished Toor Dal 1kg",
            "price": "₹178.00",
            "net_quantity": "1 kg",
            "fssai_license": "10014011002233",
            "consumer_care": "care@tataconsumer.com / 1800-108-4488",
            "manufacturer": "Tata Consumer Products Ltd",
        },
    )
    session.add(ecom_listing)

    # Case 4: Glare / Recapture Case (Reflective Foil Package)
    insp_glare = Inspection(
        id=uuid.UUID("f4444444-4444-4444-4444-444444444444"),
        organisation_id=delhi_dept.id,
        product_id=prod_oil.id,
        channel="package",
        status="needs_recapture",
        rule_version_id=rule_version_2026.id,
        score=None,
        latitude=28.6200,
        longitude=77.2100,
        district="Central Delhi",
        state_code="DL",
        officer_notes="Excessive overhead light glare over the Net Quantity and MRP declaration areas. Recapture required with diffuse lighting.",
        captured_at=datetime(2026, 2, 14, 15, 0, 0, tzinfo=timezone.utc),
        created_by=user_officer.id,
    )
    session.add(insp_glare)
    session.flush()

    img_glare = ProductImage(
        id=uuid.UUID("f4444444-aaaa-4444-4444-444444444444"),
        inspection_id=insp_glare.id,
        object_key="inspections/f4444444-4444-4444-4444-444444444444/originals/glare_defect_oil.jpg",
        sha256="4b8e0d1f3a5c7b9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f2a4c6b8e0d1f3a5c7b9d",
        mime_type="image/jpeg",
        size_bytes=3120000,
        width_px=3024,
        height_px=4032,
        captured_at=datetime(2026, 2, 14, 15, 0, 0, tzinfo=timezone.utc),
        quality_jsonb={"blur_score": 110.0, "glare_ratio": 0.42, "resolution_ok": True, "needs_recapture": True},
        transform_jsonb={},
        calibration_jsonb={"mode": "aruco_50mm", "px_per_mm": 15.0, "confidence": 0.82},
        status="needs_recapture",
    )
    session.add(img_glare)

    rev_glare = ReviewAction(
        id=uuid.uuid4(),
        inspection_id=insp_glare.id,
        field_id=None,
        violation_id=None,
        reviewer_id=user_reviewer.id,
        action="request_recapture",
        original_value_jsonb=None,
        corrected_value_jsonb=None,
        reason="Heavy packaging glare prevents reliable OCR parsing. Request officer to re-photograph using diffuse lighting.",
        created_at=datetime(2026, 2, 14, 15, 10, 0, tzinfo=timezone.utc),
    )
    session.add(rev_glare)

    # Case 5: Hindi / Mixed-Language Multi-Lingual Atta Pack (Rule 6 Multi-Lingual Compliance)
    insp_hindi = Inspection(
        id=uuid.UUID("f5555555-5555-5555-5555-555555555555"),
        organisation_id=delhi_dept.id,
        product_id=prod_atta.id,
        channel="package",
        status="completed",
        rule_version_id=rule_version_2026.id,
        score=100.0,
        score_status="verified",
        latitude=28.6500,
        longitude=77.2300,
        district="North Delhi",
        state_code="DL",
        officer_notes="Dual language Hindi/English front declaration inspected. Full compliance with Rule 6.",
        captured_at=datetime(2026, 2, 15, 11, 0, 0, tzinfo=timezone.utc),
        created_by=user_officer.id,
    )
    session.add(insp_hindi)
    session.flush()

    img_hindi = ProductImage(
        id=uuid.UUID("f5555555-aaaa-5555-5555-555555555555"),
        inspection_id=insp_hindi.id,
        object_key="inspections/f5555555-5555-5555-5555-555555555555/originals/aashirvaad_hindi_5kg.jpg",
        sha256="5c7b9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f5a7b9c",
        mime_type="image/jpeg",
        size_bytes=3450000,
        width_px=3024,
        height_px=4032,
        captured_at=datetime(2026, 2, 15, 11, 0, 0, tzinfo=timezone.utc),
        quality_jsonb={"blur_score": 340.0, "glare_ratio": 0.008, "resolution_ok": True, "needs_recapture": False},
        transform_jsonb={"homography_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
        calibration_jsonb={"mode": "aruco_50mm", "px_per_mm": 18.0, "confidence": 0.98},
        status="valid",
    )
    session.add(img_hindi)

    field_hindi_netq = ExtractedField(
        id=uuid.UUID("f5555555-cccc-5555-5555-555555555555"),
        inspection_id=insp_hindi.id,
        image_id=img_hindi.id,
        field_type="net_quantity",
        raw_text="शुद्ध चक्की आटा ५ कि.ग्रा. / Net Quantity: 5 kg",
        normalized_jsonb={"value": 5, "unit": "kg", "measured_height_mm": 6.2, "required_min_mm": 4.0},
        bbox_jsonb={"x": 0.20, "y": 0.75, "w": 0.30, "h": 0.06},
        polygon_jsonb={"vertices": [[200, 750], [500, 750], [500, 810], [200, 810]]},
        confidence=0.97,
        language="hin",
        model_version="PaddleOCR-PP-OCRv5-Multilingual",
        model_version_id=model_paddle.id,
        review_status="confirmed",
    )
    session.add(field_hindi_netq)

    # Case 6: Imported Commodity (Swiss Chocolatier - Country of Origin & Importer Check)
    insp_imported = Inspection(
        id=uuid.UUID("f6666666-6666-6666-6666-666666666666"),
        organisation_id=delhi_dept.id,
        product_id=prod_choc.id,
        channel="package",
        status="completed",
        rule_version_id=rule_version_2026.id,
        score=100.0,
        score_status="verified",
        latitude=28.5500,
        longitude=77.2000,
        district="South Delhi",
        state_code="DL",
        officer_notes="Imported dark chocolate bar. Rule 6(1) Country of Origin ('Switzerland') and Importer address properly stickered.",
        captured_at=datetime(2026, 2, 15, 12, 30, 0, tzinfo=timezone.utc),
        created_by=user_officer.id,
    )
    session.add(insp_imported)
    session.flush()

    img_imported = ProductImage(
        id=uuid.UUID("f6666666-aaaa-6666-6666-666666666666"),
        inspection_id=insp_imported.id,
        object_key="inspections/f6666666-6666-6666-6666-666666666666/originals/swiss_choc_back.jpg",
        sha256="6d3e5f7a9b1c3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f5a7b9c1d3e5f7a9b1c3d5e",
        mime_type="image/jpeg",
        size_bytes=2890000,
        width_px=3024,
        height_px=4032,
        captured_at=datetime(2026, 2, 15, 12, 30, 0, tzinfo=timezone.utc),
        quality_jsonb={"blur_score": 305.0, "glare_ratio": 0.012, "resolution_ok": True, "needs_recapture": False},
        transform_jsonb={"homography_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
        calibration_jsonb={"mode": "aruco_50mm", "px_per_mm": 17.5, "confidence": 0.96},
        status="valid",
    )
    session.add(img_imported)

    field_imported_origin = ExtractedField(
        id=uuid.UUID("f6666666-cccc-6666-6666-666666666666"),
        inspection_id=insp_imported.id,
        image_id=img_imported.id,
        field_type="origin",
        raw_text="Country of Origin: Switzerland. Imported & Marketed by: Global Gourmet Imports Pvt Ltd, Mumbai-400001.",
        normalized_jsonb={"country_of_origin": "Switzerland", "importer": "Global Gourmet Imports Pvt Ltd", "city": "Mumbai", "pincode": "400001"},
        bbox_jsonb={"x": 0.10, "y": 0.30, "w": 0.80, "h": 0.15},
        polygon_jsonb={"vertices": [[100, 300], [900, 300], [900, 450], [100, 450]]},
        confidence=0.98,
        language="eng",
        model_version="PaddleOCR-PP-OCRv5-Multilingual",
        model_version_id=model_paddle.id,
        review_status="confirmed",
    )
    session.add(field_imported_origin)

    # 9B. Batch Inspection Session, Batch Image, and Product Detections (Shelf Inspection)
    batch_session = InspectionSession(
        id=uuid.UUID("71111111-1111-1111-1111-111111111111"),
        organisation_id=delhi_dept.id,
        client_session_id="MOB-SESS-20260215-001",
        created_by=user_officer.id,
        channel="batch",
        status="complete",
        lat=28.6139,
        lon=77.2090,
        gps_accuracy_m=4.2,
        captured_at=datetime(2026, 2, 15, 14, 0, 0, tzinfo=timezone.utc),
        idempotency_key="DELHI_OFFICER_BATCH_SESS_20260215_001",
    )
    session.add(batch_session)
    session.flush()

    batch_img = BatchImage(
        id=uuid.UUID("72222222-1111-1111-1111-111111111111"),
        session_id=batch_session.id,
        object_key="sessions/71111111-1111-1111-1111-111111111111/batches/shelf_scan_01.jpg",
        sha256="5a7b9c1d3e5f7a9b1c3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f5a7b9c1d3e5f7a9b",
        mime_type="image/jpeg",
        size_bytes=4250000,
        width_px=3840,
        height_px=2160,
        captured_at=datetime(2026, 2, 15, 14, 0, 0, tzinfo=timezone.utc),
        lat=28.6139,
        lon=77.2090,
        gps_accuracy_m=4.2,
        quality_jsonb={"blur_score": 310.0, "glare_ratio": 0.015, "lighting_ok": True},
        transform_jsonb={"shelf_rectification_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
        calibration_jsonb={"mode": "aruco_50mm", "px_per_mm": 12.5, "confidence": 0.94},
        status="valid",
    )
    session.add(batch_img)
    session.flush()

    det1 = ProductDetection(
        id=uuid.UUID("73333333-1111-1111-1111-111111111111"),
        batch_image_id=batch_img.id,
        inspection_id=None,
        detection_index=0,
        bbox_jsonb={"x": 0.10, "y": 0.20, "w": 0.25, "h": 0.60},
        polygon_jsonb={"vertices": [[100, 200], [350, 200], [350, 800], [100, 800]]},
        crop_object_key="sessions/71111111-1111-1111-1111-111111111111/crops/det_0.jpg",
        detection_confidence=0.98,
        status="detected",
    )
    det2 = ProductDetection(
        id=uuid.UUID("74444444-1111-1111-1111-111111111111"),
        batch_image_id=batch_img.id,
        inspection_id=None,
        detection_index=1,
        bbox_jsonb={"x": 0.40, "y": 0.20, "w": 0.25, "h": 0.60},
        polygon_jsonb={"vertices": [[400, 200], [650, 200], [650, 800], [400, 800]]},
        crop_object_key="sessions/71111111-1111-1111-1111-111111111111/crops/det_1.jpg",
        detection_confidence=0.96,
        status="detected",
    )
    session.add_all([det1, det2])
    session.flush()

    # 10. Reports
    report_compliant = Report(
        id=uuid.UUID("91111111-1111-1111-1111-111111111111"),
        inspection_id=insp_compliant.id,
        type="PDF",
        version="1.0",
        object_key="reports/f1111111-1111-1111-1111-111111111111/statutory_report_v1.0.pdf",
        sha256="8b1c3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f2a4c6b",
        generated_by=user_officer.id,
        approved_by=user_officer.id,
        generated_at=datetime(2026, 2, 10, 11, 45, 0, tzinfo=timezone.utc),
    )
    session.add(report_compliant)

    # 11. Review Action
    rev_action = ReviewAction(
        id=uuid.uuid4(),
        inspection_id=insp_compliant.id,
        field_id=field_netq_1.id,
        violation_id=None,
        reviewer_id=user_reviewer.id,
        action="accept",
        corrected_value_jsonb={"verified_value": 5.0, "unit": "kg"},
        reason="Field verified against clear calibration card reference.",
        created_at=datetime(2026, 2, 10, 11, 40, 0, tzinfo=timezone.utc),
    )
    session.add(rev_action)
    session.flush()

    # 12. Tamper-Evident Hash-Chained Audit Trail
    audit_t0 = datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc)
    
    # Event 1: Super admin creates organisation
    ev1 = AuditService.log_event(
        session=session,
        action="CREATE",
        entity_type="organisation",
        entity_id=delhi_dept.id,
        actor_id=user_super.id,
        organisation_id=doca_central.id,
        after_state={"name": delhi_dept.name, "type": delhi_dept.type, "state": "DL"},
        event_time=audit_t0,
    )
    
    # Event 2: Rule Admin releases rule version 2026.0
    ev2 = AuditService.log_event(
        session=session,
        action="RELEASE_RULE_VERSION",
        entity_type="rule_version",
        entity_id=rule_version_2026.id,
        actor_id=user_rule_admin.id,
        organisation_id=doca_central.id,
        after_state={"version": "2026.0", "status": "immutable", "sha256": rule_pack_sha256},
        event_time=audit_t0 + timedelta(minutes=15),
    )

    # Event 3: Officer captures compliant inspection
    ev3 = AuditService.log_event(
        session=session,
        action="CREATE_INSPECTION",
        entity_type="inspection",
        entity_id=insp_compliant.id,
        actor_id=user_officer.id,
        organisation_id=delhi_dept.id,
        after_state={"channel": "package", "product": str(prod_atta.id), "status": "draft"},
        event_time=audit_t0 + timedelta(hours=1),
    )

    # Event 4: Reviewer approves fields
    ev4 = AuditService.log_event(
        session=session,
        action="REVIEW_ACCEPT",
        entity_type="extracted_field",
        entity_id=field_netq_1.id,
        actor_id=user_reviewer.id,
        organisation_id=delhi_dept.id,
        after_state={"field": "net_quantity", "decision": "accept"},
        event_time=audit_t0 + timedelta(hours=1, minutes=40),
    )

    # Event 5: Officer approves statutory report
    ev5 = AuditService.log_event(
        session=session,
        action="APPROVE_REPORT",
        entity_type="report",
        entity_id=report_compliant.id,
        actor_id=user_officer.id,
        organisation_id=delhi_dept.id,
        after_state={"report_type": "PDF", "sha256": report_compliant.sha256},
        event_time=audit_t0 + timedelta(hours=1, minutes=45),
    )

    # 13. Offenders Intelligence Record
    offender_rec = Offender(
        id=uuid.uuid4(),
        brand_id=brand_fortune.id,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        inspection_count=18,
        confirmed_count=4,
        severity_score=72.5,
        last_seen_at=datetime(2026, 2, 12, 14, 15, 0, tzinfo=timezone.utc),
    )
    session.add(offender_rec)

    # 14. Sync Queue (Offline Mobile Field App Sync)
    sync_item = SyncQueue(
        id=uuid.uuid4(),
        device_id="DEV-ANDROID-TAB-901",
        local_event_id="LOCAL-EV-20260212-004",
        entity_type="inspection_capture",
        payload_jsonb={
            "capture_timestamp": "2026-02-12T14:15:00Z",
            "gps_accuracy": 3.5,
            "calibration_mode": "aruco_50mm",
            "image_sha256": "9b2e4f6a8c0d1e3f5a7b9c1d3e5f7a9b1c3d5e7f2a4c6b8e0d1f3a5c7b9d1e3f",
        },
        status="synced",
        attempts=1,
        idempotency_key="DEV-ANDROID-TAB-901_LOCAL-EV-20260212-004",
        received_at=datetime(2026, 2, 12, 14, 20, 0, tzinfo=timezone.utc),
        processed_at=datetime(2026, 2, 12, 14, 20, 0, tzinfo=timezone.utc),
    )
    session.add(sync_item)

    session.commit()
    print("[SUCCESS] LabelSetu Database successfully seeded with full production corpus!")


if __name__ == "__main__":
    with db_session() as session:
        seed_database(session)
