from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Mother
from app.schemas.appointment import AppointmentCreateRequest, AppointmentUpdateRequest, AppointmentResponse
from app.core.security import get_current_user, require_role, CurrentUser

router = APIRouter()

VALID_STATUSES = {"scheduled", "completed", "missed", "cancelled"}


def _get_appointment_or_404(appointment_id: str, db: Session) -> Appointment:
    try:
        appt_uuid = UUID(appointment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid appointment_id format")
    appt = db.query(Appointment).filter(Appointment.id == appt_uuid).first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appt


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("phm")),
):
    """Only a PHM can schedule an appointment, and only for a mother she manages."""
    mother = db.query(Mother).filter(Mother.id == payload.mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    if str(mother.phm_id) != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only schedule appointments for mothers you manage",
        )

    appt = Appointment(
        mother_id=payload.mother_id,
        phm_id=UUID(user.id),
        scheduled_date=payload.scheduled_date,
        notes=payload.notes,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    mother_id: UUID = Query(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    mother = db.query(Mother).filter(Mother.id == mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")

    allowed = (
        (user.role == "mother" and str(mother.id) == user.id)
        or (user.role == "phm" and str(mother.phm_id) == user.id)
        or (user.role == "doctor" and mother.doctor_id and str(mother.doctor_id) == user.id)
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this mother's appointments")

    return (
        db.query(Appointment)
        .filter(Appointment.mother_id == mother_id)
        .order_by(Appointment.scheduled_date.desc())
        .all()
    )


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: str,
    payload: AppointmentUpdateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("phm")),
):
    """Only the PHM who scheduled it can update it (status, notes, reschedule)."""
    appt = _get_appointment_or_404(appointment_id, db)
    if str(appt.phm_id) != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own appointments")

    updates = payload.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"status must be one of {sorted(VALID_STATUSES)}",
        )

    for field, value in updates.items():
        setattr(appt, field, value)

    db.commit()
    db.refresh(appt)
    return appt