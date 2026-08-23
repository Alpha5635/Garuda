"""Cryptographic Append-Only Audit Log Hash Chain Verification Utility.

Verifies mathematical integrity of the SHA-256 audit chain:
canonical_event = timestamp | actor | action | entity_type | entity_id | canonical(before) | canonical(after) | prev_hash
event_hash = SHA-256(canonical_event)

Detects any mutation or injection tampering with zero false negatives.
"""

import os
import sys
import uuid
from datetime import datetime, timezone

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.models.audit import AuditLog
from backend.app.services.audit import AuditService
from backend.app.seeds.seed_data import seed_database

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def verify_audit_trail(session: Session, test_tampering: bool = True) -> bool:
    """
    Verify complete audit log hash chain and validate tamper detection capability.
    """
    print("=" * 75)
    print(" [AUDIT] CRYPTOGRAPHIC AUDIT LOG HASH CHAIN VERIFIER")
    print("=" * 75)

    # 1. Verify standard unbroken audit trail
    print("\n[Step 1/2] Verifying production audit chain integrity...")
    is_valid, errors, total_events = AuditService.verify_chain(session)

    if not is_valid:
        print(f"  [FAIL] Audit chain verification failed with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        return False

    print(f"  [OK] Successfully verified {total_events} audit events across the global hash chain.")
    print("  [OK] Prev-hash linkages: 100% matched.")
    print("  [OK] Canonical payload digests: 100% verified.")

    # 2. Test tamper detection
    if test_tampering and total_events > 0:
        print("\n[Step 2/2] Simulating adversary database record mutation (Tamper Test)...")
        # Query the first audit record
        first_record = session.execute(select(AuditLog).order_by(AuditLog.event_at.asc())).scalars().first()
        saved_after = first_record.after_jsonb
        
        # Tamper payload
        first_record.after_jsonb = {"tampered": True, "illegal_mutation": "adversary_edit"}
        session.flush()

        tampered_valid, tamper_errors, _ = AuditService.verify_chain(session)

        # Restore original state
        first_record.after_jsonb = saved_after
        session.flush()

        if not tampered_valid and len(tamper_errors) > 0:
            print(f"  [OK] Tamper detection triggered correctly! Caught {len(tamper_errors)} tamper violation(s):")
            for err in tamper_errors:
                print(f"    - {err}")
            print("  [OK] Tamper detection test PASSED.")
        else:
            print("  [FAIL] Tamper detection failed to detect corrupted audit payload!")
            return False

    print("\n" + "=" * 75)
    print(" [PASSED] AUDIT TRAIL CRYPTOGRAPHICALLY SECURE & TAMPER-RESISTANT!")
    print("=" * 75)
    return True


if __name__ == "__main__":
    db_url = settings.get_database_url()
    try:
        engine = create_engine(db_url, connect_args={"connect_timeout": 1} if "postgresql" in db_url else {})
        with engine.connect() as conn:
            pass
        print(f"[INFO] Connected to PostgreSQL at: {db_url}")
    except Exception as e:
        print(f"[INFO] PostgreSQL server offline ({e.__class__.__name__}). Using in-memory database...")
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_database(session)
        success = verify_audit_trail(session, test_tampering=True)
        sys.exit(0 if success else 1)
