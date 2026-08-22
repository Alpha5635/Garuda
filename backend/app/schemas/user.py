import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole = UserRole.OFFICER
    organisation_id: uuid.UUID | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    organisation_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
