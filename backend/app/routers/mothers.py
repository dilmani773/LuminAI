from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mother, Report, ContinuousMonitoring, Alert
from app.schemas.mother import MotherResponse, MotherUpdateRequest, MotherSummaryResponse
from app.core.security import get_current_user, CurrentUser

router = APIRouter()


def _get_mother_or_404(mother_id: str, db: Session) -> Mother:
    try:
        mother_uuid = UUID(mother_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid mother_id format")
    mother = db.query(Mother).filter(Mother.id == mother_uuid).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    return mother


def _authorize_access(mother: Mother, user: CurrentUser):
    """
    Who can view/edit a mother's profile:
    - the mother herself
    - the PHM who manages her
    - the doctor assigned to her
    (Any-doctor emergency access goes through the separate break-glass
    endpoint, not this one, since that path requires a logged reason.)
    """
    allowed = (
        (user.role == "mother" and str(mother.id) == user.id)
        or (user.role == "phm" and str(mother.phm_id) == user.id)
        or (user.role == "doctor" and mother.doctor_id and str(mother.doctor_id) == user.id)
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this mother's profile",
        )


@router.get("/{mother_id}", response_model=MotherResponse)
def get_mother(mother_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    mother = _get_mother_or_404(mother_id, db)
    _authorize_access(mother, user)
    return mother


@router.patch("/{mother_id}", response_model=MotherResponse)
def update_mother(
    mother_id: str,
    payload: MotherUpdateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    mother = _get_mother_or_404(mother_id, db)
    _authorize_access(mother, user)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(mother, field, value)

    db.commit()
    db.refresh(mother)
    return mother


@router.get("/{mother_id}/summary", response_model=MotherSummaryResponse)
def get_mother_summary(mother_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    """
    One call for dashboard patient-list / patient-detail screens: profile +
    latest report + latest monitoring entry + open alerts.
    """
    mother = _get_mother_or_404(mother_id, db)
    _authorize_access(mother, user)

    latest_report = (
        db.query(Report)
        .filter(Report.mother_id == mother.id)
        .order_by(Report.created_at.desc())
        .first()
    )
    latest_monitoring = (
        db.query(ContinuousMonitoring)
        .filter(ContinuousMonitoring.mother_id == mother.id)
        .order_by(ContinuousMonitoring.visit_date.desc())
        .first()
    )
    open_alerts = (
        db.query(Alert)
        .filter(Alert.mother_id == mother.id, Alert.status == "open")
        .order_by(Alert.created_at.desc())
        .all()
    )

    return MotherSummaryResponse(
        profile=mother,
        latest_report=latest_report,
        latest_monitoring=latest_monitoring,
        open_alerts=open_alerts,
    )