from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class MealPlanGenerateRequest(BaseModel):
    mother_id: UUID


class MealPlanDoctorCreateRequest(BaseModel):
    """A doctor authoring a meal plan directly, bypassing the agent."""
    mother_id: UUID
    trimester: str | None = None
    plan_sinhala_msg: str
    warning_sinhala_msg: str | None = None


class MealPlanUpdateRequest(BaseModel):
    plan_sinhala_msg: str | None = None
    warning_sinhala_msg: str | None = None


class MealPlanResponse(BaseModel):
    id: UUID
    mother_id: UUID
    source_report_id: UUID | None = None
    trimester: str | None = None
    plan_sinhala_msg: str
    warning_sinhala_msg: str | None = None
    origin: str
    status: str
    reviewed_by_role: str | None = None
    reviewed_by_id: UUID | None = None
    created_at: datetime

    class Config:
        from_attributes = True