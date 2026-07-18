from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Doctor, Mother
from app.schemas.doctor import DoctorResponse
from app.schemas.mother import MotherResponse
from app.core.security import require_role, CurrentUser

router = APIRouter()


@router.get("/me", response_model=DoctorResponse)
def get_my_profile(db: Session = Depends(get_db), user: CurrentUser = Depends(require_role("doctor"))):
    doctor = db.query(Doctor).filter(Doctor.id == UUID(user.id)).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor


@router.get("/me/mothers", response_model=list[MotherResponse])
def get_my_assigned_mothers(db: Session = Depends(get_db), user: CurrentUser = Depends(require_role("doctor"))):
    """List every mother assigned to the currently logged-in doctor. This is
    her regular assigned caseload - not the same as break-glass access,
    which lets a doctor look up ANY mother in an emergency (see
    routers/break_glass.py)."""
    return db.query(Mother).filter(Mother.doctor_id == UUID(user.id)).all()