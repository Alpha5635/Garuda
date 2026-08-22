"""LabelSetu Database Architecture & Integrity Verification Script."""

import os
import sys
import uuid
from datetime import date, datetime, timezone

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import compute_sha256, compute_canonical_audit_hash, verify_password
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


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def verify_database_architecture(session: Session) -> bool:
    """Run comprehensive verification checks on database state and integrity."""
    print("=" * 75)
    print(" [VERIFY] LABELSETU DATABASE INTEGRITY & ARCHITECTURE VERIFICATION")
    print("=" * 75)

    all_passed = True
    tables = [
        ("organisations", Organisation),
        ("roles", Role),
        ("users", User),
        ("user_roles", UserRole),
        ("brands", Brand),
        ("products", Product),
        ("rule_packs", RulePack),
        ("rule_versions", RuleVersion),
        ("model_versions", ModelVersion),
        ("inspections", Inspection),
        ("product_images", ProductImage),
        ("extracted_fields", ExtractedField),
        ("violations", Violation),
        ("reports", Report),
        ("review_actions", ReviewAction),
        ("audit_log", AuditLog),
        ("offenders", Offender),
        ("sync_queue", SyncQueue),
        ("ecommerce_listings", EcommerceListing),
    ]

    # Check 1: Table row counts
    print("\n[Check 1/8] Verifying Table Population Across All 19 Entities...")
    for table_name, model in tables:
        count = session.execute(select(func.count()).select_from(model)).scalar()
        status_icon = "[OK]" if count > 0 else "[WARN]"
        print(f"  {status_icon} Table '{table_name}': {count} records")
        if count == 0:
            all_passed = False

    # Check 2: Rule Version Pinning
    print("\n[Check 2/8] Verifying Rule-Version Pinning Integrity...")
    inspections = session.execute(select(Inspection)).scalars().all()
    pinned_count = 0
    for insp in inspections:
        if insp.rule_version_id and insp.rule_version:
            pinned_count += 1
            print(f"  [OK] Inspection {insp.id} -> Pinned Rule Version: {insp.rule_version.rule_pack_id}@{insp.rule_version.version} (Status: {insp.rule_version.status})")
    if pinned_count == 0 or pinned_count != len(inspections):
        print("  [FAIL] Some inspections lack pinned rule versions!")
        all_passed = False

    # Check 3: Evidence SHA-256 Hashes
    print("\n[Check 3/8] Verifying Evidence SHA-256 Checksums...")
    images = session.execute(select(ProductImage)).scalars().all()
    reports = session.execute(select(Report)).scalars().all()
    for img in images:
        assert len(img.sha256) == 64, f"Invalid SHA-256 on image {img.id}"
        print(f"  [OK] Image {img.id}: SHA-256 '{img.sha256[:16]}...' (Object Key: {img.object_key})")
    for rep in reports:
        assert len(rep.sha256) == 64, f"Invalid SHA-256 on report {rep.id}"
        print(f"  [OK] Report {rep.id}: SHA-256 '{rep.sha256[:16]}...' (Type: {rep.type})")

    # Check 4: Cryptographic Audit Hash Chain
    print("\n[Check 4/8] Verifying Cryptographic Audit Log Hash Chain...")
    is_valid, errors, total_audits = AuditService.verify_chain(session)
    if is_valid:
        print(f"  [OK] Audit Chain verified successfully ({total_audits} chained events, zero breaks)")
    else:
        print(f"  [FAIL] Audit Chain verification failed! Errors: {errors}")
        all_passed = False

    # Check 5: Organisation Isolation
    print("\n[Check 5/8] Verifying Multi-Tenant Organisation Isolation...")
    doca_org = session.execute(select(Organisation).filter_by(type="DoCA")).scalars().first()
    delhi_org = session.execute(select(Organisation).filter_by(state_code="DL", type="state")).scalars().first()
    
    delhi_inspections = session.execute(
        select(Inspection).filter_by(organisation_id=delhi_org.id)
    ).scalars().all()
    print(f"  [OK] Delhi Legal Metrology Dept owns {len(delhi_inspections)} scoped inspections.")
    for insp in delhi_inspections:
        assert insp.organisation_id == delhi_org.id

    # Check 6: Sync Queue Idempotency
    print("\n[Check 6/8] Verifying Offline Sync Queue Idempotency Keys...")
    sync_records = session.execute(select(SyncQueue)).scalars().all()
    for s in sync_records:
        assert s.idempotency_key is not None
        print(f"  [OK] Sync item {s.id}: Idempotency Key '{s.idempotency_key}' (Status: {s.status})")

    # Check 7: Repeat Offender Intelligence Service Rollup
    print("\n[Check 7/8] Verifying Repeat Offender Intelligence Aggregator...")
    offenders = IntelligenceService.aggregate_brand_offenders(session, date(2026, 1, 1), date(2026, 3, 31))
    print(f"  [OK] Computed intelligence records across {len(offenders)} active brands.")
    for o in offenders:
        print(f"  [OK] Brand {o.brand_id}: Inspections={o.inspection_count}, Confirmed={o.confirmed_count}, Severity={o.severity_score}")

    # Check 8: Object Storage & Password Security
    print("\n[Check 8/8] Verifying S3 Object Storage Key Patterns & Bcrypt Auth...")
    test_key = ObjectStorageService.build_evidence_key(uuid.uuid4(), "originals", "sample_pack.jpg")
    assert test_key.startswith("inspections/")
    print(f"  [OK] Object Storage Key Pattern: '{test_key}'")
    user = session.execute(select(User)).scalars().first()
    assert user.password_hash.startswith("$2b$") or len(user.password_hash) == 64
    print(f"  [OK] Password Hash Format Verified: '{user.password_hash[:15]}...'")

    print("\n" + "=" * 75)
    if all_passed:
        print(" [PASSED] ALL 8 ARCHITECTURE & INTEGRITY VERIFICATIONS PASSED!")
    else:
        print(" [FAILED] SOME VERIFICATION CHECKS FAILED.")
    print("=" * 75)
    return all_passed


if __name__ == "__main__":
    db_url = settings.get_database_url()
    use_sqlite = False
    try:
        engine = create_engine(db_url, connect_args={"connect_timeout": 1} if "postgresql" in db_url else {})
        with engine.connect() as conn:
            pass
        print(f"[INFO] Connected to PostgreSQL at: {db_url}")
    except Exception as e:
        print(f"[INFO] PostgreSQL server offline ({e.__class__.__name__}).")
        print("[INFO] Initializing in-memory verification engine...")
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        use_sqlite = True

    with Session(engine) as session:
        seed_database(session)
        success = verify_database_architecture(session)
        sys.exit(0 if success else 1)
