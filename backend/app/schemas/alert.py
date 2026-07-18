from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: UUID
    mother_id: UUID
    phm_id: UUID
    source_type: str
    severity: str
    message_sinhala: str
    status: str
    created_at: datetime
    resolved_at: datetime | None = None

    class Config:
        from_attributes = True