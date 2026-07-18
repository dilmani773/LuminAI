from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report, Mother
from app.schemas.report import ReportResponse
from app.core.security import get_current_user, CurrentUser
from app.services.file_storage import save_upload
from app.agents.report_analysis_agent import analyze_report

router = APIRouter()

VALID_REPORT_TYPES = {"fbc", "urine", "blood_sugar", "ultrasound", "card_scan", "other"}


def _authorize_mother_access(mother: Mother, user: CurrentUser):
    allowed = (
        (user.role == "mother" and str(mother.id) == user.id)
        or (user.role == "phm" and str(mother.phm_id) == user.id)
        or (user.role == "doctor" and mother.doctor_id and str(mother.doctor_id) == user.id)
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this mother's reports")


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def upload_report(
    mother_id: UUID = Form(...),
    report_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """
    A mother uploads her own report, or a PHM uploads on behalf of a mother
    she manages. Runs the Report Analysis Agent synchronously before saving,
    so the response already includes risk_level + explanation_sinhala.
    """
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"report_type must be one of {sorted(VALID_REPORT_TYPES)}",
        )

    mother = db.query(Mother).filter(Mother.id == mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")

    if user.role == "mother":
        if str(mother.id) != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Mothers can only upload their own reports")
        uploaded_by_role, uploaded_by_id = "mother", UUID(user.id)
    elif user.role == "phm":
        if str(mother.phm_id) != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only upload reports for mothers you manage")
        uploaded_by_role, uploaded_by_id = "phm", UUID(user.id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only a mother or her PHM can upload reports")

    file_bytes = file.file.read()
    file_url = save_upload(file_bytes, file.filename or "upload")

    analysis = analyze_report(file_url, report_type)

    report = Report(
        mother_id=mother_id,
        report_type=report_type,
        file_url=file_url,
        uploaded_by_role=uploaded_by_role,
        uploaded_by_id=uploaded_by_id,
        hb_level=analysis.get("hb_level"),
        blood_sugar=analysis.get("blood_sugar"),
        urine_protein=analysis.get("urine_protein"),
        risk_level=analysis.get("risk_level"),
        explanation_sinhala=analysis.get("explanation_sinhala"),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=list[ReportResponse])
def list_reports(
    mother_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    mother = db.query(Mother).filter(Mother.id == mother_id).first()
    if not mother:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mother not found")
    _authorize_mother_access(mother, user)

    return (
        db.query(Report)
        .filter(Report.mother_id == mother_id)
        .order_by(Report.created_at.desc())
        .all()
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    try:
        report_uuid = UUID(report_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report_id format")

    report = db.query(Report).filter(Report.id == report_uuid).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    mother = db.query(Mother).filter(Mother.id == report.mother_id).first()
    _authorize_mother_access(mother, user)
    return report