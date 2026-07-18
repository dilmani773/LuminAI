from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: UUID
    mother_id: UUID
    report_type: str
    file_url: str
    hb_level: str | None = None
    blood_sugar: str | None = None
    urine_protein: str | None = None
    risk_level: str | None = None
    explanation_sinhala: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True