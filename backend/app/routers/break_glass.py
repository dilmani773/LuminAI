from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mother, Report, BreakGlassAccess
from app.schemas.break_glass import BreakGlassRequest, BreakGlassResponse
from app.core.security import require_role, CurrentUser

router = APIRouter()


@router.post("", response_model=BreakGlassResponse, status_code=status.HTTP_201_CREATED)
def request_break_glass_access(
    payload: BreakGlassRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("doctor")),
):
    """
    Any logged-in doctor can request emergency access to any mother's
    critical profile - not just their assigned mothers. This covers both a
    genuine emergency and a mother voluntarily seeing a different doctor
    (see docs discussion) - no real-time mother consent is required, but a
    reason is mandatory and every access is permanently logged for
    accountability.
    """
    if not payload.reason or not payload.reason.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A reason is required for emergency access")

    mother = db.query(Mother).filter(Mother.phone == payload.mother_phone).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No mother found with that phone number")

    # Log the access BEFORE returning any data - if logging fails, access should fail too
    access_log = BreakGlassAccess(
        mother_id=mother.id,
        doctor_id=UUID(user.id),
        reason=payload.reason.strip(),
    )
    db.add(access_log)
    db.commit()
    db.refresh(access_log)

    latest_report = (
        db.query(Report)
        .filter(Report.mother_id == mother.id)
        .order_by(Report.created_at.desc())
        .first()
    )

    return BreakGlassResponse(
        mother_id=mother.id,
        full_name=mother.full_name,
        age=mother.age,
        blood_group=mother.blood_group,
        known_allergies=mother.known_allergies,
        edd_date=mother.edd_date,
        gravidity=mother.gravidity,
        identified_risk_conditions=mother.identified_risk_conditions,
        latest_risk_level=latest_report.risk_level if latest_report else None,
        access_logged_at=access_log.accessed_at,
    )