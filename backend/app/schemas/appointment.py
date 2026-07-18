from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class AppointmentCreateRequest(BaseModel):
    mother_id: UUID
    scheduled_date: datetime
    notes: str | None = None


class AppointmentUpdateRequest(BaseModel):
    """All optional - only what's sent gets updated."""
    scheduled_date: datetime | None = None
    status: str | None = None   # "scheduled" | "completed" | "missed" | "cancelled"
    notes: str | None = None


class AppointmentResponse(BaseModel):
    id: UUID
    mother_id: UUID
    phm_id: UUID
    scheduled_date: datetime
    status: str
    notes: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True