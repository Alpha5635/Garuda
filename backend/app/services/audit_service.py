import json
import hashlib
import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditChain
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditVerificationResponse, AuditEventSchema


class AuditService:
    @staticmethod
    def compute_event_hash(previous_hash: str, payload_dict: dict) -> str:
        payload_str = json.dumps(payload_dict, sort_keys=True)
        raw_str = f"{previous_hash}:{payload_str}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    async def log_event(
        self,
        session: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_email: str = "system",
        inspection_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        before_state: dict | None = None,
        after_state: dict | None = None,
        request_id: str | None = None
    ) -> AuditChain:
        repo = AuditRepository(session)
        latest_event = await repo.get_latest_event()
        prev_hash = latest_event.current_hash if latest_event else "GENESIS_HASH_00000000000000000000000000000000000000000000000000000000"

        payload = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "actor": actor_email,
            "before": before_state,
            "after": after_state
        }
        current_hash = self.compute_event_hash(prev_hash, payload)

        event = AuditChain(
            inspection_id=inspection_id,
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            before_state=before_state,
            after_state=after_state,
            request_id=request_id,
            previous_hash=prev_hash,
            current_hash=current_hash
        )
        return await repo.create(event)

    async def verify_inspection_chain(
        self,
        session: AsyncSession,
        inspection_id: uuid.UUID
    ) -> AuditVerificationResponse:
        repo = AuditRepository(session)
        events = await repo.get_by_inspection_id(inspection_id)

        if not events:
            return AuditVerificationResponse(
                inspection_id=str(inspection_id),
                intact=True,
                total_events=0,
                algorithm="SHA-256",
                records=[]
            )

        records_schema = [AuditEventSchema.model_validate(e) for e in events]
        
        # Verify chain integrity
        prev_hash = events[0].previous_hash
        for event in events:
            payload = {
                "action": event.action,
                "entity_type": event.entity_type,
                "entity_id": str(event.entity_id),
                "actor": event.actor_email,
                "before": event.before_state,
                "after": event.after_state
            }
            expected_hash = self.compute_event_hash(prev_hash, payload)
            if expected_hash != event.current_hash or event.previous_hash != prev_hash:
                return AuditVerificationResponse(
                    inspection_id=str(inspection_id),
                    intact=False,
                    total_events=len(events),
                    broken_at_event_id=str(event.id),
                    algorithm="SHA-256",
                    records=records_schema
                )
            prev_hash = event.current_hash

        return AuditVerificationResponse(
            inspection_id=str(inspection_id),
            intact=True,
            total_events=len(events),
            broken_at_event_id=None,
            algorithm="SHA-256",
            records=records_schema
        )


audit_service = AuditService()
