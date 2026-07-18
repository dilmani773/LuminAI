from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ContinuousMonitoring, Mother, Alert
from app.schemas.monitoring import MonitoringCreateRequest, MonitoringResponse
from app.core.security import get_current_user, require_role, CurrentUser
from app.agents.emergency_agent import check_monitoring_trend

router = APIRouter()

VALID_ALERT_SEVERITIES = {"high", "critical"}


def _authorize_mother_access(mother: Mother, user: CurrentUser):
    allowed = (
        (user.role == "mother" and str(mother.id) == user.id)
        or (user.role == "phm" and str(mother.phm_id) == user.id)
        or (user.role == "doctor" and mother.doctor_id and str(mother.doctor_id) == user.id)
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this mother's monitoring history")


def _entry_to_dict(entry: ContinuousMonitoring) -> dict:
    return {
        "visit_date": entry.visit_date.isoformat() if entry.visit_date else None,
        "bp_systolic": entry.bp_systolic,
        "bp_diastolic": entry.bp_diastolic,
        "weight_kg": entry.weight_kg,
        "fundal_height_cm": entry.fundal_height_cm,
        "urine_protein": entry.urine_protein,
        "oedema": entry.oedema,
        "fhs": entry.fhs,
    }


@router.post("", response_model=MonitoringResponse, status_code=status.HTTP_201_CREATED)
def log_monitoring_entry(
    payload: MonitoringCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("phm")),
):
    """
    Only a PHM can log a monitoring entry, and only for a mother she manages.
    After saving, runs the Emergency Agent's trend check across her recent
    history - if a dangerous pattern is flagged, an Alert is created
    automatically for the responsible PHM.
    """
    mother = db.query(Mother).filter(Mother.id == payload.mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    if str(mother.phm_id) != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only log monitoring entries for mothers you manage",
        )

    entry = ContinuousMonitoring(
        mother_id=payload.mother_id,
        recorded_by_phm_id=UUID(user.id),
        visit_date=payload.visit_date or datetime.utcnow(),
        bp_systolic=payload.bp_systolic,
        bp_diastolic=payload.bp_diastolic,
        weight_kg=payload.weight_kg,
        fundal_height_cm=payload.fundal_height_cm,
        urine_protein=payload.urine_protein,
        oedema=payload.oedema,
        fhs=payload.fhs,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Pull last 4 entries (including the one just saved), oldest first, for the trend check
    recent = (
        db.query(ContinuousMonitoring)
        .filter(ContinuousMonitoring.mother_id == payload.mother_id)
        .order_by(ContinuousMonitoring.visit_date.desc())
        .limit(4)
        .all()
    )
    recent.reverse()
    trend_result = check_monitoring_trend([_entry_to_dict(e) for e in recent])

    if trend_result.get("should_alert"):
        severity = trend_result.get("risk_level")
        if severity not in VALID_ALERT_SEVERITIES:
            severity = "high"  # safe fallback so a malformed agent response never blocks an alert being raised
        alert = Alert(
            mother_id=mother.id,
            phm_id=mother.phm_id,
            source_type="monitoring_trend",
            monitoring_entry_id=entry.id,
            severity=severity,
            message_sinhala=trend_result.get("message_sinhala", ""),
            status="open",
        )
        db.add(alert)
        db.commit()

    return entry


@router.get("", response_model=list[MonitoringResponse])
def list_monitoring_entries(
    mother_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    mother = db.query(Mother).filter(Mother.id == mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    _authorize_mother_access(mother, user)

    return (
        db.query(ContinuousMonitoring)
        .filter(ContinuousMonitoring.mother_id == mother_id)
        .order_by(ContinuousMonitoring.visit_date.desc())
        .all()
    )