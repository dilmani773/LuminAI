from uuid import UUID
from datetime import date, datetime

from pydantic import BaseModel


class BreakGlassRequest(BaseModel):
    mother_phone: str  # doctor looks her up by phone, not internal ID - matches a real emergency
    reason: str        # required - short text, e.g. "referred for high BP at Base Hospital"


class BreakGlassResponse(BaseModel):
    """
    Only the critical info an emergency doctor actually needs - not the
    mother's full record. Deliberately narrow.
    """
    mother_id: UUID
    full_name: str
    age: int | None = None
    blood_group: str | None = None
    known_allergies: str | None = None
    edd_date: date | None = None
    gravidity: str | None = None
    identified_risk_conditions: str | None = None
    latest_risk_level: str | None = None  # from her most recent report, if any
    access_logged_at: datetime