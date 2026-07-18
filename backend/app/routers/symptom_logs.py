from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SymptomLog, Mother, Alert
from app.schemas.symptom_log import SymptomLogCreateRequest, SymptomLogResponse
from app.core.security import get_current_user, require_role, CurrentUser
from app.agents.emergency_agent import check_symptom_log

router = APIRouter()

VALID_ALERT_SEVERITIES = {"high", "critical"}


def _authorize_mother_access(mother: Mother, user: CurrentUser):
    allowed = (
        (user.role == "mother" and str(mother.id) == user.id)
        or (user.role == "phm" and str(mother.phm_id) == user.id)
        or (user.role == "doctor" and mother.doctor_id and str(mother.doctor_id) == user.id)
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this mother's symptom logs")


@router.post("", response_model=SymptomLogResponse, status_code=status.HTTP_201_CREATED)
def submit_symptom_log(
    payload: SymptomLogCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("mother")),
):
    """
    Only a mother can submit her own symptom check-in (used when she's not
    near her PHM). Runs the Emergency Agent's symptom check immediately - if
    a danger sign is flagged, an Alert is created automatically for her PHM.
    """
    mother = db.query(Mother).filter(Mother.id == UUID(user.id)).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")

    check_result = check_symptom_log(payload.symptoms)

    log = SymptomLog(
        mother_id=mother.id,
        symptoms=",".join(payload.symptoms),
        danger_sign_detected=check_result.get("danger_sign_detected", False),
        risk_level=check_result.get("risk_level"),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    if check_result.get("should_alert"):
        severity = check_result.get("risk_level")
        if severity not in VALID_ALERT_SEVERITIES:
            severity = "high"  # safe fallback so a malformed agent response never blocks an alert being raised
        alert = Alert(
            mother_id=mother.id,
            phm_id=mother.phm_id,
            source_type="symptom_log",
            symptom_log_id=log.id,
            severity=severity,
            message_sinhala=check_result.get("message_sinhala", ""),
            status="open",
        )
        db.add(alert)
        db.commit()

    return log


@router.get("", response_model=list[SymptomLogResponse])
def list_symptom_logs(
    mother_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    mother = db.query(Mother).filter(Mother.id == mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    _authorize_mother_access(mother, user)

    return (
        db.query(SymptomLog)
        .filter(SymptomLog.mother_id == mother_id)
        .order_by(SymptomLog.created_at.desc())
        .all()
    )