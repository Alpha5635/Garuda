import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditEventSchema(BaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID | None = None
    actor_email: str
    action: str
    entity_type: str
    entity_id: str
    before_state: dict | None = None
    after_state: dict | None = None
    previous_hash: str
    current_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditVerificationResponse(BaseModel):
    inspection_id: str
    intact: bool
    total_events: int
    broken_at_event_id: str | None = None
    algorithm: str = "SHA-256"
    records: list[AuditEventSchema] = []
