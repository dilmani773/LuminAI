from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, Mother
from app.schemas.alert import AlertResponse
from app.core.security import get_current_user, require_role, CurrentUser

router = APIRouter()

VALID_STATUSES = {"open", "resolved"}


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """
    PHMs see their own alerts (who the alert is addressed to is always the
    logged-in PHM - never taken from a query param, so a PHM can't read
    another PHM's alerts by guessing an id). Doctors see alerts for mothers
    currently assigned to them, read-only.
    """
    if status_filter and status_filter not in VALID_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"status must be one of {sorted(VALID_STATUSES)}")

    if user.role == "phm":
        query = db.query(Alert).filter(Alert.phm_id == UUID(user.id))
    elif user.role == "doctor":
        query = (
            db.query(Alert)
            .join(Mother, Alert.mother_id == Mother.id)
            .filter(Mother.doctor_id == UUID(user.id))
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only a PHM or doctor can view alerts")

    if status_filter:
        query = query.filter(Alert.status == status_filter)

    return query.order_by(Alert.created_at.desc()).all()


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("phm")),
):
    """Only the PHM the alert is addressed to can resolve it."""
    try:
        alert_uuid = UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid alert_id format")

    alert = db.query(Alert).filter(Alert.id == alert_uuid).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    if str(alert.phm_id) != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only resolve alerts addressed to you")

    alert.status = "resolved"
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert