from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr


class PHMRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    moh_zone: str
    phone: str | None = None


class PHMResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    moh_zone: str
    phone: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True  # lets this read straight off the SQLAlchemy model