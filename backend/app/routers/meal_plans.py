from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MealPlan, Mother, Report, ContinuousMonitoring
from app.schemas.meal_plan import (
    MealPlanGenerateRequest,
    MealPlanDoctorCreateRequest,
    MealPlanUpdateRequest,
    MealPlanResponse,
)
from app.core.security import get_current_user, require_role, CurrentUser
from app.agents.nutritionist_agent import generate_meal_plan

router = APIRouter()


def _authorize_view_access(mother: Mother, user: CurrentUser):
    """Mother, her managing PHM, or her assigned doctor can view meal plans."""
    allowed = (
        (user.role == "mother" and str(mother.id) == user.id)
        or (user.role == "phm" and str(mother.phm_id) == user.id)
        or (user.role == "doctor" and mother.doctor_id and str(mother.doctor_id) == user.id)
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this mother's meal plans")


def _authorize_review_access(mother: Mother, user: CurrentUser):
    """Only her managing PHM or her assigned doctor can confirm/edit/author - not the mother herself, this is a clinical review step."""
    allowed = (
        (user.role == "phm" and str(mother.phm_id) == user.id)
        or (user.role == "doctor" and mother.doctor_id and str(mother.doctor_id) == user.id)
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have review access for this mother's meal plans")


@router.post("/generate", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_plan(
    payload: MealPlanGenerateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """PHM or assigned doctor triggers the Nutritionist Agent for a mother.
    Creates a plan with status=pending_review, origin=agent."""
    mother = db.query(Mother).filter(Mother.id == payload.mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    _authorize_review_access(mother, user)

    reports = db.query(Report).filter(Report.mother_id == mother.id).order_by(Report.created_at.desc()).limit(5).all()
    monitoring = (
        db.query(ContinuousMonitoring)
        .filter(ContinuousMonitoring.mother_id == mother.id)
        .order_by(ContinuousMonitoring.visit_date.desc())
        .limit(4)
        .all()
    )

    result = generate_meal_plan(
        mother_id=str(mother.id),
        reports=[{"report_type": r.report_type, "risk_level": r.risk_level, "hb_level": r.hb_level} for r in reports],
        monitoring_history=[{"bp_systolic": m.bp_systolic, "bp_diastolic": m.bp_diastolic, "weight_kg": m.weight_kg} for m in monitoring],
    )

    plan = MealPlan(
        mother_id=mother.id,
        source_report_id=reports[0].id if reports else None,
        trimester=result.get("trimester"),
        plan_sinhala_msg=result.get("plan_sinhala_msg", ""),
        warning_sinhala_msg=result.get("warning_sinhala_msg"),
        origin="agent",
        status="pending_review",
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
def doctor_author_plan(
    payload: MealPlanDoctorCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("doctor")),
):
    """A doctor writes a meal plan directly, bypassing the agent entirely."""
    mother = db.query(Mother).filter(Mother.id == payload.mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    _authorize_review_access(mother, user)

    plan = MealPlan(
        mother_id=mother.id,
        trimester=payload.trimester,
        plan_sinhala_msg=payload.plan_sinhala_msg,
        warning_sinhala_msg=payload.warning_sinhala_msg,
        origin="doctor_authored",
        status="confirmed",
        reviewed_by_role="doctor",
        reviewed_by_id=UUID(user.id),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("", response_model=list[MealPlanResponse])
def list_meal_plans(
    mother_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    mother = db.query(Mother).filter(Mother.id == mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    _authorize_view_access(mother, user)

    return (
        db.query(MealPlan)
        .filter(MealPlan.mother_id == mother_id)
        .order_by(MealPlan.created_at.desc())
        .all()
    )


@router.post("/{plan_id}/confirm", response_model=MealPlanResponse)
def confirm_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    try:
        plan_uuid = UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan_id format")
    plan = db.query(MealPlan).filter(MealPlan.id == plan_uuid).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found")

    mother = db.query(Mother).filter(Mother.id == plan.mother_id).first()
    _authorize_review_access(mother, user)

    plan.status = "confirmed"
    plan.reviewed_by_role = user.role
    plan.reviewed_by_id = UUID(user.id)
    db.commit()
    db.refresh(plan)
    return plan


@router.patch("/{plan_id}", response_model=MealPlanResponse)
def edit_plan(
    plan_id: str,
    payload: MealPlanUpdateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    try:
        plan_uuid = UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan_id format")
    plan = db.query(MealPlan).filter(MealPlan.id == plan_uuid).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found")

    mother = db.query(Mother).filter(Mother.id == plan.mother_id).first()
    _authorize_review_access(mother, user)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(plan, field, value)
    plan.status = "edited"
    plan.reviewed_by_role = user.role
    plan.reviewed_by_id = UUID(user.id)

    db.commit()
    db.refresh(plan)
    return plan