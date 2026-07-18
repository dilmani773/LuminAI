from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class MonitoringCreateRequest(BaseModel):
    mother_id: UUID
    visit_date: datetime | None = None  # defaults to now if not provided
    bp_systolic: float | None = None
    bp_diastolic: float | None = None
    weight_kg: float | None = None
    fundal_height_cm: float | None = None
    urine_protein: str | None = None
    oedema: bool = False
    fhs: str | None = None


class MonitoringResponse(BaseModel):
    id: UUID
    mother_id: UUID
    visit_date: datetime
    bp_systolic: float | None = None
    bp_diastolic: float | None = None
    weight_kg: float | None = None
    fundal_height_cm: float | None = None
    urine_protein: str | None = None
    oedema: bool | None = None
    fhs: str | None = None

    class Config:
        from_attributes = True