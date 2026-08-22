"""Automated test suite for LabelSetu database architecture and integrity principles."""

import io
import uuid
from datetime import date, datetime, timedelta, timezone
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError
from botocore.exceptions import ClientError

from backend.app.core.security import (
    compute_sha256,
    get_password_hash,
    verify_password,
    canonical_json_dumps,
)
from backend.app.db.base import Base
from backend.app.models.organisation import Organisation
from backend.app.models.role import Role, UserRole
from backend.app.models.user import User
from backend.app.models.catalog import Brand, Product
from backend.app.models.rule import RulePack, RuleVersion
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
from backend.app.services.sync import SyncService
from backend.app.services.intelligence import IntelligenceService
from backend.app.storage.s3 import ObjectStorageService
from backend.app.seeds.seed_data import seed_database


@pytest.fixture(scope="function")
def db_session_fixture():
    """Create a fresh in-memory SQLite database session for isolated testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    SessionClass = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionClass()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


def test_schema_creation_and_all_19_tables(db_session_fixture: Session):
    """Test 1: Verify all 19 tables can be created on a blank database."""
    tables = Base.metadata.tables.keys()
    required_tables = [
        "organisations",
        "roles",
        "users",
        "user_roles",
        "brands",
        "products",
        "rule_packs",
        "rule_versions",
        "model_versions",
        "inspections",
        "product_images",
        "extracted_fields",
        "violations",
        "reports",
        "review_actions",
        "audit_log",
        "offenders",
        "sync_queue",
        "ecommerce_listings",
    ]
    for tbl in required_tables:
        assert tbl in tables, f"Missing table {tbl} in database metadata!"


def test_database_seed_execution(db_session_fixture: Session):
    """Test 2: Verify seed script executes cleanly and populates essential baseline data."""
    seed_database(db_session_fixture)

    org_count = db_session_fixture.execute(select(func.count(Organisation.id))).scalar()
    user_count = db_session_fixture.execute(select(func.count(User.id))).scalar()
    role_count = db_session_fixture.execute(select(func.count(Role.id))).scalar()
    brand_count = db_session_fixture.execute(select(func.count(Brand.id))).scalar()
    product_count = db_session_fixture.execute(select(func.count(Product.id))).scalar()
    rule_version_count = db_session_fixture.execute(select(func.count(RuleVersion.id))).scalar()
    inspection_count = db_session_fixture.execute(select(func.count(Inspection.id))).scalar()

    assert org_count >= 5
    assert user_count >= 5
    assert role_count == 7
    assert brand_count >= 4
    assert product_count >= 4
    assert rule_version_count >= 1
    assert inspection_count >= 3


def test_foreign_key_and_cascade_relationships(db_session_fixture: Session):
    """Test 3: Verify foreign-key relationships and cascade deletes on child entities."""
    org = Organisation(name="Test Cascade Org", type="state", state_code="KA", status="active")
    db_session_fixture.add(org)
    db_session_fixture.flush()

    brand = Brand(canonical_name="Test Brand", manufacturer_org_id=org.id)
    db_session_fixture.add(brand)
    db_session_fixture.flush()

    prod = Product(brand_id=brand.id, generic_name="Test Flour", category="food_staples")
    db_session_fixture.add(prod)
    db_session_fixture.flush()

    rp = RulePack(id="test-pack", name="Test Pack", jurisdiction="India")
    db_session_fixture.add(rp)
    db_session_fixture.flush()

    rv = RuleVersion(
        rule_pack_id=rp.id,
        version="1.0",
        effective_from=datetime.now(timezone.utc),
        content_jsonb={"rules": []},
        sha256="dummy_sha256",
        status="active",
    )
    db_session_fixture.add(rv)
    db_session_fixture.flush()

    insp = Inspection(
        organisation_id=org.id,
        product_id=prod.id,
        channel="package",
        status="draft",
        rule_version_id=rv.id,
    )
    db_session_fixture.add(insp)
    db_session_fixture.flush()

    img = ProductImage(
        inspection_id=insp.id,
        object_key="test/img.jpg",
        sha256="abc" * 21 + "a",
        status="uploaded",
    )
    viol = Violation(
        inspection_id=insp.id,
        rule_version_id=rv.id,
        rule_id="RULE-01",
        status="detected",
        severity="Major",
        message="Test violation",
    )
    field = ExtractedField(
        inspection_id=insp.id,
        field_type="mrp",
        raw_text="MRP Rs 50",
    )
    db_session_fixture.add_all([img, viol, field])
    db_session_fixture.commit()

    # Verify children exist
    assert db_session_fixture.execute(select(func.count(ProductImage.id)).filter_by(inspection_id=insp.id)).scalar() == 1
    assert db_session_fixture.execute(select(func.count(Violation.id)).filter_by(inspection_id=insp.id)).scalar() == 1
    assert db_session_fixture.execute(select(func.count(ExtractedField.id)).filter_by(inspection_id=insp.id)).scalar() == 1

    # Delete inspection -> cascade deletes child image, violation, field
    db_session_fixture.delete(insp)
    db_session_fixture.commit()

    assert db_session_fixture.execute(select(func.count(ProductImage.id)).filter_by(inspection_id=insp.id)).scalar() == 0
    assert db_session_fixture.execute(select(func.count(Violation.id)).filter_by(inspection_id=insp.id)).scalar() == 0
    assert db_session_fixture.execute(select(func.count(ExtractedField.id)).filter_by(inspection_id=insp.id)).scalar() == 0


def test_rule_version_pinning_and_immutability(db_session_fixture: Session):
    """Test 4: Verify that inspections pin exact rule versions and released versions are immutable."""
    seed_database(db_session_fixture)

    inspection = db_session_fixture.execute(select(Inspection)).scalars().first()
    assert inspection.rule_version_id is not None
    assert inspection.rule_version is not None
    assert inspection.rule_version.version == "2026.0"
    assert inspection.rule_version.status == "immutable"
    assert len(inspection.rule_version.content_jsonb["rules"]) >= 6


def test_sha256_evidence_metadata(db_session_fixture: Session):
    """Test 5: Verify SHA-256 hashes on evidence images and reports."""
    seed_database(db_session_fixture)

    images = db_session_fixture.execute(select(ProductImage)).scalars().all()
    reports = db_session_fixture.execute(select(Report)).scalars().all()

    for img in images:
        assert len(img.sha256) == 64
        assert img.object_key.startswith("inspections/")

    for rep in reports:
        assert len(rep.sha256) == 64
        assert rep.object_key.startswith("reports/")


def test_audit_hash_chain_and_tamper_detection(db_session_fixture: Session):
    """Test 6: Verify tamper-evident SHA-256 hash chaining and tamper detection."""
    seed_database(db_session_fixture)

    # 1. Verify un-tampered chain
    is_valid, errors, total = AuditService.verify_chain(db_session_fixture)
    assert is_valid is True
    assert len(errors) == 0
    assert total >= 5

    # 2. Simulate intentional tampering with a past audit record
    first_record = db_session_fixture.execute(
        select(AuditLog).order_by(AuditLog.event_at.asc())
    ).scalars().first()
    
    # Tamper with the state payload
    first_record.after_jsonb = {"tampered": "illegal_state_change"}
    db_session_fixture.commit()

    # 3. Chain verification must immediately fail and catch the tampered record
    is_valid_tampered, errors_tampered, _ = AuditService.verify_chain(db_session_fixture)
    assert is_valid_tampered is False
    assert len(errors_tampered) > 0
    assert any("Tampered payload" in err for err in errors_tampered)


def test_organisation_level_isolation(db_session_fixture: Session):
    """Test 7: Verify multi-tenant organisation isolation."""
    seed_database(db_session_fixture)

    delhi_org = db_session_fixture.execute(select(Organisation).filter_by(state_code="DL", type="state")).scalars().first()
    mh_org = db_session_fixture.execute(select(Organisation).filter_by(state_code="MH", type="state")).scalars().first()

    # Query Delhi inspections
    delhi_inspections = db_session_fixture.execute(
        select(Inspection).filter_by(organisation_id=delhi_org.id)
    ).scalars().all()
    assert len(delhi_inspections) > 0
    assert all(insp.organisation_id == delhi_org.id for insp in delhi_inspections)

    # Query MH inspections (empty initially)
    mh_inspections = db_session_fixture.execute(
        select(Inspection).filter_by(organisation_id=mh_org.id)
    ).scalars().all()
    assert len(mh_inspections) == 0


def test_sync_queue_idempotency(db_session_fixture: Session):
    """Test 8: Verify offline sync queue prevents duplicate ingestion using idempotency_key."""
    sync_key = "DEV-01_EVENT-999"
    
    item1 = SyncQueue(
        device_id="DEV-01",
        local_event_id="EVENT-999",
        entity_type="inspection_capture",
        payload_jsonb={"test": 1},
        status="synced",
        idempotency_key=sync_key,
    )
    db_session_fixture.add(item1)
    db_session_fixture.commit()

    # Attempting to insert duplicate idempotency_key must raise IntegrityError
    item2 = SyncQueue(
        device_id="DEV-01",
        local_event_id="EVENT-999",
        entity_type="inspection_capture",
        payload_jsonb={"test": 2},
        status="pending",
        idempotency_key=sync_key,
    )
    db_session_fixture.add(item2)
    with pytest.raises(IntegrityError):
        db_session_fixture.commit()
    db_session_fixture.rollback()


def test_raw_ocr_preservation_on_correction(db_session_fixture: Session):
    """Test 9: Verify that raw OCR extraction is never overwritten when officer creates a review correction."""
    seed_database(db_session_fixture)

    field = db_session_fixture.execute(select(ExtractedField).filter_by(field_type="net_quantity")).scalars().first()
    original_raw_text = field.raw_text

    reviewer = db_session_fixture.execute(select(User).filter_by(email="reviewer.delhi@gov.in")).scalars().first()
    
    # Reviewer corrects value
    rev_action = ReviewAction(
        inspection_id=field.inspection_id,
        field_id=field.id,
        reviewer_id=reviewer.id,
        action="correct",
        corrected_value_jsonb={"corrected_net_qty": 500, "unit": "g"},
        reason="Officer corrected numeral misread.",
    )
    field.review_status = "corrected"
    db_session_fixture.add(rev_action)
    db_session_fixture.commit()

    # Ensure raw_text remains untouched
    field_reloaded = db_session_fixture.execute(select(ExtractedField).filter_by(id=field.id)).scalars().one()
    assert field_reloaded.raw_text == original_raw_text
    assert field_reloaded.review_status == "corrected"
    assert len(field_reloaded.review_actions) >= 1


def test_declarative_rule_pack_structure_and_coverage(db_session_fixture: Session):
    """Test 10: Verify declarative LMPC rule pack contains all mandatory clauses and calibration tables."""
    seed_database(db_session_fixture)

    rv = db_session_fixture.execute(select(RuleVersion).filter_by(version="2026.0")).scalars().first()
    rules = rv.content_jsonb.get("rules", [])
    rule_ids = [r["rule_id"] for r in rules]

    assert "LMPC-6-1-A-ADDRESS-005" in rule_ids
    assert "LMPC-6-1-C-NETQ-002" in rule_ids
    assert "LMPC-6-1-D-DATE-003" in rule_ids
    assert "LMPC-6-1-E-MRP-001" in rule_ids
    assert "LMPC-6-2-CARE-004" in rule_ids
    assert "LMPC-7-NUMERAL-HEIGHT-006" in rule_ids

    # Check Table I calibration structure
    table_1 = rv.content_jsonb.get("tables", {}).get("table_1_weight_volume", [])
    assert len(table_1) == 3
    assert table_1[0]["max_g_ml"] == 200
    assert table_1[0]["min_height_normal_mm"] == 1.0


def test_multichannel_inspections_and_ecommerce_listings(db_session_fixture: Session):
    """Test 11: Verify multi-channel inspection records across package, ecommerce, and consumer channels."""
    seed_database(db_session_fixture)

    package_insp = db_session_fixture.execute(select(Inspection).filter_by(channel="package")).scalars().all()
    ecom_insp = db_session_fixture.execute(select(Inspection).filter_by(channel="ecommerce")).scalars().all()
    listings = db_session_fixture.execute(select(EcommerceListing)).scalars().all()

    assert len(package_insp) >= 2
    assert len(ecom_insp) >= 1
    assert len(listings) >= 1
    assert listings[0].platform == "Blinkit"


def test_model_version_registry(db_session_fixture: Session):
    """Test 12: Verify model version evaluation registry."""
    seed_database(db_session_fixture)

    models = db_session_fixture.execute(select(ModelVersion)).scalars().all()
    assert len(models) >= 2
    paddle = [m for m in models if "PaddleOCR" in m.name][0]
    assert paddle.metrics_jsonb["precision"] >= 0.95


def test_offenders_intelligence_data(db_session_fixture: Session):
    """Test 13: Verify repeat offender analytics records."""
    seed_database(db_session_fixture)

    offenders = db_session_fixture.execute(select(Offender)).scalars().all()
    assert len(offenders) >= 1
    assert offenders[0].inspection_count > 0
    assert offenders[0].confirmed_count > 0


def test_production_password_hashing_and_verification():
    """Test 14: Verify production bcrypt password hashing and verification."""
    password = "SecureMetrologyPassword2026!"
    hashed = get_password_hash(password)

    assert hashed.startswith("$2b$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False

    # Verify legacy salted SHA-256 fallback compatibility
    legacy_hash = compute_sha256(("DemoPass2026!" + "labelsetu_demo_salt_2026").encode("utf-8"))
    assert verify_password("DemoPass2026!", legacy_hash) is True
    assert verify_password("WrongLegacyPass", legacy_hash) is False


def test_search_vector_trigger_and_fts_query(db_session_fixture: Session):
    """Test 15: Verify search_vector automatic population on INSERT and UPDATE."""
    seed_database(db_session_fixture)

    delhi_org = db_session_fixture.execute(select(Organisation).filter_by(state_code="DL")).scalars().first()
    rv = db_session_fixture.execute(select(RuleVersion).filter_by(version="2026.0")).scalars().first()

    # INSERT: Create new inspection
    new_insp = Inspection(
        organisation_id=delhi_org.id,
        channel="package",
        status="review_required",
        rule_version_id=rv.id,
        district="South East Delhi",
        state_code="DL",
        officer_notes="Suspected counterfeit packaging detected in wholesale market.",
    )
    db_session_fixture.add(new_insp)
    db_session_fixture.commit()

    # Reload from DB and verify search_vector is automatically populated
    reloaded = db_session_fixture.execute(select(Inspection).filter_by(id=new_insp.id)).scalars().one()
    assert reloaded.search_vector is not None
    assert "South East Delhi" in str(reloaded.search_vector) or "Delhi" in str(reloaded.search_vector)
    assert "Suspected" in str(reloaded.search_vector) or "counterfeit" in str(reloaded.search_vector)

    # UPDATE: Modify officer notes / status
    reloaded.officer_notes = "Updated notes: Laboratory chemical calibration completed."
    reloaded.search_vector = None  # Reset to trigger auto-refresh
    db_session_fixture.commit()

    reloaded_updated = db_session_fixture.execute(select(Inspection).filter_by(id=new_insp.id)).scalars().one()
    assert reloaded_updated.search_vector is not None
    assert "Laboratory" in str(reloaded_updated.search_vector) or "calibration" in str(reloaded_updated.search_vector)


def test_object_storage_s3_service_operations():
    """Test 16: Verify MinIO/S3 ObjectStorageService upload, download, head, delete, and SHA-256 integrity."""
    class MockS3Client:
        def __init__(self):
            self.store = {}

        def upload_fileobj(self, Fileobj, Bucket, Key, ExtraArgs=None):
            self.store[(Bucket, Key)] = Fileobj.read()

        def download_fileobj(self, Bucket, Key, Fileobj):
            if (Bucket, Key) not in self.store:
                raise ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "GetObject")
            Fileobj.write(self.store[(Bucket, Key)])

        def head_object(self, Bucket, Key):
            if (Bucket, Key) not in self.store:
                raise ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject")
            return {"ContentLength": len(self.store[(Bucket, Key)]), "Metadata": {"sha256": "dummy"}}

        def delete_object(self, Bucket, Key):
            self.store.pop((Bucket, Key), None)

        def generate_presigned_url(self, ClientMethod, Params, ExpiresIn):
            return f"http://localhost:9000/{Params['Bucket']}/{Params['Key']}?presigned=true"

    mock_client = MockS3Client()
    ObjectStorageService.set_client(mock_client)

    test_content = b"LabelSetu High-Resolution Evidence Photo JPEG Bytes"
    expected_sha256 = compute_sha256(test_content)
    test_key = ObjectStorageService.build_evidence_key(uuid.uuid4(), "originals", "package_pdp.jpg")

    # 1. Test Upload
    uploaded_hash = ObjectStorageService.upload_bytes(
        bucket=ObjectStorageService.BUCKET_EVIDENCE,
        object_key=test_key,
        data=test_content,
        content_type="image/jpeg",
    )
    assert uploaded_hash == expected_sha256
    assert ObjectStorageService.verify_content_sha256(test_content, uploaded_hash) is True

    # 2. Test Head Object
    head = ObjectStorageService.head_object(ObjectStorageService.BUCKET_EVIDENCE, test_key)
    assert head is not None
    assert head["ContentLength"] == len(test_content)

    # 3. Test Download
    downloaded = ObjectStorageService.download_bytes(ObjectStorageService.BUCKET_EVIDENCE, test_key)
    assert downloaded == test_content

    # 4. Test Presigned URLs
    upload_url = ObjectStorageService.get_presigned_upload_url(ObjectStorageService.BUCKET_EVIDENCE, test_key)
    download_url = ObjectStorageService.get_presigned_download_url(ObjectStorageService.BUCKET_EVIDENCE, test_key)
    assert test_key in upload_url
    assert test_key in download_url

    # 5. Test Delete
    deleted = ObjectStorageService.delete_object(ObjectStorageService.BUCKET_EVIDENCE, test_key)
    assert deleted is True
    assert ObjectStorageService.head_object(ObjectStorageService.BUCKET_EVIDENCE, test_key) is None

    # Reset client
    ObjectStorageService.set_client(None)


def test_sync_service_atomic_ingestion_and_idempotency(db_session_fixture: Session):
    """Test 17: Verify SyncService atomic ingestion and idempotency duplicate prevention."""
    seed_database(db_session_fixture)

    delhi_org = db_session_fixture.execute(select(Organisation).filter_by(state_code="DL")).scalars().first()
    rv = db_session_fixture.execute(select(RuleVersion).filter_by(version="2026.0")).scalars().first()
    officer = db_session_fixture.execute(select(User).filter_by(email="officer.delhi@gov.in")).scalars().first()

    test_insp_id = uuid.uuid4()
    test_img_id = uuid.uuid4()
    test_field_id = uuid.uuid4()
    test_viol_id = uuid.uuid4()

    sync_payload = {
        "inspection": {
            "id": str(test_insp_id),
            "organisation_id": str(delhi_org.id),
            "channel": "package",
            "status": "completed",
            "rule_version_id": str(rv.id),
            "score": 90.0,
            "district": "North Delhi",
            "state_code": "DL",
            "created_by": str(officer.id),
        },
        "images": [
            {
                "id": str(test_img_id),
                "object_key": f"inspections/{test_insp_id}/originals/field_capture.jpg",
                "sha256": "5" * 64,
                "status": "valid",
            }
        ],
        "extracted_fields": [
            {
                "id": str(test_field_id),
                "image_id": str(test_img_id),
                "field_type": "mrp",
                "raw_text": "MRP Rs 150.00",
                "normalized_jsonb": {"amount": 150.0, "currency": "INR"},
                "confidence": 0.97,
            }
        ],
        "violations": [
            {
                "id": str(test_viol_id),
                "rule_id": "LMPC-7-QUIET-ZONE-007",
                "clause": "Rule 7 Clearance",
                "severity": "Minor",
                "message": "Quiet zone clearance boundary warning.",
                "confidence": 0.91,
            }
        ],
    }

    # First ingestion attempt
    sync_rec, is_new = SyncService.ingest_offline_event(
        session=db_session_fixture,
        device_id="TAB-OFFICER-007",
        local_event_id="EVT-2026-X100",
        entity_type="inspection_capture",
        payload_jsonb=sync_payload,
        auto_process=True,
    )
    db_session_fixture.commit()

    assert is_new is True
    assert sync_rec.status == "synced"
    assert sync_rec.attempts == 1

    # Verify entities created in database
    created_insp = db_session_fixture.execute(select(Inspection).filter_by(id=test_insp_id)).scalar_one_or_none()
    assert created_insp is not None
    assert created_insp.score == 90.0
    assert len(created_insp.images) == 1
    assert len(created_insp.extracted_fields) == 1
    assert len(created_insp.violations) == 1

    # Duplicate ingestion attempt with identical idempotency key
    sync_rec_dup, is_new_dup = SyncService.ingest_offline_event(
        session=db_session_fixture,
        device_id="TAB-OFFICER-007",
        local_event_id="EVT-2026-X100",
        entity_type="inspection_capture",
        payload_jsonb=sync_payload,
        auto_process=True,
    )
    assert is_new_dup is False
    assert sync_rec_dup.id == sync_rec.id

    # Verify no duplicate inspections or images were created
    total_inspections_with_id = db_session_fixture.execute(
        select(func.count(Inspection.id)).filter_by(id=test_insp_id)
    ).scalar()
    assert total_inspections_with_id == 1


def test_sync_service_failure_handling(db_session_fixture: Session):
    """Test 18: Verify SyncService handles failed transactions safely without corrupting database."""
    invalid_payload = {
        "inspection": {
            # Missing mandatory organisation_id and rule_version_id
            "channel": "package",
        }
    }

    sync_rec, is_new = SyncService.ingest_offline_event(
        session=db_session_fixture,
        device_id="TAB-OFFICER-ERR",
        local_event_id="EVT-INVALID-001",
        entity_type="inspection_capture",
        payload_jsonb=invalid_payload,
        auto_process=True,
    )
    db_session_fixture.commit()

    assert sync_rec.status == "failed"
    assert sync_rec.attempts == 1
    assert sync_rec.error_message is not None
    assert "missing" in sync_rec.error_message.lower()


def test_repeat_offender_intelligence_aggregation(db_session_fixture: Session):
    """Test 19: Verify IntelligenceService repeat offender risk calculation."""
    seed_database(db_session_fixture)

    period_start = date(2026, 1, 1)
    period_end = date(2026, 3, 31)

    offenders = IntelligenceService.aggregate_brand_offenders(
        session=db_session_fixture,
        period_start=period_start,
        period_end=period_end,
    )
    db_session_fixture.commit()

    assert len(offenders) >= 1
    for o in offenders:
        assert o.inspection_count >= 1
        assert o.severity_score >= 0.0
        assert o.last_seen_at is not None

    # Test summary helper
    brand_fortune = db_session_fixture.execute(select(Brand).filter_by(canonical_name="Fortune")).scalars().first()
    summary = IntelligenceService.get_brand_intelligence_summary(db_session_fixture, brand_fortune.id)
    assert summary["canonical_name"] == "Fortune"
    assert summary["total_inspections"] >= 1

    # Test heatmap helper
    heatmap = IntelligenceService.get_district_compliance_heatmap(db_session_fixture)
    assert len(heatmap) >= 1
    assert "district" in heatmap[0]
    assert "total_inspections" in heatmap[0]


def test_alembic_migrations_files_exist():
    """Test 20: Verify Alembic migration files 0001 and 0002 exist and are sequential."""
    import os
    versions_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "alembic", "versions")
    files = os.listdir(versions_dir)
    assert any(f.startswith("0001_") for f in files)
    assert any(f.startswith("0002_") for f in files)
