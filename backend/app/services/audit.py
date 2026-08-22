"""Tamper-evident audit trail service implementing cryptographic SHA-256 hash chaining."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from backend.app.core.security import compute_canonical_audit_hash
from backend.app.models.audit import AuditLog


class AuditService:
    """Service to create, chain, and verify append-only tamper-evident audit logs."""

    @staticmethod
    def get_latest_hash(session: Session, organisation_id: Optional[uuid.UUID] = None) -> Optional[str]:
        """Fetch the most recent event_hash in the chain."""
        stmt = select(AuditLog.event_hash).order_by(desc(AuditLog.event_at), desc(AuditLog.id)).limit(1)
        if organisation_id:
            stmt = stmt.where(AuditLog.organisation_id == organisation_id)
        result = session.execute(stmt).scalar_one_or_none()
        return result

    @classmethod
    def log_event(
        cls,
        session: Session,
        action: str,
        entity_type: str,
        entity_id: str | uuid.UUID,
        actor_id: Optional[uuid.UUID] = None,
        organisation_id: Optional[uuid.UUID] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        event_time: Optional[datetime] = None,
    ) -> AuditLog:
        """
        Create and append a new hash-chained audit record.
        """
        now = event_time or datetime.now(timezone.utc)
        
        # Link to globally latest event hash
        prev_hash = cls.get_latest_hash(session)
        
        event_hash = compute_canonical_audit_hash(
            timestamp=now,
            actor_id=str(actor_id) if actor_id else None,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            before_jsonb=before_state,
            after_jsonb=after_state,
            prev_hash=prev_hash,
        )

        audit_entry = AuditLog(
            organisation_id=organisation_id,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            before_jsonb=before_state,
            after_jsonb=after_state,
            event_at=now,
            prev_hash=prev_hash,
            event_hash=event_hash,
            request_id=request_id,
        )
        session.add(audit_entry)
        session.flush()
        return audit_entry

    @classmethod
    def verify_chain(
        cls,
        session: Session,
        organisation_id: Optional[uuid.UUID] = None,
    ) -> Tuple[bool, List[str], int]:
        """
        Recompute and verify the entire cryptographic audit chain.
        Returns:
            is_valid (bool): True if unbroken, False if tampered.
            errors (List[str]): List of specific tampering / mismatch errors.
            count (int): Total records verified.
        """
        stmt = select(AuditLog).order_by(AuditLog.event_at.asc(), AuditLog.id.asc())
        if organisation_id:
            stmt = stmt.where(AuditLog.organisation_id == organisation_id)
        
        records = session.execute(stmt).scalars().all()
        errors: List[str] = []
        expected_prev_hash: Optional[str] = None

        for idx, rec in enumerate(records):
            # 1. Check prev_hash link
            if rec.prev_hash != expected_prev_hash:
                errors.append(
                    f"Chain break at record #{idx} (ID: {rec.id}): prev_hash '{rec.prev_hash}' does not match expected '{expected_prev_hash}'"
                )

            # 2. Recompute event_hash
            recomputed_hash = compute_canonical_audit_hash(
                timestamp=rec.event_at,
                actor_id=str(rec.actor_id) if rec.actor_id else None,
                action=rec.action,
                entity_type=rec.entity_type,
                entity_id=str(rec.entity_id),
                before_jsonb=rec.before_jsonb,
                after_jsonb=rec.after_jsonb,
                prev_hash=rec.prev_hash,
            )

            if recomputed_hash != rec.event_hash:
                errors.append(
                    f"Tampered payload at record #{idx} (ID: {rec.id}): stored hash '{rec.event_hash}' != calculated '{recomputed_hash}'"
                )

            expected_prev_hash = rec.event_hash

        is_valid = len(errors) == 0
        return is_valid, errors, len(records)
