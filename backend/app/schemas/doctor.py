from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr


class DoctorRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    specialization: str | None = None
    phone: str | None = None


class DoctorResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    specialization: str | None = None
    phone: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True