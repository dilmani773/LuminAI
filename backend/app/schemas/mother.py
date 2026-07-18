from uuid import UUID
from datetime import date, datetime

from pydantic import BaseModel

from app.schemas.report import ReportResponse
from app.schemas.monitoring import MonitoringResponse
from app.schemas.alert import AlertResponse


class MotherRegisterRequest(BaseModel):
    full_name: str
    phone: str
    password: str
    phm_id: UUID  # mother must register under an existing PHM
    age: int | None = None
    blood_group: str | None = None
    known_allergies: str | None = None
    lmp_date: date | None = None
    edd_date: date | None = None
    gravidity: str | None = None
    past_obstetric_history: str | None = None
    identified_risk_conditions: str | None = None


class MotherResponse(BaseModel):
    id: UUID
    full_name: str
    phone: str
    age: int | None = None
    clinic_registration_date: date | None = None
    blood_group: str | None = None
    known_allergies: str | None = None
    lmp_date: date | None = None
    edd_date: date | None = None
    gravidity: str | None = None
    phm_id: UUID
    doctor_id: UUID | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class MotherUpdateRequest(BaseModel):
    """
    All fields optional - only what's sent gets updated. Deliberately excludes
    phone, password, and phm_id: changing login identity or reassigning a PHM
    are separate, more sensitive actions, not a casual profile edit.
    """
    full_name: str | None = None
    age: int | None = None
    blood_group: str | None = None
    known_allergies: str | None = None
    lmp_date: date | None = None
    edd_date: date | None = None
    gravidity: str | None = None
    past_obstetric_history: str | None = None
    identified_risk_conditions: str | None = None


class MotherSummaryResponse(BaseModel):
    """
    One-call view for dashboard patient lists / patient detail headers:
    profile + latest report + latest monitoring entry + open alerts.
    """
    profile: MotherResponse
    latest_report: ReportResponse | None = None
    latest_monitoring: MonitoringResponse | None = None
    open_alerts: list[AlertResponse] = []


class DoctorAssignRequest(BaseModel):
    doctor_id: UUID