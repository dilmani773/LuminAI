from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class SymptomLogCreateRequest(BaseModel):
    symptoms: list[str]  # e.g. ["severe_headache", "blurry_vision"]


class SymptomLogResponse(BaseModel):
    id: UUID
    mother_id: UUID
    symptoms: str
    danger_sign_detected: bool
    risk_level: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True